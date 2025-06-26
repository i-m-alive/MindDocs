import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=shivrajserver2.database.windows.net;"
    "DATABASE=myappdb;"
    "UID=sqladmin;"
    "PWD=Ranju@Raj1;"  # Use %40 if in connection string URL
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

try:
    conn = pyodbc.connect(conn_str)
    print("✅ Connected to Azure SQL!")
except Exception as e:
    print("❌ Connection failed:", e)
