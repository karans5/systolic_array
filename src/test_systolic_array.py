import os
import random
from pathlib import Path
import cocotb
from cocotb_coverage.coverage import coverage_db
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
import struct

#import coverage
from model_systolic_array import *

# Inputs

@cocotb.test()
async def test_mac(dut):
    '''Test the ARRAY module'''

    # Initialize and start the clock
    clock = Clock(dut.CLK, 10, units="us")
    cocotb.start_soon(clock.start(start_high=False))

    # Reset the DUT
    dut.RST_N.value = 0
    await RisingEdge(dut.CLK)
    dut.RST_N.value = 1
    await RisingEdge(dut.CLK)


   
