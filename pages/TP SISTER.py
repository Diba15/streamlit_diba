import streamlit as st

tab2, tab3, tab4, tab5 = st.tabs(["TP2", "TP3", "TP4", "TP5"])

with tab2:
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

with tab3:
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

    st.write(
        "Setelah koneksi terbentuk, kedua ujung socket (baik server maupun klien) dapat mengirim dan menerima data "
        "melalui pemanggilan send() dan recv() atau fungsi serupa. Socket berada dalam status ESTABLISHED selama "
        "proses pertukaran data berlangsung.")

    st.subheader("Closing")

    st.write(
        "etelah pertukaran data selesai, salah satu atau kedua ujung socket dapat memutus koneksi dengan pemanggilan "
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

    st.write(
        "**HALO DEK!** merupakan sebuah aplikasi sederhana untuk keperluan chatting. Aplikasi **HALO DEK!** merupakan "
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

with tab4:
    import streamlit as st
    from PIL import Image

    st.title("TP MOD 4")

    st.write("**Nama : Dimas Bagas Saputro**")
    st.write("**NIM : 1301228515**")
    st.write("**Kelas : IFX-46-GAB**")

    st.header("Topik : Pengantar Remote Invocation")

    st.subheader("1. Ungkapkan secara lengkap bagaimana RPC bekerja!", divider="red")

    st.write(
        "Remote Procedure Call (RPC) adalah protokol komunikasi yang memfasilitasi pemanggilan fungsi atau prosedur "
        "di komputer yang berbeda atau dalam konteks yang berbeda. Proses dimulai ketika klien memanggil fungsi pada "
        "server, mengirim argumen yang harus diubah (marshalling) menjadi format yang dapat ditransmisikan melalui "
        "jaringan. Data dikirim melalui jaringan, dan di sisi server, data tersebut diubah kembali (unmarshalling) "
        "ke dalam bentuk yang dapat digunakan oleh server. Fungsi dijalankan di server, dan hasilnya dikirim kembali "
        "ke klien melalui proses serupa. RPC memastikan komunikasi transparan, sehingga pemanggilan fungsi jarak "
        "jauh terasa seperti pemanggilan lokal. Ini memungkinkan aplikasi berkomunikasi dengan komponen lain di "
        "mesin yang berbeda atau dalam bahasa pemrograman yang berbeda dengan mudah, membantu dalam pengembangan "
        "sistem yang terdistribusi.")

    st.subheader("2. Ungkapkan secara lengkap perbedaan RPC dan RMI!", divider="red")

    st.write(
        "Remote Procedure Call (RPC) dan Remote Method Invocation (RMI) adalah dua teknologi komunikasi jarak jauh "
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

with tab5:
    import streamlit as st
    from PIL import Image

    st.title("TP MOD 5")

    st.write("**Nama : Dimas Bagas Saputro**")
    st.write("**NIM : 1301228515**")
    st.write("**Kelas : IFX-46-GAB**")

    st.header("Topik : Pengantar Inderect Communication")

    st.subheader("1. Ungkapkan secara lengkap bagaimana indirect communication bekerja!", divider="red")

    st.write(
        "Indirect Communication, atau Komunikasi secara tidak langsung, beroperasi dengan memanfaatkan berbagai alat "
        "dan teknologi untuk mengirimkan pesan antara pengirim dan penerima tanpa perlu interaksi tatap muka "
        "langsung. Biasanya, pengirim menyusun pesan, yang kemudian diterjemahkan ke dalam format yang sesuai dengan "
        "media atau perantara yang dipilih. Media ini, yang bisa berupa panggilan telepon, email, pesan teks, "
        "atau platform media sosial, berperan sebagai perantara melalui mana pesan ditransmisikan. Penerima, "
        "yang berlokasi jauh, mengakses pesan melalui perangkat komunikasi mereka, mendekripsi atau "
        "menginterpretasikannya jika diperlukan, dan kemudian merespons atau mengambil tindakan yang sesuai. "
        "Komunikasi tidak langsung memungkinkan pertukaran informasi yang efisien dan jarak jauh, dan umumnya "
        "digunakan dalam metode komunikasi kontemporer, melewati hambatan fisik dan memungkinkan interaksi efektif "
        "dalam jarak jauh.")

    st.subheader("2. Ungkapkan deduksi Anda tentang protokol publish subscribe dan message queue !", divider="red")

    st.subheader("Protokol Publish-Subscribe")

    st.write("Protokol 'Publish-Subscribe' adalah paradigma komunikasi yang menghubungkan penerbit (publisher) dengan "
             "pelanggan (subscriber) melalui sebuah perantara (broker) yang bertindak sebagai penyedia layanan. Dalam "
             "sistem publish-subscribe, penerbit tidak perlu mengetahui identitas atau lokasi pelanggan, dan pelanggan "
             "tidak perlu mengetahui identitas penerbit.")

    st.subheader("Message Queue")

    st.write(
        "Message Queue adalah mekanisme yang digunakan untuk mengirim dan menerima pesan antara komponen perangkat "
        "lunak dalam sistem terdistribusi. ")

    st.write("Kedua protokol ini memiliki peran yang signifikan dalam dunia komputasi terdistribusi dan memungkinkan "
             "komunikasi yang efisien dan andal antara komponen perangkat lunak dalam sistem yang kompleks. Keputusan "
             "untuk menggunakan salah satu atau keduanya tergantung pada kebutuhan sistem dan kompleksitas komunikasi "
             "yang diinginkan.")

    st.header("Topik : MQTT Programming")

    st.write("Buatlah program sederhana menggunakan indirect communication publisher subscriber dengan spesifikasi "
             "sebagai berikut:")
    st.write(
        "1. Subscriber akan melakukan subscribe topik bernama 'info_waktu'. subsciber akan menampilkan (print) hasil "
        "waktu yang diterimanya.")
    st.write("2. Publisher akan mempublish topik 'info_waktu' yang merupakan waktu pada publisher (tahun, bulan, hari, "
             "jam, detik). publisher akan mempublish waktunya (tahun, bulan, hari, jam, detik) setiap 10 detik.")

    st.subheader("tp5.py")

    code_server = '''
    import paho.mqtt.client as mqtt
    import time
    import datetime


    def on_message(message):
        print('Info Waktu:', str(message.payload.decode("utf-8")))


    # alamat broker yang akan digunakan
    broker_address = "localhost"
    # buat client bernama P1
    print("creating new instance")
    client = mqtt.Client("P1")
    # pada client dikaitkan callback function
    client.on_message = on_message
    # client terkoneksi dengan broker
    print("connecting to broker")
    client.connect(broker_address, port=3333)

    # client P1 mulai
    client.loop_start()
    # client P1 subscribe ke topik "info_waktu"
    # P1 <- broker
    print("Subscribing to topic", "info_waktu")
    client.subscribe("info_waktu")
    # client P1 publish ke broker dengan topik "info_waktu"
    # P1 -> broker
    print("Publishing message to topic", "info_waktu")

    while True:
        # Dapatkan waktu saat ini
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Publish waktu ke topik "info_waktu"
        client.publish("info_waktu", current_time)
        print("Published message to topic 'info_waktu':", current_time)
        # Tunggu selama 10 detik sebelum mem-publish lagi
        time.sleep(10)


    '''

    st.code(code_server, language="python")

    server_img = Image.open("./image/tp5/result.png")

    st.image(server_img, "Result MQTT")

