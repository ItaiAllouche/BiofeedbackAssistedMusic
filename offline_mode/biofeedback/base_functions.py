# %%
from scipy.signal import find_peaks, butter, filtfilt
from scipy import interpolate
import numpy as np
import numpy.typing as npt
from ssqueezepy import ssq_cwt
import matplotlib.pyplot as plt
# Frequency sampling
FS = 32
# Valid duration
T = 6
# Segment threshold
A = 0.3
# Max and Min frequency (in Hz)
F_min = 1.4
F_max = 2.3
# Parameters for "max equation"
alpha = 31.7
beta = 1.4

# %%
def viz(Tx, Wx):
    plt.imshow(np.abs(Wx), aspect='auto', cmap='turbo')
    plt.colorbar()
    plt.title('Wx')
    plt.show()
    plt.imshow(np.abs(Tx), aspect='auto', vmin=0, vmax=.2, cmap='turbo')
    plt.colorbar()
    plt.title('Tx')
    plt.show()
# %%
def peak2peak(magnitude_vec: np.ndarray) -> float:
    peaks_idx, _ = find_peaks(magnitude_vec)
    if(peaks_idx.size > 1):
        peaks_value = magnitude_vec[peaks_idx]
        sorted_idx = np.argsort(peaks_value)
        return peaks_value[sorted_idx[-1]] - peaks_value[sorted_idx[-2]]
    return 0
# %%
#TODO: add window to smooth the signal on the edges
def compute_cwt(signal: np.ndarray, wavelet: tuple, fs: int) -> tuple:

    """Compute CWT over acceleration data.

    Args:
        tapered_bout: array of floats
            vector magnitude with one bout of activity (in g)
        fs: integer
            sampling frequency (in Hz)
        wavelet: tuple
            mother wavelet used to compute CWT

    Returns:
        Tuple of ndarrays with interpolated frequency and wavelet coefficients
    """
    signal = np.concatenate((np.zeros(5*fs),
                             signal,
                             np.zeros(5*fs)))
    magnitude_cwt = ssq_cwt(signal[:-1], wavelet=wavelet, fs=fs)
    coefs = magnitude_cwt[0]
    coefs = np.append(coefs, coefs[:, -1:], 1)

    # magnitude of cwt
    coefs = np.abs(coefs**2)

    # interpolate coefficients
    freqs = magnitude_cwt[2]
    freqs_interp = np.arange(0.5, 4.5, 0.05)
    ip = interpolate.interp2d(range(coefs.shape[1]), freqs, coefs)
    coefs_interp = ip(range(coefs.shape[1]), freqs_interp)

    # trim spectrogram from the coi
    coefs_interp = coefs_interp[:, 5*fs:-5*fs]
    return magnitude_cwt, freqs_interp, coefs_interp

# %%
def identify_peaks_in_cwt(freqs_interp: np.ndarray, coefs_interp: np.ndarray,
                          fs: int, step_freq: tuple,
                          alpha: float, beta: float):
    """Identify dominant peaks in wavelet coefficients.

    Method uses alpha and beta parameters to identify dominant peaks in
    one-second non-overlapping windows in the product of Continuous Wavelet
    Transformation. Dominant peaks need to occur within the step frequency
    range.

    Args:
        freqs_interp: array of floats
            frequency-domain (in Hz)
        coefs_interp: array of floats
            wavelet coefficients (-)
        fs: integer
            sampling frequency (in Hz)
        step_freq: tuple
            step frequency range
        alpha: float
            maximum ratio between dominant peak below and within
            step frequency range
        beta: float
            maximum ratio between dominant peak above and within
            step frequency range

    Returns:
        Ndarray with dominant peaks
    """

    # identify dominant peaks within coefficients
    dp = np.zeros((coefs_interp.shape[0], int(coefs_interp.shape[1]/fs)))
    loc_min = np.argmin(abs(freqs_interp-step_freq[0]))
    loc_max = np.argmin(abs(freqs_interp-step_freq[1]))
    for i in range(int(coefs_interp.shape[1]/fs)):
        # segment measurement into one-second non-overlapping windows
        x_start = i*fs
        x_end = (i + 1)*fs
        # identify peaks and their location in each window
        window = np.sum(coefs_interp[:, np.arange(x_start, x_end)], axis=1)
        locs, _ = find_peaks(window)
        pks = window[locs]
        ind = np.argsort(-pks)
        locs = locs[ind]
        pks = pks[ind]
        index_in_range = []

        # account peaks that satisfy condition
        for j in range(len(locs)):
            if loc_min <= locs[j] <= loc_max:
                index_in_range.append(j)
            if len(index_in_range) >= 1:
                break
        peak_vec = np.zeros(coefs_interp.shape[0])
        if len(index_in_range) > 0:
            if locs[0] > loc_max:
                if pks[0]/pks[index_in_range[0]] < beta:
                    peak_vec[locs[index_in_range[0]]] = 1
            elif locs[0] < loc_min:
                if pks[0]/pks[index_in_range[0]] < alpha:
                    peak_vec[locs[index_in_range[0]]] = 1
            else:
                peak_vec[locs[index_in_range[0]]] = 1
        dp[:, i] = peak_vec

    return dp

