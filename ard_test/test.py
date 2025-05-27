import serial
import time


def readserial(comport, baudrate, timestamp=False):

    file = open("test.csv","w+")
    file.close()

    file = open("test.csv","a+")

    ser = serial.Serial(comport, baudrate, timeout=0.1)         # 1/timeout is the frequency at which the port is read
    print("remove weight")

    time.sleep(5)
    ser.write(b"t")
    print("place weight")

    time.sleep(10)

    ser.write(b"108.0")


    time.sleep(5)

    ser.write(b"n")
    
    print("done weighting")
    print("done calibrating")

    i = 0

    while True:

        data = ser.readline().decode().strip()

        if data and timestamp:
            timestamp = time.strftime('%H:%M:%S')
            print(f'{timestamp} > {data}')
        elif data:
            print(data)
        if len(data.split(":")) > 1:
            i += 1
            out_str = f"{i}, {data.split(':')[1].strip()}\n"
            file.write(out_str)

if __name__ == '__main__':

    readserial('COM3', 57600, True)                          # COM port, Baudrate, Show timestamp
