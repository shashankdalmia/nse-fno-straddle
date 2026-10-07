import time
from datetime import date, timedelta
import pandas as pd

from update import (
    process_date,
    save_history
)

START_DATE = date(2026, 1, 1)
END_DATE = date.today() - timedelta(days=1)


COLUMNS = [
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
]


def main():

    print("=" * 70)
    print("FRESH NSE F&O STRADDLE HISTORY REBUILD")
    print("=" * 70)

    print(f"Start date : {START_DATE}")
    print(f"End date   : {END_DATE}")
    print()
    print("IMPORTANT:")
    print("Existing history.csv will be completely rebuilt.")
    print("Old CURRENT/NEAR/FAR records will NOT be retained.")
    print("=" * 70)

    all_records = []

    d = START_DATE

    trading_days = 0
    successful_days = 0
    failed_days = 0

    while d <= END_DATE:

        # Monday-Friday only.
        # NSE holiday dates are handled by the absence
        # of the NSE bhavcopy file.
        if d.weekday() < 5:

            trading_days += 1

            print()
            print("-" * 70)
            print(f"Processing: {d}")
            print("-" * 70)

            try:

                rows = process_date(d)

                if rows:

                    all_records.extend(rows)

                    successful_days += 1

                    print(
                        f"{d}: "
                        f"{len(rows)} records collected"
                    )

                else:

                    failed_days += 1

                    print(
                        f"{d}: "
                        f"No NSE data / no valid records"
                    )

            except Exception as e:

                failed_days += 1

                print(
                    f"{d}: ERROR"
                )

                print(
                    str(e)
                )

            # Small pause to avoid hammering NSE
            time.sleep(1)

        d += timedelta(days=1)

    print()
    print("=" * 70)
    print("RAW COLLECTION COMPLETE")
    print("=" * 70)

    print(
        f"Weekdays checked     : {trading_days}"
    )

    print(
        f"Successful days      : {successful_days}"
    )

    print(
        f"Days without records : {failed_days}"
    )

    print(
        f"Raw records collected: {len(all_records)}"
    )

    if not all_records:

        print()
        print("NO RECORDS FOUND.")
        print("history.csv was NOT changed.")
        return

    # -------------------------------------------------
    # Create fresh dataframe
    # -------------------------------------------------

    history = pd.DataFrame(
        all_records
    )

    # Ensure exact column order
    history = history[COLUMNS]

    # -------------------------------------------------
    # Remove accidental duplicates
    # -------------------------------------------------

    history = (
        history
        .drop_duplicates(
            subset=[
                "Trade Date",
                "Symbol",
                "Expiry Bucket"
            ],
            keep="last"
        )
    )

    # -------------------------------------------------
    # Sort
    # -------------------------------------------------

    history = history.sort_values(
        [
            "Trade Date",
            "Symbol",
            "Expiry Bucket"
        ]
    )

    # -------------------------------------------------
    # Save completely fresh history
    # -------------------------------------------------

    save_history(
        history
    )

    print()
    print("=" * 70)
    print("BACKFILL COMPLETE")
    print("=" * 70)

    print(
        f"Final history rows : {len(history)}"
    )

    print(
        f"Trading days       : {successful_days}"
    )

    print()
    print("Fresh history.csv has been created.")
    print("Old incorrect bucket assignments have been removed.")
    print("=" * 70)


if __name__ == "__main__":
    main()
