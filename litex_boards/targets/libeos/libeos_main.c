#include "Fw_global_config.h"
#include "qf_hardwaresetup.h"
#include "s3x_clock.h"
#include "FreeRTOS.h"
#include "RtosTask.h"
#if LOAD_FPGA
#include "fpga_loader.h"
#include "quicklogic_quickfeather_bit.h"
#endif

// LiteX BIOS entry point
int main(int i, char **c);

void main_task(void *pParameter);
void SystemInit(void);

void main_task(void *pParameter)
{
	(void)(pParameter);
	main(0, NULL);
}

void SystemInit(void)
{
	xTaskHandle hMain;
	qf_hardwareSetup();

#if LOAD_FPGA
	load_fpga_with_mem_init(sizeof(axFPGABitStream), axFPGABitStream, sizeof(axFPGAMemInit), axFPGAMemInit);
	fpga_iomux_init(sizeof(axFPGAIOMuxInit), axFPGAIOMuxInit);
#endif

	NVIC_SetPriority(Uart_IRQn, configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY);

	xTaskCreate(main_task, "main", 1024, NULL, (UBaseType_t)(PRIORITY_NORMAL), &hMain);
	vTaskStartScheduler();
	while(1);
}
