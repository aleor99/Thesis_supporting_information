/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "stdbool.h"
#include "stm32f4xx_it.h"
#include "string.h"
#include "stdio.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define BUFFSIZE          10000
#define TIMEOUT             50
#define ON                  1
#define OFF                 0
#define START1            0xC0
#define START2            0x40
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
UART_HandleTypeDef huart1;
UART_HandleTypeDef huart2;

/* USER CODE BEGIN PV */
int j=0;
uint8_t buffer[BUFFSIZE];
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART2_UART_Init(void);
static void MX_USART1_UART_Init(void);
/* USER CODE BEGIN PFP */
uint8_t sample(void);
uint32_t millis(void);
void display_data(int points);
int acquire_data(void);
int findNextStartCondition(int k);
int gbuffer(int i);
void printHexByte(uint8_t b);
uint8_t UART1_rxBuffer[19];
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */
  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USART2_UART_Init();
  MX_USART1_UART_Init();
  /* USER CODE BEGIN 2 */
  HAL_UART_Receive_IT(&huart2, UART1_rxBuffer, sizeof(UART1_rxBuffer));
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
	  int points = acquire_data();
	  display_data(points);

    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 16;
  RCC_OscInitStruct.PLL.PLLN = 336;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV4;
  RCC_OscInitStruct.PLL.PLLQ = 4;
  RCC_OscInitStruct.PLL.PLLR = 2;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief USART1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART1_UART_Init(void)
{

  /* USER CODE BEGIN USART1_Init 0 */

  /* USER CODE END USART1_Init 0 */

  /* USER CODE BEGIN USART1_Init 1 */

  /* USER CODE END USART1_Init 1 */
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 9600;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART1_Init 2 */

  /* USER CODE END USART1_Init 2 */

}

