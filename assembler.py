class RType:
    def __init__(self, opcode, funct3, funct7):
        self.opcode = opcode
        self.funct3 = funct3
        self.funct7 = funct7

class IType:
    def __init__(self, opcode, funct3):
        self.opcode = opcode
        self.funct3 = funct3

class SType:
    def __init__(self, opcode, funct3):
        self.opcode = opcode
        self.funct3 = funct3

class BType:
    def __init__(self, opcode, funct3):
        self.opcode = opcode
        self.funct3 = funct3

class UType:
    def __init__(self, opcode):
        self.opcode = opcode

class JType:
    def __init__(self, opcode):
        self.opcode = opcode

class register:
    def __init__(self, index):
        self.index = index

instructions = {
#RType
    "add":  RType(0b0110011, 0x0, 0x00),
    "sub":  RType(0b0110011, 0x0, 0x20),
    "xor":  RType(0b0110011, 0x4, 0x00),
    "or":   RType(0b0110011, 0x6, 0x00),
    "and":  RType(0b0110011, 0x7, 0x00),
    "sll":  RType(0b0110011, 0x1, 0x00),
    "srl":  RType(0b0110011, 0x5, 0x00),
    "sra":  RType(0b0110011, 0x5, 0x20),
    "slt":  RType(0b0110011, 0x2, 0x00),
    "sltu": RType(0b0110011, 0x3, 0x00),
#IType
    "addi": IType(0b0010011,0x0),
    "xori": IType(0b0010011,0x4),
    "ori": IType(0b0010011,0x6),
    "andi": IType(0b0010011,0x7),
    "slli": IType(0b0010011,0x1),
    "srli": IType(0b0010011,0x5),
    "srai": IType(0b0010011,0x5),
    "slti": IType(0b0010011,0x2),
    "sltiu": IType(0b0010011,0x3),
    "lb": IType(0b0000011,0x0),
    "lh": IType(0b0000011,0x1),
    "lw": IType(0b0000011,0x2),
    "lbu": IType(0b0000011,0x4),
    "lhu": IType(0b0000011,0x5),
# SType
    "sb": SType(0b0100011, 0x0),
    "sh": SType(0b0100011, 0x1),
    "sw": SType(0b0100011, 0x2),
# BType
    "beq": BType(0b1100011, 0x0),
    "bne": BType(0b1100011, 0x1),
    "blt": BType(0b1100011, 0x4),
    "bge": BType(0b1100011, 0x5),
    "bltu": BType(0b1100011, 0x6),
    "bgeu": BType(0b1100011, 0x7),
# JType & IType (Jump Instructions)
    "jal": JType(0b1101111),
    "jalr": IType(0b1100111, 0x0),
# UType
    "lui": UType(0b0110111),
    "auipc": UType(0b0010111),
# IType (Environment/System Instructions)
    "ecall": IType(0b1110011, 0x0), 
    "ebreak": IType(0b1110011, 0x0),
}

registers = {
    "x0": register(0),   "zero": register(0),
    "x1": register(1),   "ra": register(1),
    "x2": register(2),   "sp": register(2),
    "x3": register(3),   "gp": register(3),
    "x4": register(4),   "tp": register(4),
    "x5": register(5),   "t0": register(5),
    "x6": register(6),   "t1": register(6),
    "x7": register(7),   "t2": register(7),
    "x8": register(8),   "s0": register(8),
    "x9": register(9),   "s1": register(9),
    "x10": register(10), "a0": register(10),
    "x11": register(11), "a1": register(11),
    "x12": register(12), "a2": register(12),
    "x13": register(13), "a3": register(13),
    "x14": register(14), "a4": register(14),
    "x15": register(15), "a5": register(15),
    "x16": register(16), "a6": register(16),
    "x17": register(17), "a7": register(17),
    "x18": register(18), "s2": register(18),
    "x19": register(19), "s3": register(19),
    "x20": register(20), "s4": register(20),
    "x21": register(21), "s5": register(21),
    "x22": register(22), "s6": register(22),
    "x23": register(23), "s7": register(23),
    "x24": register(24), "s8": register(24),
    "x25": register(25), "s9": register(25),
    "x26": register(26), "s10": register(26),
    "x27": register(27), "s11": register(27),
    "x28": register(28), "t3": register(28),
    "x29": register(29), "t4": register(29),
    "x30": register(30), "t5": register(30),
    "x31": register(31), "t6": register(31)
}

label_table = {}
offset_table = {} # bảng lưu giá trị của label-PC, phục vụ lệnh auipc
DMEM = {}

def Encode_RType(line):
    line = line.replace(","," ")
    line = line.strip()
    part = line.split()
    opcode = part[0]
    rd = part[1]
    rs1 = part[2]
    rs2 = part[3]

    a = (
          (instructions[opcode].funct7 << 25) |
          (registers[rs2].index << 20) |
          (registers[rs1].index << 15) |
          (instructions[opcode].funct3 << 12) |
          (registers[rd].index << 7) |
          instructions[opcode].opcode
        )
    return format(a, '032b')

