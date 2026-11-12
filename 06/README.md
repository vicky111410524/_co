# Project 6: Hack Assembler（Hack 組譯器）

* **學號 / 姓名**：111410524 許毓庭
* **開發語言**：Python 3
* **課程單元**：Nand2Tetris — Chapter 6 (Assembler)

---

## 1. 專案簡介

本專案使用 Python 實作一個完整的 **Hack 組譯器（`HackAssembler.py`）**，能將 Hack 組合語言原始碼（`.asm`）翻譯為 Hack 電腦架構可執行的 16 位元二進位機器碼（`.hack`）。支援完整的 A-instruction、C-instruction 運算組合，以及標籤（Labels）與自訂變數（Variables）的符號表解析。

---

## 2. 檔案結構

```text
06/
├── HackAssembler.py      # Hack 組譯器主程式
├── README.md             # 專案說明文件
├── add/
│   ├── Add.asm           # 測試檔：純加法運算（無符號）
│   └── Add.hack          # 產出之機器碼
├── max/
│   ├── MaxL.asm          # 測試檔：最大值比較（無符號版）
│   └── Max.asm           # 測試檔：最大值比較（含標籤與變數）
├── rect/
│   ├── RectL.asm         # 測試檔：繪製矩形（無符號版）
│   └── Rect.asm          # 測試檔：繪製矩形（含標籤與變數）
└── pong/
    ├── PongL.asm         # 測試檔：Pong 遊戲（無符號版）
    └── Pong.asm          # 測試檔：Pong 遊戲（含標籤與變數，約 2.7 萬行）

```

---

## 3. 執行方式

開啟終端機並進入 `06` 資料夾後，透過命令列傳入目標 `.asm` 檔案路徑即可執行組譯，程式會自動在同目錄下生成對應的 `.hack` 檔案：

```bash
python HackAssembler.py add/Add.asm
python HackAssembler.py max/Max.asm
python HackAssembler.py rect/Rect.asm
python HackAssembler.py pong/Pong.asm

```

---

## 4. 程式架構與實作邏輯

組譯器採用標準的兩階段掃描（Two-Pass Assembly）架構：

1. **預處理（Preprocessing）**
* 自動過濾所有單行與行尾註解（`// ...`）、空白字元與空行。


2. **符號表初始化（Symbol Table Initialization）**
* 預先載入內建符號：`R0`～`R15`（對應記憶體位址 `0`～`15`）、`SP`（`0`）、`LCL`（`1`）、`ARG`（`2`）、`THIS`（`3`）、`THAT`（`4`）、`SCREEN`（`16384`）、`KBD`（`24576`）。


3. **第一階段掃描（First Pass）**
* 逐行計算有效指令的 ROM 位址，遇到標籤宣告 `(XXX)` 時，將標籤名稱與對應的下一條指令 ROM 位址存入符號表，且不計入實際機器碼行數。


4. **第二階段掃描（Second Pass）**
* **A-instruction（`@value`）**：若為十進位數字，直接轉換為 `0` 開頭的 16 位元二進位碼；若為符號名稱，則查詢符號表取得位址，首次出現的自訂變數由 RAM 位址 `16` 開始依序配置。
* **C-instruction（`dest=comp;jump`）**：拆解運算欄位並查表對應為 `111` 開頭的 16 位元控制位元（包含 `a` 位元、`c1`～`c6`、`d1`～`d3` 與 `j1`～`j3`）。



---

## 5. 測試與驗證

本程式產出的所有 `.hack` 機器碼，皆已透過 Nand2Tetris 官方工具 `Assembler.bat` 與指令列比對工具 `fc.exe` 進行逐行驗證，確認與官方標準答案 100% 一致：

* `Add.asm`：比對通過（`File compilation & comparison succeeded`）
* `MaxL.asm` / `Max.asm`：比對通過
* `RectL.asm` / `Rect.asm`：比對通過
* `PongL.asm` / `Pong.asm`：比對通過（`FC: 找不到相異處`）

