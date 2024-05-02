# smartwave_uart

Smartwave's UART modules can be interfaced with through the `uart_interface.py` and SmartwaveAPI

The interface provides four primary functions as follows:

- `uart_init` : Configures Smartwave with 2 UARTs

    - Parameters:
    
        - baudrate :
            the baudrate to use for UART communication


        - parity_select: 
            0 - No parity bits
            1 - Odd parity
            2 - Even parity

        - stop_bits_select:
            0 - No stop bits
            1 - 1 bit
            2 - 1.5 bits
            3 - 2 bits
        
        - shift_direction:
            0 - send LSB first
            1 - send MSB first

        - tx_len:
            length (in bits) of the data transmission

        - timeout_microseconds: 
            the UART's timeout in microseconds.
                - must be a factor of 10
                - maximum value is 10,230

    - Pins:


        |signal   |pin |
        |---------|----|
        |uart0 TX | A1 |
        |uart0 RX | A2 |
        |uart1 TX | A3 |
        |uart2 RX | A4 |

- `uart_send` : Send a sequence of packets via the selected UART

    - Parameters:
    
        - data_bytes:
            A list of values to send via UART

        - uart_select:
            0 - send via UART0
            1 - send via UART1

- `uart_check_received` : Check if a there is a received UART transaction on the specified UART that has not yet been read by uart_receive.

    - Paramters:
        - uart_select: the UART device to check

    - Returns:
        - True if the selected UART has an unread transaction
        - False otherwise

- `uart_receive` : Read the received data from the specifieed UART and return it as a list

    - Parameters:
    
        - uart_select: the UART device to read from

    - Returns:

        - a list of all the bytes received on the selected UART since the last time `uart_receive` was called




Using these four functions, it is possible to drive the UART modules as needed by importing and using the `uart_interface.py` into your script.