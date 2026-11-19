import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "retail_warehouse.db"
ANALYSIS_SQL_PATH = BASE_DIR / "sql" / "02_analysis.sql"
OUTPUT_DIR = BASE_DIR / "data"


def run_queries() -> None:
    conn = sqlite3.connect(DB_PATH)
    with open(ANALYSIS_SQL_PATH, "r", encoding="utf-8") as f:
        queries = [q.strip() for q in f.read().split(";") if q.strip()]

    report_names = [
        "01_shrinkage_by_category",
        "02_store_out_of_stock_rates",
        "03_process_bottlenecks"
    ]

    for name, query in zip(report_names, queries):
        print(f"\n--- REPORT: {name.upper()} ---")
        df = pd.read_sql_query(query, conn)
        print(df.to_string(index=False))

        # Export as CSV for Power BI / Excel dashboards
        csv_path = OUTPUT_DIR / f"{name}.csv"
        df.to_csv(csv_path, index=False)

    conn.close()
    print(f"\nCSV reports exported to: {OUTPUT_DIR}")


if __name__ == "__main__":
    run_queries()
