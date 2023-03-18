import json

class CodeGenerator():
    def generate(data):
        alphabet = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

        dict = {}
        with open('src\Desktop Application\Version2\currentConfig.json','w') as f:
            count = 0
            for i in range(0,len(data)):
                for j in range(0,len(data[i][1])):
                    letter = alphabet[count]
                    count += 1
                    dict[letter] = data[i][1][j]
            json.dump(dict,f)
        f.close()
                    


        with open(r'C:\Users\Ahmed Nazir\Desktop\testArduino\testArduino.ino', 'w') as f:
            f.write("#include <SoftwareSerial.h>\n")
            f.write("#include <SPI.h>\n")
            f.write("#include <SD.h>\n")


            for i in range(0,len(data)):
                f.write('#include "' + data[i][0] + '.h"\n')
            f.write('\n')

            
            f.write('File myFile;\n')
            f.write('SoftwareSerial espSerial(2,3);\n')
            f.write('\n')

            f.write('const int chipSelect = 10;\n')
            f.write('\n')

            f.write('int wiredSend = 0;\n')
            f.write('int wifiSend = 0;\n')
            f.write('int wiredRead;\n')
            f.write('int wifiRead;\n')
            f.write('\n')

            counterData = 0
            counterPinArr = []
            for i in range(0,len(data)):
                for j in range(0,len(data[i][1])):
                    counterData += 1
                counterPinArr.append(len(data[i][2]))
            


            for i in range(0,len(data)):
                for j in range(0,len(data[i][1])):
                    f.write('float ' + data[i][1][j] + ';\n')
            f.write('\n')

            # === READ DATA ===
            count = 0
            pins = ''
            f.write('void readData(){\n')
            for i in range(0,len(data)):
                f.write('  ' + data[i][0] + '_SensorValues ' + data[i][0] + '_Values = read' + data[i][0] + '(')
                for j in range(0,len(data[i][2])):
                    f.write(data[i][2][j])
                    if j != counterPinArr[i]-1:
                        f.write(',')
                f.write(');\n')
            
            for i in range(0,len(data)):
                for j in range(0,len(data[i][1])):
                    f.write('  ' + data[i][1][j] + ' = ' + data[i][0] + '_Values.' + alphabet[j])
                    f.write(';\n')
            f.write('}')
            f.write('\n')

            # === SETUP ===
            f.write('void setup() {\n')
            f.write('  Serial.begin(9600);\n')
            f.write('  espSerial.begin(9600);\n')
            f.write('  SD.begin();\n')
            f.write('\n')

            for i in range(0,len(data)):
                f.write('  setup' + data[i][0] + '(')
                for j in range(0,len(data[i][2])):
                    f.write(data[i][2][j])
                    if j != counterPinArr[i]-1:
                        f.write(',')
                f.write(');\n')
            f.write('}\n')
            f.write('\n')

            # === LOOP ===
            f.write('void loop() {\n')
            f.write('  // === Start and Stop Wireless Serial Comm === //\n')
            f.write('  wifiRead = espSerial.read();\n')
            f.write('  if(wifiRead == 81){\n')
            f.write('    wifiSend = 1;\n')
            f.write('    SD.remove("TestData.txt");\n')
            f.write('    myFile = SD.open("TestData.txt", FILE_WRITE);\n')
            f.write('    if (myFile) {\n')
            f.write('      myFile.close();\n')
            f.write('     }\n')
            f.write('  }\n')
            f.write('  if(wifiRead == 87){\n')
            f.write('    wifiSend = 0;\n')
            f.write('  }\n')


            f.write('\n')

            f.write('  if(wifiSend){\n')
            f.write('    readData();\n')
            f.write('\n')
            f.write('    // === Send Bytestring to Serial Port === //\n')
            f.write("    espSerial.print('(');\n")
            count = 0
            for i in range(0,len(data)):
                for j in range(0,len(data[i][1])):
                    f.write("    espSerial.print('" + alphabet[count] + "');\n")
                    count += 1
                    f.write('    espSerial.print(' + data[i][1][j][-1] + ');\n')
                    f.write('    espSerial.print(' + data[i][1][j] + ');\n')
                    if count != counterData:
                        f.write("    espSerial.print('" + ',' + "');\n")
            f.write("    espSerial.println(')');\n")

            f.write('\n')

            # === WRITE TO SD CARD ===
            f.write('    // === Write Data to SD Card === //\n')
            f.write('    myFile = SD.open("TestData.txt", FILE_WRITE);\n')
            f.write('    if (myFile) {\n')
            f.write("      myFile.print('(');\n")
            count = 0
            for i in range(0,len(data)):
                for j in range(0,len(data[i][1])):
                    f.write("      myFile.print('" + alphabet[count] + "');\n")
                    count += 1
                    f.write('      myFile.print(' + data[i][1][j][-1] + ');\n')
                    f.write('      myFile.print(' + data[i][1][j] + ');\n')
                    if count != counterData:
                        f.write("      myFile.print('" + ',' + "');\n")
            f.write("      myFile.println(')');\n")
            f.write('      myFile.close();\n')
            f.write('    }\n')
            f.write('    delay(1100);\n')
            f.write('  }\n')

            f.write('\n')
            f.write('\n')

            f.write('  // === Start and Stop Wired Serial Comm === //\n')
            f.write('  wiredRead = Serial.read();\n')
            f.write("  if(wiredRead == 'G'){\n")
            f.write('    wiredSend = 1;\n')
            f.write('    SD.remove("TestData.txt");\n')
            f.write('    myFile = SD.open("TestData.txt", FILE_WRITE);\n')
            f.write('    if (myFile) {\n')
            f.write('      myFile.close();\n')
            f.write('     }\n')
            f.write('  }\n')
            f.write("  if(wiredRead == 'P'){\n")
            f.write('    wiredSend = 0;\n')
            f.write('  }\n')
            f.write("  if(wiredRead =='R'){\n")
            f.write('    myFile = SD.open("TestData.txt");\n')
            f.write('    if (myFile){\n')
            f.write('      while (myFile.available()){\n')
            f.write('        Serial.write(myFile.read());\n')
            f.write('      }\n')
            f.write('    myFile.close();\n')
            f.write('    }\n')
            f.write('  }\n')
            f.write('\n')


            f.write('  if(wiredSend){\n')
            f.write('    readData();\n')
            f.write('\n')
            f.write('    // === Send Bytestring to Serial Port === //\n')
            f.write("    Serial.print('(');\n")
            count = 0
            for i in range(0,len(data)):
                for j in range(0,len(data[i][1])):
                    f.write("    Serial.print('" + alphabet[count] + "');\n")
                    count += 1
                    f.write('    Serial.print(' + data[i][1][j][-1] + ');\n')
                    f.write('    Serial.print(' + data[i][1][j] + ');\n')
                    if count != counterData:
                        f.write("    Serial.print('" + ',' + "');\n")
            f.write("    Serial.println(')');\n")

            f.write('\n')

            # === WRITE TO SD CARD ===
            f.write('    // === Write Data to SD Card === //\n')
            f.write('    myFile = SD.open("TestData.txt", FILE_WRITE);\n')
            f.write('    if (myFile) {\n')
            f.write("      myFile.print('(');\n")
            count = 0
            for i in range(0,len(data)):
                for j in range(0,len(data[i][1])):
                    f.write("      myFile.print('" + alphabet[count] + "');\n")
                    count += 1
                    f.write('      myFile.print(' + data[i][1][j][-1] + ');\n')
                    f.write('      myFile.print(' + data[i][1][j] + ');\n')
                    if count != counterData:
                        f.write("      myFile.print('" + ',' + "');\n")
            f.write("      myFile.println(')');\n")
            f.write('      myFile.close();\n')
            f.write('    }\n')
            f.write('    delay(1100);\n')
            f.write('  }\n')
            f.write('}\n')

        f.close()
