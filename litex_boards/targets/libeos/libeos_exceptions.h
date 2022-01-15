#ifndef LIBEOS_EXCEPTIONS_H
#define LIBEOS_EXCEPTIONS_H

void HardFault_Handler(void);
void Uart_Handler(void);
void CpuWdtInt_Handler(void);
void Pkfb_Handler(void);
void Timer_Handler(void);
void FbMsg_Handler(void);
void vApplicationStackOverflowHook(TaskHandle_t pxTask, char *pcTaskName);

#endif // LIBEOS_EXCEPTIONS_H
