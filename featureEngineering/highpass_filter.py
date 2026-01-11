import pandas as pd
import numpy as np

INPUT_FILE = "data.csv"              
OUTPUT_FILE = "data_hpf.csv"         

SAMPLE_RATE_HZ = 100.0               
CUTOFF_HPF_HZ = 0.5                  



def compute_alpha_hpf(dt, cutoff_hz):
    """Return alpha for first-order high-pass filter."""
    rc = 1.0 / (2.0 * np.pi * cutoff_hz)
    alpha = rc / (rc + dt)
    return alpha


def high_pass_filter(x, alpha):

    y = np.zeros_like(x, dtype=float)
    y[0] = 0.0
    for i in range(1, len(x)):
        y[i] = alpha * (y[i-1] + x[i] - x[i-1])
    return y


def main():
    df = pd.read_csv(INPUT_FILE)

    expected_cols = ["Accel_X", "Accel_Y", "Accel_Z",
                     "Gyro_X", "Gyro_Y", "Gyro_Z"]

    for col in expected_cols:
        if col not in df.columns:
            raise ValueError(f"Missing column '{col}' in CSV. Found: {df.columns.tolist()}")

    dt = 1.0 / SAMPLE_RATE_HZ
    alpha_hpf = compute_alpha_hpf(dt, CUTOFF_HPF_HZ)

    print(f"[HPF] dt = {dt:.6f} s, cutoff = {CUTOFF_HPF_HZ} Hz, alpha = {alpha_hpf:.4f}")

    for col in expected_cols:
        x = df[col].values.astype(float)
        df[f"{col}_HPF"] = high_pass_filter(x, alpha_hpf)

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"[HPF] Saved filtered data to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
