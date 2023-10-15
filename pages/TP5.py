import streamlit as st
from PIL import Image

st.title("TP MOD 5")

st.write("**Nama : Dimas Bagas Saputro**")
st.write("**NIM : 1301228515**")
st.write("**Kelas : IFX-46-GAB**")

st.header("Topik : Pengantar Inderect Communication")

st.subheader("1. Ungkapkan secara lengkap bagaimana indirect communication bekerja!", divider="red")

st.write("")

st.subheader("2. Ungkapkan deduksi Anda tentang protokol publish subscribe dan message queue !", divider="red")

st.subheader("Protokol Publish-Subscribe")

st.write("Protokol 'Publish-Subscribe' adalah paradigma komunikasi yang menghubungkan penerbit (publisher) dengan "
         "pelanggan (subscriber) melalui sebuah perantara (broker) yang bertindak sebagai penyedia layanan. Dalam "
         "sistem publish-subscribe, penerbit tidak perlu mengetahui identitas atau lokasi pelanggan, dan pelanggan "
         "tidak perlu mengetahui identitas penerbit.")

st.subheader("Message Queue")

st.write("Message Queue adalah mekanisme yang digunakan untuk mengirim dan menerima pesan antara komponen perangkat "
         "lunak dalam sistem terdistribusi. ")

st.write("Kedua protokol ini memiliki peran yang signifikan dalam dunia komputasi terdistribusi dan memungkinkan "
         "komunikasi yang efisien dan andal antara komponen perangkat lunak dalam sistem yang kompleks. Keputusan "
         "untuk menggunakan salah satu atau keduanya tergantung pada kebutuhan sistem dan kompleksitas komunikasi "
         "yang diinginkan.")

st.header("Topik : MQTT Programming")

st.write("Buatlah program sederhana menggunakan indirect communication publisher subscriber dengan spesifikasi "
         "sebagai berikut:")
st.write("1. Subscriber akan melakukan subscribe topik bernama 'info_waktu'. subsciber akan menampilkan (print) hasil "
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
