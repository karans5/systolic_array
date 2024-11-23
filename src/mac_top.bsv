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
    // FIFOs for MAC computation
    FIFO#(Bit#(16)) fifo_A_mac <- mkFIFO;
    FIFO#(Bit#(16)) fifo_B_mac <- mkFIFO;
    FIFO#(Bit#(32)) fifo_C_mac <- mkFIFO;
    FIFO#(Bit#(1)) fifo_select_mac <- mkFIFO;
    
    // FIFOs for output routing
    FIFO#(Bit#(16)) fifo_A_out <- mkFIFO;
    FIFO#(Bit#(16)) fifo_B_out <- mkFIFO;
    FIFO#(Bit#(1)) fifo_select_out <- mkFIFO;
    
    // Instantiate the MAC module
    MAC_ifc mac <- mkMac;
    
    // Rule to process inputs for MAC computation
    rule process_inputs;
        let a = fifo_A_mac.first(); fifo_A_mac.deq();
        let b = fifo_B_mac.first(); fifo_B_mac.deq();
        let c = fifo_C_mac.first(); fifo_C_mac.deq();
        let sel = fifo_select_mac.first(); fifo_select_mac.deq();
        
        // Send inputs to MAC
        mac.get_A(a);
        mac.get_B(b);
        mac.get_C(c);
        mac.set_S1_or_S2(sel);
    endrule
    
    // Input methods - enqueue to both MAC and output FIFOs
    method Action put_A(Bit#(16) value);
        fifo_A_mac.enq(value);
        fifo_A_out.enq(value);
    endmethod
    
    method Action put_B(Bit#(16) value);
        fifo_B_mac.enq(value);
        fifo_B_out.enq(value);
    endmethod
    
    method Action put_C(Bit#(32) value);
        fifo_C_mac.enq(value);
    endmethod
    
    method Action put_select(Bit#(1) mode);
        fifo_select_mac.enq(mode);
        fifo_select_out.enq(mode);
    endmethod
    
    // Output methods - from output FIFOs
    method ActionValue#(Bit#(16)) get_A_out();
        let value = fifo_A_out.first();
        fifo_A_out.deq();
        return value;
    endmethod
    
    method ActionValue#(Bit#(16)) get_B_out();
        let value = fifo_B_out.first();
        fifo_B_out.deq();
        return value;
    endmethod
    
    method ActionValue#(Bit#(1)) get_select_out();
        let value = fifo_select_out.first();
        fifo_select_out.deq();
        return value;
    endmethod
    
    // MAC output - direct from MAC unit
    method Bit#(32) get_MAC();
        return mac.get_MAC();
    endmethod
    
endmodule: mk_MAC_top

endpackage: mac_top
