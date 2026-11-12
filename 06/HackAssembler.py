import sys
from pathlib import Path

# C-instruction 對照表
COMP_TABLE = {
    "0":   "0101010", "1":   "0111111", "-1":  "0111010",
    "D":   "0001100", "A":   "0110000", "!D":  "0001101",
    "!A":  "0110001", "-D":  "0001111", "-A":  "0110011",
    "D+1": "0011111", "A+1": "0110111", "D-1": "0001110",
    "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
    "M":   "1110000", "!M":  "1110001", "-M":  "1110011",
    "M+1": "1110111", "M-1": "1110010", "D+M": "1000010",
    "D-M": "1010011", "M-D": "1000111", "D&M": "1000000",
    "D|M": "1010101",
}

DEST_TABLE = {
    "":    "000", "M":   "001", "D":   "010", "MD":  "011", "DM":  "011",
    "A":   "100", "AM":  "101", "MA":  "101", "AD":  "110", "DA":  "110",
    "AMD": "111", "ADM": "111",
}

JUMP_TABLE = {
    "":    "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
}


def assemble(asm_path: Path) -> None:
    # 初始化內建符號表
    symbols = {
        "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
        "SCREEN": 16384, "KBD": 24576,
    }
    for i in range(16):
        symbols[f"R{i}"] = i

    # 讀取檔案並清除註解與空白
    raw_lines = asm_path.read_text(encoding="utf-8").splitlines()
    cleaned_lines = []
    for line in raw_lines:
        code_part = line.split("//")[0].strip().replace(" ", "").replace("\t", "")
        if code_part:
            cleaned_lines.append(code_part)

    # First Pass：記錄所有標籤 (LABEL) 對應的 ROM 位址
    instructions = []
    rom_address = 0
    for line in cleaned_lines:
        if line.startswith("(") and line.endswith(")"):
            label = line[1:-1]
            symbols[label] = rom_address
        else:
            instructions.append(line)
            rom_address += 1

    # Second Pass：將每行指令轉譯為 16-bit 二進位機器碼
    next_var_address = 16
    machine_code = []

    for inst in instructions:
        if inst.startswith("@"):
            # A-instruction
            symbol = inst[1:]
            if symbol.isdigit():
                address = int(symbol)
            else:
                if symbol not in symbols:
                    symbols[symbol] = next_var_address
                    next_var_address += 1
                address = symbols[symbol]
            machine_code.append(f"0{address:015b}")
        else:
            # C-instruction: dest=comp;jump
            dest, rest = ("", inst)
            if "=" in inst:
                dest, rest = inst.split("=", 1)
            comp, jump = (rest, "")
            if ";" in rest:
                comp, jump = rest.split(";", 1)

            binary = "111" + COMP_TABLE[comp] + DEST_TABLE[dest] + JUMP_TABLE[jump]
            machine_code.append(binary)

    # 輸出同名的 .hack 檔案
    hack_path = asm_path.with_suffix(".hack")
    hack_path.write_text("\n".join(machine_code) + "\n", encoding="utf-8")
    print(f"組譯完成：{hack_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python HackAssembler.py <檔案路徑.asm>")
        sys.exit(1)
    assemble(Path(sys.argv[1]))