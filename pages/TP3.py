import streamlit as st
from PIL import Image

st.title("TP MOD 3")

st.write("**Nama : Dimas Bagas Saputro**")
st.write("**NIM : 1301228515**")
st.write("**Kelas : IFX-46-GAB**")

st.header("Topik : Pengantar Socket")

st.subheader("1. Ungkapkan secara lengkap lifecycle TCP Socket!", divider="red")

tcp = Image.open('./image/tcp_lifecycle.png')

st.image(tcp, caption="TCP Lifecycle")

st.subheader("Creation")

st.write("Proses dimulai dengan membuat socket menggunakan pemanggilan sistem operasi seperti socket().")

st.subheader("Binding")

st.write("Socket server harus mengikat socket ke alamat dan port tertentu dengan memanggil bind().")

st.subheader("Listening")

st.write("Socket server yang sudah diikat akan memanggil listen() untuk memulai mendengarkan koneksi masuk. Socket "
         "server sekarang berada dalam status LISTEN dan siap untuk menerima koneksi baru.")

st.subheader("Accepting")

st.write("Ketika koneksi masuk terdeteksi, socket server akan memanggil accept() untuk menerima koneksi tersebut. "
         "Socket baru yang disebut 'socket anak' akan dibuat untuk mengelola komunikasi dengan klien. Socket anak ini "
         "akan berada dalam status ESTABLISHED, sementara socket server tetap dalam status LISTEN.")

st.subheader("Data Transfer")

st.write("Setelah koneksi terbentuk, kedua ujung socket (baik server maupun klien) dapat mengirim dan menerima data "
         "melalui pemanggilan send() dan recv() atau fungsi serupa. Socket berada dalam status ESTABLISHED selama "
         "proses pertukaran data berlangsung.")

st.subheader("Closing")

st.write("etelah pertukaran data selesai, salah satu atau kedua ujung socket dapat memutus koneksi dengan pemanggilan "
         "close(). Jika salah satu ujung mengirimkan pesan penutupan (FIN), socket akan memasuki fase FIN_WAIT dan "
         "CLOSE_WAIT bergantung pada sisi mana yang mengirimkan pesan penutupan. Setelah kedua sisi menutup koneksi "
         "dan menerima pesan penutupan dari sisi lain, socket akan berpindah ke status CLOSED.")

st.subheader("2. Ungkapkan secara lengkap lifecycle UDP Socket!", divider="red")

udp = Image.open('./image/udp_lifecycle.png')

st.image(udp, caption="UDP Lifecycle")

st.subheader("Creation")

st.write("Proses dimulai dengan membuat socket UDP menggunakan pemanggilan sistem operasi seperti socket().")

st.subheader("Binding")

st.write("Socket UDP dapat diikat ke alamat dan port tertentu dengan pemanggilan bind().")

st.subheader("Data Transfer")

st.write("Socket UDP dapat mengirim dan menerima datagram (pakets) menggunakan pemanggilan sendto() dan recvfrom() "
         "atau fungsi serupa.")

st.subheader("Closing")

st.write("UDP tidak memiliki pesan penutupan seperti TCP. Aplikasi dapat memilih untuk menghentikan socket UDP dan "
         "melepaskannya dengan memanggil close() atau fungsi serupa jika diperlukan. Namun, dalam banyak kasus, "
         "socket UDP dibiarkan terbuka untuk menerima dan mengirim datagram kapan saja selama aplikasi berjalan.")

st.header("Topik : Pemrograman Socket")

st.write("**HALO DEK!** merupakan sebuah aplikasi sederhana untuk keperluan chatting. Aplikasi **HALO DEK!** merupakan "
         "aplikasi yang populer dan banyak digunakan untuk berkomunikasi. Aplikasi **HALO DEK!** memungkinkan pengguna "
         "untuk berkomunikasi secara langsung dengan mudah. Anda telah mempelajari dan mengimplementasikan kode "
         "socket di kelas. Sekarang, Anda diharapkan membuat aplikasi sederhana chatting sederhana tersebut "
         "menggunakan socket. Berikut adalah ketentuan pembuatan aplikasi **HALO DEK!**.")

halo = Image.open("./image/halo_dek.png")

st.image(halo, "Example of how HALO DEK! apps work")

st.subheader("TCP", divider="red")

st.subheader("Server.py")

code_server = '''
import socket

TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024
s = socket.socket(socket.AF_INET,  # Internet
                  socket.SOCK_STREAM)  # TCP
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

print("Server Halo DEK Sedang Berjalan...")

while 1:
    conn, addr = s.accept()
    print("Alamat: ", addr)
    data = conn.recv(BUFFER_SIZE)
    print("Client Halo DEK! : ", data.decode())
    conn.send(data)

conn.close()
'''

st.code(code_server, language="python")

code_client = '''
import socket

TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024
PESAN = input("Masukkan Pesan : ")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP
s.connect((TCP_IP, TCP_PORT))
s.send(PESAN.encode())
data = s.recv(BUFFER_SIZE)
s.close()
print("data diterima : ", data.decode())
'''
st.subheader("client.py")

st.code(code_client, language="python")

st.subheader("UDP", divider="red")

st.subheader("Server.py")

code_server = '''
import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP

sock.bind((UDP_IP, UDP_PORT))

print("Server Halo DEK Sedang Berjalan...")

while True:
    data, addr = sock.recvfrom(1024)
    print(addr)
    print("Client Halo Dek! : ", data.decode())
'''

st.code(code_server, language="python")

code_client = '''
import socket

UDP_IP = '127.0.0.1'
UDP_PORT = 5005

PESAN = input("Masukkan Pesan : ")
print("target IP : ", UDP_IP)
print("target port:", UDP_PORT)
print("pesan : ", PESAN)
sock = socket.socket(socket.AF_INET, #Internet
 socket.SOCK_DGRAM) #UDP
sock.sendto(PESAN.encode (), (UDP_IP, UDP_PORT))

'''
st.subheader("client.py")

st.code(code_client, language="python")
