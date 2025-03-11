import numpy as np
import matplotlib.pyplot as plt
import h5py
import os
from miaplpy.objects.slcStack import slcStack
from scipy.signal import savgol_filter
from scipy.signal import butter, filtfilt , lfilter
from spatz.change.phase_noise_time import temporallyUnwrapArcPhase , computeIfgsAndBaselines
import datetime
def load_slc_stack(file_path,geometry_file):
    """Loads SLC stack, temporal baselines (tbase), and perpendicular baselines (pbase) from an HDF5 file."""
    with h5py.File(file_path, 'r') as f:
        print("Available datasets in HDF5 file:", list(f.keys()))  # Debugging output
        
        # Ensure required datasets exist
        if 'slc' not in f or 'date' not in f or 'bperp' not in f:
            raise KeyError(f"Missing required datasets in {file_path}. Available datasets: {list(f.keys())}")

        # Load SLC stack
        slc = np.array(f['slc'])  # Shape: (num_ifgs, height, width)

        # Load acquisition dates and convert them to decimal years
        acquisition_dates = np.array(f['date'])  # Dates in YYYYMMDD format
        acquisition_dates = [datetime.datetime.strptime(str(d, "utf-8"), "%Y%m%d") for d in acquisition_dates]
        tbase = np.array([(date - acquisition_dates[0]).days for date in acquisition_dates]) / 365.25  # Convert to years

        # Load perpendicular baselines
        pbase = np.array(f['bperp'])  # Shape: (num_ifgs,)
        # Load `loc_inc` and `slant_range` from geometry file
    with h5py.File(geometry_file, 'r') as g:
        print("Available datasets in geometry HDF5 file:", list(g.keys()))  # Debugging output

        if 'incidenceAngle' not in g or 'slantRangeDistance' not in g:
            raise KeyError(f"Missing required datasets in {geometry_file}. Available datasets: {list(g.keys())}")

        loc_inc = np.array(g['incidenceAngle'])
        loc_inc = np.deg2rad(loc_inc)  # Convert to radians

        slant_range = np.array(g['slantRangeDistance'])  # Extract slant range


    print("SLC Stack Loaded Successfully")
    print(f"SLC Shape: {slc.shape}, Temporal Baselines: {tbase.shape}, Perpendicular Baselines: {pbase.shape}")
    
    return slc, tbase, pbase,loc_inc, slant_range
# Compute Amplitude Dispersion Index (ADI)
def compute_adi(slc_stack):
    """Computes ADI from the SLC stack."""
    amp_stack = np.abs(slc_stack)
    mean_amp = np.mean(amp_stack, axis=0)
    std_amp = np.std(amp_stack, axis=0)
    mean_amplitude = mean_amp / np.max(mean_amp)
    adi = std_amp / mean_amp
    return adi , mean_amplitude
# Select first-order and TCS points
def select_points(adi, ADI_THR_PS, ADI_THR_TCS):
    """Selects first-order and TCS points based on ADI thresholds."""
    first_order_mask = adi < ADI_THR_PS
    tcs_mask = (adi >= ADI_THR_PS) & (adi < ADI_THR_TCS)
    return first_order_mask, tcs_mask
def select_reference_pixel(mask):
    """Selects a valid reference pixel within the bounds of the dataset."""
    indices = np.argwhere(mask)  # Get (row, col) indices of valid pixels
    if len(indices) == 0:
        raise ValueError("No valid first-order pixels found!")
    ref_pixel = indices[0]  # Select the first valid pixel
    return ref_pixel[0], ref_pixel[1]  # (row, col)
# # Compute Arc Phases
# def compute_arc_phase(slc_stack, ref_row, ref_col):
#     """Computes arc phases relative to a reference index."""
#     reference = slc_stack[:, ref_row, ref_col]
#     arc_phases = np.angle(slc_stack * np.conjugate(reference[:, np.newaxis, np.newaxis]))
#     return arc_phases
def compute_arc_phase(slc_stack, ref_row, ref_col):
    """Computes arc phases relative to a reference index, ensuring proper phase computation and unwrapping."""
    reference = slc_stack[:, ref_row, ref_col]
    arc_phases = np.angle(slc_stack / reference[:, np.newaxis, np.newaxis])  # Correct computation
    arc_phases = np.unwrap(arc_phases, axis=0)  # Phase unwrapping to prevent discontinuities
    return arc_phases
