## PPG_Waveform_Validation

A Python tool for detecting and excluding incorrectly formed photoplethysmogram (PPG) waveforms, particularly those suspected to originate from Masimo Root devices. This repository provides an algorithm to identify PPG waveforms with abnormal gradient patterns, allowing researchers and practitioners to filter out unreliable data for improved signal quality.

### Table of Contents
[Overview](#overview)
[Features](#features)
[Installation](#installation)
[Usage](#usage)
[Code Explanation](#codeexplanation)


### Overview
The code in this repository addresses the issue of malformed or noisy PPG waveforms, especially those possibly originating from Masimo Root devices. By analyzing the gradient patterns of each waveform, the tool identifies abnormal waveforms that may contain excessive noise or irregularities, which could compromise data integrity in PPG analysis workflows.

### Features
- Automated detection of malformed PPG waveforms
- Customizable thresholds and detection parameters
- Easy integration with existing PPG processing workflows

### Installation
To install the necessary dependencies, clone this repository and install the required packages:

```bash
git clone https://github.com/yourusername/PPG-Waveform-Validation.git
cd PPG-Waveform-Validation
pip install -r requirements.txt
```

### Usage
Here's an example of how to use the detect_abnormal_waveform function:

```python
from ppg_waveform_validation import detect_abnormal_waveform

# Load your PPG data
ppg_data = load_ppg_data("your_data_file.csv")

# Detect abnormal waveforms
is_abnormal = detect_abnormal_waveform(ppg_data, hz=100)

if is_abnormal:
    print("Abnormal waveform detected.")
else:
    print("Waveform appears normal.")
```

### Code Explanation
### Key Components
1. Gradient Check (check_gradient function):
- This function computes the gradient (slope) of each beat within a PPG waveform and evaluates how consistently the gradient increases over time.
- It tracks consecutive increases in gradient values, storing the lengths of these increasing sections, then calculates the total proportion of increasing gradient regions relative to the full waveform.
- A higher proportion may indicate an abnormal waveform.
  
2. Abnormal Waveform Detection (detect_abnormal_waveform function):
- Peaks in the PPG signal are identified using arr.detect_peaks(data, hz), and segments (beats) between peaks are extracted.
- For each beat, the gradient is calculated. Using check_gradient, the code calculates the proportion of gradient segments that meet an increasing threshold.
- The code then calculates the proportion of beats where this increasing pattern exceeds 0.7. If at least 70% of beats meet this criterion, the waveform is flagged as abnormal.
- The result (True for abnormal and False for normal) can be used to filter out suspected Masimo-origin waveforms.

### Parameters
- hz: The sampling rate of the PPG signal (default is 100 Hz). Adjust this according to your data’s sampling rate for optimal peak detection.

  
