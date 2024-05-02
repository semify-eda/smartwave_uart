from sharedhelpers import *
import time
import SmartWaveAPI

"""
UART Parity Select Values
"""
PARITY_SELECT_NONE = 0
PARITY_SELECT_ODD  = 1
PARITY_SELECT_EVEN = 2

"""
UART Stop Bits Select
"""
STOP_BITS_NONE = 0
STOP_BITS_1    = 1
STOP_BITS_1_5  = 2
STOP_BITS_2    = 3

"""
UART Shift Direction
"""
SHIFT_LSB_FIRST = 0
SHIFT_MSB_FIRST = 1

def uart_init(sw, baudrate : int = 115200, parity_select : int = 0, stop_bits_select : int = 1, shift_direction : int = 0, txlen : int = 8, timeout_microseconds : int = 10230):
    """
    @brief: 
        Configures Smartwave with 2 UARTs. UART0 is configured with TX on A1 and RX on A2. UART1 is configured with TX on A3 and RX on A4.

    @params:
        baudrate :
            the baudrate to use for UART communication

        parity_select: 
            0 - No parity bits
            1 - Odd parity
            2 - Even parity

        stop_bits_select:
            0 - No stop bits
            1 - 1 bit
            2 - 1.5 bits
            3 - 2 bits
        
        shift_direction:
            0 - send LSB first
            1 - send MSB first

        tx_len:
            length (in bits) of the data transmission

        timeout_microseconds: 
            the UART's timeout in microseconds.
                - must be a factor of 10
                - maximum value is 10,230
    """

    SmartWaveAPI.configitems.GPIO.color = "#8E24AA"
    sw.createGPIO("A1", "TX0")
    sw.createGPIO("A3", "TX1")
    SmartWaveAPI.configitems.GPIO.color = "#1E88E5"
    sw.createGPIO("A2", "RX0")
    sw.createGPIO("A4", "RX1")

    connect_to_stim_0 = FPGA_Reg.registers["wfg_interconnect_top"]["wfg_drive_uart_top_0_select_0"]["wfg_stim_mem_top_0"]
    connect_to_stim_1 = FPGA_Reg.registers["wfg_interconnect_top"]["wfg_drive_uart_top_1_select_0"]["wfg_stim_mem_top_1"]
    connect_to_uart_0 = FPGA_Reg.registers["wfg_interconnect_top"]["wfg_record_mem_top_0_select_0"]["wfg_drive_uart_top_0"]
    connect_to_uart_1 = FPGA_Reg.registers["wfg_interconnect_top"]["wfg_record_mem_top_1_select_0"]["wfg_drive_uart_top_1"]

    configure_interconnect(sw, uart0=connect_to_stim_0, uart1=connect_to_stim_1, recorder0=connect_to_uart_0, recorder1=connect_to_uart_1)

    configure_pin_mux(sw, output_pin_a1=FPGA_Reg.output_pins["wfg_drive_uart_top_0_tx"],
                            output_pin_a3=FPGA_Reg.output_pins["wfg_drive_uart_top_1_tx"],
                            input_pin_a2=FPGA_Reg.input_pins["wfg_drive_uart_top_0_rx"],
                            input_pin_a4=FPGA_Reg.input_pins["wfg_drive_uart_top_1_rx"]
                            )

    configure_record_mem_0(sw)
    configure_record_mem_1(sw)

    div = int(100000000 / baudrate)

    t = int(timeout_microseconds/10)
    if (t > 1023): t = 1023


    configure_drive_uart_0(sw, en=1, div=div, txlen=txlen, paritysel=parity_select, stopsel=stop_bits_select, shiftdir=shift_direction, timeout=t)
    configure_drive_uart_1(sw, en=1, div=div, txlen=txlen, paritysel=parity_select, stopsel=stop_bits_select, shiftdir=shift_direction, timeout=t)
    configure_stim_mem_0(sw, en=0, count=0x01)
    configure_stim_mem_1(sw, en=0, count=0x01)
    

