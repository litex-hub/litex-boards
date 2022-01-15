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
#include <stdio.h>
#include <string.h>
#include "FreeRTOS.h"
#include "task.h"
#include "eoss3_dev.h"
#include "sec_debug.h"
#include "dbg_uart.h"


void save_assert_info(char* file, int line)
{
	char assert_info[270];
	dbg_str("****ASSERT****\n");
	dbg_str_str("assert", file);
	dbg_str_int("line", line);
	sprintf(assert_info, "%s(%d)\0", strrchr(file, '\\') ? strrchr(file, '\\') + 1 : file, line);
	strncpy((char*) 0x20000000, assert_info, strlen(assert_info));

	REBOOT_STATUS_REG &= ~REBOOT_CAUSE;
	REBOOT_STATUS_REG |= REBOOT_CAUSE_SOFTFAULT;	/* CHANGING THIS VALUE OR REGISTER REQUIRE CORRESPONDING CHANGE IN BOOTLOADER */
}


void invoke_soft_fault(void)
{
	dbg_fatal_error("SOFT FAULT\n");
	{ taskDISABLE_INTERRUPTS(); for( ;; ); }
}

