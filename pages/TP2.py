import streamlit as st

st.title("TP MOD 2")

st.write("**Nama : Dimas Bagas Saputro**")
st.write("**NIM : 1301228515**")
st.write("**Kelas : IFX-46-GAB**")

st.header("Topik : Pengantar Python")

st.subheader("1. Kapan python dibuat dan siapa penemunya?")

st.write(
    "**Seorang pemrogram komputer asal Belanda bernama Guido Van Rossum menciptakan Python dan dibuat pada akhir "
    "tahun 1980, Guido Van Rossum mempublikasikan versi 0.9.0 Python pada tahun  1991.**")

st.subheader("2. Apa perbedaan Python 2 dan Python 3?")

st.write("**Python 2 dan Python 3 adalah dua versi utama dari bahasa pemrograman Python, dan keduanya memiliki "
         "perbedaan yang signifikan. Salah satu perbedaan terbesar adalah cara penanganan print, di mana Python 2 "
         "menggunakan pernyataan print tanpa tanda kurung, sedangkan Python 3 menggunakan fungsi print() dengan tanda "
         "kurung. Selain itu, Python 2 menghasilkan hasil pembagian bulat jika membagi dua bilangan bulat, "
         "sedangkan Python 3 menghasilkan hasil pembagian desimal. Perubahan penting lainnya melibatkan penanganan "
         "string dan Unicode, dengan Python 3 yang lebih konsisten dalam mendukung Unicode dan menggunakan UTF-8 "
         "sebagai encoding default. Selain itu, Python 3 menghapus beberapa fitur yang dianggap usang, "
         "seperti xrange() yang digantikan oleh range() yang lebih efisien.**")

st.header("Topik : Pemrograman Python")


def tambah(x, y):
    st.write("Hasil Pertambahan: ", x + y)


def kurang(x, y):
    st.write("Hasil Pengurangan: ", x - y)


def kali(x, y):
    st.write("Hasil Perkalian: ", x * y)


def bagi(x, y):
    st.write("Hasil Pembagian: ", x / y)


code = '''
def tambah(x, y):
    print("Hasil Pertambahan: ", x + y)


def kurang(x, y):
    print("Hasil Pengurangan: ", x - y)


def kali(x, y):
    print("Hasil Perkalian: ", x * y)


def bagi(x, y):
    print("Hasil Pembagian: ", x / y)


def calculator():
    print("Kalkulator Sederhana")
    print("=================================")
    print(f"{'Nama':<{5}}", ":", "Dimas Bagas Saputro")
    print(f"{'NIM':<{5}}", ":", "1301228515")
    print(f"{'Kelas':<{4}}", ":", "IFX-46-GAB")
    print("=================================")
    x = int(input("Masukkan Variable Pertama: "))
    y = int(input("Masukkan Variable Kedua: "))
    print("=================================")
    print("Operasi")
    print("1. Tambah")
    print("2. Kurang")
    print("3. Kali")
    print("4. Bagi")
    operasi = input("Pilih Operasi: ")
    if operasi == "1":
        tambah(x, y)
    elif operasi == "2":
        kurang(x, y)
    elif operasi == "3":
        kali(x, y)
    elif operasi == "4":
        bagi(x, y)


if __name__ == '__main__':
    calculator()
'''

st.code(code, language='python')

with st.form(key="form_variable"):
    x = st.number_input("Masukkan Variable Pertama", value=None)
    y = st.number_input("Masukkan Variable Kedua", value=None)
    operasi = st.selectbox('Pilih Operasi', ('Tambah', 'Kurang', 'Kali', 'Bagi'))
    submit = st.form_submit_button("Submit")

    if submit:
        if operasi == 'Tambah':
            tambah(x, y)
        elif operasi == 'Kurang':
            kurang(x, y)
        elif operasi == 'Kali':
            kali(x, y)
        elif operasi == 'Bagi':
            bagi(x, y)
