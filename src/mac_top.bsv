package mac_top;

import mac::*;  
import mac_fp::*;  
import mac_int::*;
import FIFO::*;
import GetPut::*;

//interface declaration for MAC top module
interface MAC_top_ifc;
    // Input interfaces
    method Action put_A(Bit#(16) value);
    method Action put_B(Bit#(16) value);
    method Action put_C(Bit#(32) value);
    method Action put_select(Bit#(1) mode);
    
    // Output interfaces for passing values through
    method ActionValue#(Bit#(16)) get_A_out();
    method ActionValue#(Bit#(16)) get_B_out();
    method ActionValue#(Bit#(1)) get_select_out();
    method Bit#(32) get_MAC();  // Direct output, no ActionValue needed
endinterface: MAC_top_ifc

(*synthesize*)
module mk_MAC_top(MAC_top_ifc);
    // FIFOs for input/output buffering
    FIFO#(Bit#(16)) fifo_A <- mkFIFO;
    FIFO#(Bit#(16)) fifo_B <- mkFIFO;
    FIFO#(Bit#(32)) fifo_C <- mkFIFO;
    FIFO#(Bit#(1)) fifo_select <- mkFIFO;
    
    // Instantiate the MAC module
    MAC_ifc mac <- mkMac;
    
    // Rule to process inputs
    rule process_inputs;
        let a = fifo_A.first();
        let b = fifo_B.first();
        let c = fifo_C.first();
        let sel = fifo_select.first();
        
        // Send inputs to MAC
        mac.get_A(a);
        mac.get_B(b);
        mac.get_C(c);
        mac.set_S1_or_S2(sel);
    endrule
    
    // Input methods
    method Action put_A(Bit#(16) value);
        fifo_A.enq(value);
    endmethod
    
    method Action put_B(Bit#(16) value);
        fifo_B.enq(value);
    endmethod
    
    method Action put_C(Bit#(32) value);
        fifo_C.enq(value);
    endmethod
    
    method Action put_select(Bit#(1) mode);
        fifo_select.enq(mode);
    endmethod
    
    // Output methods - from FIFOs
    method ActionValue#(Bit#(16)) get_A_out();
        fifo_A.deq();
        return fifo_A.first();
    endmethod
    
    method ActionValue#(Bit#(16)) get_B_out();
        fifo_B.deq();
        return fifo_B.first();
    endmethod
    
    method ActionValue#(Bit#(1)) get_select_out();
        fifo_select.deq();
        return fifo_select.first();
    endmethod
    
    // MAC output - direct from MAC unit
    method Bit#(32) get_MAC();
        return mac.get_MAC();
    endmethod
    
endmodule: mk_MAC_top

endpackage: mac_top
