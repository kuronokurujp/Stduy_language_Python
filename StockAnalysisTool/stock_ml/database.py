
"""SQLite helper using SQLAlchemy."""
from pathlib import Path
from sqlalchemy import create_engine, MetaData, Table, Column, String, Date, Float
from sqlalchemy.orm import sessionmaker

DB_PATH = Path(__file__).resolve().parent.parent / "stock_data.sqlite3"
ENGINE = create_engine(f"sqlite:///{DB_PATH}")
METADATA = MetaData()

price_table = Table(
    "prices",
    METADATA,
    Column("ticker", String, primary_key=True),
    Column("date", Date, primary_key=True),
    Column("open", Float),
    Column("high", Float),
    Column("low", Float),
    Column("close", Float),
    Column("volume", Float),
)

METADATA.create_all(ENGINE)
Session = sessionmaker(bind=ENGINE)
