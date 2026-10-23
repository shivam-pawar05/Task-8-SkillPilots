import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "etl.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

def make_engine():
    url = URL.create(
        "mysql+pymysql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        query={"charset": "utf8mb4"},
    )
    return create_engine(url, pool_pre_ping=True)

def run_etl():
    engine = make_engine()
    try:
        logging.info("ETL job started")

        # EXTRACT: load source records into a Pandas DataFrame.
        with engine.connect() as connection:
            df = pd.read_sql(
                text("""
                    SELECT order_id, customer_name, product_name,
                           quantity, unit_price, order_date
                    FROM sales
                """),
                connection,
            )

        if df.empty:
            logging.warning("Source table sales is empty; no report rows written.")
            return

        # TRANSFORM: validate values and calculate order totals.
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        df = df.dropna(subset=["order_id", "quantity", "unit_price", "order_date"])
        df = df[(df["quantity"] >= 0) & (df["unit_price"] >= 0)].copy()
        df["total_amount"] = (df["quantity"] * df["unit_price"]).round(2)
        df["order_month"] = df["order_date"].dt.to_period("M").astype(str)

        # Aggregate one report row per month and product.
        report = (
            df.groupby(["order_month", "product_name"], as_index=False)
              .agg(
                  total_quantity=("quantity", "sum"),
                  total_sales=("total_amount", "sum"),
                  order_count=("order_id", "nunique"),
              )
        )
        report["total_sales"] = report["total_sales"].round(2)

        # LOAD: replace the report table contents on each run.
        # This makes the job repeatable and avoids duplicate report rows.
        report.to_sql(
            name="sales_report",
            con=engine,
            if_exists="replace",
            index=False,
            chunksize=1000,
            method="multi",
        )

        logging.info(
            "ETL job completed successfully: %s report rows loaded",
            len(report),
        )
        print(f"ETL completed. Loaded {len(report)} rows into sales_report.")
    except Exception:
        logging.exception("ETL job failed")
        raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    run_etl()
