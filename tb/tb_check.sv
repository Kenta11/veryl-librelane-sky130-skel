// Functional check: for each vector, hold the inputs stable for 2 clocks so
// every DUT's registered output settles, then compare against a golden
// {cout,sum} = a + b + cin computed directly. All four adders must match.
// Not part of the ASIC flow; this only validates the RTL before synthesis.
module tb_check;
    localparam int W = 32;
    localparam int NR = 500;   // random vectors

    logic clk = 0;
    logic rst_n = 0;
    logic [W-1:0] a = 0, b = 0;
    logic cin = 0;

    logic [W-1:0] sum_beh, sum_rip, sum_csa, sum_ks;
    logic cout_beh, cout_rip, cout_csa, cout_ks;

    always #5 clk = ~clk;

    adder_compare_AdderBehavioral  #(.WIDTH(W)) u_beh (.i_clk(clk), .i_rst(rst_n), .i_a(a), .i_b(b), .i_cin(cin), .o_sum(sum_beh), .o_cout(cout_beh));
    adder_compare_AdderRipple      #(.WIDTH(W)) u_rip (.i_clk(clk), .i_rst(rst_n), .i_a(a), .i_b(b), .i_cin(cin), .o_sum(sum_rip), .o_cout(cout_rip));
    adder_compare_AdderCarrySelect #(.WIDTH(W)) u_csa (.i_clk(clk), .i_rst(rst_n), .i_a(a), .i_b(b), .i_cin(cin), .o_sum(sum_csa), .o_cout(cout_csa));
    adder_compare_AdderKoggeStone  #(.WIDTH(W)) u_ks  (.i_clk(clk), .i_rst(rst_n), .i_a(a), .i_b(b), .i_cin(cin), .o_sum(sum_ks),  .o_cout(cout_ks));

    int errors = 0, checks = 0;

    task automatic run(logic [W-1:0] va, logic [W-1:0] vb, logic vc);
        logic [W:0] golden;
        a = va; b = vb; cin = vc;
        @(posedge clk);            // input register captures
        @(posedge clk);            // output register captures
        #1;
        golden = {1'b0, va} + {1'b0, vb} + vc;
        check("behavioral",   sum_beh, cout_beh, golden);
        check("ripple",       sum_rip, cout_rip, golden);
        check("carry_select", sum_csa, cout_csa, golden);
        check("kogge_stone",  sum_ks,  cout_ks,  golden);
    endtask

    task automatic check(string name, logic [W-1:0] s, logic c, logic [W:0] g);
        checks++;
        if ({c, s} !== g) begin
            errors++;
            if (errors <= 20)
                $display("  MISMATCH %-14s a=%h b=%h cin=%b -> got {%1b,%h} exp {%1b,%h}",
                         name, a, b, cin, c, s, g[W], g[W-1:0]);
        end
    endtask

    int i;
    initial begin
        repeat (4) @(posedge clk);
        rst_n = 1;
        // directed corner cases
        run({W{1'b1}}, {W{1'b1}}, 1'b1);          // all ones + carry
        run({W{1'b1}}, 32'd1,     1'b0);          // carry ripples end to end
        run(32'd0,     32'd0,     1'b1);          // just carry-in
        run(32'h8000_0000, 32'h8000_0000, 1'b0); // msb carry-out
        run(32'hFFFF_FFFF, 32'd0,  1'b1);         // FF..F + carry
        run(32'd0,     32'd0,     1'b0);          // zero
        // random
        for (i = 0; i < NR; i++)
            run({$random, $random}, {$random, $random}, ($random & 32'd1));

        if (errors == 0)
            $display("ALL ADDERS PASS (%0d checks: %0d vectors x 4 designs)", checks, checks/4);
        else
            $display("FAILED: %0d mismatches out of %0d checks", errors, checks);
        $finish;
    end
endmodule