def Encode_IType(line):
    line = line.replace(",", " ")
    line = line.replace("(", " ")
    line = line.replace(")", " ")
    line = line.replace("%lo"," ")
    line = line.strip()
    part = line.split()

    opcode = part[0]
    if ( opcode == "ecall"):
        imm_11_5 = 0x0
        imm_4_0 = 0x0
        rd = rs1 = "x0"
    elif (opcode == "ebreak"):
        imm_11_5 = 0x0
        imm_4_0 = 0x1
        rd = rs1 = "x0"
    else:
        if (opcode[0] == "l" or opcode == "jalr"):
            rd = part[1]
            rs1 = part[3]
            try:
                imm = int(part[2],0)
            except:
                try:
                    imm = offset_table[part[2]] & 0xfff
                except:
                    imm = label_table[part[2]] & 0xfff
        else:
            rd = part[1]
            rs1 = part[2]
            try:
                imm = int(part[3],0)
            except:
                imm = label_table[part[3]]
        
        imm_11_5 = (imm>>5) & 0x7f
        imm_4_0 = imm & 0x1f

        if ( opcode == "slli" or opcode == "srli" ):
            imm_11_5 = 0x00
        elif opcode == "srai":
            imm_11_5 = 0x20

    a = (
        (imm_11_5 << 25) |
        (imm_4_0 << 20) |
        (registers[rs1].index << 15) |
        (instructions[opcode].funct3 << 12) |
        (registers[rd].index << 7) |
        instructions[opcode].opcode
    )

    return format(a, '032b')

def Encode_SType(line):
    line = line.replace(",", " ")
    line = line.replace("(", " ")
    line = line.replace(")", " ")
    line = line.replace("%lo"," ")
    line = line.strip()
    part = line.split()

    opcode = part[0]
    rs2 = part[1]
    rs1 = part[3]
    try:
        imm = int(part[2],0)
    except:
        imm = offset_table[part[2]] & 0xfff

    imm_11_5 = (imm >> 5) & 0x7F
    imm_4_0 = imm & 0x1F

    a = (
        (imm_11_5 << 25) |
        (registers[rs2].index << 20) |
        (registers[rs1].index << 15) |
        (instructions[opcode].funct3 << 12) |
        (imm_4_0 << 7) |
        instructions[opcode].opcode
    )

    return format(a, '032b')

def Encode_BType(line, PC):
    line = line.replace(",", " ")
    line = line.strip()
    part = line.split()

    opcode = part[0]
    rs1 = part[1]
    rs2 = part[2]
    try: 
        imm = int(part[3],0)
    except:
        imm = label_table[part[3]] - PC
    
    imm = imm & 0x1FFF
    imm_12 = (imm >> 12) & 1
    imm_10_5 = (imm >> 5) & 0x3F
    imm_4_1 = (imm >> 1) & 0xF
    imm_11 = (imm >> 11) & 1

    a = (
        (imm_12 << 31) |
        (imm_10_5 << 25) |
        (registers[rs2].index << 20) |
        (registers[rs1].index << 15) |
        (instructions[opcode].funct3 << 12) |
        (imm_4_1 << 8) |
        (imm_11 << 7) |
        instructions[opcode].opcode
    )

    return format(a, '032b')

def Encode_UType(line, PC):
    line = line.replace(",", " ")
    line = line.replace("(", " ")
    line = line.replace(")", " ")
    line = line.replace("%hi"," ")
    line = line.strip()
    part = line.split()

    opcode = part[0]
    rd = part[1]

    if opcode == "lui":
        try:
            imm = int(part[2], 0)
        except:
            imm = ((label_table[part[2]] + 0x800) >> 12) & 0xfffff

    else:  # auipc
        try:
            imm = int(part[2], 0)
        except:
            label = part[2]
            offset_table[label] = label_table[label] - PC 
            imm = ((offset_table[label] +0x800 ) >> 12) & 0xfffff

    a = (
        ((imm & 0xFFFFF) << 12) |
        (registers[rd].index << 7) |
        instructions[opcode].opcode
    )

    return format(a, '032b')

def Encode_JType(line, PC):
    line = line.replace(",", " ")
    line = line.strip()
    part = line.split()

    opcode = part[0]
    rd = part[1]
    try: 
        imm = int(part[2],0)
    except:
        imm = label_table[part[2]] - PC

    imm_20 = (imm >> 20) & 1
    imm_10_1 = (imm >> 1) & 0x3FF
    imm_11 = (imm >> 11) & 1
    imm_19_12 = (imm >> 12) & 0xFF

    a = (
        (imm_20 << 31) |
        (imm_10_1 << 21) |
        (imm_11 << 20) |
        (imm_19_12 << 12) |
        (registers[rd].index << 7) |
        instructions[opcode].opcode
    )

    return format(a, '032b')

