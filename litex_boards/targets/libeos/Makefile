include ../include/generated/variables.mak
include $(SOC_DIRECTORY)/software/common.mak

# FPGA binary is typically loaded by the bootloader;
# set LOAD_FPGA=1 to embed FPGA binary in this app and load it on start
# (useful for debugging)
LOAD_FPGA ?= 0

CFLAGS += -I$(LIBEOS_DIRECTORY) \
	-I$(QORC_SDK)/BSP/quickfeather/inc \
	-I$(QORC_SDK)/HAL/inc \
	-I$(QORC_SDK)/Libraries/CMSIS/inc \
	-I$(QORC_SDK)/Libraries/DatablockManager/inc \
	-I$(QORC_SDK)/Libraries/FPGA/inc \
	-I$(QORC_SDK)/Libraries/Power/inc \
	-I$(QORC_SDK)/Libraries/Utils/inc \
	-I$(QORC_SDK)/FreeRTOS/include \
	-I$(QORC_SDK)/FreeRTOS/portable/GCC/ARM_CM4F_quicklogic_s3XX

# rename uart_init() to avoid conflict - LiteX has a function with the same name
CFLAGS += -Duart_init=eos_uart_init

# provide stack end symbol named _fstack in LiteX linker script to vectors_CM4F_gcc using __StackTop name
CFLAGS += -D__StackTop=_fstack

OBJECTS = libeos_exceptions.o libeos_main.o pincfg_table_quickfeather.o s3x_pwrcfg.o sec_debug.o \
	vectors_CM4F_gcc.o \
	eoss3_hal_uart.o eoss3_hal_timer.o eoss3_hal_wdt.o eoss3_hal_spi.o eoss3_hal_pad_config.o qf_hardwaresetup.o \
	dbg_uart.o \
	s3x_clock.o s3x_clock_hal.o s3x_pi.o s3x_qos.o s3x_lpm.o s3x_dfs.o s3x_cpuload.o \
	tasks.o heap_4.o port.o list.o timers.o queue.o

VPATH = $(LIBEOS_DIRECTORY):\
	$(QORC_SDK)/HAL/src:$(QORC_SDK)/HAL/startup:\
	$(QORC_SDK)/BSP/quickfeather/src:\
	$(QORC_SDK)/FreeRTOS:$(QORC_SDK)/FreeRTOS/portable/MemMang:\
	$(QORC_SDK)/FreeRTOS/portable/GCC/ARM_CM4F_quicklogic_s3XX:\
	$(QORC_SDK)/Libraries/FPGA/src:$(QORC_SDK)/Libraries/Utils/src:$(QORC_SDK)/Libraries/Power/src

ifeq ($(LOAD_FPGA), 1)
	CFLAGS += -I$(BUILDINC_DIRECTORY)/../../gateware
	CFLAGS += -DLOAD_FPGA
	OBJECTS += fpga_loader.o
endif

all: libeos.a

libeos.a: $(OBJECTS)
	$(AR) crs $@ $^

# pull in dependency info for *existing* .o files
-include $(OBJECTS:.o=.d)

%.o: %.c
	$(call compile, -fno-lto)

.PHONY: all clean

clean:
	$(RM) $(OBJECTS) libeos.a .*~ *~
