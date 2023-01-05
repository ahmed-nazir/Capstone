The board used in our Formulate project is the ESP8266 12E (NodeMCU 1.0)

- This process is to be done to reset the board to its original state if firmware becomes corrupt


////FLASH FIRMWARE/////

Required:
- NodeMCU Firmware Flasher (https://github.com/nodemcu/nodemcu-flasher)
- Firmware is from (https://github.com/espressif/ESP8266_NONOS_SDK/releases) the version we used was ESP8266_NONOS_SDK v2.0.0



Steps:
- Ensure nothing is connected to the NodeMCU and connect via micro USB

- Go to the advanced tab and set the parameters as follows
	- Baudrate: 230400
	- Flash size: 4MBytes
	- Flash speed: 40MHz
	- SPI Mode: QIO

- Go to the config tab and flash the following files
	- boot_v1.6.bin			@ 0x00000
	- user1.1024.new.2.bin 		@ 0x01000
	- esp_init_data_default.bin	@ 0x3FC000
	- blank.bin				@ 0x7E000

- Open the Arduino IDE and open the serial monitor with the correct COM port and set the baudrate to 115200 and select Newline and CR
	- Send an "AT" command, if it returns "OK" firmware is flashed successfully

	- Set the baudrate to 9600 permanently with "AT+UART_DEF=9600,8,1,0,0"
	
	- Change baudrate to 9600 on the serial monitor and test the "AT" command again after clicking the reset button on the NodeMCU