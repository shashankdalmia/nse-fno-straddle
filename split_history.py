import pandas as pd
import os

df = pd.read_csv("history.csv")

df["Trade Date"] = pd.to_datetime(df["Trade Date"])

os.makedirs("monthly", exist_ok=True)

for month, data in df.groupby(df["Trade Date"].dt.strftime("%Y-%m")):

    filename = f"monthly/{month}.csv"

    data.to_csv(
        filename,
        index=False
    )

    print(
        f"{month}: {len(data)} rows -> {filename}"
    )

print("MONTHLY SPLIT COMPLETE")
