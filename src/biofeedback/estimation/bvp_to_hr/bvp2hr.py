import numpy as np
from scipy.fft import fft, fftfreq
from biofeedback.estimation.base_functions import bandpass_filter

SAMPLING_RATE = 64 #Hz
LOW_FREQ = 0.5 #Hz
HIGH_FREQ = 5 #Hz

def get_hr_from_bvp(bvp: np.ndarray) -> float:
    import matplotlib.pyplot as plt
    # plt.plot(bvp)
    filtered_bvp_signal = bandpass_filter(bvp, LOW_FREQ, HIGH_FREQ, sampling_rate=SAMPLING_RATE)
    # n = len(filtered_bvp_signal)
    # frequencies = fftfreq(n, 1/SAMPLING_RATE)
    # fft_values = abs(fft(filtered_bvp_signal))
    # frequencies = frequencies[:len(frequencies)//2]
    # fft_values = fft_values[:len(fft_values)//2]
    # fft_values /= sum(fft_values)
    # hr_in_hz = fft_values@frequencies
    # hr_bpm = 60*hr_in_hz
    # return hr_bpm
    from scipy.signal import correlate, find_peaks
    r = correlate(filtered_bvp_signal, filtered_bvp_signal)
    r = r[len(r)//2:]
    peaks,_ = find_peaks(r, prominence=r[0]/4)
    # !!!Show graphs!!!
    # plt.plot(r)
    # plt.scatter(peaks, r[peaks], color='r')
    # plt.show()
    if len(peaks) < 2:
        return 1
    return 60/((peaks[1]-peaks[0])/64)
