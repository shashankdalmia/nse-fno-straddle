import time
from datetime import date, timedelta

import pandas as pd

from update import process_date, load_history, save_history


START_DATE = date(2026, 1, 1)
END_DATE = date.today() - timedelta(days=1)


def main():

    history = load_history()

    if history.empty:
        history = pd.DataFrame(columns=[
            "Trade Date",
            "Symbol",
            "Expiry Bucket",
            "Expiry",
            "Futures Close",
            "ATM Strike",
            "CE Close",
            "PE Close",
            "Straddle",
            "Straddle %"
        ])

    # Existing records
    current_keys = set(
        zip(
            history["Trade Date"].astype(str),
            history["Symbol"].astype(str),
            history["Expiry Bucket"].astype(str)
        )
    )

    new_records = []

    d = START_DATE
    processed = 0

    while d <= END_DATE:

        if d.weekday() < 5:

            print("=" * 50)
            print(f"Processing {d}")
            print("=" * 50)

            try:

                rows = process_date(d)

                if rows:

                    added_today = 0

                    for row in rows:

                        key = (
                            row["Trade Date"],
                            row["Symbol"],
                            row["Expiry Bucket"]
                        )

                        if key not in current_keys:

                            new_records.append(row)
                            current_keys.add(key)
                            added_today += 1

                    processed += 1

                    print(
                        f"{d}: {len(rows)} rows found, "
                        f"{added_today} new rows added"
                    )

                else:

                    print(
                        f"{d}: No NSE file/data"
                    )

            except Exception as e:

                print(
                    f"{d}: ERROR - {e}"
                )

            time.sleep(1)

        d += timedelta(days=1)

    # Add all new records at once
    if new_records:

        new_df = pd.DataFrame(new_records)

        final_df = pd.concat(
            [history, new_df],
            ignore_index=True
        )

        final_df = final_df.drop_duplicates(
            subset=[
                "Trade Date",
                "Symbol",
                "Expiry Bucket"
            ],
            keep="last"
        )

        save_history(final_df)

        print("=" * 50)
        print("BACKFILL COMPLETE")
        print(f"Trading days processed: {processed}")
        print(f"New records added: {len(new_records)}")
        print(f"Total history rows: {len(final_df)}")
        print("=" * 50)

    else:

        print("=" * 50)
        print("NO NEW RECORDS")
        print(f"Trading days processed: {processed}")
        print(f"Existing history rows: {len(history)}")
        print("=" * 50)


if __name__ == "__main__":
    main()
