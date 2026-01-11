import pandas as pd
import numpy as np


INPUT_FILE = "data/sample1.csv"          
OUTPUT_FILE = "data_filtered.csv" 

SAMPLE_RATE_HZ = 100.0            
CUTOFF_LPF_HZ = 5.0               
CUTOFF_HPF_HZ = 0.5               
MA_WINDOW = 5                     
# =====================================


def compute_alpha_lpf(dt, cutoff_hz):
    """Return alpha for first-order low-pass filter."""
    # RC = 1 / (2π f_c)
    rc = 1.0 / (2.0 * np.pi * cutoff_hz)
    alpha = dt / (rc + dt)
    return alpha


def compute_alpha_hpf(dt, cutoff_hz):
    """Return alpha for first-order high-pass filter."""
    # RC = 1 / (2π f_c)
    rc = 1.0 / (2.0 * np.pi * cutoff_hz)
    alpha = rc / (rc + dt)
    return alpha


def low_pass_filter(x, alpha):

    y = np.zeros_like(x, dtype=float)
    y[0] = x[0]
    for i in range(1, len(x)):
        y[i] = y[i-1] + alpha * (x[i] - y[i-1])
    return y


def high_pass_filter(x, alpha):

    y = np.zeros_like(x, dtype=float)
    y[0] = 0.0
    for i in range(1, len(x)):
        y[i] = alpha * (y[i-1] + x[i] - x[i-1])
    return y


def moving_average_filter(x, window_size):

    if window_size <= 1:
        return x.astype(float)

    kernel = np.ones(window_size) / window_size
  
    y = np.convolve(x, kernel, mode='same')
    return y


def main():

    df = pd.read_csv(INPUT_FILE)


    expected_cols = ["Accel_X", "Accel_Y", "Accel_Z", "Gyro_X", "Gyro_Y", "Gyro_Z"]
    for col in expected_cols:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in CSV. Found columns: {df.columns.tolist()}")

    dt = 1.0 / SAMPLE_RATE_HZ

    alpha_lpf = compute_alpha_lpf(dt, CUTOFF_LPF_HZ)
    alpha_hpf = compute_alpha_hpf(dt, CUTOFF_HPF_HZ)

    print(f"Using dt = {dt:.6f} s")
    print(f"Low-pass alpha = {alpha_lpf:.4f}, cutoff = {CUTOFF_LPF_HZ} Hz")
    print(f"High-pass alpha = {alpha_hpf:.4f}, cutoff = {CUTOFF_HPF_HZ} Hz")
    print(f"Moving average window = {MA_WINDOW} samples")


    for col in expected_cols:
        x = df[col].values.astype(float)


        df[f"{col}_LPF"] = low_pass_filter(x, alpha_lpf)

        df[f"{col}_HPF"] = high_pass_filter(x, alpha_hpf)


        df[f"{col}_MA"] = moving_average_filter(x, MA_WINDOW)


    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Filtered data saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
