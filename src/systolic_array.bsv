package systolic_array;

import Vector::*;
import mac_top::*;
import FIFO::*;
import RegFile::*;

// Interface for the 4x4 systolic array
interface Systolic_Array_ifc;
    // Input interfaces for each row (A values)
    method Action put_A_row0(Bit#(16) value);
    method Action put_A_row1(Bit#(16) value);
    method Action put_A_row2(Bit#(16) value);
    method Action put_A_row3(Bit#(16) value);
    
    // Input interfaces for each column (B values)
    method Action put_B_col0(Bit#(16) value);
    method Action put_B_col1(Bit#(16) value);
    method Action put_B_col2(Bit#(16) value);
    method Action put_B_col3(Bit#(16) value);
    
    // Input interfaces for each column (select values)
    method Action put_select_col0(Bit#(1) value);
    method Action put_select_col1(Bit#(1) value);
    method Action put_select_col2(Bit#(1) value);
    method Action put_select_col3(Bit#(1) value);
    
    // Input interfaces for each column (C values)
    method Action put_C_col0(Bit#(32) value);
    method Action put_C_col1(Bit#(32) value);
    method Action put_C_col2(Bit#(32) value);
    method Action put_C_col3(Bit#(32) value);
    
    // Output interface to get MAC results from last row
    method Vector#(4, Bit#(32)) get_MAC_results();
endinterface

(* synthesize *)
module mkSystolic_Array(Systolic_Array_ifc);
    // Create a 4x4 array of MAC units
    Vector#(4, Vector#(4, MAC_top_ifc)) mac_array <- replicateM(replicateM(mk_MAC_top));
    
    // Input FIFOs for A (one per row)
    Vector#(4, FIFO#(Bit#(16))) fifo_A_rows <- replicateM(mkFIFO);
    
    // Input FIFOs for B, select, and C (one per column)
    Vector#(4, FIFO#(Bit#(16))) fifo_B_cols <- replicateM(mkFIFO);
    Vector#(4, FIFO#(Bit#(1))) fifo_select_cols <- replicateM(mkFIFO);
    Vector#(4, FIFO#(Bit#(32))) fifo_C_cols <- replicateM(mkFIFO);
    
    // Registers to store MAC results
    Vector#(4, Reg#(Bit#(32))) mac_results <- replicateM(mkReg(0));
    
    // Single rule for systolic array operation
    rule systolic_step;
        // Process each cell in the array
        for (Integer i = 0; i < 4; i = i + 1) begin
            for (Integer j = 0; j < 4; j = j + 1) begin
                // Handle A values (horizontal flow)
                if (j == 0) begin
                    // First column gets A from input FIFO
                    let a = fifo_A_rows[i].first();
                    fifo_A_rows[i].deq();
                    mac_array[i][j].put_A(a);
                end else begin
                    // Other columns get A from previous MAC unit
                    let a <- mac_array[i][j-1].get_A_out();
                    mac_array[i][j].put_A(a);
                end
                
                // Handle B and select values (vertical flow)
                if (i == 0) begin
                    // First row gets B and select from input FIFOs
                    let b = fifo_B_cols[j].first();
                    let s = fifo_select_cols[j].first();
                    fifo_B_cols[j].deq();
                    fifo_select_cols[j].deq();
                    mac_array[i][j].put_B(b);
                    mac_array[i][j].put_select(s);
                end else begin
                    // Other rows get B and select from previous MAC unit
                    let b <- mac_array[i-1][j].get_B_out();
                    let s <- mac_array[i-1][j].get_select_out();
                    mac_array[i][j].put_B(b);
                    mac_array[i][j].put_select(s);
                end
                
                // Handle C values and MAC computation
                if (i == 0) begin
                    // First row gets C from input FIFOs
                    let c = fifo_C_cols[j].first();
                    fifo_C_cols[j].deq();
                    mac_array[i][j].put_C(c);
                end else begin
                    // Other rows get C from previous MAC unit's result
                    mac_array[i][j].put_C(mac_array[i-1][j].get_MAC());
                end
                
                // Store last row's MAC results
                if (i == 3) begin
                    mac_results[j] <= mac_array[i][j].get_MAC();
                end
            end
        end
    endrule
    
    // Input methods
    method Action put_A_row0(Bit#(16) value);
        fifo_A_rows[0].enq(value);
    endmethod
    
    method Action put_A_row1(Bit#(16) value);
        fifo_A_rows[1].enq(value);
    endmethod
    
    method Action put_A_row2(Bit#(16) value);
        fifo_A_rows[2].enq(value);
    endmethod
    
    method Action put_A_row3(Bit#(16) value);
        fifo_A_rows[3].enq(value);
    endmethod
    
    method Action put_B_col0(Bit#(16) value);
        fifo_B_cols[0].enq(value);
    endmethod
    
    method Action put_B_col1(Bit#(16) value);
        fifo_B_cols[1].enq(value);
    endmethod
    
    method Action put_B_col2(Bit#(16) value);
        fifo_B_cols[2].enq(value);
    endmethod
    
    method Action put_B_col3(Bit#(16) value);
        fifo_B_cols[3].enq(value);
    endmethod
    
    method Action put_select_col0(Bit#(1) value);
        fifo_select_cols[0].enq(value);
    endmethod
    
    method Action put_select_col1(Bit#(1) value);
        fifo_select_cols[1].enq(value);
    endmethod
    
    method Action put_select_col2(Bit#(1) value);
        fifo_select_cols[2].enq(value);
    endmethod
    
    method Action put_select_col3(Bit#(1) value);
        fifo_select_cols[3].enq(value);
    endmethod
    
    method Action put_C_col0(Bit#(32) value);
        fifo_C_cols[0].enq(value);
    endmethod
    
    method Action put_C_col1(Bit#(32) value);
        fifo_C_cols[1].enq(value);
    endmethod
    
    method Action put_C_col2(Bit#(32) value);
        fifo_C_cols[2].enq(value);
    endmethod
    
    method Action put_C_col3(Bit#(32) value);
        fifo_C_cols[3].enq(value);
    endmethod
    
    method Vector#(4, Bit#(32)) get_MAC_results();
        return readVReg(mac_results);
    endmethod
    
endmodule

endpackage
