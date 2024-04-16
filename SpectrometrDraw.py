# importing libraries
import time
import sys
import numpy as np
import matplotlib.pyplot as plt
import serial
import serial.tools
import signal

# print(serial.tools.list_ports())
usbPort = serial.Serial('/dev/ttyUSB0', 115200, timeout=5, write_timeout=1)

# to run GUI event loop
plt.ion()
figure, ax = plt.subplots(figsize=(10, 8))
plt.title("Spectrometer", fontsize=20)
plt.xlabel("Spectre")
plt.ylabel("Values")

def signal_handler(sig, frame):
    print("\nClosing serial port...")
    usbPort.close()
    print("Serial port is closed.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def decode_binary_stream(binary_stream):
    decoded_values = []

    # Loop through the binary stream in chunks of 2 bytes (16 bits)
    for i in range(0, len(binary_stream), 2):
        # Get the 2-byte chunk
        chunk = binary_stream[i:i+2]
        decimal_value = int.from_bytes(chunk, byteorder='big', signed=False)
        decoded_values.append(decimal_value)

    return decoded_values


if not usbPort.isOpen():
    print("Failed to open serial port.")
    exit(1)

while True:
    try:
        usbPort.write(b"R")
        # TODO: read_until would be the best to cut off the  end of the stream sign
        usbReponse = usbPort.read(2048*2)
        usbPort.read(2)
        values = decode_binary_stream(usbReponse)
        # print(fr"Device response {usbReponse}")
        # print(fr"Decoded {values}")
        # print(fr"Decoded {len(values)}")
        ax.clear()
        ax.plot(values)
        figure.canvas.draw()
        figure.canvas.flush_events()
        # time.sleep(1)
    except serial.SerialException as e:
        print("Serial error:", e)
        usbPort.close()
