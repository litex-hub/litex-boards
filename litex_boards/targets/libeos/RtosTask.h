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
 *    File   : RtosTask.h
 *    Purpose: Define the Task handles, queues and priorities
 *
 *
 *=========================================================*/

#ifndef __RTOSTASK_H__
#define __RTOSTASK_H__
#include <string.h>
#include "FreeRTOS.h"
#include "task.h"
#include <queue.h>
#include "portable.h"

#define STACK_BAISC_UNIT        4
#define STACK_SIZE_ALLOC(size)  (size * STACK_BAISC_UNIT)

/*====================================================*/

/* Enum so that all of these are visibile in 1 place */
typedef enum {
    PRIORITY_LOWEST = 0,

    PRIORITY_LOWER  = (configMAX_PRIORITIES/4),

    PRIORITY_NORMAL = (configMAX_PRIORITIES/2),

    PRIORITY_HIGH  = ((configMAX_PRIORITIES*3)/4),

    PRIORITY_HAL_TIMER = configMAX_PRIORITIES-2,
    PRIORITY_LOADER = configMAX_PRIORITIES-1,

    PRIORITY_HIGHEST = configMAX_PRIORITIES,
} TaskPriorities;


#define PRIORITY_TASK_BLE              ((unsigned)(PRIORITY_NORMAL))
#define STACK_SIZE_TASK_BLE            (256)
extern xTaskHandle xHandleTaskBLE;
extern QueueHandle_t BLE_MsgQ;
extern signed portBASE_TYPE StartRtosTaskBLE( void);

#define PRIORITY_TASK_AP_COMM              ((unsigned)(PRIORITY_NORMAL))
#define STACK_SIZE_TASK_AP_COMM        (256)
extern xTaskHandle xHandleTaskAPComm;
extern QueueHandle_t xHandleQueueAPComm;
extern signed portBASE_TYPE StartRtosTaskApComm(void);  // to remove warnings		uxPriority not used in the function


#define PRIORITY_TASK_AUDIO               ((unsigned)(PRIORITY_HIGH))
#define STACK_SIZE_TASK_AUDIO        (256)
extern xTaskHandle xHandleTaskAudio;
extern QueueHandle_t xHandleQueueAudio;
extern signed portBASE_TYPE StartRtosTaskAudio( void);  // to remove warnings


#define PRIORITY_TASK_NEURONS              ((unsigned)(PRIORITY_HIGH))
#define STACK_SIZE_TASK_NEURONS        (256)
extern xTaskHandle xHandleTaskNeurons;
extern QueueHandle_t NeuronMsgQ;
extern signed portBASE_TYPE StartRtosTaskNeurons( void);  // to remove warnings

#define PRIORITY_TASK_DATASAVE       ((unsigned)(PRIORITY_LOWER))
#define STACK_SIZE_TASK_DATASAVE     (256)
extern xTaskHandle xHandleTaskDataSave;
extern signed portBASE_TYPE StartRtosTaskDataSave( void);	// to remove warnings


#define PRIORITY_TASK_SENSIML_RECO           ((unsigned)(PRIORITY_NORMAL))
#define STACK_SIZE_TASK_SENSIML_RECO    (256)
extern signed portBASE_TYPE StartRtosTaskRecognition(void);	// to remove warnings

#define PRIORITY_TASK_FFESENSORS              ((unsigned)(PRIORITY_HIGH))
#define STACK_SIZE_TASK_FFESENSORS        (256)
extern xTaskHandle xHandleTaskFFESensors;
extern QueueHandle_t FFESensorsMsgQ;
extern signed portBASE_TYPE StartRtosTaskFFESensors( void);

#define PRIORITY_TASK_ADC                 (((unsigned)(PRIORITY_HIGH))+1)
#define STACK_SIZE_TASK_ADC              (256)
extern xTaskHandle xHandleTaskADC;
extern QueueHandle_t xHandleQueueADC;
extern signed portBASE_TYPE StartRtosTaskADC( void);

#define PRIORITY_TASK_HOST              ((unsigned)(PRIORITY_NORMAL))
#define STACK_SIZE_TASK_HOST            (256)
extern xTaskHandle xHandleTaskHost;
extern QueueHandle_t Host_MsgQ;
extern signed portBASE_TYPE StartRtosTaskHost( void);

#define PRIORITY_TASK_H2D_RX              ((unsigned)(PRIORITY_HIGH))
#define STACK_SIZE_TASK_H2D_RX            (256)
extern xTaskHandle xHandleTaskH2DRx;
extern QueueHandle_t H2DRx_MsgQ;
//extern signed portBASE_TYPE _start_rtos_task_h2drx( void);

#endif /* __RTOSTASK_H__ */
