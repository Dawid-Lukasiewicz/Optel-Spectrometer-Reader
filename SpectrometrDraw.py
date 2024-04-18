# importing libraries
import time
import sys
import numpy as np
import matplotlib.pyplot as plt
import serial
import serial.tools
import signal

offset = 256
releaseTime = 4000
waveLengthRange = np.linspace(200, 700, 2048)

# print(serial.tools.list_ports())
usbPort = serial.Serial('/dev/ttyUSB0', 115200, timeout=5, write_timeout=1)

# to run GUI event loop
plt.ion()
figure, ax = plt.subplots(figsize=(10, 8))

def signal_handler(sig, frame):
    print("\nClosing serial port...")
    usbPort.read_all()
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

def encode_number(value):
    # Podziel wartość na części wysokiego i niskiego bajtu
    high_byte = value // 256
    low_byte = value % 256
    return bytes([high_byte, low_byte])

if not usbPort.isOpen():
    print("Failed to open serial port.")
    exit(1)

# K, #5, Offset_UV_VIS_MSB, Offset_UV_VIS_LSB
usbPort.write(b"K5"+encode_number(offset))
print(b"K5"+encode_number(offset))
usbPort.write(b"T"+encode_number(releaseTime))
print(b"T"+encode_number(releaseTime))

while True:
    try:
        usbPort.write(b"R")
        # TODO: read_until would be the best to cut off the  end of the stream sign
        # It is no worth  now, I would need to read 2 bytes at once. The frame end is signed with value 65277
        usbReponse = usbPort.read(2048*2)
        usbPort.read(2)
        values = decode_binary_stream(usbReponse)
        # print(fr"Device response {usbReponse}")
        # print(fr"Decoded {values}")
        # print(fr"Decoded {len(values)}")
        ax.clear()
        ax.plot(waveLengthRange, values)
        ax.set_title("Spectrometer - pomiar widma", fontsize=20)
        ax.set_xlabel("długość fali [nm]")
        ax.set_ylabel("Natężenie światła [u.j]")
        figure.canvas.draw()
        figure.canvas.flush_events()
    except serial.SerialException as e:
        print("Serial error:", e)
        usbPort.close()
