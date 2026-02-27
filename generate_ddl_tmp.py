from sqlalchemy import create_mock_engine
from sqlalchemy.schema import CreateTable
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from app.db.database import Base
import app.db.models

def dump(sql, *multiparams, **params):
    print(sql.compile(dialect=engine.dialect))

engine = create_mock_engine("postgresql://", dump)

print("CREATE SCHEMA IF NOT EXISTS fsbb;")

for table in Base.metadata.sorted_tables:
    print(str(CreateTable(table).compile(dialect=engine.dialect)).strip() + ";")