# %%
def find_continuous_dominant_peaks(valid_peaks: np.ndarray, min_t: int,
                                   delta: int) -> npt.NDArray[np.float64]:
    """Identifies continuous and sustained peaks within matrix.

    Args:
        valid_peaks: nparray
            binary matrix (1=peak,0=no peak) of valid peaks
        min_t: integer
            minimum duration of peaks (in seconds)
        delta: integer
            maximum difference between consecutive peaks (in multiplication of
                                                          0.05Hz)

    Returns:
        Ndarray with binary matrix (1=peak,0=no peak) of continuous peaks
    """
    valid_peaks = np.concatenate((valid_peaks,
                                  np.zeros((valid_peaks.shape[0], 1))), axis=1)
    cont_peaks = np.zeros((valid_peaks.shape[0], valid_peaks.shape[1]))
    for slice_ind in range(valid_peaks.shape[1] - min_t):
        slice_mat = valid_peaks[:, np.arange(slice_ind, slice_ind + min_t)]
        windows = ([i for i in np.arange(min_t)] +
                   [i for i in np.arange(min_t-2, -1, -1)])
        for win_ind in windows:
            pr = np.where(slice_mat[:, win_ind] != 0)[0]
            count = 0
            if len(pr) > 0:
                for i in range(len(pr)):
                    index = np.arange(max(0, pr[i] - delta),
                                      min(pr[i] + delta + 1,
                                          slice_mat.shape[0]
                                          ))
                    if win_ind == 0 or win_ind == min_t - 1:
                        cur_peak_loc = np.transpose(np.array(
                            [np.ones(len(index))*pr[i], index], dtype=int
                            ))
                    else:
                        cur_peak_loc = np.transpose(np.array(
                            [index, np.ones(len(index))*pr[i], index],
                            dtype=int
                            ))

                    peaks = np.zeros((cur_peak_loc.shape[0],
                                      cur_peak_loc.shape[1]), dtype=int)
                    if win_ind == 0:
                        peaks[:, 0] = slice_mat[cur_peak_loc[:, 0],
                                                win_ind]
                        peaks[:, 1] = slice_mat[cur_peak_loc[:, 1],
                                                win_ind + 1]
                    elif win_ind == min_t - 1:
                        peaks[:, 0] = slice_mat[cur_peak_loc[:, 0],
                                                win_ind]
                        peaks[:, 1] = slice_mat[cur_peak_loc[:, 1],
                                                win_ind - 1]
                    else:
                        peaks[:, 0] = slice_mat[cur_peak_loc[:, 0],
                                                win_ind - 1]
                        peaks[:, 1] = slice_mat[cur_peak_loc[:, 1],
                                                win_ind]
                        peaks[:, 2] = slice_mat[cur_peak_loc[:, 2],
                                                win_ind + 1]

                    cont_peaks_edge = cur_peak_loc[np.sum(
                        peaks[:, np.arange(2)], axis=1) > 1, :]
                    cpe0 = cont_peaks_edge.shape[0]
                    if win_ind == 0 or win_ind == min_t - 1:  # first or last
                        if cpe0 == 0:
                            slice_mat[cur_peak_loc[:, 0], win_ind] = 0
                        else:
                            count = count + 1
                    else:
                        cont_peaks_other = cur_peak_loc[np.sum(
                            peaks[:, np.arange(1, 3)], axis=1) > 1, :]
                        cpo0 = cont_peaks_other.shape[0]
                        if cpe0 == 0 or cpo0 == 0:
                            slice_mat[cur_peak_loc[:, 1], win_ind] = 0
                        else:
                            count = count + 1
            if count == 0:
                slice_mat = np.zeros((slice_mat.shape[0], slice_mat.shape[1]))
                break
        cont_peaks[:, np.arange(
            slice_ind, slice_ind + min_t)] = np.maximum(
                cont_peaks[:, np.arange(slice_ind, slice_ind + min_t)],
                slice_mat)

    return cont_peaks[:, :-1]

