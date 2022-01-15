/*==========================================================
 * Copyright 2020 QuickLogic Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *==========================================================*/

#include "Fw_global_config.h"
#include "s3x_clock.h"
#include "eoss3_hal_audio.h"
#include "s3x_dfs.h"
#include "s3x_pi.h"

UINT8_t S3clkd_size, S3_dfs_max_index;

S3x_ClkD S3clk [] = {
    [CLK_C10] =  {
        .name = "C10",
        .clkd_id = CLK_C10,
        .type = SRC_CLK,
        .sync_clk = SYNC_CLKD(2, CLK_C01, CLK_C09),
        .cru_ctrl = CRU_CTRL(0x0, 0x1fe, 9, 0x4, 0x50, 0x7f, 0),
        .flags = HW_GATED,
        .def_max_rate = HSOSC_DEF_RATE,
        .init_state = INIT_STATE(F_48MHZ, 0x5f, INIT_GATE_ON),
    },
    [CLK_C02] = {
        .name = "C2",
        .clkd_id = CLK_C02,
        .type = SRC_CLK ,
        .sync_clk = SYNC_CLKD (0, 0, 0),
        .cru_ctrl = CRU_CTRL (0x8, 0x1fe, 9, 0x130, 0x44, 0x7, 1),
        .def_max_rate = (F_40MHZ),
        .init_state = INIT_STATE(F_1MHZ, 7, INIT_GATE_OFF),
    },
    [CLK_C08X4] = {
        .name = "C8X4",
        .clkd_id = CLK_C08X4,
        .type = SRC_CLK,
        .sync_clk = SYNC_CLKD (1, CLK_C08X1, 0),
        .cru_ctrl = CRU_CTRL (0x10, 0x1fe, 9, 0x134, 0x48, 0x1, 2),
        .def_max_rate = (F_40MHZ),
        .init_state = INIT_STATE(F_2MHZ, 0x1, INIT_GATE_OFF),
    },
    [CLK_C11] = {
        .name = "C11",
        .clkd_id = CLK_C11,
        .type = SRC_CLK,
        .sync_clk = SYNC_CLKD (0, 0, 0),
        .cru_ctrl = CRU_CTRL (0x14, 0x1fe, 9, 0x138, 0x54, 0x1, 3),
        .flags = LOCK_KEY,
        .def_max_rate = (F_12MHZ),
        .init_state = INIT_STATE(F_2MHZ, 0, INIT_GATE_OFF),
    },
    [CLK_C16] = { // FPGA clk source 0
        .name = "C16",
        .clkd_id = CLK_C16,
        .type = SRC_CLK,
        .sync_clk = SYNC_CLKD (0, 0, 0),
        .cru_ctrl = CRU_CTRL (0x20, 0x1fe, 9, 0x24, 0x64, 0x01, 5),
        .def_max_rate = (F_24MHZ),
        .init_state = INIT_STATE(F_10MHZ, 1, INIT_GATE_OFF),
    },
    [CLK_C30] = {
        .name = "C30",
        .clkd_id = CLK_C30,
        .type = SRC_CLK,
        .sync_clk = SYNC_CLKD (1, CLK_C31, 0xFF),
        .cru_ctrl = CRU_CTRL (0x28, 0x1fe, 9, 0x144, 0x120, 0xF, 6),
        .def_max_rate = (F_6MHZ),
        .init_state = INIT_STATE(PDM2PCM_CLK_C30, 5, INIT_GATE_OFF),

    },
    [CLK_C19] = {
        .name = "C19",
        .clkd_id = CLK_C19,
        .type = SRC_CLK,
        .sync_clk = SYNC_CLKD (0, 0, 0),
        .cru_ctrl = CRU_CTRL (0x2c, 0x1fe, 9, 0x13c, 0x6c, 0x1, 7),
        .def_max_rate = (F_1MHZ),
        .init_state = INIT_STATE(F_256KHZ/4, 1, INIT_GATE_OFF),
    },
    [CLK_C21] = {
        .name = "C21",
        .clkd_id = CLK_C21,
        .type = SRC_CLK,
        .sync_clk = SYNC_CLKD (0, 0, 0),
        .cru_ctrl = CRU_CTRL (0x34, 0x1fe, 9, 0x38, 0x70, 0x1, 8),
        .def_max_rate = (F_48MHZ),
        .init_state = INIT_STATE(F_1MHZ, 1, INIT_GATE_OFF),
    },
    [CLK_C01] = {
        .name = "C1",
        .clkd_id = CLK_C01,
        .type = SD_CLK,
        .sync_clk = SRC_DOMAIN (CLK_C10),
        .cru_ctrl = CRU_CTRL (0x110, 0xf, 4, 0, 0x40, 0x2ff, 4),
        .def_max_rate = (F_10MHZ),
        .init_state = INIT_STATE(F_10MHZ, 0x01, INIT_GATE_ON),
    },
    [CLK_C08X1] = {
        .name = "C8x",
        .clkd_id = CLK_C08X1,
        .type = FD_CLK,
        .div_val = 4,
        .sync_clk = SRC_DOMAIN (CLK_C08X4),
        .cru_ctrl = CRU_CTRL (0, 4, 0, 0, 0x4c, 0xd, 2),
        .def_max_rate = (F_12MHZ),
        .init_state = INIT_STATE(F_256KHZ, 8, INIT_GATE_OFF),
    },
    [CLK_C09] = {
        .name = "C9",
        .clkd_id = CLK_C09,
        .type = SD_CLK,
        .sync_clk = SRC_DOMAIN (CLK_C10),
        .cru_ctrl = CRU_CTRL (0x114, 0xf, 4, 0, 0x11c, 0x7, 4),
        .def_max_rate = (F_10MHZ),
        .init_state = INIT_STATE(F_6MHZ, 1, INIT_GATE_ON),
    },
    [CLK_C31] = {
        .name = "C31",
        .clkd_id = CLK_C31,
        .type = SD_CLK,
        .sync_clk = SRC_DOMAIN (CLK_C30),
        .cru_ctrl = CRU_CTRL (0x118, 0xf, 4, 0, 0x120, 0xF , 4),
        .def_max_rate = (F_10MHZ),
        .init_state = INIT_STATE(PDM2PCM_CLK_C31 , 8, INIT_GATE_OFF),
    },
};

