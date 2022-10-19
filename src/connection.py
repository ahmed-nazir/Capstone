from lib2to3.pgen2.pgen import DFAState
import serial
import time
import pandas as pd
import datetime

# make sure the 'COM#' is set according the Windows Device Manager
ser = serial.Serial('COM4', 9800, timeout=1)
time.sleep(2)

data = []
t = []
df = pd.DataFrame(data,columns=['Temperature'])

for i in range(50):
    now = datetime.datetime.now()
    line = ser.readline()   # read a byte
    if line:
        string = line.decode()  # convert the byte string to a unicode string
        #num = int(string) # convert the unicode string to an int
        print(string)
        data.append([now.strftime("%Y-%m-%d %H:%M:%S"),string])

ser.close()
df = pd.DataFrame(data,columns=['Time','Temperature'])
print(df)