import pandas as pd
import numpy as np


INPUT_FILE = "data.csv"              
OUTPUT_FILE = "data_lpf.csv"        

SAMPLE_RATE_HZ = 100.0               
CUTOFF_LPF_HZ = 5.0                 
# ===========================


def compute_alpha_lpf(dt, cutoff_hz):

    rc = 1.0 / (2.0 * np.pi * cutoff_hz)
    alpha = dt / (rc + dt)
    return alpha


def low_pass_filter(x, alpha):

    y = np.zeros_like(x, dtype=float)
    y[0] = x[0]
    for i in range(1, len(x)):
        y[i] = y[i-1] + alpha * (x[i] - y[i-1])
    return y


def main():
    df = pd.read_csv(INPUT_FILE)

    expected_cols = ["Accel_X", "Accel_Y", "Accel_Z",
                     "Gyro_X", "Gyro_Y", "Gyro_Z"]

    for col in expected_cols:
        if col not in df.columns:
            raise ValueError(f"Missing column '{col}' in CSV. Found: {df.columns.tolist()}")

    dt = 1.0 / SAMPLE_RATE_HZ
    alpha_lpf = compute_alpha_lpf(dt, CUTOFF_LPF_HZ)

    print(f"[LPF] dt = {dt:.6f} s, cutoff = {CUTOFF_LPF_HZ} Hz, alpha = {alpha_lpf:.4f}")

    for col in expected_cols:
        x = df[col].values.astype(float)
        df[f"{col}_LPF"] = low_pass_filter(x, alpha_lpf)

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"[LPF] Saved filtered data to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