S3x_Pi S3Pi [] = {
        [PI_A1] =  {
            .name = "A1",
            .pctrl = PI_CTRL(0xd0, 0xd4, 0x208 , 0x218, 1, 0x40, 0x40 ),
            .ginfo = PI_GINFO(2, S3X_CFG_DMA_A1_CLK, S3X_A1_CLK, 0 , 0, 0),
            .cfg_state = PI_SET_SHDN,
        },
        [PI_I2S] =  {
            .name = "I2S_S",
            .pctrl = PI_CTRL(0xe0, 0, 0x208, 0x218, 0x10, 0x20, 0x20),
            .ginfo = PI_GINFO(1, S3X_I2S_A1_CLK, 0, 0 , 0, 0),
            .cfg_state = PI_SET_SHDN,
        },
        [PI_EFUSE] =  {
            .name = "EFUSE",
            .pctrl = PI_CTRL(0xe0, 0, 0x208, 0x218, 0x4, 0x4, 0x4),
            .ginfo = PI_GINFO(2, S3X_EFUSE_01_CLK, S3X_EFUSE_02_CLK, 0, 0, 0),
            .cfg_state = PI_SET_SHDN,
        },
        [PI_FFE] =  {
            .name = "FFE",
            .pctrl = PI_CTRL(0x90, 0x94, 0x200, 0x210, 1, 1, 1),
            .ginfo = PI_GINFO(3, S3X_FFE_X4_CLK, S3X_FFE_X1_CLK, S3X_FFE_CLK, 0, 0),
            .cfg_state = PI_SET_SHDN,
        },
        [PI_PF] =  {
            .name = "PF",
            .pctrl = PI_CTRL(0xb0, 0xb4, 0x200, 0x210, 1, 4, 4),
            .ginfo = PI_GINFO(2, S3X_PKT_FIFO_CLK, S3X_ASYNC_FIFO_0_CLK, 0, 0, 0),
            .cfg_state = PI_SET_SHDN,
        },
        [PI_FB] =  {
            .name = "FB",
            .pctrl = PI_CTRL(0xa0, 0xa4, 0x200, 0x210, 1, 2, 2),
            .ginfo = PI_GINFO(4, S3X_FB_02_CLK, S3X_FB_16_CLK, S3X_FB_21_CLK , S3X_CLKGATE_FB, 0),
            .cfg_state = PI_NO_CFG,
        },

        [PI_AD0_ADMA] =  {
            .name = "AD_DMA",
            .pctrl = PI_CTRL(0xE4, 0, 0x20c, 0x21c, 0x1, 0x1, 0x1),
            .ginfo = PI_GINFO(1, S3X_AUDIO_DMA_CLK, 0, 0, 0, 0),
            .cfg_state = PI_SET_SHDN,
         },
         [PI_AD1_LEFT] =  {
            .name = "AD_L",
            .pctrl = PI_CTRL(0xE4, 0, 0x20c, 0x21c, 0x2, 0x2, 0xa),
            .ginfo = PI_GINFO(1, S3X_PDM_LEFT, 0, 0, 0, 0),
            .cfg_state = PI_SET_SHDN,
        },
         [PI_AD2_RIGHT] =  {
            .name = "AD_R",
            .pctrl = PI_CTRL(0xE4, 0, 0x20c, 0x21c, 0x4, 0x4, 0x4),
            .ginfo = PI_GINFO(1, S3X_PDM_RIGHT, 0, 0, 0, 0),
            .cfg_state = PI_SET_SHDN,
        },
        [PI_AD3_LPSD] =  {
            .name = "AD_LPSD",
            .pctrl = PI_CTRL(0xE4, 0, 0x20c, 0x21c, 0x8, 0x8, 0x8),
            .ginfo = PI_GINFO(1, S3X_LPSD, 0, 0, 0, 0),
            .cfg_state = PI_SET_SHDN,
        },
         [PI_AD4_I2SM] =  {
            .name = "AD_I2SM",
            .pctrl = PI_CTRL(0xE4, 0, 0x20c, 0x21c, 0x10, 0x10, 0x10),
            .ginfo = PI_GINFO(1, S3X_I2S_MASTER, 0, 0, 0, 0),
            .cfg_state = PI_SET_SHDN,
        },
        [PI_AD5_APB] =  {
            .name = "AD_APB",
            .pctrl = PI_CTRL(0xE4, 0, 0x20c, 0x21c, 0x20, 0x20, 0x20),
            .ginfo = PI_GINFO(1, S3X_AUDIO_APB, 0, 0, 0, 0),
            .cfg_state = PI_SET_SHDN,
        },
        [PI_SDMA] =  {
            .name = "SDMA",
            .pctrl = PI_CTRL(0x70, 0x74, 0x208, 0x218, 1, 1, 1),
            .ginfo = PI_GINFO(2, S3X_SDMA_SRAM_CLK, S3X_SDMA_CLK, 0, 0, 0),
            .cfg_state = PI_SET_SHDN,
        },
};

