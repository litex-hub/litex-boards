/*
© IBM Corp. 2020
Licensed under the Apache License, Version 2.0 (the "License"), as modified by the terms below; you may not use the files in this
repository except in compliance with the License as modified.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Modified Terms:

   1)	For the purpose of the patent license granted to you in Section 3 of the License, the "Work" hereby includes implementations of
   the work of authorship in physical form.

   2)	Notwithstanding any terms to the contrary in the License, any licenses necessary for implementation of the Work that are available
   from OpenPOWER via the Power ISA End User License Agreement (EULA) are explicitly excluded hereunder, and may be obtained from OpenPOWER
   under the terms and conditions of the EULA.

Unless required by applicable law or agreed to in writing, the reference design distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language
governing permissions and limitations under the License.

Additional rights, including the ability to physically implement a softcore that is compliant with the required sections of the Power
ISA Specification, are available at no cost under the terms of the OpenPOWER Power ISA EULA, which can be obtained (along with the Power
ISA) here: https://openpowerfoundation.org.

Brief explanation of modifications:

Modification 1: This modification extends the patent license to an implementation of the Work in physical form – i.e.,
it unambiguously permits a user to make and use the physical chip.

Modification 2: This modification clarifies that licenses for the Power ISA are provided via the (royalty-free) Power ISA EULA,
and not under this license.  To prevent fragmentation of the Power ISA, the Power ISA EULA requires that Power ISA Cores be
licensed consistent with the terms of the Power ISA EULA.  By ensuring that rights available via the Power ISA EULA are received
under (and subject to) the EULA, this consistency is maintained in accordance with the terms of the EULA. Any necessary additional
licenses for the specific Power ISA Core are granted under this modified Apache license.
*/

