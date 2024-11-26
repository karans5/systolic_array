# Systolic Array Implementation

A 4x4 systolic array implementation in Bluespec SystemVerilog (BSV) that supports both integer and floating-point MAC (Multiply-Accumulate) operations. The design features a flexible architecture with configurable data flow and operation modes.

## Project Structure

```
systolic_array/
├── src/                    # BSV source files
│   ├── systolic_array.bsv  # Main systolic array implementation
│   ├── mac_top.bsv        # Top-level MAC interface
│   └── ...                # Other BSV files
├── verilog/               # Generated Verilog files
├── intermediate/          # Build intermediates
└── systolic_array_verif/  # Verification files
```

## Features

- 4x4 grid of MAC (Multiply-Accumulate) units
- Dual-mode operation:
  - Integer MAC operations
  - Floating-point MAC operations
- Pipelined data flow
- Configurable accumulation
- Systolic data movement:
  - Horizontal flow for matrix A
  - Vertical flow for matrix B
  - Cascaded accumulation for results

## Project Status

1. **Integer (32-bit)**
   - Code Implementation: Completed
   - Verification: Partially Completed
     - Coverpoints: Not-Completed
     - Cocotb Test: Completed
     - Reference Model: Completed

2. **BFloat16**
   - Code Implementation: Completed
   - Verification: Partially Completed
     - Coverpoints: Not-Completed
     - Cocotb Test: Completed
     - Reference Model: Completed

## Prerequisites

- Bluespec Compiler (bsc)
- Verilator
- Python 3.x
- Git

## Build and Simulation Steps

1. **Clone the MAC Repository**
   ```bash
   make clone_mac
   ```
   This will clone the required MAC implementation and copy BSV files to src/.

2. **Generate Verilog**
   ```bash
   make generate_verilog
   ```
   This step compiles the BSV code and generates Verilog in the verilog/ directory.

3. **Run Simulation**
   ```bash
   make simulate
   ```
   This will run the simulation using Verilator.

4. **Clean Build**
   ```bash
   make clean_build
   ```
   This removes all generated files and build artifacts.

## Usage

The systolic array supports matrix multiplication and accumulation operations. Each MAC unit in the array can be configured for either integer or floating-point operation using the select signal.

Input data flows through the array in a systolic pattern:
- Matrix A elements flow horizontally
- Matrix B elements flow vertically
- Results accumulate and propagate through the array

## Contributing

Feel free to submit issues and enhancement requests.