uint8_t policyInitial = 1;

S3x_Policy_Node dfs_node[]  = {
/* 0th Policy is only for lpm not for run mode */
    [0] = { // Sleep
        .clk_domain = {CLK_C01, CLK_C09, CLK_C10, CLK_C08X4},
        .rate = {F_256KHZ, F_256KHZ, F_48MHZ, F_256KHZ},
        .step_width =  800,/* msec */
        .cpuload_downthreshold = 0,
        .cpuload_upthreshold = 98,
        .policySleep = 0xFF,                   // Sleep policy: this is the sleep state, do nothing
        .minHSOSC = F_48MHZ,
    },

    [1] = { // Minimum performance
        .clk_domain = {CLK_C01, CLK_C09, CLK_C10, CLK_C08X4},
        .rate = {F_3MHZ, F_3MHZ, F_48MHZ, F_256KHZ},
        .step_width = 100,/* msec */
        .cpuload_downthreshold = 0,             // Lowest active state, never go lower
        .cpuload_upthreshold = 110,
        .policySleep = 0,                       // When idle, go to deep sleep (node 0)
        .minHSOSC = F_48MHZ,
    },
    [2] = {
        .clk_domain = {CLK_C01, CLK_C09, CLK_C10, CLK_C08X4},
        .rate = {C01_N2_CLK, C09_N2_CLK, C10_N2_CLK, C8X4_N2_CLK},
        .step_width =  STEP_2,/* msec */
        .cpuload_downthreshold = CPU_DOWN2,
    },

    [3] = {
        .clk_domain = {CLK_C01, CLK_C09, CLK_C10, CLK_C08X4},
        .rate = {C01_N3_CLK, C09_N3_CLK, C10_N3_CLK, C8X4_N3_CLK},
        .step_width = STEP_3,/* msec */
        .cpuload_downthreshold = CPU_DOWN3,
    },

    [4] = {
        .clk_domain = {CLK_C01, CLK_C09, CLK_C10, CLK_C08X4},
        .rate = {C01_N4_CLK, C09_N4_CLK, C10_N4_CLK, C8X4_N4_CLK},
        .step_width = STEP_3,/* msec */
        .cpuload_downthreshold = CPU_DOWN4,
    },
};

void S3x_pwrcfg_init(void)
{
    S3clkd_size = SIZEOF_ARRAY(S3clk);
    S3_dfs_max_index = (SIZEOF_ARRAY(dfs_node) - 1 );
    DFS_Initialize();
    S3x_Clk_Init();
    S3x_pi_init();
    DFS_StartTimer();
}

/* This value is determined from the icf and ld file.
    ROM and RAM2 blocks can be put into light sleep */
#define SRAM_IN_LPM_BLOCKS (0x7e3f)
static int sram_lpm_blocks = SRAM_IN_LPM_BLOCKS;

void s3x_sram_in_lpm(void)
{
    // Bit 0 is S0 (mem addr 0x0 to 0x00007fff) and so on
    /* LPMF */
    //PMU_WVAL(0x230, sram_lpm_blocks);
    __ISB();
    /* DS RAM, Leave 3 block of HWA Section,
    * 1 for SHM
    */
    PMU_WVAL(0x100, sram_lpm_blocks);
    __ISB();
}

/* This API is used to enable/disable sram in lpm
 * 0 -> disables lpm for all blocks
 * 1 -> enables lpm for ROM/RAM2 blocks.
*/
void set_sram_lpm_blocks(int state)
{
    if (state == 0)      /* Disable sram blocks going into lpm */
    {
        sram_lpm_blocks = 0x0;
    }
    else                /* Enable lpm blocks going into lpm */
    {
        sram_lpm_blocks = SRAM_IN_LPM_BLOCKS;
    }
}
