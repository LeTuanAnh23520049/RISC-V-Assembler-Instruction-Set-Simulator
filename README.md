# RISC-V RV32I Toolchain & Verification Automation

This repository provides an automated simulation and verification toolchain for the **RISC-V (RV32I)** Instruction Set Architecture. It consists of a custom **Assembler**, an **Instruction Set Simulator (ISS)**, and an **Automation Runner** integrated with RARS.

## Project Architecture

- `assembler.py`: Translates RISC-V assembly source code into machine code binaries.
- `iss.py`: Simulates CPU execution, updates register states, and manages Data Memory (`DMEM`).
- `run_automation.py`: Orchestrates the automated pipeline by executing the Assembler, ISS, and comparing results with RARS golden outputs.
- `program.asm`: Input RISC-V assembly source file to be processed.

---

## Execution Outputs

Running the automation pipeline generates the following output files:

| File Name | Description |
| :--- | :--- |
| `instruction.bin` | Compiled 32-bit machine code binary |
| `label_table.bin` | Generated symbol table for jumps and branch labels |
| `DATA_MEMORY.bin` | Binary dump of Data Memory initialization |
| `dmem.txt` | Final Data Memory state after ISS execution |
| `registers.txt` | Final Register File state after ISS execution |
| `dmem_rars.txt` | Golden Reference Data Memory state exported from RARS |

---

## How to Run

### Prerequisites
- Python 3.x
- Java Runtime Environment (Required for RARS execution)

### Execution Steps
1. Place your RISC-V assembly source code inside `program.asm`.
2. Run the automation script from the root directory:
   ```bash
   python run_automation.py