import numpy as np
from scipy.fft import fft, fftfreq, correlate, find_peaks
from biofeedback.estimation.base_functions import bandpass_filter
from functools import partial

SAMPLING_RATE = 64 #Hz
LOW_FREQ = 0.5 #Hz
HIGH_FREQ = 5 #Hz

hr_history: list[float] = []
def get_hr_from_bvp(bvp: np.ndarray, reset=False) -> float:
    if reset:
        hr_history = []
    filtered_bvp_signal = bandpass_filter(bvp, LOW_FREQ, HIGH_FREQ, sampling_rate=SAMPLING_RATE)
    r = correlate(filtered_bvp_signal, filtered_bvp_signal)
    r = r[len(r)//2:]
    peaks,_ = find_peaks(r, prominence=r[0]/4)
    def b(peaks):
        return 60/((peaks[1]-peaks[0])/64)
    MIN_HR, MAX_HR, FALLBACK_HR = 55, 160, 60
    # Edge cases
    if len(peaks) < 2 or b(peaks) < MIN_HR or b(peaks) > MAX_HR:
        if len(hr_history) == 0:
            return FALLBACK_HR
        else:
            # Returns latest HR
            return hr_history[-1]
    hr = b(peaks)
    # Updating history by removing last HR and adding newest HR
    if len(hr_history) > 2:
        hr_history.pop(0)
    hr_history.append(hr)
    w = np.array([i+1 for i in range(len(hr_history))])
    # Update newest HR by weighted average of history
    hr_history[-1] = sum([hr_history[i]*w[i] for i in range(len(hr_history))])/sum(w)
    
    return hr_history[-1]
    # plt.plot(r)
    # plt.scatter(peaks, r[peaks], color='r')
    # plt.show()
    