def uart_send(sw, data_bytes : list, uart_select : int):
    """
    @brief: send a sequence of packets via UART

    @params:
        data_bytes:
            A list of values to send via UART

        uart_select:
            0 - send via UART0
            1 - send via UART1
    """
    configure_mem(sw, uart_select, data_bytes)
    configure_core(sw, en=1, sync_count=16, subcycle_count=8)
    if(uart_select == 0):
        reenable_stim_mem_0(sw, 0, len(data_bytes) * 4)
    else:
        reenable_stim_mem_1(sw, 0, len(data_bytes) * 4)


def uart_check_received(sw, uart_select : int) -> bool:
    """
    @brief: check if a UART transaction was recieved that has not yet been viewed by uart_receive

    @params:
        uart_select: the UART device to check

    @returns:
        bool:
            True if the selected UART has recieved a transaction
            False otherwise
    """
    if(uart_select == 0):
        record0_base = read_register(sw, FPGA_Reg.registers["wfg_record_mem_top_0"]["ADDR"]["addr"])
        return record0_base != uart_receive.record0_last
    else:
        record1_base = read_register(sw, FPGA_Reg.registers["wfg_record_mem_top_1"]["ADDR"]["addr"])
        return record1_base != uart_receive.record1_last

def uart_receive(sw, uart_select : int) -> list:
    """
    @brief: poll a UART target and return the data its received as a list

    @params:
        uart_select: the UART device to poll

    @returns: a list of all the bytes received on the selected UART since the last time `uart_receive` was called
    """
    l = []
    if(uart_select == 0):
        record0_cur = read_register(sw, FPGA_Reg.registers["wfg_record_mem_top_0"]["ADDR"]["addr"])
        while(uart_receive.record0_last != record0_cur):
            if(uart_receive.record0_last < record0_cur):
                for i in range(uart_receive.record0_last, record0_cur, 4):
                    l.append(read_register(sw, 0x20000 + (4 << 13) + i))
                uart_receive.record0_last = record0_cur
                record0_cur = read_register(sw, FPGA_Reg.registers["wfg_record_mem_top_0"]["ADDR"]["addr"])
            if(uart_receive.record0_last > record0_cur):
                for i in range(uart_receive.record0_last, 0x2000, 4):
                    l.append(read_register(sw, 0x20000 + (4 << 13) + i))
                for i in range(0, record0_cur, 4):
                    l.append(read_register(sw, 0x20000 + (4 << 13) + i))
                uart_receive.record0_last = record0_cur
                record0_cur = read_register(sw, FPGA_Reg.registers["wfg_record_mem_top_0"]["ADDR"]["addr"])
    else:
        record1_cur = read_register(sw, FPGA_Reg.registers["wfg_record_mem_top_1"]["ADDR"]["addr"])
        while(uart_receive.record1_last != record1_cur):
            if(uart_receive.record1_last < record1_cur):
                for i in range(uart_receive.record1_last, record1_cur, 4):
                    l.append(read_register(sw, 0x20000 + (5 << 13) + i))
                uart_receive.record1_last = record1_cur
                record1_cur = read_register(sw, FPGA_Reg.registers["wfg_record_mem_top_1"]["ADDR"]["addr"])
            if(uart_receive.record1_last > record1_cur):
                for i in range(uart_receive.record1_last, 0x2000, 4):
                    l.append(read_register(sw, 0x20000 + (5 << 13) + i))
                for i in range(0, record1_cur, 4):
                    l.append(read_register(sw, 0x20000 + (5 << 13) + i))
                uart_receive.record1_last = record1_cur
                record1_cur = read_register(sw, FPGA_Reg.registers["wfg_record_mem_top_1"]["ADDR"]["addr"])
    return l
uart_receive.record0_last = 0
uart_receive.record1_last = 0