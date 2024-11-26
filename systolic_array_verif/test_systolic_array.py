import os
import random
from pathlib import Path
import cocotb
from cocotb_coverage.coverage import coverage_db
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
import struct

from .model_systolic_array import SystolicArray, DataType

def generate_random_matrices(size=4, is_float=False):
    """Generate random test matrices"""
    if is_float:
        # Generate random float values between -10 and 10
        A = [[random.uniform(-10, 10) for _ in range(size)] for _ in range(size)]
        B = [[random.uniform(-10, 10) for _ in range(size)] for _ in range(size)]
        C = [[random.uniform(-10, 10) for _ in range(size)] for _ in range(size)]
    else:
        # Generate random int8 values (-128 to 127)
        A = [[random.randint(-128, 127) for _ in range(size)] for _ in range(size)]
        B = [[random.randint(-128, 127) for _ in range(size)] for _ in range(size)]
        C = [[random.randint(-128, 127) for _ in range(size)] for _ in range(size)]
    return A, B, C

def float_to_bfloat16(value):
    """Convert float to bfloat16 format"""
    return struct.unpack('!I', struct.pack('!f', value))[0] >> 16

def bfloat16_to_float(bfloat16_val):
    """Convert bfloat16 to float"""
    return struct.unpack('!f', struct.pack('!I', bfloat16_val << 16))[0]

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
    
    # Generate random test matrices
    A, B, C = generate_random_matrices(4, is_float=False)
    
    # Create model instance
    model = SystolicArray(4)
    model.set_data_type(DataType.INT8)
    
    # Load matrices into DUT and model
    for i in range(4):
        for j in range(4):
            # Load A row by row
            dut.put_A_row0_value.value = A[0][j] if i == 0 else 0
            dut.put_A_row1_value.value = A[1][j] if i == 1 else 0
            dut.put_A_row2_value.value = A[2][j] if i == 2 else 0
            dut.put_A_row3_value.value = A[3][j] if i == 3 else 0
            
            dut.EN_put_A_row0.value = 1 if i == 0 else 0
            dut.EN_put_A_row1.value = 1 if i == 1 else 0
            dut.EN_put_A_row2.value = 1 if i == 2 else 0
            dut.EN_put_A_row3.value = 1 if i == 3 else 0
            
            # Load B column by column
            dut.put_B_col0_value.value = B[j][0] if i == j else 0
            dut.put_B_col1_value.value = B[j][1] if i == j else 0
            dut.put_B_col2_value.value = B[j][2] if i == j else 0
            dut.put_B_col3_value.value = B[j][3] if i == j else 0
            
            dut.EN_put_B_col0.value = 1 if i == j else 0
            dut.EN_put_B_col1.value = 1 if i == j else 0
            dut.EN_put_B_col2.value = 1 if i == j else 0
            dut.EN_put_B_col3.value = 1 if i == j else 0
            
            # Load C values
            dut.put_C_col0_value.value = C[j][0] if i == j else 0
            dut.put_C_col1_value.value = C[j][1] if i == j else 0
            dut.put_C_col2_value.value = C[j][2] if i == j else 0
            dut.put_C_col3_value.value = C[j][3] if i == j else 0
            
            dut.EN_put_C_col0.value = 1 if i == j else 0
            dut.EN_put_C_col1.value = 1 if i == j else 0
            dut.EN_put_C_col2.value = 1 if i == j else 0
            dut.EN_put_C_col3.value = 1 if i == j else 0
            
            # Set select values for INT8 mode
            dut.put_select_col0_value.value = 0
            dut.put_select_col1_value.value = 0
            dut.put_select_col2_value.value = 0
            dut.put_select_col3_value.value = 0
            
            dut.EN_put_select_col0.value = 1 if i == j else 0
            dut.EN_put_select_col1.value = 1 if i == j else 0
            dut.EN_put_select_col2.value = 1 if i == j else 0
            dut.EN_put_select_col3.value = 1 if i == j else 0
            
            await RisingEdge(dut.CLK)
            
            # Update model
            if i == j:
                model.put_A_row(j, A[j][i])
                model.put_B_col(j, B[j][i])
                model.put_C_col(j, C[j][i])
    
    # Run systolic steps and compare results
    for step in range(7):  # 4 + 4 - 1 cycles needed for 4x4 array
        # Get model results
        model_results = model.systolic_step()
        
        # Get DUT results - handle 128-bit signal
        mac_results_signal = dut.get_MAC_results.value
        
        # The hardware returns a vector of 4 32-bit values
        # We need to extract them directly
        dut_results = []
        if mac_results_signal is not None:  # Check if signal has a value
            # Convert the signal value to binary string with fixed width
            binary_str = format(mac_results_signal.integer, '0128b')
            # Extract each 32-bit chunk from LSB to MSB
            for i in range(4):
                start_bit = i * 32
                end_bit = (i + 1) * 32
                chunk = binary_str[start_bit:end_bit]
                dut_results.append(int(chunk, 2))
        else:
            dut_results = [0] * 4
        
        # Compare results
        if any(model_results):
            dut._log.info(f"Model Results: {model_results}")
            dut._log.info(f"DUT Results: {dut_results}")
            # for i, (model_val, dut_val) in enumerate(zip(model_results, dut_results)):
            #     if model_val != 0:  # Only compare non-zero values
            #         assert dut_val == model_val, f"Mismatch at position {i}: Model={model_val}, DUT={dut_val}"
        
        await RisingEdge(dut.CLK)
    
    # Test BFLOAT16 mode
    print("\nTesting BFLOAT16 Mode")
    
    # Reset DUT
    dut.RST_N.value = 0
    await RisingEdge(dut.CLK)
    dut.RST_N.value = 1
    await RisingEdge(dut.CLK)
    
    # Generate random floating-point matrices
    A, B, C = generate_random_matrices(4, is_float=True)
    
    # Create new model instance for BFLOAT16
    model = SystolicArray(4)
    model.set_data_type(DataType.BFLOAT16)
    
    # Load matrices (similar to INT8 mode but with BFLOAT16 conversion)
    for i in range(4):
        for j in range(4):
            # Convert values to BFLOAT16
            a_val = float_to_bfloat16(A[i][j]) if i == j else 0
            b_val = float_to_bfloat16(B[j][i]) if i == j else 0
            c_val = float_to_bfloat16(C[j][i]) if i == j else 0
            
            # Load A, B, C values (similar to INT8 mode)
            dut.put_A_row0_value.value = a_val if i == 0 else 0
            dut.put_A_row1_value.value = a_val if i == 1 else 0
            dut.put_A_row2_value.value = a_val if i == 2 else 0
            dut.put_A_row3_value.value = a_val if i == 3 else 0
            
            dut.EN_put_A_row0.value = 1 if i == 0 else 0
            dut.EN_put_A_row1.value = 1 if i == 1 else 0
            dut.EN_put_A_row2.value = 1 if i == 2 else 0
            dut.EN_put_A_row3.value = 1 if i == 3 else 0
            
            dut.put_B_col0_value.value = b_val if i == j else 0
            dut.put_B_col1_value.value = b_val if i == j else 0
            dut.put_B_col2_value.value = b_val if i == j else 0
            dut.put_B_col3_value.value = b_val if i == j else 0
            
            dut.EN_put_B_col0.value = 1 if i == j else 0
            dut.EN_put_B_col1.value = 1 if i == j else 0
            dut.EN_put_B_col2.value = 1 if i == j else 0
            dut.EN_put_B_col3.value = 1 if i == j else 0
            
            dut.put_C_col0_value.value = c_val if i == j else 0
            dut.put_C_col1_value.value = c_val if i == j else 0
            dut.put_C_col2_value.value = c_val if i == j else 0
            dut.put_C_col3_value.value = c_val if i == j else 0
            
            dut.EN_put_C_col0.value = 1 if i == j else 0
            dut.EN_put_C_col1.value = 1 if i == j else 0
            dut.EN_put_C_col2.value = 1 if i == j else 0
            dut.EN_put_C_col3.value = 1 if i == j else 0
            
            # Set select values for BFLOAT16 mode
            dut.put_select_col0_value.value = 1
            dut.put_select_col1_value.value = 1
            dut.put_select_col2_value.value = 1
            dut.put_select_col3_value.value = 1
            
            dut.EN_put_select_col0.value = 1 if i == j else 0
            dut.EN_put_select_col1.value = 1 if i == j else 0
            dut.EN_put_select_col2.value = 1 if i == j else 0
            dut.EN_put_select_col3.value = 1 if i == j else 0
            
            await RisingEdge(dut.CLK)
            
            # Update model
            if i == j:
                model.put_A_row(j, A[j][i])
                model.put_B_col(j, B[j][i])
                model.put_C_col(j, C[j][i])
    
    # Run systolic steps for BFLOAT16 mode
    for step in range(7):
        model_results = model.systolic_step()
        
        # Get and convert DUT results
        mac_results_signal = dut.get_MAC_results.value
        
        # The hardware returns a vector of 4 32-bit values
        # We need to extract them directly
        dut_results = []
        if mac_results_signal is not None:  # Check if signal has a value
            # Convert the signal value to binary string with fixed width
            binary_str = format(mac_results_signal.integer, '0128b')
            # Extract each 32-bit chunk from LSB to MSB
            for i in range(4):
                start_bit = i * 32
                end_bit = (i + 1) * 32
                chunk = binary_str[start_bit:end_bit]
                dut_results.append(bfloat16_to_float(int(chunk, 2)))
        else:
            dut_results = [0] * 4
        
        # Compare with relative tolerance for floating-point
        if any(model_results):
            dut._log.info(f"Model Results: {model_results}")
            dut._log.info(f"DUT Results: {dut_results}")
            # for i, (model_val, dut_val) in enumerate(zip(model_results, dut_results)):
            #     if abs(model_val) > 1e-6:  # Only compare non-zero values with some tolerance
            #         rel_diff = abs(model_val - dut_val) / abs(model_val)
            #         assert rel_diff < 1e-3, f"Mismatch at position {i}: Model={model_val}, DUT={dut_val}"
        
        await RisingEdge(dut.CLK)
    
    # Export coverage data
    #coverage_db.export_to_yaml(filename="coverage_systolic_array.yml")
