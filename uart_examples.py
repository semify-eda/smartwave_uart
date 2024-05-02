from uart_interface import *
from threading import Thread


def example_receive(sw):
    while(1):
        data = uart_receive(sw, 0)
        print(f"UART0 RECEIVED: {data}")
        time.sleep(2.0)

def example_transmit(sw):
    data = []
    for i in range (0, 0xff):
        data.append(i)
    while(1):
        uart_send(sw, data, 1)
        time.sleep(2.0)

def example_tx_rx(sw):
    dataSend = []
    dataSendLong = []
    data0 = []
    data1 = []
    data2 = []
    dataRec = []

    x = 0

    for i in range (0x0, 1030):
        if i < 0x10: dataSend.append(i)
        data0.append(0)
        data1.append(1)
        data2.append(2)
        dataSendLong.append(i)
    while(1):
        if(x % 4 == 0):
            uart_send(sw, data0, 1)
        elif(x % 4 == 1): 
            uart_send(sw, data1, 1)
        elif(x % 4 == 2):
            uart_send(sw, data2, 1)
        else:
            uart_send(sw, dataSendLong, 1)

        time.sleep(0.1)
        if(uart_check_received(sw, 0)):
            dataRec = uart_receive(sw, 0)
            print(f"UART0 RECEIVED: {dataRec}")
            x = x + 1

def main():
    
    with SmartWave().connect() as sw:

        uart_init(sw, baudrate=115200 , txlen=8, stop_bits_select=STOP_BITS_1, parity_select=PARITY_SELECT_ODD, shift_direction=SHIFT_LSB_FIRST, timeout_microseconds=9990)

        ### Example TX/RX
        example_tx_rx(sw)

        ### Example receive:
        example_receive(sw)

        ### Example transmit:
        example_transmit(sw)
        

if __name__ == "__main__":
    main()