`timescale 1 ns / 1 ns

// Asynchronous SRAM Wishbone Slave (IS61WV5128)
// 32b non-pipelined, 3-cycle write, 512Kx8

module issiram  #(
   parameter WB_BITWIDTH = 32,
   parameter RAM_BITWIDTH = 8
)(
   input                clk,
   input                rst,
   input                wbs_stb_i,
   input                wbs_cyc_i,
   input  [29:0]        wbs_adr_i,
   input                wbs_we_i,
   input  [3:0]         wbs_sel_i,
   input  [31:0]        wbs_dat_i,
   output               wbs_ack_o,
   output [31:0]        wbs_dat_o,
   output               mem_ce_n,
   output               mem_oe_n,
   output               mem_we_n,
   output [18:0]        mem_adr,
   inout  [7:0]         mem_dat
);

   reg    [18:0]        cmd_adr_q;
   wire   [18:0]        cmd_adr_d;
   reg                  ack_q;
   wire                 ack_d;
   reg    [31:0]        rd_dat_q;
   wire   [31:0]        rd_dat_d;
   reg    [3:0]         wr_sel_q;
   wire   [3:0]         wr_sel_d;
   reg    [31:0]        wr_dat_q;
   wire   [31:0]        wr_dat_d;
   reg    [5:0]         seq_q;
   wire   [5:0]         seq_d;

   wire                 stall;
   wire                 base_match;
   wire                 cmd_val;
   wire                 cmd_we;
   wire                 idle;
   wire                 read;
   wire                 write;
   wire                 oe;

   // FF
   always @(posedge clk) begin
      if (rst) begin
         cmd_adr_q <= 'h0;
         ack_q <= 'b0;
         rd_dat_q <= 'h0;
         wr_sel_q <= 'b0;
         wr_dat_q <= 'h0;
         seq_q <= 'b111111;
      end else begin
         cmd_adr_q <= cmd_adr_d;
         ack_q <= ack_d;
         rd_dat_q <= rd_dat_d;
         wr_sel_q <= wr_sel_d;
         wr_dat_q <= wr_dat_d;
         seq_q <= seq_d;
      end
   end

   // WB Interface

   assign stall = 0;          // not supported
   assign base_match = 1;     // if need to check address range locally

   assign cmd_val = idle & wbs_cyc_i & wbs_stb_i & ~stall & base_match & ~ack_q;
   assign cmd_we  = wbs_we_i;
   assign cmd_adr_d = cmd_val ? {wbs_adr_i[16:0], 2'b00} : cmd_adr_q;
   assign wr_sel_d  = cmd_val ? wbs_sel_i : wr_sel_q;
   assign wr_dat_d  = cmd_val ? wbs_dat_i : wr_dat_q;

   // R/W Sequencer

   // R2,W3
   // cmod-a7; runs 100

   //tbl rwseq
   //n seq_q                            seq_d
   //n |       cmd_val                  |      read
   //n |       |cmd_we                  |      |write
   //n |       ||wr_sel_q               |      ||oe
   //n |       |||                      |      |||ack_d
   //n |       |||                      |      ||||
   //n |       |||                      |      ||||
   //n |       |||                      |      ||||idle
   //b 543210  ||3210                   543210 |||||
   //t iiiiii  iiiiii                   oooooo ooooo
   //*------------------------------------------------
   //* Idle ******************************************
   //s 111111  ------                   ------ ----1
   //s 111111  0-----                   111111 0010-        * ...zzz...
   //s 111111  10----                   010000 0010-        * read32
   //s 111111  11----                   110000 0010-        * write32
   //* Read 0a****************************************
   //s 010000  ------                   011000 00100
   //* Read 0b****************************************
   //s 011000  ------                   010001 10100
   //* Read 1a****************************************
   //s 010001  ------                   011001 00100
   //* Read 1b****************************************
   //s 011001  ------                   010010 10100
   //* Read 2a ***************************************
   //s 010010  ------                   011010 00100
   //* Read 2b ***************************************
   //s 011010  ------                   010011 10100
   //* Read 3a ***************************************
   //s 010011  ------                   011011 00100
   //* Read 3b ***************************************
   //s 011011  ------                   111111 10110        * done
   //* Write 0a **************************************
   //s 110000  -----1                   110100 01100
   //s 110000  -----0                   110001 00100
   //* Write 0b **************************************
   //s 110100  ------                   111000 01000
   //* Write 0c **************************************
   //s 111000  ------                   110001 01100
   //* Write 1a **************************************
   //s 110001  ----1-                   110101 01100
   //s 110001  ----0-                   110010 00100
   //* Write 1b **************************************
   //s 110101  ------                   111001 01000
   //* Write 1c **************************************
   //s 111001  ------                   110010 01100
   //* Write 2a **************************************
   //s 110010  ---1--                   110110 01100
   //s 110010  ---0--                   110011 00100
   //* Write 2b **************************************
   //s 110110  ------                   111010 01000
   //* Write 2c **************************************
   //s 111010  ------                   110011 01100
   //* Write 3a **************************************
   //s 110011  --1---                   110111 01100
   //s 110011  --0---                   111111 00110        * done
   //* Write 3b **************************************
   //s 110111  ------                   111011 01000
   //* Write 3c **************************************
   //s 111011  ------                   111111 01110        * done
   //*------------------------------------------------
   //tbl rwseq

   // Tristate Data

   assign rd_dat_d[7:0]   = (read & (seq_q[1:0] == 2'b00)) ? mem_dat : rd_dat_q[7:0];
   assign rd_dat_d[15:8]  = (read & (seq_q[1:0] == 2'b01)) ? mem_dat : rd_dat_q[15:8];
   assign rd_dat_d[23:16] = (read & (seq_q[1:0] == 2'b10)) ? mem_dat : rd_dat_q[23:16];
   assign rd_dat_d[31:24] = (read & (seq_q[1:0] == 2'b11)) ? mem_dat : rd_dat_q[31:24];

   assign mem_dat = write ? (seq_q[1:0] == 2'b00 ? wr_dat_q[7:0]    :
                             seq_q[1:0] == 2'b01 ? wr_dat_q[15:8]   :
                             seq_q[1:0] == 2'b10 ? wr_dat_q[23:16]  :
                                                   wr_dat_q[31:24]) :
                             8'bz;

   // Outputs

   assign wbs_ack_o = ack_q & ~rst;
   assign wbs_dat_o = rd_dat_q;

   assign mem_ce_n = 'b0;
   assign mem_oe_n = ~oe;
   assign mem_we_n = ~write;
   assign mem_adr = {cmd_adr_q[18:2], seq_q[1:0]};

  // Generated
//vtable rwseq
assign seq_d[5] =
  (seq_q[5] & seq_q[4] & seq_q[3] & seq_q[2] & seq_q[1] & seq_q[0] & ~cmd_val) +
  (seq_q[5] & seq_q[4] & seq_q[3] & seq_q[2] & seq_q[1] & seq_q[0] & cmd_val & cmd_we) +
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0] & wr_sel_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0] & ~wr_sel_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & seq_q[2] & ~seq_q[1] & ~seq_q[0]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0] & wr_sel_q[1]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0] & ~wr_sel_q[1]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & seq_q[2] & ~seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0] & wr_sel_q[2]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0] & ~wr_sel_q[2]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & seq_q[2] & seq_q[1] & ~seq_q[0]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0] & wr_sel_q[3]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0] & ~wr_sel_q[3]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & seq_q[2] & seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]);
assign seq_d[4] =
  (seq_q[5] & seq_q[4] & seq_q[3] & seq_q[2] & seq_q[1] & seq_q[0] & ~cmd_val) +
  (seq_q[5] & seq_q[4] & seq_q[3] & seq_q[2] & seq_q[1] & seq_q[0] & cmd_val & ~cmd_we) +
  (seq_q[5] & seq_q[4] & seq_q[3] & seq_q[2] & seq_q[1] & seq_q[0] & cmd_val & cmd_we) +
  (~seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0]) +
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0]) +
  (~seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0]) +
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0]) +
  (~seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0]) +
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0]) +
  (~seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]) +
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0] & wr_sel_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0] & ~wr_sel_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & seq_q[2] & ~seq_q[1] & ~seq_q[0]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0] & wr_sel_q[1]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0] & ~wr_sel_q[1]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & seq_q[2] & ~seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0] & wr_sel_q[2]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0] & ~wr_sel_q[2]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & seq_q[2] & seq_q[1] & ~seq_q[0]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0] & wr_sel_q[3]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0] & ~wr_sel_q[3]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & seq_q[2] & seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]);
assign seq_d[3] =
  (seq_q[5] & seq_q[4] & seq_q[3] & seq_q[2] & seq_q[1] & seq_q[0] & ~cmd_val) +
  (~seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0]) +
  (~seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0]) +
  (~seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0]) +
  (~seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]) +
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & seq_q[2] & ~seq_q[1] & ~seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & seq_q[2] & ~seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & seq_q[2] & seq_q[1] & ~seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0] & ~wr_sel_q[3]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & seq_q[2] & seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]);
assign seq_d[2] =
  (seq_q[5] & seq_q[4] & seq_q[3] & seq_q[2] & seq_q[1] & seq_q[0] & ~cmd_val) +
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0] & wr_sel_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0] & wr_sel_q[1]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0] & wr_sel_q[2]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0] & wr_sel_q[3]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0] & ~wr_sel_q[3]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]);
assign seq_d[1] =
  (seq_q[5] & seq_q[4] & seq_q[3] & seq_q[2] & seq_q[1] & seq_q[0] & ~cmd_val) +
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0]) +
  (~seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0]) +
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0]) +
  (~seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]) +
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0] & ~wr_sel_q[1]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0] & wr_sel_q[2]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0] & ~wr_sel_q[2]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & seq_q[2] & seq_q[1] & ~seq_q[0]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0] & wr_sel_q[3]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0] & ~wr_sel_q[3]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & seq_q[2] & seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]);
assign seq_d[0] =
  (seq_q[5] & seq_q[4] & seq_q[3] & seq_q[2] & seq_q[1] & seq_q[0] & ~cmd_val) +
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0]) +
  (~seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0]) +
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0]) +
  (~seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]) +
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0] & ~wr_sel_q[0]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0] & wr_sel_q[1]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & seq_q[2] & ~seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0] & ~wr_sel_q[2]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0] & wr_sel_q[3]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0] & ~wr_sel_q[3]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & seq_q[2] & seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]);
assign read =
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0]) +
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0]) +
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0]) +
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]);
assign write =
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0] & wr_sel_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & seq_q[2] & ~seq_q[1] & ~seq_q[0]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0] & wr_sel_q[1]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & seq_q[2] & ~seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0] & wr_sel_q[2]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & seq_q[2] & seq_q[1] & ~seq_q[0]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0] & wr_sel_q[3]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & seq_q[2] & seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]);
assign oe =
  (seq_q[5] & seq_q[4] & seq_q[3] & seq_q[2] & seq_q[1] & seq_q[0] & ~cmd_val) +
  (seq_q[5] & seq_q[4] & seq_q[3] & seq_q[2] & seq_q[1] & seq_q[0] & cmd_val & ~cmd_we) +
  (seq_q[5] & seq_q[4] & seq_q[3] & seq_q[2] & seq_q[1] & seq_q[0] & cmd_val & cmd_we) +
  (~seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0]) +
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0]) +
  (~seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0]) +
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0]) +
  (~seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0]) +
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0]) +
  (~seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]) +
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0] & wr_sel_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0] & ~wr_sel_q[0]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & ~seq_q[1] & ~seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0] & wr_sel_q[1]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0] & ~wr_sel_q[1]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & ~seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0] & wr_sel_q[2]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0] & ~wr_sel_q[2]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & ~seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0] & wr_sel_q[3]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0] & ~wr_sel_q[3]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]);
assign ack_d =
  (~seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]) +
  (seq_q[5] & seq_q[4] & ~seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0] & ~wr_sel_q[3]) +
  (seq_q[5] & seq_q[4] & seq_q[3] & ~seq_q[2] & seq_q[1] & seq_q[0]);
assign idle =
  (seq_q[5] & seq_q[4] & seq_q[3] & seq_q[2] & seq_q[1] & seq_q[0]);
//vtable rwseq

endmodule
