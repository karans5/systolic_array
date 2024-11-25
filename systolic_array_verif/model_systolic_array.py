from enum import Enum
import sys
import os

# Add MAC model path to system path
mac_verif_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../mac/mac_verif"))
sys.path.append(mac_verif_path)

from model_mac import refmodel

class DataType(Enum):
    INT8 = 0
    BFLOAT16 = 1

class SystolicArray:
    def __init__(self, size=4):
        self.size = size
        self.data_type = DataType.INT8
        
        # Initialize matrices
        self.A = [[0 for _ in range(size)] for _ in range(size)]
        self.B = [[0 for _ in range(size)] for _ in range(size)]
        self.C = [[0 for _ in range(size)] for _ in range(size)]
        
        # MAC outputs for each cell
        self.mac_outputs = [[0 for _ in range(size)] for _ in range(size)]
        
        # Registers for A values (horizontal propagation)
        self.A_regs = [[0 for _ in range(size)] for _ in range(size)]
        
        # Registers for B values (vertical propagation)
        self.B_regs = [[0 for _ in range(size)] for _ in range(size)]
    
    def set_data_type(self, dtype):
        """Set the data type (INT8 or BFLOAT16)"""
        self.data_type = dtype
    
    def put_A_row(self, row, value):
        """Input A value for a specific row"""
        if 0 <= row < self.size:
            # Store in first column of the row
            self.A[row][0] = value
    
    def put_B_col(self, col, value):
        """Input B value for a specific column"""
        if 0 <= col < self.size:
            # Store in first row of the column
            self.B[0][col] = value
    
    def put_C_col(self, col, value):
        """Input C value for a specific column"""
        if 0 <= col < self.size:
            self.C[0][col] = value
    
    def systolic_step(self):
        """Perform one step of systolic array computation"""
        # Store current outputs
        prev_outputs = [[self.mac_outputs[i][j] for j in range(self.size)] for i in range(self.size)]
        
        # Update MAC outputs
        for i in range(self.size):
            for j in range(self.size):
                # Get inputs for this MAC unit
                a_in = self.A_regs[i][j]
                b_in = self.B_regs[i][j]
                c_in = prev_outputs[i-1][j] if i > 0 else self.C[i][j]
                
                # Perform MAC operation
                self.mac_outputs[i][j] = refmodel(a_in, b_in, c_in, 1 if self.data_type == DataType.BFLOAT16 else 0)
        
        # Propagate A values horizontally
        for i in range(self.size):
            for j in range(self.size-1, 0, -1):
                self.A_regs[i][j] = self.A_regs[i][j-1]
            self.A_regs[i][0] = self.A[i][0]
            self.A[i][0] = 0  # Clear input
        
        # Propagate B values vertically
        for j in range(self.size):
            for i in range(self.size-1, 0, -1):
                self.B_regs[i][j] = self.B_regs[i-1][j]
            self.B_regs[0][j] = self.B[0][j]
            self.B[0][j] = 0  # Clear input
        
        # Return bottom row results
        return [self.mac_outputs[self.size-1][j] for j in range(self.size)]
