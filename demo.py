print("hello")

my_string = "abcde"
new_string = my_string[::-1]
print(new_string)  # Output: edcba

print("Nhap so tu nhien: ")
n = int(input())
if(n%2==0):
    print("So", n , "la so chan")
else:
    print("So", n , "la so le")

my_string = "Hoang Le Giang"
new_string = my_string.split()
print(new_string)

def call_tinh_tong_so_tien():
    ma_hoa_don = ma_hoa_don_entry.get()
    if ma_hoa_don:
        tinh_tong_so_tien(ma_hoa_don)
        ma_hoa_don_entry.delete(0, tk.END)  # Clear the entry after action
    else:
        messagebox.showwarning("Lỗi", "Vui lòng nhập MaHoaDon")

tk.Button(root, text="Tinh Tong So Tien", command=call_tinh_tong_so_tien).grid(row=2, column=0, columnspan=2, pady=10)
