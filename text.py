mport tkinter as tk
from tkinter import messagebox
import sqlalchemy as sql
from sqlalchemy import create_engine, text
import urllib
# Database connection setup
server = "USER\\SQLEXPRESS"
database = "QuanLyTiemKaraoke"
params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    "Trusted_Connection=yes;"
)
