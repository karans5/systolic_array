import os
import random
from pathlib import Path
import cocotb
from cocotb_coverage.coverage import coverage_db
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
import struct

from model_systolic_array import SystolicArray, DataType

def read_matrix_file(file_path, is_float=False):
    """Read matrix data from files"""
    matrices = {'A': [], 'B': [], 'C': []}
    
    for matrix in ['A', 'B', 'C']:
        filename = f'{file_path}/{matrix}_matrix.txt'
        with open(filename, 'r') as file:
            next(file)  # Skip header if present
            matrix_data = []
            for line in file:
                values = line.strip().split()
                if values:
                    row = [float(x) if is_float else int(x) for x in values]
                    matrix_data.append(row)
            matrices[matrix] = matrix_data
    
    return matrices['A'], matrices['B'], matrices['C']

def float_to_bfloat16(value):
    """Convert float to bfloat16 format"""
    return struct.unpack('!I', struct.pack('!f', value))[0] >> 16

@cocotb.test()
async def test_systolic_array(dut):
    """Test the systolic array module"""
    
    # Initialize and start the clock
    clock = Clock(dut.CLK, 10, units="us")
    cocotb.start_soon(clock.start(start_high=False))
    
    # Reset the DUT
    dut.RST_N.value = 0
    await RisingEdge(dut.CLK)
    dut.RST_N.value = 1
    await RisingEdge(dut.CLK)
    
    # Test INT8 mode
    print("\nTesting INT8 Mode")
    
    # Set to INT8 mode
    dut.set_data_type.value = 0  # INT8 mode
    dut.EN_set_data_type.value = 1
    await RisingEdge(dut.CLK)
    assert dut.RDY_set_data_type.value == 1, "RDY_set_data_type not asserted"
    dut.EN_set_data_type.value = 0
    
    # Create model instance
    model = SystolicArray(4)
    model.set_data_type(DataType.INT8)
    
    # Read test matrices
    matrix_A, matrix_B, matrix_C = read_matrix_file('/home/shakti/project_2/systolic_array/test_cases/int8/')
    
    # Load matrices into DUT and model
    for i in range(4):
        # Load row of matrix A
        for j in range(4):
            # DUT
            dut.put_A_row_value.value = matrix_A[i][j]
            dut.put_A_row_index.value = i
            dut.EN_put_A_row.value = 1
            await RisingEdge(dut.CLK)
            assert dut.RDY_put_A_row.value == 1, "RDY_put_A_row not asserted"
            dut.EN_put_A_row.value = 0
            
            # Model
            model.put_A_row(i, matrix_A[i][j])
            
        # Load column of matrix B
        for j in range(4):
            # DUT
            dut.put_B_col_value.value = matrix_B[j][i]
            dut.put_B_col_index.value = i
            dut.EN_put_B_col.value = 1
            await RisingEdge(dut.CLK)
            assert dut.RDY_put_B_col.value == 1, "RDY_put_B_col not asserted"
            dut.EN_put_B_col.value = 0
            
            # Model
            model.put_B_col(i, matrix_B[j][i])
            
        # Load column of matrix C
        for j in range(4):
            # DUT
            dut.put_C_col_value.value = matrix_C[j][i]
            dut.put_C_col_index.value = i
            dut.EN_put_C_col.value = 1
            await RisingEdge(dut.CLK)
            assert dut.RDY_put_C_col.value == 1, "RDY_put_C_col not asserted"
            dut.EN_put_C_col.value = 0
            
            # Model
            model.put_C_col(i, matrix_C[j][i])
    
    # Run systolic steps and compare results
    for _ in range(7):  # 4 + 4 - 1 cycles needed for 4x4 array
        # Get model results
        model_results = model.systolic_step()
        
        # Trigger DUT step
        dut.EN_systolic_step.value = 1
        await RisingEdge(dut.CLK)
        assert dut.RDY_systolic_step.value == 1, "RDY_systolic_step not asserted"
        dut.EN_systolic_step.value = 0
        
        # Get DUT results
        dut_results = []
        for i in range(4):
            dut_results.append(int(dut.get_result_value[i].value))
        
        # Compare results
        if any(model_results):
            print(f"INT8 Step Results - Model: {model_results}, DUT: {dut_results}")
            for i in range(4):
                assert dut_results[i] == model_results[i], \
                    f"Mismatch at position {i}: DUT={dut_results[i]}, Model={model_results[i]}"
    
    # Test BFLOAT16 mode
    print("\nTesting BFLOAT16 Mode")
    
    # Reset DUT
    dut.RST_N.value = 0
    await RisingEdge(dut.CLK)
    dut.RST_N.value = 1
    await RisingEdge(dut.CLK)
    
    # Set to BFLOAT16 mode
    dut.set_data_type.value = 1  # BFLOAT16 mode
    dut.EN_set_data_type.value = 1
    await RisingEdge(dut.CLK)
    assert dut.RDY_set_data_type.value == 1, "RDY_set_data_type not asserted"
    dut.EN_set_data_type.value = 0
    
    # Create new model instance for BFLOAT16
    model = SystolicArray(4)
    model.set_data_type(DataType.BFLOAT16)
    
    # Read test matrices for BFLOAT16
    matrix_A, matrix_B, matrix_C = read_matrix_file('/home/shakti/project_2/systolic_array/test_cases/bfloat16/', is_float=True)
    
    # Load matrices into DUT and model (similar to INT8 but with BFLOAT16 conversion)
    for i in range(4):
        for j in range(4):
            # Convert to BFLOAT16 format for DUT
            a_val = float_to_bfloat16(matrix_A[i][j])
            b_val = float_to_bfloat16(matrix_B[j][i])
            c_val = float_to_bfloat16(matrix_C[j][i])
            
            # Load A
            dut.put_A_row_value.value = a_val
            dut.put_A_row_index.value = i
            dut.EN_put_A_row.value = 1
            await RisingEdge(dut.CLK)
            dut.EN_put_A_row.value = 0
            model.put_A_row(i, matrix_A[i][j])
            
            # Load B
            dut.put_B_col_value.value = b_val
            dut.put_B_col_index.value = i
            dut.EN_put_B_col.value = 1
            await RisingEdge(dut.CLK)
            dut.EN_put_B_col.value = 0
            model.put_B_col(i, matrix_B[j][i])
            
            # Load C
            dut.put_C_col_value.value = c_val
            dut.put_C_col_index.value = i
            dut.EN_put_C_col.value = 1
            await RisingEdge(dut.CLK)
            dut.EN_put_C_col.value = 0
            model.put_C_col(i, matrix_C[j][i])
    
    # Run systolic steps and compare results for BFLOAT16
    for _ in range(7):
        model_results = model.systolic_step()
        
        dut.EN_systolic_step.value = 1
        await RisingEdge(dut.CLK)
        dut.EN_systolic_step.value = 0
        
        dut_results = []
        for i in range(4):
            # Convert DUT BFLOAT16 results back to float for comparison
            bfloat16_val = int(dut.get_result_value[i].value)
            float_val = struct.unpack('!f', struct.pack('!I', bfloat16_val << 16))[0]
            dut_results.append(float_val)
        
        if any(model_results):
            print(f"BFLOAT16 Step Results - Model: {model_results}")
            print(f"BFLOAT16 Step Results - DUT: {dut_results}")
            for i in range(4):
                # Use relative tolerance for float comparison
                assert abs(dut_results[i] - model_results[i]) / abs(model_results[i]) < 0.01, \
                    f"Mismatch at position {i}: DUT={dut_results[i]}, Model={model_results[i]}"
    
    # Export coverage data
    coverage_db.export_to_yaml(filename="coverage_systolic_array.yml")
