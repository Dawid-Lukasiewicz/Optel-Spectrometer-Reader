## Installation
```
python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```
## Usage
The basic usage of script should be enough to perform good measurement.
- The below command sets release time of the spectrometer to 1ms
- Sets the offset of spectrometer to max value
- Sets usb port of the spectrometer to desired value [See your PC USB ports]
- Number of measurements taken is set to default that is 10. If You want to change use -n flag

```
python SpectrometrDraw.py -t 1 -o 510 -d COM<n>
```