# Visualize Arc Phase Time Series in Subplots
def plot_arc_phase(arc_phases, first_order_mask):
    """Plots arc phase time series for selected first-order points with subplots."""
    num_ifgs, rows, cols = arc_phases.shape
    num_subplots = 10  # Divide IFG index into 4 parts
    ifg_per_subplot = num_ifgs // num_subplots

    plt.figure(figsize=(14, 8))

    selected_indices = np.argwhere(first_order_mask)[:15]  # Pick first 10 valid points
    row_indices, col_indices = selected_indices[:, 0], selected_indices[:, 1]

    for i in range(num_subplots):
        ax = plt.subplot(4, 4, i + 1)  # 2x2 grid
        start_ifg = i * ifg_per_subplot
        end_ifg = start_ifg + ifg_per_subplot

        for row, col in zip(row_indices, col_indices):
            ax.plot(range(start_ifg, end_ifg), arc_phases[start_ifg:end_ifg, row, col], alpha=0.7, label=f'Pixel ({row}, {col})')

        ax.set_xlabel("Interferogram Index")
        ax.set_ylabel("Phase (radians)")
        ax.set_title(f"Arc Phase (IFG {start_ifg} - {end_ifg})")
        # ax.legend(fontsize='small', loc='upper right')

    plt.tight_layout()
    #plt.show()
    
    selected_indices = np.argwhere(first_order_mask)[:10]  # Pick first 10 valid points
    row_indices, col_indices = selected_indices[:, 0], selected_indices[:, 1]

    for row, col in zip(row_indices, col_indices):
        plt.figure()
        plt.plot(arc_phases[:, row, col], '.')
        plt.ylim([-np.pi*4, np.pi*4])
    plt.show()
def plot_comparison(arc_phases, smoothed_butter, smoothed_savgol, first_order_mask):
    """Plots separate time series for each selected first-order pixel, comparing original, Butterworth, and Savitzky-Golay filters."""
    num_ifgs, rows, cols = arc_phases.shape
    selected_indices = np.argwhere(first_order_mask)[:5]  # Pick first 5 valid points
    row_indices, col_indices = selected_indices[:, 0], selected_indices[:, 1]

    for row, col in zip(row_indices, col_indices):
        plt.figure(figsize=(8, 5))
        plt.plot(arc_phases[:, row, col], '.', markersize=4, alpha=0.7, label="Original")
        plt.plot(smoothed_butter[:, row, col], '.', linewidth=1.5, label="Butterworth Filter")
        plt.plot(smoothed_savgol[:, row, col], '.', linewidth=1.5, label="Savitzky-Golay Filter")

        plt.xlabel("Interferogram Index")
        plt.ylabel("Phase (radians)")
        plt.title(f"Pixel ({row}, {col}) - Arc Phase Comparison")
        plt.ylim([-np.pi, np.pi])  # Set consistent y-limits
        plt.legend(fontsize="small")
        plt.grid(True)
    plt.show()
def butter_lowpass_filter(data, cutoff, fs, order=5):
    """
    Apply a Butterworth low-pass filter to smooth phase series.
    
    Parameters:
    - data (np.ndarray): 1D array of unwrapped phase values.
    - cutoff (float): Cutoff frequency for the filter (Hz).
    - fs (float): Sampling frequency (assumed time intervals).
    - order (int): Order of the Butterworth filter.

    Returns:
    - np.ndarray: Smoothed phase series.
    """
    nyquist = 0.5 * fs  # Nyquist frequency
    normal_cutoff = cutoff / nyquist  # Normalize cutoff
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    n_samples = len(data)
    pad_length = max(3 * order, 15)  # Required pad length for filtfilt
    if n_samples > pad_length:  
        smoothed_data = filtfilt(b, a, data)  # Use filtfilt if enough data
        #print('filtfilt is being used')
    elif n_samples > order:  
        smoothed_data = lfilter(b, a, data)  # Use lfilter if slightly short
       # print('lfilter is being used')
    else:
        print(f"⚠ Warning: Skipping Butterworth filter (data too short: {n_samples} samples)")
        smoothed_data = data  # Return raw data if not enough samples

    return smoothed_data
def sav_golay_smooth(arc_phase, window_length, polyorder):
    """
    Apply a Savitzky-Golay filter to smooth the phase series.

    Parameters:
    - phase_series (np.ndarray): 1D array of unwrapped phase values.
    - window_length (int): The length of the filter window (must be odd).
    - polyorder (int): Polynomial order for Savitzky-Golay filter.

    Returns:
    - np.ndarray: Smoothed phase series.
    """
    n_samples = len(arc_phase)  # Get length of phase series
    # Ensure window_length does not exceed available data
    adjusted_window = min(window_length, n_samples)
    
    # Ensure window_length is at least 3 (minimum for smoothing)
    if adjusted_window < 3:
        adjusted_window = 3  
    # Ensure window_length is odd (required by savgol_filter)
    if adjusted_window % 2 == 0:
        adjusted_window -= 1  
    # Ensure window_length is greater than polyorder
    if adjusted_window <= polyorder:
        adjusted_window = polyorder + 1  
    # Apply smoothing only if valid window size is possible
    if adjusted_window >= 3 and n_samples >= adjusted_window:
        return savgol_filter(arc_phase, adjusted_window, polyorder)
    return arc_phase  # Return original if filtering is not possible
