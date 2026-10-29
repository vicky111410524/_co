# 積體電路設計自動化（EDA）軟體應用與晶片設計流程實作

## AI對話:https://share.gemini.google/DZw8suCgz18W

## 一、實驗目的
1. **EDA 核心概念與關鍵價值理解**：深入剖析電子設計自動化（EDA）於現代半導體產業的核心地位，理解軟體演算法如何協助工程師進行數百億級電晶體的抽象階層管理。
2. **IC 設計前後端完整流程掌握**：建立對積體電路設計全生命週期的架構性認識，涵蓋前端暫存器傳輸級（RTL）撰寫、邏輯合成，到後端實體佈局繞線（P&R）、靜態時序分析（STA）及實體規則驗證。
3. **Web 與開源 EDA 工具鏈實作體驗**：透過免安裝的網頁版與開源 EDA 工具（Veryl2Chip、Hack Computer HDL、OpenROAD / SkyWater 130nm PDK 工具鏈），完成邏輯門模擬、網表轉譯、晶片佈局及虛擬硬體測試。
4. **半導體與 EDA 前沿發展趨勢探討**：結合實際操作體驗，分析生成式 AI（AI for EDA）與開源半導體生態對降低晶片設計門檻與加速晶片迭代的深遠影響。

---

## 二、EDA 是什麼？（核心概念與產業價值）

### 1. EDA 的定義與半導體產業重要性
電子設計自動化（Electronic Design Automation, EDA）是指利用計算機軟體輔助完成半導體晶片與積體電路（IC）系統之架構設計、邏輯合成、電路模擬、實體佈局（Layout）及規則驗證的工程技術。隨著摩爾定律推進，晶片複雜度超越人力手工繪製極限，EDA 成為連結軟體演算法與實體矽晶圓製造的必要橋樑。

### 2. 抽象階層管理（System $\rightarrow$ RTL $\rightarrow$ Netlist $\rightarrow$ GDSII）
EDA 透過嚴密的階層化抽象處理，將極度複雜的硬體設計分層降維：
* **System / Architecture**：高階演算法與系統架構定義（C/C++ / SystemC / Python）。
* **RTL (Register-Transfer Level)**：採用硬體描述語言（Verilog / SystemVerilog / Veryl）定義暫存器間的資料傳輸與邏輯運算。
* **Netlist (Gate-Level)**：經邏輯合成後，將 RTL 轉換為具體標準邏輯門（AND, OR, DFF）的連線網表。
* **GDSII / OASIS (Physical Layout)**：完成幾何佈局與金屬走線後，生成給晶圓代工廠用於製作光罩的實體幾何檔案。

### 3. PPA 多目標最佳化
EDA 軟體的核心任務是在嚴格的設計約束下，進行多目標演算法尋優：
* **Power (功耗)**：最小化晶片之動態開關功耗與靜態漏電功耗。
* **Performance (性能)**：優化關鍵路徑（Critical Path）延遲，提升晶片最高工作頻率 ($F_{\max}$)。
* **Area (面積)**：縮減晶片實體佔用面積，以提升單晶圓產量並降低製造成本。

### 4. EDA 技術的未來發展趨勢
* **AI for EDA**：利用大語言模型（LLM）輔助生成與優化 RTL 程式碼；並應用強化學習（RL）最佳化 Placement（佈局）與 Routing（繞線）搜尋路徑，將傳統數週的佈局時間縮短至數小時。
* **開源半導體生態**：以 SkyWater 130nm 開源 PDK 與 OpenROAD、Yosys 等開源工具鏈為核心，消弭商業 EDA 昂貴的授權壁壘，推動晶片設計民主化（Democratization of IC Design）。

---

## 三、實驗使用工具與開源專案解析

1. **Nand2tetris / Hack Computer HDL 網頁模擬器 (`ccc-js/hack-computer`)**：
   * **特色與機制**：專為計算機系統架構教學設計的前端模擬器。透過自訂的 Hack HDL 語法，由最基礎的 NAND 閘一路封裝出 Mux、DMux、Adder，乃至完整的算術邏輯單元（ALU）。
2. **Veryl2Chip Web IDE (`ccc-eda/veryl2chip`)**：
   * **特色與機制**：陳鍾誠教授與開源社群開發的網頁整合環境。核心採用 Rust 編寫並編譯為 WebAssembly 於瀏覽器內執行。支援新型硬體描述語言 Veryl、RTL / 網表級雙模式仿真、FPGA/ASIC 後端佈局繞線動畫，以及整合 PMOD 周邊的虛擬 iCEBreaker 開發板。
