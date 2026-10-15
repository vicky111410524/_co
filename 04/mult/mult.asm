// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// mult.asm
// 計算 R0 * R1 並將結果存入 R2。
// (R0, R1, R2 分別代表 RAM[0], RAM[1], RAM[2])

    // 1. 初始化結果 RAM[2] = 0
    @R2
    M=0

    // 2. 將 R1 的數值存入計數器變數 i
    @R1
    D=M
    @i
    M=D

(LOOP)
    // 檢查計數器 i 是否 <= 0，若是則結束迴圈
    @i
    D=M
    @END
    D;JLE

    // R2 = R2 + R0 (累加)
    @R0
    D=M
    @R2
    M=M+D

    // 計數器減 1 (i = i - 1)
    @i
    M=M-1

    // 跳回 LOOP 繼續執行
    @LOOP
    0;JMP

(END)
    // 無限迴圈以結束程式
    @END
    0;JMP