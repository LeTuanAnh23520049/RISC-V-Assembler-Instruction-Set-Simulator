    .data
result:     .word 0
array:      .word 1,2,3,4,5
bytes:      .byte 5,6,7,8
msg:        .ascii "OK"

    .text

_start:

    # base address
    lui x1, 0x10010
    addi x1, x1, 0

    # load byte
    addi x2, x1, 24
    lb x3, 0(x2)
    lb x4, 1(x2)
    lb x5, 2(x2)
    lb x6, 3(x2)

    # load word
    addi x7, x1, 4
    lw x8, 0(x7)
    lw x9, 4(x7)
    lw x10, 8(x7)

    # arithmetic
    add x11, x8, x9
    sub x12, x10, x8
    and x13, x11, x12
    or  x14, x11, x12
    xor x15, x11, x12

    # shift
    sll x16, x8, x3
    srl x17, x10, x3
    sra x18, x10, x3

    # immediate
    addi x19, x0, 10
    addi x20, x0, 20
    andi x21, x19, 7
    ori  x22, x20, 3
    xori x23, x19, 5

    # compare
    slt  x24, x19, x20
    sltu x25, x20, x19
    slti x26, x19, 15
    sltiu x27, x20, 30

    # store
    sw x11, 0(x1)
    sb x3,  4(x1)
    sh x4,  6(x1)

    # branch test (co dieu kien, khong loop)
    addi x28, x0, 15
    add x29, x8, x9   # 1+2 = 3

    beq x29, x28, equal_case
    bne x29, x28, notequal_case

equal_case:
    addi x30, x0, 111
    sw x30, 0(x1)
    beq x0, x0, end   # branch 1 lan de skip

notequal_case:
    addi x31, x0, 222
    sw x31, 0(x1)

end:
    addi x0, x0, 0    # ket thuc (NOP)

    # auipc test (khong nhay)
    auipc x5, 0x12345
    addi  x5, x5, 0
    
 # ===== dump register ra memory =====

    lui x6, 0x10010        # x6 = 0x10010000
    addi x6, x6, 0x20      # x6 = 0x10010020

    sw x1,   0(x6)
    sw x2,   4(x6)
    sw x3,   8(x6)
    sw x4,  12(x6)
    sw x5,  16(x6)
    sw x6,  20(x6)
    sw x7,  24(x6)
    sw x8,  28(x6)
    sw x9,  32(x6)
    sw x10, 36(x6)
    sw x11, 40(x6)
    sw x12, 44(x6)
    sw x13, 48(x6)
    sw x14, 52(x6)
    sw x15, 56(x6)
    sw x16, 60(x6)
    sw x17, 64(x6)
    sw x18, 68(x6)
    sw x19, 72(x6)
    sw x20, 76(x6)
    sw x21, 80(x6)
    sw x22, 84(x6)
    sw x23, 88(x6)
    sw x24, 92(x6)
    sw x25, 96(x6)
    sw x26,100(x6)
    sw x27,104(x6)
    sw x28,108(x6)
    sw x29,112(x6)
    sw x30,116(x6)
    sw x31,120(x6)