3. **開源 ASIC / FPGA 工具鏈（對照 Cornell ECE 5745 課程實力鏈）**：
   * **特色與機制**：參考康乃爾大學 ECE 5745 (Complex Digital ASIC Design) 課程體系。前端採用 Verilator / Yosys 進行仿真與邏輯合成，後端結合 OpenROAD 進行晶片 Placement/Routing，並基於 SkyWater 130nm (sky130_fd_sc_hd) 標準元件庫產出符合 DRC/LVS 規範的 GDSII 檔案。

---

## 四、IC 設計的完整作業流程與階段

現代 IC 設計從需求定義到交付流片的完整自動化流程分為 9 大步驟：

```
[規格定義] ➔ [RTL寫作] ➔ [1.RTL解析] ➔ [2.網表生成] ➔ [3.技術無關最佳化]
                                                             │
[GDSII檔] ↵ [9.DRC/驗證] ↵ [8.靜態時序STA] ↵ [7.詳細繞線] ↵ [4-6.映射/擺放/CTS]
```

### 1. 前端邏輯處理階段（Front-End）
* **① RTL 語法解析與 AST 建構**：EDA 編譯器讀取 Veryl 或 Verilog 語法，進行語法與語意檢查，並構建抽象語法樹（AST）。
* **② 邏輯網表（Netlist）生成**：將 AST 中的運算子轉譯為技術無關的基礎邏輯門（Generic Gates）連線結構。
* **③ 技術無關最佳化（Tech-independent Optimization）**：利用布林代數化簡、卡諾圖化簡及冗餘邏輯消去等演算法，最小化邏輯門數量與邏輯深度。

### 2. 後端實體設計階段（Back-End / Physical Design）
* **ASIC 製造流程（以 SkyWater 130nm 為例）**：
  * **④ 標準元件映射（Standard Cell Mapping）**：將技術無關網表映射至晶圓廠提供的 SkyWater 130nm 標準元件庫（如 AND, NAND, DFF）。
  * **⑤ Row Placement 佈局**：將標準元件擺放至晶片基底的 row 結構中，利用模擬退火演算法（Simulated Annealing）最小化元件間總連線長度。
  * **⑥ CTS 時脈樹綜合與全域繞線**：構建平衡的 Clock Tree 以降低時序偏斜（Clock Skew），並劃分晶片區域進行粗粒度全域導線規劃。
  * **⑦ 詳細繞線（Detailed Routing）**：在多層實體金屬層（Metal 1~5）上繪製精確的導線寬度與間距，避開幾何干擾。
  * **⑧ 靜態時序分析（STA）**：檢查 Setup Time 與 Hold Time，確認關鍵路徑延遲滿足預期工作頻率要求。
  * **⑨ DRC/LVS 實體驗證與 GDSII 輸出**：進行設計規則檢查（DRC）與網表對照（LVS），無誤後產出 GDSII 光罩檔。
* **FPGA 燒錄流程（以 iCE40UP5K 為例）**：
  * **④ LUT4 映射**：將邏輯門轉換為 4 輸入查找表（LUT4）與 Flip-Flop 組合。
  * **⑤ / ⑥ P&R 佈局繞線**：將 LUT 映射至 FPGA 內部的實體 CLB 區塊，並設定可程式化金屬開關陣列。
  * **⑦ Bitstream 位元流生成**：將佈局繞線結果編碼為二進位位元流（`.bin`），用於燒錄晶片配置記憶體。

---

## 五、實驗操作流程

1. **步驟一：門級邏輯設計與測試驗證（Hack HDL）**
   * 進入 Hack Computer 網頁介面，點擊 `Load Chip` 載入邏輯描述檔 `ALU.hdl`。
   * 載入定義好輸入波形與控制訊號的 `ALU.tst` 測試腳本。
   * 點擊 `Run` 執行單步或連續仿真，檢查引腳數值，最終確認系統顯示 `"Comparison ended successfully"`。
2. **步驟二：Veryl 語法編寫與 RTL 仿真（Veryl2Chip）**
   * 開啟 Veryl2Chip Web IDE，載入內建範例專案（如 `FIFO` 或 `RV32I CPU`）。
   * 於編輯器中撰寫 Veryl 模組與邏輯斷言（`$assert`），系統自動進行即時語法檢查。
   * 點擊 `▶ tests` 啟動 WebAssembly 仿真核心，並在底面板開啟 VCD 波形圖分析訊號脈波。
