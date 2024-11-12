import numpy as np
from pyvital import arr


class PPGWaveformValidator:
    def __init__(self, hz=100, beat_prop_threshold = 0.7, abnormality_threshold=0.7):
        """
        Initialize the PPGWaveformValidator with a specified sampling rate.

        Parameters:
        - hz (int): Sampling rate of the PPG signal. Default is 100 Hz (Intellivue/PLETH).
        - beat_prop_threshold (float): Threshold for the proportion of continuously increasing gradients in the beat.
                                       Default is 0.7, meaning that 70% or more data points in the beat need to have 
                                       continuously increasing gradients for the waveform to be flagged as abnormal.
        - abnormality_threshold (float): Proportion threshold to flag a waveform as abnormal.
                                    Default is 0.7, meaning 70% or more beats need to meet 
                                    the criteria for the waveform to be flagged as abnormal.
        """
        self.hz = hz
        self.beat_prop_threshold = beat_prop_threshold
        self.abnormality_threshold = abnormality_threshold


    def check_gradient(self, gradient):
        """
        Calculate the proportion of continuously increasing gradient segments in a beat.

        Parameters:
        gradient (array): Array of gradient values for the beat.

        Returns:
        float: Proportion of increasing gradient segments.
        """
        # Initialize a list to track lengths of consecutive increasing segments
        increasing_lengths = []
        current_length = 0

        # Iterate through the gradient array to measure consecutive increases
        for i in range(1, len(gradient)):
            if gradient[i] > gradient[i - 1]:
                current_length += 1  # Increment length if gradient is increasing
            else:
                if current_length > 0:
                    increasing_lengths.append(current_length)  # Store the length
                    current_length = 0  # Reset the length

        # Store the last increasing segment if any
        if current_length > 0:
            increasing_lengths.append(current_length)

        # Calculate the proportion of increasing segments over the total gradient length
        total_increasing_length = sum(increasing_lengths)
        proportion = total_increasing_length / len(gradient)

        return proportion


    def detect_abnormal_waveform(self, data):
        """
        Detect if a PPG waveform is abnormal based on the gradient properties.

        Parameters:
        data (array): Array of PPG segments (ex. PPG signal data segmented into 1024 points).

        Returns:
        bool: True if the waveform is detected as abnormal, False otherwise.
        """
        minlist, maxlist = arr.detect_peaks(data, self.hz) 

        # Ensure maxlist and minlist have valid values
        if len(minlist) == 0 or len(maxlist) == 0:
            return True  # Consider waveform abnormal if no peaks detected

        # Ignore the first peak in maxlist to align with minlist length
        maxlist = maxlist[1:]

        beat_prop = []
        for j in range(len(minlist) - 1):
            # Extract the beat segment from max peak to the next min peak
            beat = data[maxlist[j]:minlist[j+1]]
            if len(beat) == 0:
                continue

            x_values = np.arange(len(beat))

            # Check if x_values is valid
            if len(x_values) == 0:
                continue

            try:
                gradient = np.gradient(beat, x_values)
            except:
                continue

            prop = self.check_gradient(gradient)
            beat_prop.append(prop)

        if len(beat_prop) == 0:
            return True  # Consider abnormal if no valid beats were processed

        beat_prop = np.array(beat_prop)

        # Calculate the ratio of beats that detected as abnormal
        ratio = np.sum(beat_prop >= self.beat_prop_threshold) / len(beat_prop)

        # Flag as abnormal if 70% or more of beats meet the abnormal threshold
        return ratio >= self.abnormality_threshold

