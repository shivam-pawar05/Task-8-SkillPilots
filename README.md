# Automated MySQL ETL Pipeline with Python

A beginner-friendly ETL project that extracts sales data from MySQL, transforms it using Pandas, and loads monthly product summaries into a MySQL reporting table. It can be scheduled using Windows Task Scheduler.

## Features

- Connects to MySQL with SQLAlchemy and PyMySQL.
- Extracts source rows into a Pandas DataFrame.
- Validates numeric/date fields and calculates sales totals.
- Aggregates quantity, sales, and distinct order count by month and product.
- Loads the output into `sales_report`.
- Logs successful runs and errors to `logs/etl.log`.
- Can be run on demand or scheduled in Windows.

## Requirements

- Python 3.10 or newer
- MySQL Server
- MySQL Workbench (optional, for running SQL scripts)
- Windows for the Task Scheduler instructions below

## Folder structure

```text
mysql-etl-automation/
├── main.py
├── config.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
├── sql/
│   └── create_tables.sql
└── logs/
    └── etl.log       # created when the script runs
```

## 1. Create and activate a virtual environment

Open Command Prompt in this project folder:

```bat
python -m venv .venv
.venv\Scripts\activate
```

If `python` is not recognized, install Python and enable the option to add Python to PATH.

## 2. Install dependencies

```bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Create the source database and sample data

Open MySQL Workbench, connect to your local MySQL server, open `sql/create_tables.sql`, and execute the script. It creates the `etl_demo` database, the `sales` source table, and sample sales rows.

The script uses `ON DUPLICATE KEY UPDATE` so rerunning it will update the sample rows rather than create duplicate order IDs.

## 4. Configure database credentials

Edit `.env` and enter your own MySQL connection settings:

```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_actual_mysql_password
DB_NAME=etl_demo
```

Do not commit `.env` to a public repository. The included `.gitignore` excludes it.

## 5. Run the ETL script

With the virtual environment activated:

```bat
python main.py
```

Expected output on the supplied sample data:

```text
ETL completed. Loaded 5 rows into sales_report.
```

The exact row count can differ if you modify the source data. The first successful run creates/replaces `sales_report`.

## 6. Verify the report

Run this query in MySQL Workbench:

```sql
USE etl_demo;
SELECT * FROM sales_report ORDER BY order_month, product_name;
```

The report includes `order_month`, `product_name`, `total_quantity`, `total_sales`, and `order_count`.

## 7. Schedule it using Windows Task Scheduler

1. Find the full path to the project folder.
2. Open **Task Scheduler** and choose **Create Basic Task**.
3. Give it a name such as `MySQL Sales ETL`.
4. Choose a daily trigger and select the time.
5. Choose **Start a program**.
6. In **Program/script**, enter the full path to the virtual environment Python executable, for example:
   `C:\path\to\mysql-etl-automation\.venv\Scripts\python.exe`
7. In **Add arguments**, enter:
   `main.py`
8. In **Start in**, enter the project folder path, for example:
   `C:\path\to\mysql-etl-automation`
9. Finish the wizard. Right-click the task and select **Run** to test it.
10. Check `logs\etl.log` and verify the `sales_report` table.

Use your actual folder path; the example path above is a placeholder.

## How it works

1. **Extract:** SQLAlchemy connects to MySQL and reads `sales` into a Pandas DataFrame.
2. **Transform:** The script validates fields, calculates `quantity * unit_price`, derives the month, and groups by month and product.
3. **Load:** Pandas writes the summary to `sales_report`.
4. **Schedule:** Task Scheduler launches the same script on a timetable.

## Important notes

- `if_exists="replace"` recreates the reporting table each run. This is suitable for a small demo, but table indexes, grants, and custom table definitions may be lost. For production, create the report table explicitly and use a transactional upsert or staging-table swap.
- This sample reads the full source table. For large databases, use incremental extraction, date filters, or chunked reads.
- Use a dedicated least-privilege MySQL account for real projects rather than an administrator account.
- If the connection fails, check that MySQL is running, the host/port are correct, and the credentials in `.env` are valid.
