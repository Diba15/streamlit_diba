import streamlit as st
from PIL import Image

st.title("TP MOD 4")

st.write("**Nama : Dimas Bagas Saputro**")
st.write("**NIM : 1301228515**")
st.write("**Kelas : IFX-46-GAB**")

st.header("Topik : Pengantar Remote Invocation")

st.subheader("1. Ungkapkan secara lengkap bagaimana RPC bekerja!", divider="red")

st.write("Remote Procedure Call (RPC) adalah protokol komunikasi yang memfasilitasi pemanggilan fungsi atau prosedur "
         "di komputer yang berbeda atau dalam konteks yang berbeda. Proses dimulai ketika klien memanggil fungsi pada "
         "server, mengirim argumen yang harus diubah (marshalling) menjadi format yang dapat ditransmisikan melalui "
         "jaringan. Data dikirim melalui jaringan, dan di sisi server, data tersebut diubah kembali (unmarshalling) "
         "ke dalam bentuk yang dapat digunakan oleh server. Fungsi dijalankan di server, dan hasilnya dikirim kembali "
         "ke klien melalui proses serupa. RPC memastikan komunikasi transparan, sehingga pemanggilan fungsi jarak "
         "jauh terasa seperti pemanggilan lokal. Ini memungkinkan aplikasi berkomunikasi dengan komponen lain di "
         "mesin yang berbeda atau dalam bahasa pemrograman yang berbeda dengan mudah, membantu dalam pengembangan "
         "sistem yang terdistribusi.")

st.subheader("2. Ungkapkan secara lengkap perbedaan RPC dan RMI!", divider="red")

st.write("Remote Procedure Call (RPC) dan Remote Method Invocation (RMI) adalah dua teknologi komunikasi jarak jauh "
         "yang memungkinkan aplikasi untuk berinteraksi melintasi jaringan. Perbedaan utama adalah bahwa RPC bersifat "
         "lebih umum, tidak terbatas pada bahasa pemrograman atau tipe data tertentu, dan menggunakan representasi "
         "data umum seperti XML atau JSON, sedangkan RMI khusus untuk bahasa pemrograman Java, memungkinkan "
         "pemanggilan metode objek Java melalui serialisasi objek Java bawaan dalam konteks JVM. RPC juga memiliki "
         "fleksibilitas lebih besar dalam pemilihan protokol komunikasi, sementara RMI biasanya menggunakan JRMP.")

st.header("Topik : RPC Programming")

st.write("Buatlah aplikasi voting sederhana menggunakan RPC, dengan ketentuan sebagai berikut:")
st.write("a. Server mampu:")
st.write("i. Menerima permintaan vote dari user.")
st.write("ii. Menyimpan jumlah perolehan hasil pemilihan pada masing-masing calon.")
st.write("b. Client mampu:")
st.write("i. Menampilkan list calon yang ada")
st.write("ii. Memilih calon yang ada.")

st.subheader("server_rpc.py")

code_server = '''
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


with SimpleXMLRPCServer(("localhost", 9000), requestHandler=RequestHandler) as server:
    server.register_introspection_functions()

    dimas = 0
    kelvin = 0
    riko = 0

    # server.register_function(sum)

    def poll_func(y):
        global dimas, kelvin, riko
        if y == 1:
            dimas = dimas + 1
            return 0
        elif y == 2:
            kelvin = kelvin + 1
            return 0
        elif y == 3:
            riko = riko + 1
            return 0
        else:
            return 0


    server.register_function(poll_func, "poll")


    def show_poll():
        return f"Poll Pemilihan Saat ini: Dimas: {dimas} Kelvin: {kelvin} Riko: {riko}"


    server.register_function(show_poll, "show_poll")
    server.serve_forever()

'''

st.code(code_server, language="python")

server_img = Image.open("./image/server_rpc.png")

st.image(server_img, "Result Server RPC")

st.subheader("client_rpc.py")

code_client = '''
# Client Side
# import library xmlrpc client karena akan digunakan rpc
import xmlrpc.client

# buat stub/skeleton (proxy) pada client
s = xmlrpc.client.ServerProxy('http://localhost:9000')

# Munculkan Masing-masing Calon
print("Calon Ketua Kelas: 1. Dimas Bagas Saputro 2. Kelvin Pradiza Lazuardy 3. M Riko Trisaputra")
pilih = int(input("Pilih Calon: "))

s.poll(pilih)

print(s.show_poll())

'''

st.code(code_client, language="python")

client_img = Image.open("./image/client_rpc.png")

st.image(client_img, "Result Client RPC")
