# PPG_Waveform_Validation

A Python tool for detecting and excluding incorrectly formed photoplethysmogram (PPG) waveforms, particularly those suspected to originate from Masimo Root devices. This repository provides an algorithm to identify PPG waveforms with abnormal gradient patterns, allowing researchers and practitioners to filter out unreliable data for improved signal quality.

### Table of Contents
- [Overview](#overview)<br>
- [Features](#features)<br>
- [Installation](#installation)<br>
- [Usage](#usage)<br>
- [Parameters](#parameters)<br>
- [Code Explanation](#code-explanation)<br>
- [Detected Abnormal PPG Waveform](#detected-abnormal-ppg-waveform)<br>


### Overview
The code in this repository addresses the issue of malformed or noisy PPG waveforms, especially those possibly originating from Masimo Root devices. By analyzing the gradient patterns of each waveform, the tool identifies abnormal waveforms that may contain excessive noise or irregularities, which could compromise data integrity in PPG analysis workflows.


### Features
- **Bandpass Filtering**: Applies a Chebyshev Type II filter and moving average to smooth and clean PPG signals.
- **Gradient Analysis**: Calculates the proportion of continuously increasing gradient segments within each beat.
- **Abnormality Detection**: Flags PPG segments as abnormal if a specified threshold for abnormal gradient properties is met.
- **File-Based Analysis**: Processes PPG data from vital files using customizable thresholds for beat and waveform abnormality.

### Installation
To install the necessary dependencies, clone this repository and install the required packages:

```bash
git clone https://github.com/shk36/PPG-Waveform-Validation.git
cd PPG-Waveform-Validation
pip install numpy scipy vitaldb
```

### Usage
**1. Initialize the Validator**<br>
Create an instance of *PPGWaveformValidator* by specifying the vital file path, segment length, sampling rate, and thresholds.

```python
from ppg_waveform_validator import PPGWaveformValidator

validator = PPGWaveformValidator(
    vital_path='/path/to/vital/files',
    nsec=10.24,  # Segment length in seconds
    hz=100,  # Sampling rate in Hz
    trkname='Intellivue/PLETH'  # Track name for PPG data
)
```

**2. Validate a VitalFile**<br>
Use the *detect_masimo_vitalfile* function to validate all segments within a vitalfile based on a threshold for abnormal segments.

```python
filename = 'sample.vital'
result = validator.detect_masimo_vitalfile(filename)

if result == 'invalid':
    print(f"Vitalfile {filename} is invalid waveform data.")
elif result:
    print(f"Vitalfile {filename} is abnormal.")
else:
    print(f"Vitalfile {filename} is normal.")
```

### Parameters
- **vital_path (str)**: Path to the directory containing vital files.
- **nsec (float)**: Length of each segment in seconds.
- **hz (int)**: Sampling rate of the PPG signal (default 100 Hz).
- **trkname (str)**: Track name in the vital file (default is 'Intellivue/PLETH').
- **beat_prop_threshold (float)**: Minimum proportion of gradient-increasing segments in a beat to consider it abnormal.
- **abnormality_threshold (float)**: Minimum proportion of beats in a segment that must be abnormal to flag it as an abnormal waveform.


### Code Explanation
**1. Gradient Check (*check_gradient* function):**
- This function computes the gradient (slope) of each beat within a PPG waveform and evaluates how consistently the gradient increases over time.
- It tracks consecutive increases in gradient values, storing the lengths of these increasing sections, then calculates the total proportion of increasing gradient regions relative to the full waveform.
- A higher proportion may indicate an abnormal waveform.
  
**2. Abnormal Waveform Detection (*detect_abnormal_seg* function):**
- Peaks in the PPG signal are identified using *arr.detect_peaks(data, hz)*, and segments (beats) between peaks are extracted.
- For each beat, the gradient is calculated. Using *check_gradient*, the code calculates the proportion of gradient segments that meet an increasing threshold.
- The code then calculates the proportion of beats where this increasing pattern exceeds 0.7. If at least 70% of beats meet this criterion, the waveform is flagged as abnormal.
- The result (True for abnormal and False for normal) can be used to filter out suspected Masimo-origin waveforms.

  
### Detected Abnormal PPG Waveform
This image shows an example of an abnormal PPG waveform detected by the algorithm.

![abnormal_ppg_waveform](https://github.com/user-attachments/assets/a86efec2-f81a-42ea-9f94-51c4c1d05816)

