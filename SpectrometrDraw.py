# importing libraries
import numpy as np
import time
import matplotlib.pyplot as plt
import serial
import serial.tools

def decode_binary_stream(binary_stream):
    """
    Decode a binary stream to decimal values.
    """
    decoded_values = []

    # Loop through the binary stream in chunks of 2 bytes (16 bits)
    for i in range(0, len(binary_stream), 2):
        # Get the 2-byte chunk
        chunk = binary_stream[i:i+2]

        # Convert the chunk to an integer
        decimal_value = int.from_bytes(chunk, byteorder='big', signed=False)

        # Add the decimal value to the list of decoded values
        decoded_values.append(decimal_value)

    return decoded_values

# print(serial.tools.list_ports())
usbPort = serial.Serial('/dev/ttyUSB0', 115200, timeout=5, write_timeout=1)

if not usbPort.isOpen():
    print("Failed to open serial port.")
    exit(1)

try:
    usbPort.write(b"R")
    usbReponse = usbPort.read(2048*2)
    values = decode_binary_stream(usbReponse)
    # print(fr"Device response {usbReponse}")
    print(fr"Decoded {values}")
    print(fr"Decoded {len(values)}")
    # usbPort.read_until
except serial.SerialException as e:
    print("Serial error:", e)

usbPort.close()

