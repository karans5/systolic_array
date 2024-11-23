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
