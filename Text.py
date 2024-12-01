import tkinter as tk
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

# Create the SQLAlchemy engine
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# Check connection
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("Successfully connected to database:", result.fetchone())  # Will print (1,) if successful
except Exception as e:
    print("Failed to connect to database:", str(e))
    exit()  # Exit if connection fails

# Function to call stored procedure TinhTongSoTien
def tinh_tong_so_tien(ma_hoa_don):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("EXEC TinhTongSoTien :ma_hoa_don"), {"ma_hoa_don": ma_hoa_don}).fetchone()
            if result:
                messagebox.showinfo("Kết quả", f"TienPhong: {result.TienPhong}\nTienDichVu: {result.TienDichVu}\nTongTien: {result.TongTien}")
            else:
                messagebox.showwarning("Không có dữ liệu", f"Không có dữ liệu trả về cho MaHoaDon: {ma_hoa_don}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi gọi stored procedure TinhTongSoTien: {str(e)}")

# Function to call stored procedure DatPhong
def dat_phong(ma_khach_hang, ma_phong, ma_nhan_vien, vao_luc):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("EXEC DatPhong :ma_khach_hang, :ma_phong, :ma_nhan_vien, :vao_luc"), 
                                  {"ma_khach_hang": ma_khach_hang, "ma_phong": ma_phong, "ma_nhan_vien": ma_nhan_vien, "vao_luc": vao_luc}).fetchone()
            if result:
                messagebox.showinfo("Kết quả", f"MaHoaDon: {result.MaHoaDon}\nMessage: {result.Message}")
            else:
                messagebox.showwarning("Không có dữ liệu", "Không có dữ liệu trả về từ DatPhong.")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi gọi stored procedure DatPhong: {str(e)}")

# GUI setup
root = tk.Tk()
root.title("Quản Lý Tiệm Karaoke")

# TinhTongSoTien GUI
tk.Label(root, text="Tinh Tong So Tien").grid(row=0, column=0, columnspan=2, pady=10)
tk.Label(root, text="MaHoaDon").grid(row=1, column=0, padx=10, pady=5)
ma_hoa_don_entry = tk.Entry(root)
ma_hoa_don_entry.grid(row=1, column=1, padx=10, pady=5)

def call_tinh_tong_so_tien():
    ma_hoa_don = ma_hoa_don_entry.get()
    if ma_hoa_don:
        tinh_tong_so_tien(ma_hoa_don)
        ma_hoa_don_entry.delete(0, tk.END)  # Clear the entry after action
    else:
        messagebox.showwarning("Lỗi", "Vui lòng nhập MaHoaDon")

tk.Button(root, text="Tinh Tong So Tien", command=call_tinh_tong_so_tien).grid(row=2, column=0, columnspan=2, pady=10)

# DatPhong GUI
tk.Label(root, text="Dat Phong").grid(row=3, column=0, columnspan=2, pady=10)
tk.Label(root, text="MaKhachHang").grid(row=4, column=0, padx=10, pady=5)
ma_khach_hang_entry = tk.Entry(root)
ma_khach_hang_entry.grid(row=4, column=1, padx=10, pady=5)

tk.Label(root, text="MaPhong").grid(row=5, column=0, padx=10, pady=5)
ma_phong_entry = tk.Entry(root)
ma_phong_entry.grid(row=5, column=1, padx=10, pady=5)

tk.Label(root, text="MaNhanVien").grid(row=6, column=0, padx=10, pady=5)
ma_nhan_vien_entry = tk.Entry(root)
ma_nhan_vien_entry.grid(row=6, column=1, padx=10, pady=5)

tk.Label(root, text="VaoLuc (YYYY-MM-DD HH:MM:SS)").grid(row=7, column=0, padx=10, pady=5)
vao_luc_entry = tk.Entry(root)
vao_luc_entry.grid(row=7, column=1, padx=10, pady=5)

def call_dat_phong():
    ma_khach_hang = ma_khach_hang_entry.get()
    ma_phong = ma_phong_entry.get()
    ma_nhan_vien = ma_nhan_vien_entry.get()
    vao_luc = vao_luc_entry.get()
    if ma_khach_hang and ma_phong and ma_nhan_vien and vao_luc:
        dat_phong(ma_khach_hang, ma_phong, ma_nhan_vien, vao_luc)
        ma_khach_hang_entry.delete(0, tk.END)  # Clear the entries after action
        ma_phong_entry.delete(0, tk.END)
        ma_nhan_vien_entry.delete(0, tk.END)
        vao_luc_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin")

tk.Button(root, text="Dat Phong", command=call_dat_phong).grid(row=8, column=0, columnspan=2, pady=10)

# Run the GUI
root.mainloop()