3. **步驟三：邏輯合成與晶片佈局繞線（Veryl2Chip）**
   * 於標題列切換目標技術鏈：`ASIC · SKY130` 或 `FPGA · iCE40`。
   * 點擊 `⚙ 合成` 觸發自動化流程，於畫面上即時觀看元件映射、佈局退火動畫、導線劃分與靜態時序分析報告。
4. **步驟四：虛擬硬體燒錄與驗證（Virtual iCEBreaker）**
   * 點擊標題列 `⚡ 板卡圖示` 開啟虛擬 iCEBreaker 開發板環境。
   * 工具鏈會將生成之位元流自動載入虛擬 FPGA 晶片。
   * 手動切換開關、按下按鈕，觀察板載 LED 燈亮滅狀態及 PMOD 顯示介面（如 7 段顯示器、VGA 螢幕）輸出是否正常。

---

## 六、實驗結果與分析

### 1. 邏輯模擬與波形驗證結果
於 Hack HDL 模擬器中，`ALU.hdl` 正確通過所有邏輯運算測試；於 Veryl2Chip 中，包含 `FIFO` 與 `RV32I` CPU 範例均成功通過 RTL 仿真與合成後網表門級仿真（Gate-Level Simulation），VCD 波形圖確認訊號於時脈上升沿（Rising Edge）正確鎖存，無競態條件（Race Condition）。

### 2. FPGA 與 ASIC 實作流程與結果對比分析

| 分析指標 / 階段 | FPGA 實作流程 (Lattice iCE40UP5K) | ASIC 實作流程 (SkyWater 130nm) |
| :--- | :--- | :--- |
| **邏輯映射單元** | 4-Input LUT (查找表) / DFF / Block RAM | 標準元件庫 (AND2_X1, DFF_X1, NOR2_X1...) |
| **實體佈局機制** | 固定的邏輯區塊陣列 (CLB Tiles) | 自動化標準元件 Row 擺放 (Placement Rows) |
| **繞線資源** | 可程式化金屬開關與接線通道 (Routing Traces) | 5 層實體銅/鋁金屬層 (Metal 1 ~ Metal 5) |
| **最終輸出成果** | 二進位燒錄檔 (`.bin`) | 晶片製造光罩檔 (`.gds` / `.def`) |
| **主要效能報告** | LUT 使用量、最高運作頻率 ($F_{\max}$) | 晶片總面積 ($\mu m^2$)、DRC 違規數、功耗 (mW) |

分析顯示，同一份 Veryl RTL 描述在不同後端設定下，EDA 工具能精確執行對應的映射演算法，並產出相符的實體架構報告。

---

## 七、實驗心得與總結

### 1. 軟硬體協同設計觀點
透過本週實驗，深刻體會到現代半導體產業本質上是「軟體演算法與硬體架構交織」的產物。硬體工程師透過抽象語言描述架構，而 EDA 軟體則運用圖論、線性規劃與幾何演算法將抽象語法實體化。

### 2. 免安裝 Web / 開源 EDA 工具對晶片學習與驗證的價值
傳統 EDA 工具環境建置極度繁瑣且授權昂貴。Veryl2Chip 與 Hack HDL 等專案成功利用 Rust 與 WebAssembly 技術將完整的編譯、模擬與佈局繞線搬入瀏覽器，大幅降低了半導體教育與 IC 設計入門的門檻。這不僅有助於學術推廣，更展現了開源半導體生態系的巨大潛力。

---

## 八、參考資料

1. **AI 自製 EDA 專案 (Veryl2Chip)**: https://github.com/ccc-eda/veryl2chip/
2. **Veryl2Chip 線上 Web IDE**: https://ccc-eda.github.io/veryl2chip/web/dist/index.html
3. **Nand2tetris Hack Computer 專案**: https://github.com/ccc-js/hack-computer
4. **Hack Computer HDL 線上模擬器**: https://ccc-js.github.io/hack-computer/dist/hdl.html
5. **電子設計自動化 (EDA) 線上書籍**: https://github.com/ccc-eda/eda-books/tree/main/book
6. **康乃爾大學 ECE 5745 Complex Digital ASIC Design 課程**: https://www.csl.cornell.edu/courses/ece5745/handouts.html