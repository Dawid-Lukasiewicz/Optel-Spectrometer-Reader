import time
from datetime import datetime
from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt
import serial
import serial.tools
import signal
import argparse

parser = argparse.ArgumentParser(description='Communication with Optel scpectrometer via USB')

parser.add_argument(
                "--offset",
                "-o",
                required=False,
                default=256,
                action="store",
                type=int,
                help="Offset of spectrometer, max is 510"
)
parser.add_argument(
                "--release_time",
                "-t",
                required=False,
                default=1,
                action="store",
                type=int,
                help="Release time of every measurement, max is 4500 ms"
)
parser.add_argument(
                "--device",
                "-d",
                required=False,
                default="/dev/ttyUSB0",
                action="store",
                type=str,
                help="Name of the USB device"
)
parser.add_argument(
                "--average_number",
                "-n",
                required=False,
                default=10,
                action="store",
                type=int,
                help="Number of measurements to calculate"
)
parser.add_argument(
                "--save_data",
                "-s",
                required=False,
                action="store_true",
                help="Save to files"
)

args = parser.parse_args()

MIN_WAVE = 200
MAX_WAVE = 700
GREEN_WAVE_REF = 532
RED_WAVE_REF = 660
SAMPLES_NUMBER = 2048
N1 = 1048
N2 = 1440
B = 189.796
A = 0.326

BYTES_PER_VALUE = 2

if args.save_data:
    curr_dir = Path().cwd()
    measure_dir = curr_dir.joinpath("measure")
    if not measure_dir.exists():
        measure_dir.mkdir()
    measure_dir = measure_dir.joinpath(str(datetime.now().strftime("%d:%m:%Y-%H:%M:%S")))
    if not measure_dir.exists():
        measure_dir.mkdir()

offset = args.offset
releaseTime = args.release_time
deviceName =  args.device
averageNumber =  args.average_number

# waveLengthRange = np.arange(B, RED_WAVE_REF, A)
waveLengthBefore = np.linspace(MIN_WAVE, GREEN_WAVE_REF-1, N1)
waveLengthRange = np.linspace(GREEN_WAVE_REF, RED_WAVE_REF, N2-N1)
waveLengthAfter  = np.linspace(RED_WAVE_REF+1, MAX_WAVE, SAMPLES_NUMBER-N2)

waveLengthRange = np.insert(waveLengthRange, 0, waveLengthBefore)
waveLengthRange = np.append(waveLengthRange, waveLengthAfter)

sampleCount = 0
samplesList = []
averageList = []
# print(serial.tools.list_ports())

try:
    usbPort = serial.Serial(deviceName, 115200, timeout=5, write_timeout=1)
except serial.SerialException as e:
    print(fr"No device: {deviceName}")
    exit(1)

# to run GUI event loop
plt.ion()
figure, ax = plt.subplots(nrows=2, ncols=1, figsize=(10, 8))

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

def number_to_16bit(value):
    # Podziel wartość na części wysokiego i niskiego bajtu
    high_byte = value // 256
    low_byte = value % 256
    return bytes([high_byte, low_byte])

if not usbPort.isOpen():
    print("Failed to open serial port.")
    exit(1)

# K, #5, Offset_UV_VIS_MSB, Offset_UV_VIS_LSB
usbPort.write(b"K5"+number_to_16bit(offset))
print("K5 "+str(offset))
usbPort.write(b"T"+number_to_16bit(releaseTime))
print("T "+str(releaseTime)+" ms")
i = 0
while True:
    try:
        usbPort.write(b"R")
        # TODO: read_until would be the best to cut off the  end of the stream sign
        # It is no worth  now, I would need to read 2 bytes at once. The frame end is signed with value 65277
        usbReponse = usbPort.read(SAMPLES_NUMBER*BYTES_PER_VALUE)
        usbPort.read(BYTES_PER_VALUE)

        values = decode_binary_stream(usbReponse)
        samplesList.append(values)
        sampleCount += 1

        if sampleCount >= averageNumber:
            sampleCount = 0
            for sampleIdx in range(SAMPLES_NUMBER):
                sampleSum = sum(samplesList[measurementIdx][sampleIdx] for measurementIdx in range(averageNumber))
                sampleAverage = sampleSum / averageNumber
                averageList.append(sampleAverage)
            ax[1].clear()
            ax[1].plot(waveLengthRange, averageList)
            ax[1].set_title("Spectrometer - średnia pomiaru widma", fontsize=20)
            ax[1].set_ylim([0, 16383])
            ax[1].set_xlabel("Długość fali [nm]")
            ax[1].set_ylabel("Natężenie światła [u.j]")
            if args.save_data:
                file = measure_dir.joinpath(fr"file{i}.txt")
                with open(file, "w") as f:
                    for idx in range(len(waveLengthRange)):
                        f.write(str(waveLengthRange[idx]) + "," + str(averageList[idx]) + "\r\n")
                i += 1
            samplesList.clear()
            averageList.clear()

        ax[0].clear()
        ax[0].plot(waveLengthRange, values)
        ax[0].set_title("Spectrometer - pomiar widma", fontsize=20)
        ax[0].set_ylim([0, 16383])
        # ax[0].set_xlabel("Długość fali [nm]")
        ax[0].set_ylabel("Natężenie światła [u.j]")
        figure.canvas.draw()
        figure.canvas.flush_events()
    except serial.SerialException as e:
        print("Serial error:", e)
        usbPort.close()
