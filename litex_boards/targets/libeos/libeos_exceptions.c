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

/*==========================================================
 *
 *    File   : exceptions.c
 *    Purpose: This file contains the default exception handlers
 *             and exception table.
 *
 *=========================================================*/

#include <stdio.h>
#include <assert.h>
#include "Fw_global_config.h"
#include "FreeRTOS.h"
#include "task.h"
#include "string.h"
#include "eoss3_hal_def.h"
#include "eoss3_hal_pad_config.h"
#include "eoss3_dev.h"
#include "eoss3_hal_rtc.h"
#include "eoss3_hal_uart.h"
#include "eoss3_hal_gpio.h"
#include "sec_debug.h"


void HardFault_Handler(void) {
	while (1);
}

int ucount = 0;
int urxcount = 0;

void Uart_Handler(void) {
	if ((UART->UART_MIS & UART_MIS_RX))
	{
		uart_isr_handler(UART_ID_HW);
		urxcount ++;
		UART->UART_ICR = UART_IC_RX;
	}
	else if (UART->UART_MIS & UART_MIS_RX_TIMEOUT) {
		uart_isr_handler(UART_ID_HW);
		ucount ++;
		UART->UART_ICR = UART_IC_RX_TIMEOUT;
	}
	INTR_CTRL->OTHER_INTR &= UART_INTR_DETECT;
}

extern void HAL_Timer_ISR(void);

void Timer_Handler(void) {
	HAL_Timer_ISR();
	INTR_CTRL->OTHER_INTR &= TIMER_INTR_DETECT;
	NVIC_ClearPendingIRQ(Timer_IRQn);
}

extern void WDT_ISR(void);

void CpuWdtInt_Handler(void) {
	WDT_ISR();
	INTR_CTRL->OTHER_INTR &= WDOG_INTR_DETECT;
	NVIC_ClearPendingIRQ(CpuWdtInt_IRQn);
}

void Pkfb_Handler(void) {
	INTR_CTRL->OTHER_INTR &= PKFB_INTR_DETECT;
}

HAL_FBISRfunction FB_ISR [MAX_FB_INTERRUPTS] = {NULL, NULL, NULL, NULL};

void FbMsg_Handler(void) {
#if (configSAVE_IRQ_HISTORY == 1)
	sec_save_irq_history("FbMsg\0", xTaskGetTickCountFromISR());
#endif
	// detect which one of the FB generators interrupted
	if ( INTR_CTRL->FB_INTR_RAW & FB_0_INTR_RAW) {
		// call that particular ISR
		if (FB_ISR[FB_INTERRUPT_0])
			FB_ISR[FB_INTERRUPT_0]();
		// clear that interrupt at FB level
		INTR_CTRL->FB_INTR = (FB_0_INTR_DETECT);
	}
	if ( INTR_CTRL->FB_INTR_RAW & FB_1_INTR_RAW) {
		// call that particular ISR
		if (FB_ISR[FB_INTERRUPT_1])
			FB_ISR[FB_INTERRUPT_1]();
		// clear that interrupt at FB level
		INTR_CTRL->FB_INTR = (FB_1_INTR_DETECT);
	}
	if ( INTR_CTRL->FB_INTR_RAW & FB_2_INTR_RAW) {
		// call that particular ISR
		if (FB_ISR[FB_INTERRUPT_2])
			FB_ISR[FB_INTERRUPT_2]();
		// clear that interrupt at FB level
		INTR_CTRL->FB_INTR = (FB_2_INTR_DETECT);
	}
	if ( INTR_CTRL->FB_INTR_RAW & FB_3_INTR_RAW) {
		// call that particular ISR
		if (FB_ISR[FB_INTERRUPT_3])
			FB_ISR[FB_INTERRUPT_3]();
		// clear that interrupt at FB level
		INTR_CTRL->FB_INTR = (FB_3_INTR_DETECT);
	}
}


void FB_RegisterISR(UINT32_t fbIrq, HAL_FBISRfunction ISRfn)
{
  if (fbIrq < MAX_FB_INTERRUPTS)
    FB_ISR [fbIrq] = ISRfn;
}

void FB_ConfigureInterrupt(UINT32_t fbIrq, UINT8_t type, UINT8_t polarity, UINT8_t destAP, UINT8_t destM4)
{
  // Edge or level and polarity
  if (type == FB_INTERRUPT_TYPE_LEVEL){
    INTR_CTRL->FB_INTR_TYPE &= ~(1 << fbIrq);
    if (polarity == FB_INTERRUPT_POL_LEVEL_LOW)
      INTR_CTRL->FB_INTR_POL &= ~(1 << fbIrq);
    else
      INTR_CTRL->FB_INTR_POL |= (1 << fbIrq);
  } else {
    INTR_CTRL->FB_INTR_TYPE |=  (1 << fbIrq);
    if ( polarity == FB_INTERRUPT_POL_EDGE_FALL)
      INTR_CTRL->FB_INTR_POL &= ~(1 << fbIrq);
    else
      INTR_CTRL->FB_INTR_POL |= (1 << fbIrq);
  }

  // Destination AP
  if (destAP == FB_INTERRUPT_DEST_AP_DISBLE)
    INTR_CTRL->FB_INTR_EN_AP &= ~(1 << fbIrq);
  else
    INTR_CTRL->FB_INTR_EN_AP |= (1 << fbIrq);

  // Destination M4
  if (destM4 == FB_INTERRUPT_DEST_M4_DISBLE)
    INTR_CTRL->FB_INTR_EN_M4 &= ~(1 << fbIrq);
  else
    INTR_CTRL->FB_INTR_EN_M4 |= (1 << fbIrq);
}

void vApplicationStackOverflowHook(TaskHandle_t pxTask, char *pcTaskName)
{
	( void ) pcTaskName;
	( void ) pxTask;
	taskDISABLE_INTERRUPTS();
	invoke_soft_fault();
}
