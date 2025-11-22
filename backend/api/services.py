import pandas as pd

REQUIRED_COLS = ["Equipment Name", "Type", "Flowrate", "Pressure", "Temperature"]

def compute_summary(file_obj):
    # Read CSV
    df = pd.read_csv(file_obj)

    # (Optional) validate columns
    for col in REQUIRED_COLS:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Safe numeric means
    def mean_of(col):
        s = pd.to_numeric(df[col], errors='coerce')
        return float(s.mean()) if s.notna().any() else None

    summary = {
        "total_count": int(len(df)),
        "averages": {
            "Flowrate": mean_of("Flowrate"),
            "Pressure": mean_of("Pressure"),
            "Temperature": mean_of("Temperature"),
        },
        "type_distribution": df["Type"].value_counts(dropna=False).to_dict(),
    }
    return summary
