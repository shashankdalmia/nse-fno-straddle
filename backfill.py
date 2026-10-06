import os
import time
from datetime import date, timedelta

from update import process_date, load_history, save_history


START_DATE = date(2026, 1, 1)
END_DATE = date.today() - timedelta(days=1)


def main():

    history = load_history()

    current_dates = set(
        (row["Trade Date"], row["Symbol"], row["Expiry Bucket"])
        for row in history
    )

    d = START_DATE
    processed = 0
    added = 0

    while d <= END_DATE:

        # Saturday / Sunday skip
        if d.weekday() < 5:

            trade_date = d.strftime("%Y-%m-%d")

            print(f"Processing {trade_date} ...")

            try:
                rows = process_date(d)

                if rows:

                    for row in rows:

                        key = (
                            row["Trade Date"],
                            row["Symbol"],
                            row["Expiry Bucket"]
                        )

                        if key not in current_dates:
                            history.append(row)
                            current_dates.add(key)
                            added += 1

                    processed += 1
                    print(
                        f"{trade_date}: "
                        f"{len(rows)} records found"
                    )

                else:
                    print(
                        f"{trade_date}: "
                        f"No NSE data available"
                    )

            except Exception as e:

                print(
                    f"{trade_date}: ERROR - {e}"
                )

            # Small delay to avoid hitting NSE too aggressively
            time.sleep(1)

        d += timedelta(days=1)

    save_history(history)

    print("--------------------------------")
    print("BACKFILL COMPLETE")
    print(f"Trading days processed: {processed}")
    print(f"New records added: {added}")
    print(f"Total history records: {len(history)}")
    print("--------------------------------")


if __name__ == "__main__":
    main()
