import numpy as np
from biofeedback.acc_to_sf.base_functions import find_walking, peak2peak

# Frequency sampling
FS = 32
# Segment threshold
A = 0.3
# Parameters for equation from algorithm flow
alpha = 31.7
beta = 1.4

# %%
def get_cadence(acc_data: np.ndarray, running: bool) -> np.ndarray:
    magnitude = np.linalg.norm(acc_data, axis=1)-1

    # Split data into segments - 1 sec non-overlapping windows
    # Only segments with length 32 are valid
    magnitude = magnitude[:len(magnitude)-len(magnitude)%32]
    magnitude_segments = magnitude.reshape(-1,FS)

    if(running):
        Fw_max = 3.2
        Fw_min = 1.7
        min_T = 2

    # walking
    else:
        Fw_max = 2.3
        Fw_min = 1.4
        min_T = 6

    # Calculate peak-to-peak amp in each segment
    ptp_amp = np.apply_along_axis(peak2peak,axis=1,arr=magnitude_segments)

    # Find segments above A
    magnitude_segments[ptp_amp < A] = 0
    magnitude = magnitude_segments.reshape(len(magnitude))
    valid = np.ones(len(ptp_amp), dtype=bool)
    valid[ptp_amp < A] = False
    #omit segments with amplitude below A
    tapered_magnitude = magnitude[np.repeat(valid, FS)]

    # Number of identified steps per second
    cadence = find_walking(magnitude=tapered_magnitude, valid=valid, fs=FS, 
                        step_freq=(Fw_min, Fw_max), alpha=alpha, beta=beta,
                        min_t=min_T, delta=20, plot_CWT=False)
    return cadence