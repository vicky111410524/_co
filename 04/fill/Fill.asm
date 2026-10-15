// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Fill.asm
// 當按下任意鍵時，將螢幕塗黑；沒有按下任何鍵時，將螢幕清空（變白）。

(LOOP)
    @KBD
    D=M         // 讀取鍵盤輸入狀態 (RAM[24576])
    @BLACK
    D;JNE       // 若有按鍵 (D != 0)，跳轉至 BLACK

(WHITE)
    @color
    M=0         // 顏色設為白色 (0)
    @FILL
    0;JMP

(BLACK)
    @color
    M=-1        // 顏色設為黑色 (-1 / 0xFFFF)

(FILL)
    @SCREEN
    D=A
    @address
    M=D         // 初始化指標 address = SCREEN (16384)

(FILL_LOOP)
    @address
    D=M
    @KBD
    D=D-A       // 計算 address - KBD
    @LOOP
    D;JEQ       // 若 address == KBD (代表 8192 個 Word 已填滿)，回主迴圈繼續監聽

    @color
    D=M
    @address
    A=M
    M=D         // 將當前顏色寫入目前螢幕記憶體位址

    @address
    M=M+1       // 指標移至下一個 16-bit 螢幕 Word

    @FILL_LOOP
    0;JMP