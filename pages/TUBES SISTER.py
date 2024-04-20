import streamlit as st
from PIL import Image
import paho.mqtt.client as mqtt
import time
import datetime


def on_message(client, userdata, message):
    print('Info Waktu:', str(message.payload.decode("utf-8")))


st.title('TUBES SISTER Laundry')

st.write(
    "Membuat program agar Laundry Bojong dan Laundry Soang dapat mengirim dan menerima pesanan laundry dari banyak "
    "client. Kedua laundry tersebut akan mengirimkan informasi ke client kapan penjemputan baju kotor dan kapan "
    "perkiraan pengantaran baju hasil laundry. Client harus follow laundry terlebih dahulu agar mendapatkan informasi "
    "dari laundry tersebut.Client dapat melihat laundry mana yang memberikan waktu selesai laundry paling cepat, "
    "kemudian memilih akan memesan ke laundry yang mana. Setiap laundry hanya mengirimkan kepada client pelanggan "
    "saja, dan client hanya dapat menerima informasi dari laundry yang di-follow saja.")

st.write("Broker Address : 0.tcp.ap.ngrok.io")
st.write("Port : 19536")

# alamat broker yang akan digunakan
broker_address = "0.tcp.ap.ngrok.io"
# buat client bernama P1
print("creating new instance")
client = mqtt.Client("Musrik")
# pada client dikaitkan callback function
client.on_message = on_message
# client terkoneksi dengan broker
print("connecting to broker")
client.connect(broker_address, port=19536)
# client P1 mulai
client.loop_start()
# client P1 subscribe ke topik "info_waktu" # P1 <- broker
# print("""
#         ====================[M E N U]====================
#         Pilih Laundry yang ingin digunakan
#         1. Laundry Bojong
#         2. Laundry Soang
#         =================================================
#         """)
# inputUser = input('Masukkan pilihan: ')

pilihan_laundry = st.selectbox("Pilih Laundry", ["Pilih Laundry","Laundry Bojong", "Laundry Soang"])

if pilihan_laundry == "Laundry Bojong":
    st.write("Mengikuti Laundry", "Bojong")
    client.subscribe("bojong")
elif pilihan_laundry == "Laundry Soang":
    st.write("Mengikuti Laundry", "Soang")
    client.subscribe("soang")

client.loop_stop()

# Dapatkan waktu saat ini
current_time = datetime.datetime.now()

if pilihan_laundry == 'Laundry Bojong':
    client.publish("waktu_penjemputan", current_time.strftime("%Y-%m-%d %H:%M:%S"))
    st.write("Pengambilan Baju di Laundry Bojong pada waktu:", current_time.strftime("%Y-%m-%d %H:%M:%S"))
    client.publish("waktu_pengantaran", (current_time + datetime.timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"))
    time.sleep(5)
    st.write("Pengantaran Baju di Laundry Bojong pada waktu:",
          (current_time + datetime.timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"))
elif pilihan_laundry == 'Laundry Soang':
    client.publish("waktu_penjemputan", current_time.strftime("%Y-%m-%d %H:%M:%S"))
    st.write("Pengambilan Baju di Laundry Soang pada waktu:", current_time.strftime("%Y-%m-%d %H:%M:%S"))
    time.sleep(5)
    client.publish("waktu_pengantaran", (current_time + datetime.timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"))
    st.write("Pengantaran Baju di Laundry Soang pada waktu:",
          (current_time + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