#TODO: copmute CWT toat least min_T concecutive valid windows 
# %%
def find_walking(magnitude: np.ndarray, valid: np.ndarray, fs: int, 
                 step_freq: tuple, alpha: float,beta: float,
                 min_t: int, delta: int, plot_CWT: bool) -> npt.NDArray[np.float64]:
    """Finds walking and calculate steps from raw acceleration data.

    Method finds periods of repetitive and continuous oscillations with
    predominant frequency occurring within know step frequency range.
    Frequency components are extracted with Continuous Wavelet Transform.

    Args:
        magnitude: array of floats
            vector magnitude with one bout of activity (in g)
        valid: array of booleans
            true elements stands for segment amplitude above treshold             
        fs: integer
            sampling frequency (in Hz)
        step_freq: tuple
            step frequency range
        alpha: float
            maximum ratio between dominant peak below and within
            step frequency range
        beta: float
            maximum ratio between dominant peak above and within
            step frequency range
        min_t: integer
            minimum duration of peaks (in seconds)
        delta: integer
            maximum difference between consecutive peaks (in multiplication of
                                                          0.05Hz)
        plot_CWT: bool
            plot cwt magnitude, coefs_interp and freqs_interp                                                  

    Returns:
        Ndarray with identified number of steps per second
    """

    # define wavelet function used in method
    wavelet = ('gmw', {'beta': 90, 'gamma': 3})

    # compute and interpolate CWT
    magnitude_cwt, freqs_interp, coefs_interp = compute_cwt(signal=magnitude, fs=fs,
                                                            wavelet=wavelet)
     # plot CWT 
    if(plot_CWT):
        plt.title('magnitude original signal')
        plt.plot(magnitude[:-1]); plt.show()

        Twxo, Wxo, *_ = magnitude_cwt
        viz(Twxo, Wxo)

        plt.imshow(np.abs(coefs_interp), aspect='auto', vmin=0, vmax=.2, cmap='turbo')
        plt.colorbar()
        plt.title('coefs_interp')
        plt.show()
    

    # get map of dominant peaks
    dp = identify_peaks_in_cwt(freqs_interp, coefs_interp, fs, step_freq,
                                alpha, beta)

    # distribute local maxima across valid periods
    valid_peaks = np.zeros((dp.shape[0], len(valid)))
    valid_peaks[:, valid] = dp

    # find peaks that are continuous in time (min_t) and frequency (delta)
    cont_peaks = find_continuous_dominant_peaks(valid_peaks, min_t, delta)

    # summarize the results
    cadence = np.zeros(valid_peaks.shape[1])
    for i in range(len(cadence)):
        ind_freqs = np.where(cont_peaks[:, i] > 0)[0]
        if len(ind_freqs) > 0:
            cadence[i] = freqs_interp[ind_freqs[0]]

    return cadence
# %%

def bandpass_filter(signal_data: np.ndarray, low_freq: float, high_freq: float, sampling_rate:int) -> np.ndarray: 
    """
    Filter frequencies out of [low_freq, high_freq].
        args:
            signal_data: 
                data in time domain
            low_freq:
                low frequency
            high_freq:
                high frequency
            sampling_rate:
                sampling rate
    """
    nyquist_freq = 0.5 * sampling_rate
    low = low_freq / nyquist_freq
    high = high_freq / nyquist_freq
    order = 4  # Filter order
    b, a = butter(order, [low, high], btype='band')
    filtered_signal = filtfilt(b, a, signal_data)
    return filtered_signal