def read_file(filename):
    with open(filename, "r") as f:
        return f.readlines()
    
def clean_code(lines):
    clean_lines = []

    for line in lines:
        line = line.split("#")[0]
        line = line.strip()
        if line != "":
            clean_lines.append(line)

    return clean_lines

def split_section(lines):

    data_section = []
    text_section = []

    current = None

    for line in lines:

        if line == ".data":
            current = "data"
            continue

        elif line == ".text":
            current = "text"
            continue

        if current == "data":
            data_section.append(line)

        elif current == "text":
            text_section.append(line)

    return data_section, text_section

def build_data_labels(data_section):

    label_table1 = {}
    DMEM = {}

    data_address = 0x10010000

    for line in data_section:
        label, data = line.split(":", 1)
        label = label.strip()
        label_table1[label] = data_address

        if ".byte" in data:
            data = data.replace(".byte", " ")
            data = data.replace(",", " ")
            data = data.strip()
            values = data.split()

            for v in values:
                DMEM[data_address] = int(v, 0) & 0xFF
                data_address += 1

        elif ".half" in data:
            data = data.replace(".half", " ")
            data = data.replace(",", " ")
            data = data.strip()
            values = data.split()

            for v in values:
                val = int(v, 0) & 0xFFFF
                # little endian
                DMEM[data_address]     = val & 0xFF
                DMEM[data_address + 1] = (val >> 8) & 0xFF
                data_address += 2

        elif ".word" in data:
            data = data.replace(".word", " ")
            data = data.replace(",", " ")
            data = data.strip()
            values = data.split()

            for v in values:
                val = int(v, 0) & 0xFFFFFFFF
                # little endian
                DMEM[data_address]     = val & 0xFF
                DMEM[data_address + 1] = (val >> 8) & 0xFF
                DMEM[data_address + 2] = (val >> 16) & 0xFF
                DMEM[data_address + 3] = (val >> 24) & 0xFF
                data_address += 4

        elif ".asciiz" in data:
            data = data.replace(".asciiz", " ").strip()
            string = data[1:-1]  # bỏ dấu "

            for ch in string:
                DMEM[data_address] = ord(ch)
                data_address += 1

            DMEM[data_address] = 0  # null terminator
            data_address += 1

        elif ".ascii" in data:
            data = data.replace(".ascii", " ").strip()
            string = data[1:-1]

            for ch in string:
                DMEM[data_address] = ord(ch)
                data_address += 1

        elif ".space" in data:
            value = data.split()
            size = int(value[1], 0)

            # nếu muốn fill = 0 thì bật đoạn này
            for i in range(size):
                DMEM[data_address + i] = 0

            data_address += size

        # align 4 byte (giữ nguyên logic của bạn)
        if data_address % 4 != 0:
            data_address += 4 - (data_address % 4)

    return label_table1, DMEM

def build_text_labels(data_section):
    label_table2 = {}

    text_address = 0x00400000

    for line in data_section:
        if ":" in line:
            label, code = line.split(":",1)
            label = label.strip()
            code = code.strip()
            label_table2[label] = text_address
            if code == "":
                continue
            text_address += 4
        else:
            text_address += 4

    return label_table2

def Encode(line, PC):
    a = ""
    if ":" in line:
        label, code = line.split(":",1)
        label = label.strip()
        code = code.strip()
        if code == "":
            return a
        else:
            line = code 

    line = line.lower()
    opcode = line.split()[0]

    inst = instructions[opcode]

    if isinstance(inst, RType):
        a = Encode_RType(line)

    elif isinstance(inst, IType):
        a = Encode_IType(line)

    elif isinstance(inst, SType):
        a = Encode_SType(line)

    elif isinstance(inst, BType):
        a = Encode_BType(line, PC)

    elif isinstance(inst, UType):
        a = Encode_UType(line, PC)

    elif isinstance(inst, JType):
        a = Encode_JType(line, PC)
    return a


lines = read_file("program.asm")
lines = clean_code(lines)
data, text= split_section(lines)

data_labels, DMEM = build_data_labels(data)
text_labels = build_text_labels(text)
label_table = {**data_labels, **text_labels}

PC = 0x00400000
output = []

for line in text:
    binary_code = Encode(line, PC)
    if binary_code != "":
        output.append(binary_code)
        PC += 4

with open("instruction.bin", "w") as f:
    for output_line in output:
        f.write(output_line + "\n")

with open("label_table.bin", "w") as f:
    for output_label in label_table:
        f.write(output_label + " : " + str( hex(label_table[output_label]) ) + "\n")
    
with open("DATA_MEMORY.bin", "w") as f:
    for addr in sorted(DMEM.keys()):
        f.write(f"{addr:08x} : {DMEM[addr]:02x}\n")


