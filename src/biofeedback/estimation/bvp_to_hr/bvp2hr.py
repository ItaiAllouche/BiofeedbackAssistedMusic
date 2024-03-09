import numpy as np
from scipy.fft import fft, fftfreq
from biofeedback.estimation.base_functions import bandpass_filter

SAMPLING_RATE = 64 #Hz
LOW_FREQ = 0.5 #Hz
HIGH_FREQ = 5 #Hz

def get_hr_from_bvp(bvp: np.ndarray) -> float:
    filtered_bvp_signal = bandpass_filter(bvp, LOW_FREQ, HIGH_FREQ, sampling_rate=SAMPLING_RATE)
    n = len(filtered_bvp_signal)
    frequencies = fftfreq(n, 1/SAMPLING_RATE)
    fft_values = fft(filtered_bvp_signal)
    common_freq = frequencies[:n//2][np.abs(fft_values[:n//2]).argmax()]
    ibi = 1 / common_freq
    hr = 60 / ibi
    return hr