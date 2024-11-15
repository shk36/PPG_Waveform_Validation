import vitaldb
import numpy as np
from pyvital import arr
import scipy.signal as signal
from scipy.signal import filtfilt


class PPGWaveformValidator:
    def __init__(self, vital_path, nsec, hz=100, trkname='Intellivue/PLETH', beat_prop_threshold=0.7, abnormality_threshold=0.7):
        """
        Initializes the PPGWaveformValidator with essential parameters for PPG analysis.

        Parameters:
        - vital_path (str): Path to the directory containing vital files.
        - nsec (float): Number of seconds for each PPG segment.
        - hz (int): Sampling rate of the PPG signal. Default is 100 Hz (Intellivue/PLETH).
        - trkname (str): Track name for PPG data, default is 'Intellivue/PLETH'.
        - beat_prop_threshold (float): Minimum proportion of increasing gradient segments in a beat to flag as abnormal.
        - abnormality_threshold (float): Minimum proportion of beats that must be abnormal to consider the segment abnormal.
        """
        self.vital_path = vital_path
        self.nsec = nsec
        self.hz = hz
        self.trkname = trkname
        self.beat_prop_threshold = beat_prop_threshold
        self.abnormality_threshold = abnormality_threshold


    def cheby2_filter(self, data):
        """
        Applies a Chebyshev Type II bandpass filter and moving average to smooth the PPG data.

        Parameters:
        - data (np.array): Scaled PPG data.

        Returns:
        - np.array: Filtered PPG data.
        """
        b, a = signal.cheby2(4, 20, [0.5, 12], 'bandpass', fs=self.hz) # 4th order filter, 20dB attenuation, 0.5-12Hz bandpass
        ppg_cb2 = filtfilt(b, a, data)

        win = round(self.hz * 50/1000) # Define the window size based on the sampling rate
        B = 1 / win * np.ones(win)

        return filtfilt(B, 1, ppg_cb2)
    

    def check_gradient(self, gradient):
        """
        Computes the proportion of continuously increasing segments in a beat's gradient.

        Parameters:
        - gradient (np.array): Array containing the gradient values for a beat.

        Returns:
        - float: Proportion of increasing segments in the gradient.
        """
        increasing_lengths = []
        current_length = 0

        # Iterate through the gradient array to measure consecutive increases
        for i in range(1, len(gradient)):
            if gradient[i] > gradient[i - 1]:
                current_length += 1  
            else:
                if current_length > 0:
                    increasing_lengths.append(current_length)  
                    current_length = 0  

        if current_length > 0:
            increasing_lengths.append(current_length)

        return sum(increasing_lengths) / len(gradient)


    def detect_abnormal_seg(self, data):
        """
        Detects abnormal Masimo waveform segments in PPG data based on gradient properties.

        Parameters:
        - data (np.array): Array representing a single PPG segment.

        Returns:
        - bool or None: Returns True if abnormal, False if normal, or None if detection is invalid.
        """
        try:
            minlist, maxlist = arr.detect_peaks(data, self.hz) 
        except:
            return None

        # Ensure maxlist and minlist have valid values
        if len(minlist) == 0 or len(maxlist) == 0:
            return None  

        # Ignore the first peak in maxlist to align with minlist length
        maxlist = maxlist[1:]

        beat_prop = []
        for j in range(len(minlist) - 1):
            beat = data[maxlist[j]:minlist[j+1]]
            if len(beat) == 0:
                continue

            x_values = np.arange(len(beat))

            if len(x_values) == 0:
                continue

            try:
                gradient = np.gradient(beat, x_values)
            except:
                continue

            prop = self.check_gradient(gradient)
            beat_prop.append(prop)

        if len(beat_prop) == 0:
            return None  

        beat_prop = np.array(beat_prop)

        # Calculate the ratio of beats that detected as abnormal
        ratio = np.sum(beat_prop >= self.beat_prop_threshold) / len(beat_prop)

        return ratio >= self.abnormality_threshold

    
    def detect_masimo_vitalfile(self, filename, threshold=0.9):
        """
        Analyzes segments within a vitalfile to determine if they exhibit abnormal Masimo waveforms.

        Parameters:
        - filename (str): Name of the vitalfile.
        - threshold (float): Threshold for the proportion of abnormal segments needed to flag the file as abnormal.

        Returns:
        - bool or str: True if abnormal, False if normal, 'invalid' if no valid segments found.
        """
        vals = vitaldb.VitalFile(self.vital_path + filename, track_names = self.trkname)
        vals = vals.to_pandas(track_names = self.trkname , interval = 1/self.hz, return_datetime = True)

        masimo_count, normal_count = 0, 0

        # Segment the data into chunks of specified duration (nsec)
        for idx in range(0, len(vals)-int(self.nsec*self.hz), int(self.nsec*self.hz)): 
            ppg_seg = vals[idx:idx + int(self.nsec*self.hz)][self.trkname].values 
            ppg_seg = ppg_seg.astype(float) 
            ppg_seg = self.cheby2_filter(arr.interp_undefined(ppg_seg))

            masimo_check = self.detect_abnormal_seg(ppg_seg)
            
            if masimo_check == False:
                normal_count += 1
            elif masimo_check == True:
                masimo_count += 1
            
        total_valid_seg = masimo_count + normal_count

        if total_valid_seg == 0:
            return 'invalid'
        
        masimo_seg_ratio = masimo_count / total_valid_seg

        print('\n=== Masimo Vitalfile Detection Results ===')
        print(f'Total valid segment count: {total_valid_seg}')
        print(f'Normal segment count: {normal_count}')
        print(f'Masimo abnormal segment count: {masimo_count}')
        print(f'Masimo abnormal segment ratio: {masimo_seg_ratio}')

        return masimo_seg_ratio >= threshold
            

