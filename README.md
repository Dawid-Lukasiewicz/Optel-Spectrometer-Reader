## Installation
### for Linux
```
python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```
### for Windows
```
python -m venv venv
.\venv\Scripts\activate.bat
pip install -r requirements.txt
```
## Usage
The basic usage of script should be enough to perform good measurement.
The below example presents the default values.
- **-t** The below command sets release time of the spectrometer to 1ms
- **-o** Sets the offset of spectrometer to default value of 256
- **-d** Sets usb port of the spectrometer to desired value [See your PC USB ports]
- **-n** Number of measurements taken is set to default that is 10. If You want to change use -n flag

### for Linux

```
python SpectrometerDraw.py -t 1 -o 256 -d /dev/ttyUSB0
```

### for Windows

```
python SpectrometerDraw.py -t 1 -o 256 -d COM3
```
