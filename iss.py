def read_file(filename):
    with open(filename, "r") as f:
        return f.readlines()

def load_dmem(filename):
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            addr_str, val_str = line.split(":")

            addr = int(addr_str.strip(), 16)
            val  = int(val_str.strip(), 16)

            memory[addr] = val & 0xFF

def dump_dmem_RARS(filename):
    if not memory:
        print("Bo nho trong.")
        return

    BASE_ADDR = 0x10010000

    # 1. Loc dia chi >= BASE_ADDR
    all_addrs = sorted(addr for addr in memory.keys() if addr >= BASE_ADDR)

    if not all_addrs:
        print("Khong co du lieu tu 0x10010000 tro len.")
        return

    start_addr = (all_addrs[0] // 32) * 32
    end_addr = (all_addrs[-1] // 32) * 32 + 32

    with open(filename, "w") as f:
        for row_addr in range(start_addr, end_addr, 32):

            # Bo qua cac dong nho hon BASE_ADDR
            if row_addr < BASE_ADDR:
                continue

            line = f"0x{row_addr:08x}"
            line += "    "

            words_in_row = []
            for word_idx in range(8):
                base_word_addr = row_addr + (word_idx * 4)

                b0 = memory.get(base_word_addr, 0)
                b1 = memory.get(base_word_addr + 1, 0)
                b2 = memory.get(base_word_addr + 2, 0)
                b3 = memory.get(base_word_addr + 3, 0)

                word_val = (b3 << 24) | (b2 << 16) | (b1 << 8) | b0
                words_in_row.append(f"0x{word_val:08x}")

            line += " ".join(words_in_row)
            f.write(line + "\n")

def dump_registers(filename):
    with open(filename, "w") as f:
        for i in range(32):
            val = registers[i] & 0xFFFFFFFF
            f.write(f"x{i:02d} : 0x{val:08x}\n")
        f.write(f"PC  : 0x{PC:08x}\n")

def dump_dmem(filename):
    with open(filename, "w") as f:
        for addr in sorted(memory.keys()):
            val = memory[addr] & 0xFF
            f.write(f"0x{addr:08x} : 0x{val:02x}\n")


def to_signed(value):
    value &= 0xFFFFFFFF
    if value & 0x80000000:
        return value - 0x100000000
    return value

def ALU(op, rs1, rs2):
    a = rs1 & 0xFFFFFFFF
    b = rs2 & 0xFFFFFFFF
    res = 0

    if op == "add":
        res = a + b

    elif op == "sub":
        res = a - b

    elif op == "xor":
        res = a ^ b

    elif op == "or":
        res = a | b

    elif op == "and":
        res = a & b

    elif op == "sll":
        res = a << (b & 0x1F)

    elif op == "srl":
        res = a >> (b & 0x1F)

    elif op == "sra":
        res = to_signed(a) >> (b & 0x1F)

    elif op == "slt":
        res = 1 if to_signed(a) < to_signed(b) else 0

    elif op == "sltu":
        res = 1 if a < b else 0

    return res & 0xFFFFFFFF

def Get_BrUn(code):
    opcode = code & 0x7f
    funct3 = (code >> 12) & 0x7
    if opcode == 0b1100011 and funct3 in [0x6, 0x7]:
        return 1
    return 0

def Branch_Comp(BrUn, RS1, RS2):
    u_rs1 = RS1 & 0xFFFFFFFF
    u_rs2 = RS2 & 0xFFFFFFFF

    BrEQ = 1 if u_rs1 == u_rs2 else 0
    
    if BrUn == 1:
        BrLT = 1 if u_rs1 < u_rs2 else 0
    else:
        s_rs1 = u_rs1 if u_rs1 < 0x80000000 else u_rs1 - 0x100000000
        s_rs2 = u_rs2 if u_rs2 < 0x80000000 else u_rs2 - 0x100000000
        
        BrLT = 1 if s_rs1 < s_rs2 else 0

    return BrEQ, BrLT

def write_byte(addr, value):
    memory[addr & 0xFFFFFFFF] = value & 0xFF

def read_byte(addr):
    return memory.get(addr & 0xFFFFFFFF, 0x00)

def DMEM(addr, write_data, MemRW, LoadType, StoreType):
    # XỬ LÝ GHI (STORE)
    if MemRW == "WRITE":
        if StoreType == "sb":
            write_byte(addr, write_data)
            
        elif StoreType == "sh":
            write_byte(addr, write_data)
            write_byte(addr + 1, write_data >> 8)
            
        elif StoreType == "sw":
            write_byte(addr, write_data)
            write_byte(addr + 1, write_data >> 8)
            write_byte(addr + 2, write_data >> 16)
            write_byte(addr + 3, write_data >> 24)
        return 0

    # XỬ LÝ ĐỌC (LOAD)
    else:
        b0 = read_byte(addr)
        b1 = read_byte(addr + 1)
        b2 = read_byte(addr + 2)
        b3 = read_byte(addr + 3)
        
        raw_32 = b0 | (b1 << 8) | (b2 << 16) | (b3 << 24)

        if LoadType == "lb":
            val = b0
            return (val ^ 0x80) - 0x80
            
        elif LoadType == "lbu":
            return b0
            
        elif LoadType == "lh":
            val = b0 | (b1 << 8)
            return (val ^ 0x8000) - 0x8000
            
        elif LoadType == "lhu":
            return b0 | (b1 << 8)
            
        elif LoadType == "lw":
            return raw_32
            
        return 0

def ImmGen(code, ImmSel):
    imm = 0

    if ImmSel == "I":
        imm = (code >> 20) & 0xFFF
        # Mở rộng dấu (bit 11)
        if imm & 0x800:
            imm -= 0x1000

    elif ImmSel == "S":
        imm_4_0 = (code >> 7) & 0x1F
        imm_11_5 = (code >> 25) & 0x7F
        imm = (imm_11_5 << 5) | imm_4_0
        # Mở rộng dấu (bit 11)
        if imm & 0x800:
            imm -= 0x1000

    elif ImmSel == "B":
        imm_11 = (code >> 7) & 0x1
        imm_4_1 = (code >> 8) & 0x0F
        imm_10_5 = (code >> 25) & 0x3F
        imm_12 = (code >> 31) & 0x1
        imm = (imm_12 << 12) | (imm_11 << 11) | (imm_10_5 << 5) | (imm_4_1 << 1)
        # Mở rộng dấu (bit 12)
        if imm & 0x1000:
            imm -= 0x2000

    elif ImmSel == "U":
        imm = code & 0xFFFFF000
        # Mở rộng dấu (bit 31) cho Python xử lý số âm
        if imm & 0x80000000:
            imm -= 0x100000000

    elif ImmSel == "J":
        imm_20 = (code >> 31) & 0x1
        imm_19_12 = (code >> 12) & 0xFF
        imm_11 = (code >> 20) & 0x1
        imm_10_1 = (code >> 21) & 0x3FF
        imm = (imm_20 << 20) | (imm_19_12 << 12) | (imm_11 << 11) | (imm_10_1 << 1)
        if imm & 0x100000:
            imm -= 0x200000

    return imm

def Read_Register_File(code):

    rd_addr = (code >> 7) & 0x1F
    rs1_addr = (code >> 15) & 0x1F
    rs2_addr = (code >> 20) & 0x1F
    #  HÀNH ĐỘNG ĐỌC 
    val_rs1 = registers[rs1_addr]
    val_rs2 = registers[rs2_addr]

    return val_rs1, val_rs2

def Write_Register_File(code, wdata, RegWEn):

    rd_addr = (code >> 7) & 0x1F
    rs1_addr = (code >> 15) & 0x1F
    rs2_addr = (code >> 20) & 0x1F

    # HÀNH ĐỘNG GHI 
    if RegWEn == 1 and rd_addr != 0:
        registers[rd_addr] = wdata & 0xFFFFFFFF

    return

def Control_Logic(code, BrEq, BrLt):
    opcode = code & 0x7f
    funct3 = (code >> 12) & 0x7
    funct7 = (code >> 25) & 0x7f

    # --- Khởi tạo giá trị mặc định 
    ImmSel = None
    RegWEn = 0
    ASel = "RS1"
    BSel = "RS2"
    ALUSel = "add"
    MemRW = "READ"
    WBSel = "ALU"
    PCSel = "PC+4"
    LoadType = None
    StoreType = None

    # R-TYPE (Các lệnh tính toán thanh ghi - thanh ghi)
    if opcode == 0b0110011:
        RegWEn = 1
        ASel = "RS1"
        BSel = "RS2"
        WBSel = "ALU"
        if funct3 == 0x0:
            ALUSel = "sub" if funct7 == 0x20 else "add"
        elif funct3 == 0x1:
            ALUSel = "sll"
        elif funct3 == 0x2:
            ALUSel = "slt"
        elif funct3 == 0x3:
            ALUSel = "sltu"
        elif funct3 == 0x4:
            ALUSel = "xor"
        elif funct3 == 0x5:
            ALUSel = "sra" if funct7 == 0x20 else "srl"
        elif funct3 == 0x6:
            ALUSel = "or"
        elif funct3 == 0x7:
            ALUSel = "and"

    # I-TYPE ARITHMETIC 
    elif opcode == 0b0010011:
        ImmSel = "I"
        RegWEn = 1
        ASel = "RS1"
        BSel = "IMM"
        WBSel = "ALU"
        if funct3 == 0x0:
            ALUSel = "add"
        elif funct3 == 0x1:
            ALUSel = "sll"
        elif funct3 == 0x2:
            ALUSel = "slt"
        elif funct3 == 0x3:
            ALUSel = "sltu"
        elif funct3 == 0x4:
            ALUSel = "xor"
        elif funct3 == 0x5:
            ALUSel = "sra" if funct7 == 0x20 else "srl"
        elif funct3 == 0x6:
            ALUSel = "or"
        elif funct3 == 0x7:
            ALUSel = "and"

    # I-TYPE LOAD (lw, lb, lh, lbu, lhu)
    elif opcode == 0b0000011:
        ImmSel = "I"
        RegWEn = 1
        ASel = "RS1"
        BSel = "IMM"
        ALUSel = "add"
        MemRW = "READ"
        WBSel = "MEM"
        if funct3 == 0x0:
            LoadType = "lb"
        elif funct3 == 0x1:
            LoadType = "lh"
        elif funct3 == 0x2:
            LoadType = "lw"
        elif funct3 == 0x4:
            LoadType = "lbu"
        elif funct3 == 0x5:
            LoadType = "lhu"

    # S-TYPE STORE (sw, sb, sh)
    elif opcode == 0b0100011:
        ImmSel = "S"
        RegWEn = 0
        ASel = "RS1"
        BSel = "IMM"
        ALUSel = "add"
        MemRW = "WRITE"
        if funct3 == 0x0:
            StoreType = "sb"
        elif funct3 == 0x1:
            StoreType = "sh"
        elif funct3 == 0x2:
            StoreType = "sw"

    # B-TYPE BRANCH (beq, bne, blt, bge...)
    elif opcode == 0b1100011:
        ImmSel = "B"
        RegWEn = 0
        ASel = "PC"
        BSel = "IMM"
        ALUSel = "add"
        is_taken = False
        if funct3 == 0x0:
            is_taken = BrEq
        elif funct3 == 0x1:
            is_taken = not BrEq
        elif funct3 == 0x4:
            is_taken = BrLt
        elif funct3 == 0x5:
            is_taken = not BrLt
        elif funct3 == 0x6:
            is_taken = BrLt
        elif funct3 == 0x7:
            is_taken = not BrLt
        PCSel = "JUMP" if is_taken else "PC+4"

    # U-TYPE LUI (Ghi giá trị tức thời vào 20 bit cao)
    elif opcode == 0b0110111:
        ImmSel = "U"
        RegWEn = 1
        WBSel = "IMM"

    # U-TYPE AUIPC (PC + giá trị tức thời 20 bit cao)
    elif opcode == 0b0010111:
        ImmSel = "U"
        RegWEn = 1
        ASel = "PC"
        BSel = "IMM"
        ALUSel = "add"
        WBSel = "ALU"

    # J-TYPE JAL (Nhảy trực tiếp)
    elif opcode == 0b1101111:
        ImmSel = "J"
        RegWEn = 1
        ASel = "PC"
        BSel = "IMM"
        ALUSel = "add"
        WBSel = "PC+4"
        PCSel = "JUMP"

    # I-TYPE JALR (Nhảy qua giá trị thanh ghi)
    elif opcode == 0b1100111:
        ImmSel = "I"
        RegWEn = 1
        ASel = "RS1"
        BSel = "IMM"
        ALUSel = "add"
        WBSel = "PC+4"
        PCSel = "JUMP"

    else:
        raise Exception(f"Lệnh không được hỗ trợ: {hex(opcode)}")

    return ImmSel, RegWEn,ASel,BSel, ALUSel, MemRW, WBSel, PCSel, LoadType, StoreType

# Khởi tạo 32 thanh ghi x0 -> x31
registers = [0] * 32

registers[2] = 0x7fffeffc  # giá trị mặc định ban đầu của các thanh ghi theo RARS
registers[3] = 0x10008000
registers[4] = 0x0

# Khởi tạo bộ nhớ trống
memory = {} 
load_dmem("DATA_MEMORY.bin")

lines = read_file("instruction.bin")

PC = 0x00400000
IMEM = {}

for inst in lines:
    inst = inst.strip()
    if not inst:
        continue

    inst_val = int(inst, 2)   # chuyển từ hex string → int 32-bit

    IMEM[PC] = inst_val
    PC += 4


PC = 0x00400000
while PC in IMEM:
    code = IMEM[PC]
    registers[0] = 0

    BrUn = Get_BrUn(code)
    rs1, rs2 = Read_Register_File(code)
    BrEQ, BrLT= Branch_Comp(BrUn, rs1, rs2 )

    ImmSel, RegWEn,ASel,BSel, ALUSel, MemRW, WBSel, PCSel, LoadType, StoreType = Control_Logic(code, BrEQ, BrLT)

    imm = ImmGen(code, ImmSel)

    if ASel == "PC": a = PC
    else: a = rs1
    if BSel == "IMM": b = imm
    else: b = rs2

    result = ALU(ALUSel, a, b)

    mem = DMEM(result, rs2, MemRW, LoadType, StoreType)

    if (WBSel == "ALU"): wdata = result
    elif (WBSel == "PC+4"): wdata = PC+4
    elif (WBSel == "IMM"): wdata = imm
    elif (WBSel == "MEM"): wdata = mem

    Write_Register_File(code, wdata, RegWEn)

    if (PCSel == "PC+4"): PC+=4
    elif (PCSel == "JUMP"): PC = result

dump_registers("registers.txt")
dump_dmem("dmem.txt")
dump_dmem_RARS("dmem_rars.txt")