/**
  * @brief USART2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART2_UART_Init(void)
{

  /* USER CODE BEGIN USART2_Init 0 */

  /* USER CODE END USART2_Init 0 */

  /* USER CODE BEGIN USART2_Init 1 */

  /* USER CODE END USART2_Init 1 */
  huart2.Instance = USART2;
  huart2.Init.BaudRate = 250000;
  huart2.Init.WordLength = UART_WORDLENGTH_8B;
  huart2.Init.StopBits = UART_STOPBITS_1;
  huart2.Init.Parity = UART_PARITY_NONE;
  huart2.Init.Mode = UART_MODE_TX_RX;
  huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart2.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart2) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART2_Init 2 */

  /* USER CODE END USART2_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
/* USER CODE BEGIN MX_GPIO_Init_1 */
/* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOH_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(LD2_GPIO_Port, LD2_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin : B1_Pin */
  GPIO_InitStruct.Pin = B1_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(B1_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : LD2_Pin */
  GPIO_InitStruct.Pin = LD2_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(LD2_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : SCL_PIN_Pin */
  GPIO_InitStruct.Pin = SCL_PIN_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(SCL_PIN_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : SDA_PIN_Pin */
  GPIO_InitStruct.Pin = SDA_PIN_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(SDA_PIN_GPIO_Port, &GPIO_InitStruct);

/* USER CODE BEGIN MX_GPIO_Init_2 */
/* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */

////////////////////////
void printHexByte(uint8_t b) //-------------------> funziona
////////////////////////
{
  char hexChars[] = "0123456789ABCDEF";

  // Calcola i valori hex dei nibble
  char highNibble = hexChars[(b >> 4) & 0x0F];
  char lowNibble = hexChars[b & 0x0F];
  // Invia i caratteri sulla seriale
  HAL_UART_Transmit(&huart2, (uint8_t *)&highNibble, 1, HAL_MAX_DELAY);
  HAL_UART_Transmit(&huart2, (uint8_t *)&lowNibble, 1, HAL_MAX_DELAY);
}



////////////////////////
void printabytes(int* bytes)//-----------------------> non l'ho provata ma penso che funzioni
///////////////////////
{
  for(int i=0; i<3; i++)
  {
    printHexByte(bytes[i] / 2);
  }
}

//////////////////
int gbuffer(int i)//---------------------------> sembra funzionare, attento al tipo ecc
//////////////////
{
    return (buffer[i] >> 6) & 0x3;
}

/////////////////////////////////
int findNextStartCondition(int k)//-------------------------> non dovrebbe avere niente di strano
/////////////////////////////////
{
  while((k < BUFFSIZE- 1) && ((gbuffer(k - 1) != 3) || (gbuffer(k) != 1)))
    k++;
    // Serial.print("Next start condition: "); Serial.println(k);
  return k;
}


//////////////////
int acquire_data()//------------------------------------> CONTROLLARE SE FUNZIONA, LE FUNZIONI dovrei averle messe
//////////////////
// Pins are hard coded for speed reason
{
  unsigned long endtime;
  unsigned int data,lastData;

  // wait until start condition is fullfilled
  bool start = false;
  while (!start)
  {
    while ((lastData = sample()) != START1);          // wait until state is START1
    while ((data = sample()) == lastData);            // wait until state change, cambia il valore dopo lo start, aspetto che non sia piu il messaggio di start
    start = (data == START2);                       // start condtion met if new state is START2
    //quando il messaggio finisce
  }

//C'e un controllo sul valore dei pinD selezionati per sda e scl, una volta che lo stop (scl e sda alti) allora il messaggio dovrebbe essere finito in teoria
  endtime = millis() + TIMEOUT; //istante in cui viene chiamata piu timeout
  lastData = START2;
  int k = 0;
  buffer[k++] = START1;
  buffer[k++] = START2;
  do {
    while ((data = sample()) == lastData);           // wait until data has changed
    // a me interessano solo quei due bit, quindi me li saldo in un buffer. Questo buffer avra valori ad 8 bit che poi modifiati ci daranno il dato in decimale o esa
    buffer[k++] = lastData = data;    //in teroia sono solo i due bit pero
  }
  //quindi alla fine della funzione avro un be=uffer di 1000 con tutti i valori, presumibilmente i valori saranno tipo 1000/10 penso
  while ((k < BUFFSIZE) && (millis() < endtime));
  return k;
}

//////////////////
uint32_t millis()
/////////////////
{
  return counter;
}

/////////////////////////



////////////////////////
uint8_t sample(void)//------------------> si potrebbe anche provare separatamente ma penso che in linea di massima vada bene
///////////////////////
{
	return ((HAL_GPIO_ReadPin(GPIOA, SDA_PIN_Pin)<<7)|(HAL_GPIO_ReadPin(GPIOB, SCL_PIN_Pin)<<6));
}


/////////////////////////////
void display_data(int points) // quindi in ingresso ho il buffer con i valori del sample
/////////////////////////////
{
  int  data, k, Bit, Byte, i, state,nextStart;
  int bytes[10];
  char flag_OK=OFF;
  int count=0, count_it=0;
  char string[64];
  uint32_t starttime;

  #define ADDRESS  0         // First state, address follows
  #define FIRST    1
  #define AST      2
  #define DATA     3
  #define AD7746            48
  #define FIRST_VAL         0x0E
  starttime = millis();

  k = 3;              // ignore start transition, nei primi tre ha niente, start1 e start2
  i = 0;
  Byte = 0;
  state = ADDRESS;
  nextStart = findNextStartCondition(k); //cerca se sono arrivato allo stop e restituisce dove sono arrivato
  do { //finche non ha printato tutti i punti
    data = gbuffer(k++);//ha sample alla fine
    if (data & 1)
    { //penso se scl e 1, il valore e aggiornato col fronte alto di clock
      Bit = (data & 2) > 0; //il bit sara 1 o 0 a seconda che sda sia 1 o 0
      Byte = (Byte << 1) + Bit;  //aggiunge il bit al byte che verra poi messo nel buffer
      if(i++>=8)
      {
    	  switch(state)
    	  {
    	  	  case ADDRESS:
    	  		  state++;
    	  		  break;
    	  	  case FIRST:
    	  		  if(Byte/2==0x02)
    	  		  {
    	  			flag_OK=ON;
    	  			HAL_UART_Transmit(&huart2, "\n", strlen("\n"), 50);
    	  		  }
    	  		  else
    	  			flag_OK=OFF;
    	  		  state++;
    	  		  break;
    	  	  default:
				if (flag_OK && count<3)
				{

				  bytes[count]=Byte;
				  count++;
				}
				if (count==3)
				{
				  //j++;
				  printabytes(bytes); //vengono printati solo i valori con tre byte così
				  //HAL_UART_Transmit(&huart2,"-->", strlen("-->"), 50);
				  //snprintf(string,sizeof(string) ,"%d", j);
				  //HAL_UART_Transmit(&huart2,string, strlen(string), 50);
				  count++;
				}
				break;
    	  }
		  if (nextStart - k < 9)
		  {
			k = nextStart + 1;
			nextStart = findNextStartCondition(k);
			state = ADDRESS;
			flag_OK=OFF;
			count=0;
		   }
          i = 0;
          Byte = 0;
       }
    }
  }
  while (k < points);
}


void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);
    HAL_UART_Transmit(&huart1, UART1_rxBuffer, sizeof(UART1_rxBuffer), 1000);
    //HAL_UART_Transmit(&huart2, UART1_rxBuffer, sizeof(UART1_rxBuffer), 1000);
    HAL_UART_Receive_IT(&huart2, UART1_rxBuffer, sizeof(UART1_rxBuffer));
}
/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
