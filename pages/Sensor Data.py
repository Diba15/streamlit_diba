import io
from time import time

import firebase_admin
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st
import streamlit.components.v1 as components
from firebase_admin import db
from keras.callbacks import ReduceLROnPlateau, EarlyStopping
from keras.layers import Dense, LSTM, BatchNormalization, Bidirectional, Dropout
from keras.models import Sequential
from keras.optimizers import Adam
from keras.regularizers import l2
from keras.utils import to_categorical
from matplotlib.ticker import FormatStrFormatter
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(page_title='Tugas Skripsi', layout='wide')

st.title("WP6003 Air Box Reader")

st.header("VSON WP6003 Bluetooth APP Air Quality Detector for PM Formaldehyde TVOC")

st.write("Tujuan dari penelitian ini adalah membangun sistem untuk mengetahui Indeks Kualitas Udara Dalam Ruangan ("
         "IAQI) menggunakan sensor yang mendeteksi TVOC, eCO2, dan CO2. Metode Long Short Term Memory (LSTM) akan "
         "digunakan untuk melatih dan memperkirakan Indeks Kualitas Udara dalam urutan data (seri waktu).")


def read_data():
    html_string = """
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4" crossorigin="anonymous"></script>
        <fieldset>
          <legend>Read data:</legend>
          <hr>
          <div class="form-check">
              <input class="form-check-input" type="radio" name="flexRadioDefault" id="existing_data">
              <label class="form-check-label" for="existing_data">
                Add Existing Data
              </label>
            </div>
            <div class="form-check">
              <input class="form-check-input" type="radio" name="flexRadioDefault" id="new_data">
              <label class="form-check-label" for="new_data">
                Add New Data
              </label>
            </div>
          <div id="form"></div>
          <button class="btn btn-light" onclick="enableNotifications()">Enable notifications</button></br>
          <button class="btn btn-light" onclick="readData()">Read sensor data</button></br>
          <button class="btn btn-light" onclick="sendCommand()">Send command</button></br>
          <input type="checkbox" id="autoRefresh" name="autoRefresh" onclick="autoRefresh()">
          <label for="autoRefresh">Auto refresh values (30s)</label>
        </fieldset>
        
        
        <fieldset>
          <legend>Sensor calibration:</legend>
          <hr>
          <div style="font-size: 14px">
          Before sensor calibration procedure please follow these instructions:
          <ol>
            <li>Take the device to a place with fresh air (such as balcony, outdoor);
            <li>Keep the device runnin for more than 10 minutes; then take it indoor
          </ol>
          </div>
          <button class="btn btn-light" onclick="calibrate()">Calibrate</button>
        </fieldset>

        <fieldset>
          <legend>Console:</legend>
          <hr>
          Info: <span id="info"></span> <br>
          Time: <span id="waktu"></span> <br>
          Temp: <span id="temperature"></span> <br>
          TVOC: <span id="tvocs"></span> <br>
          HCHO: <span id="hchos"></span> <br>
          CO2: <span id="co2s"></span>
        </fieldset>

        <script language='javascript'>

            const SENSOR_SERVICE = '0000fff0-0000-1000-8000-00805f9b34fb';
            const SENSOR_WRITE   = '0000fff1-0000-1000-8000-00805f9b34fb';
            const SENSOR_READ    = '0000fff4-0000-1000-8000-00805f9b34fb';

            var service;
            var readChar;
            var writeChar;
            var autoRefreshInterval;
            let waktu = document.getElementById('waktu');
            let tempe = document.getElementById('temperature');
            let tvocs = document.getElementById('tvocs');
            let hchos = document.getElementById('hchos');
            let co2s = document.getElementById('co2s');


            async function initConnection() {
              if(service != null) 
                return;

              try {
                service = await getService(SENSOR_SERVICE);

                writeChar = await service.getCharacteristic(SENSOR_WRITE);
                readChar = await service.getCharacteristic(SENSOR_READ);
              } catch(error) {
                console.error(error);
                logInfo('BT connection error. Please retry or refresh the browser.');
              }
            }

            async function enableNotifications() {
              await initConnection();

              logInfo('Enabling notifications');
              await readChar.startNotifications();
              readChar.addEventListener('characteristicvaluechanged', handleNotifications);

              logInfo('Waiting on data... may take some time on a first read');
            }

            async function readData() {
              await initConnection();

              await writeChar.writeValue(Uint8Array.of(0xAB));
            }

            async function sendCommand() {
              await initConnection();

              let command = prompt('Enter a command in HEX');

              await writeChar.writeValue(fromHexString(command));
            }

            async function calibrate() {
              await initConnection();

              await writeChar.writeValue(Uint8Array.of(0xAD));
              logInfo('Calibration started');
            }

            function autoRefresh() {
              if(autoRefreshInterval) {
                clearTimeout(autoRefreshInterval);
                logInfo('Auto refresh disabled');
              } else {
                autoRefreshInterval = setInterval(() => readData(), 30000);
                logInfo('Auto refresh enabled');
                readData();
              }
            }


            function handleNotifications(event) {
              let value = event.target.value;

              console.log(value);
              console.log(toHexString(value));

              let notificationType  = value.getUint8(0);

              switch(notificationType) {
                case 0x0a:
                case 0x0b:
                  logSensorData(value);
                  break;
                default:
                  // nothing to decode
              }
            }

            function logSensorData(value) {
              try {
                let time = new Date().toLocaleString();
                let temp  = value.getInt16(6) / 10.0;
                let tvoc  = value.getUint16(10) /1000.0;
                let hcho  = value.getUint16(12) /1000.0;
                let co2   = value.getUint16(16);

                log(time, temp, tvoc, hcho, co2);


              } catch(error) {
                console.error(error);
                logInfo('Value parsing failed!');
              }
            }

            async function getService(service) {
              if (!('bluetooth' in navigator)) {
                throw 'Bluetooth API not supported.';
              }

              let options = {
                acceptAllDevices: true,
                optionalServices: [service]
              };

              return navigator.bluetooth.requestDevice(options)
                .then(function (device) {
                logInfo('Connecting...')
                  return device.gatt.connect();
                })
                .then(function (server) {
                logInfo('Getting primary service...')
                  return server.getPrimaryService(service);
                });
            }

            function log(time, temp, tvoc, hcho, co2) {

                waktu.innerHTML = time;
                tempe.innerHTML = temp;
                tvocs.innerHTML = tvoc;
                hchos.innerHTML = hcho;
                co2s.innerHTML = co2;

                addData(time, temp, tvoc, hcho, co2);
            }

            function logInfo(message) {
              let element = document.getElementById('info');
              console.log(message);
              element.innerHTML = message;
            }

            function fromHexString(hexString) {
              if(hexString.length === 0 || hexString.length % 2 !== 0){
                throw new Error(`The string "${hexString}" is not valid hex.`)
              }
              return new Uint8Array(hexString.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
            }

            function toHexString(data) {
              let bytes = data;
              if(data instanceof DataView) {
                bytes = new Uint8Array(data.buffer);
              }
              return bytes.reduce((str, byte) => str + byte.toString(16).padStart(2, '0'), '');
            }

        </script>

        <script type="module">
          // Import the functions you need from the SDKs you need
          import { initializeApp } from "https://www.gstatic.com/firebasejs/10.11.1/firebase-app.js";
          import { getDatabase, ref, child, get, set, update, remove, push } from "https://www.gstatic.com/firebasejs/10.11.1/firebase-database.js";
          // TODO: Add SDKs for Firebase products that you want to use
          // https://firebase.google.com/docs/web/setup#available-libraries

          // Your web app's Firebase configuration
          const firebaseConfig = {
            apiKey: "AIzaSyDHx0LjujHKX2M_isSr3O2t04W3lZdVVjY",
            authDomain: "test-py-37ef5.firebaseapp.com",
            databaseURL: "https://test-py-37ef5-default-rtdb.firebaseio.com",
            projectId: "test-py-37ef5",
            storageBucket: "test-py-37ef5.appspot.com",
            messagingSenderId: "705120805249",
            appId: "1:705120805249:web:9c94e903243b4a4d2e8880"
          };

          // Initialize Firebase
          const app = initializeApp(firebaseConfig);
          const database = getDatabase(app);
          console.log(database);
          const test = ref(database, 'data');
          
          document.getElementById('existing_data').addEventListener('click', function() {
                document.getElementById('form').innerHTML = `
                        <select class="form-select" aria-label="Default select example" id="select_room">
                          <option selected>Select Room Name</option>
                          
                        </select>
                    `;
                    
                var room = document.getElementById('select_room');
                    
                get(test).then((snapshot) => {
                    if (snapshot.exists()) {
                        snapshot.forEach((childSnapshot) => {
                            var option = document.createElement('option');
                            option.text = childSnapshot.key;
                            option.value = childSnapshot.key;
                            room.appendChild(option);
                        });
                    }
              });
            });
            
            document.getElementById('new_data').addEventListener('click', function() {
                document.getElementById('form').innerHTML = `
                        <div class="mb-3">
                            <input class="form-control" id="new_room" type="text" placeholder="Enter Room Name" 
                            pattern="[A-Za-z0-9]+" onkeydown="if(['Space'].includes(arguments[0].code)){return false;}"/>
                        </div>
                    `;
            });
          
          

          function addData(time, temperature, tvocs, hcho, co2) {
            var existingData = document.getElementById('existing_data');
            var newData = document.getElementById('new_data');
            var room = document.getElementById('select_room');
            var new_room = document.getElementById('new_room');
            
            
            if(existingData.checked == true) {
                console.log('masuk boss');
                push(ref(database, 'data/' + room.value + '/'), {
                    time: time,
                    temperature: temperature,
                    tvoc: tvocs,
                    hcho: hcho,
                    co2: co2
                })
                .then(() => {
                    console.log('Success Add');
                })
                .catch((error) => {
                    console.log('Error Add');
                });
            } else {
                console.log('masuk gass')
                push(ref(database, 'data/' + new_room.value + '/'), {
                    time: time,
                    temperature: temperature,
                    tvoc: tvocs,
                    hcho: hcho,
                    co2: co2
                })
                .then(() => {
                    console.log('Success Add');
                })
                .catch((error) => {
                    console.log('Error Add');
                });
            }
          }

          window.addData = addData;
        </script>

        <style>
        html{
            height: 900px;
        }
        body {
          margin: 0 auto;
          color: white;
          font-family: Lato,'Helvetica Neue',Arial,Helvetica,sans-serif;
          background: none;
        }
        fieldset > * {
          margin: 5px;
        }
        </style>

        """

    components.html(html_string, width=None, height=900)


def data_sensor():
    cred_obj = firebase_admin.credentials.Certificate('test-py-37ef5-firebase-adminsdk-guf7y-092601c707.json')
    # default_app = firebase_admin.initialize_app(cred_obj, {
    #     'databaseURL': 'https://test-py-37ef5-default-rtdb.firebaseio.com'
    # })

    if firebase_admin._DEFAULT_APP_NAME in firebase_admin._apps:
        app = firebase_admin.get_app(name='[DEFAULT]')
    else:
        app = firebase_admin.initialize_app(cred_obj, {
            'databaseURL': 'https://test-py-37ef5-default-rtdb.firebaseio.com'
        })

    ref = db.reference("/data")

    data_ref = ref.get()

    # features = ["time", "temperature", "tvoc", "hcho", "co2"]

    st.title("Read Data from Firebase")

    option = st.selectbox("Select Room", list(data_ref.keys()))

    ref = db.reference("/data/" + option + "/")

    data_ref = ref.get()

    def reset_data():
        #     truncate_reference_data("data")
        ref.delete()

    st.button("Reset Data", on_click=reset_data)

    df = pd.DataFrame(data_ref.values())

    pd.to_datetime(df['time']).apply(lambda x: x.date())

    df.set_index('time', inplace=True)

    st.dataframe(df,
                 column_config={
                     "time": st.column_config.Column(
                         width="medium",
                     ),
                     "temperature": st.column_config.Column(
                         width="small",
                     ),
                     "hcho": st.column_config.Column(
                         width="medium",
                     ),
                     "tvoc": st.column_config.Column(
                         width="medium",
                     )
                 })

    st.header("Data Summary")

    st.write(df.describe())

    st.header("Data Missing Value")

    st.write(df.isna().sum())

    st.header("Data Correlation")
    #
    st.write(df.corr())

    st.header("Data Visualization")

    st.line_chart(df[["temperature", "tvoc", "hcho", "co2"]])

    st.bar_chart(df[["temperature", "tvoc", "hcho", "co2"]])

    st.area_chart(df[["temperature", "tvoc", "hcho", "co2"]])

    st.subheader("Time Series Visualization")

    plt.style.use('fivethirtyeight')
    df.plot(subplots=True,
            layout=(6, 3),
            figsize=(22, 22),
            fontsize=10,
            linewidth=2,
            sharex=False,
            title='Visualization of the original Time Series')

    st.pyplot(plt.gcf())
    st.subheader("Correlation Matrix")

    corr_matrix = df.corr(method='spearman')
    f, ax = plt.subplots(figsize=(16, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', linewidth=0.4,
                annot_kws={"size": 10}, cmap='coolwarm', ax=ax)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)

    st.pyplot(f)

    #     Filtered Data
    st.header("Filtered Data")

    st.write("Image Source: https://i-qlair.com/indoor-air-quality-monitoring-complete-guide/")
    st.image("./image/iaqi_metric.png")

    #     Filter just CO2 and TVOC
    df_filtered = df[["co2", "tvoc", "temperature"]]

    st.dataframe(df_filtered)

    #     Make a IAQI Calculation for CO2 and TVOC
    st.header("IAQI Calculation")

    def calculate_iaqi(co2, tvoc):

        if 0 <= co2 <= 500:
            iaqi_co2 = ((50 - 0) / (500 - 0)) * (co2 - 0) + 0
        elif 500 < co2 <= 1000:
            iaqi_co2 = ((100 - 51) / (1000 - 501)) * (co2 - 501) + 51
        elif 1000 < co2 <= 2000:
            iaqi_co2 = ((150 - 101) / (2000 - 1001)) * (co2 - 1001) + 101
        elif 2000 < co2 <= 5000:
            iaqi_co2 = ((200 - 151) / (5000 - 2001)) * (co2 - 2001) + 151
        elif 5000 < co2 <= 10000:
            iaqi_co2 = ((300 - 201) / (10000 - 5001)) * (co2 - 5001) + 201
        elif 10000 < co2 <= 15000:
            iaqi_co2 = ((400 - 301) / (15000 - 10001)) * (co2 - 10001) + 301
        else:
            iaqi_co2 = 1000

        if 0 <= tvoc <= 0.6:
            iaqi_tvoc = ((50 - 0) / (0.6 - 0)) * (tvoc - 0) + 0
        elif 0.6 < tvoc <= 1.0:
            iaqi_tvoc = ((100 - 51) / (1.0 - 0.6)) * (tvoc - 0.6) + 51
        elif 1.0 < tvoc <= 2.0:
            iaqi_tvoc = ((150 - 101) / (2.0 - 1.0)) * (tvoc - 1.0) + 101
        elif 2.0 < tvoc <= 3.0:
            iaqi_tvoc = ((200 - 151) / (3.0 - 2.0)) * (tvoc - 2.0) + 151
        elif 3.0 < tvoc <= 5.0:
            iaqi_tvoc = ((300 - 201) / (5.0 - 3.0)) * (tvoc - 3.0) + 201
        elif 5.0 < tvoc <= 10.0:
            iaqi_tvoc = ((400 - 301) / (10.0 - 5.0)) * (tvoc - 5.0) + 301
        elif 10.0 < tvoc <= 20.0:
            iaqi_tvoc = ((500 - 401) / (20.0 - 10.0)) * (tvoc - 10.0) + 401
        elif 20.0 < tvoc <= 30.0:
            iaqi_tvoc = ((600 - 501) / (30.0 - 20.0)) * (tvoc - 20.0) + 501
        elif 30.0 < tvoc <= 40.0:
            iaqi_tvoc = ((700 - 601) / (40.0 - 30.0)) * (tvoc - 30.0) + 601
        elif 40.0 < tvoc <= 50.0:
            iaqi_tvoc = ((800 - 701) / (50.0 - 40.0)) * (tvoc - 40.0) + 701
        elif 50.0 < tvoc <= 100.0:
            iaqi_tvoc = ((900 - 801) / (100.0 - 50.0)) * (tvoc - 50.0) + 801
        else:
            iaqi_tvoc = 1000

        return iaqi_co2, iaqi_tvoc

    st.write("Rumus yang terkandung dalam fungsi calculate_iaqi adalah sebagai berikut:")
    st.latex(r'IAQI_{CO2} = \frac{I_{H} - I_{L}}{C_{H} - C_{L}} \times (CO2 - C_{L}) + I_{L}')
    st.latex(r'IAQI_{TVOC} = \frac{I_{H} - I_{L}}{C_{H} - C_{L}} \times (TVOC - C_{L}) + I_{L}')

    # Reference of the formula
    st.link_button("Reference: Atmotube.com",
                   "https://atmotube.com/atmocube-support/indoor-air-quality-index-iaqi#:~:text=To"
                   "%20calculate%20the%20AQI%2C%20the%20EPA%20measured%20outdoor,"
                   "individual%20index%20based%20on%20the%20EPA%E2%80%99s%20breakpoint%20table.")

    st.write("Parameter yang terdapat dalam rumus di atas adalah sebagai berikut:")
    st.write("IAQI = Indeks Kualitas Udara (Air Quality Index)")
    st.write("CO2 = Konsentrasi CO2 dalam udara")
    st.write("TVOC = Konsentrasi TVOC dalam udara")
    st.write("I_H = Nilai IAQI tertinggi dalam rentang konsentrasi CO2 atau TVOC")
    st.write("I_L = Nilai IAQI terendah dalam rentang konsentrasi CO2 atau TVOC")
    st.write("C_H = Konsentrasi CO2 atau TVOC tertinggi dalam rentang konsentrasi CO2 atau TVOC")
    st.write("C_L = Konsentrasi CO2 atau TVOC terendah dalam rentang konsentrasi CO2 atau TVOC")

    df_filtered["iaqi_co2"], df_filtered["iaqi_tvoc"] = zip(
        *df_filtered.apply(lambda x: calculate_iaqi(x["co2"], x["tvoc"]), axis=1))

    # After IAQI Calculation make a new column that show category of IAQI Score of Good, Moderate, and Hazardous

    def iaqi_category(iaqi):
        if 0 <= iaqi <= 50:
            return 1
        elif 51 <= iaqi <= 100:
            return 2
        else:
            return 3

    df_filtered["iaqi_category_co2"] = df_filtered["iaqi_co2"].apply(iaqi_category)
    df_filtered["iaqi_category_tvoc"] = df_filtered["iaqi_tvoc"].apply(iaqi_category)

    def highlight_good(s):
        return ['background-color: green' if v == 1 else '' for v in s]

    def highlight_moderate(s):
        return ['background-color: yellow' if v == 2 else '' for v in s]

    def highlight_hazardous(s):
        return ['background-color: red' if v == 3 else '' for v in s]

    st.dataframe(df_filtered.style.apply(highlight_good, subset=["iaqi_category_co2", "iaqi_category_tvoc"]).apply(
        highlight_moderate, subset=["iaqi_category_co2", "iaqi_category_tvoc"]).apply(highlight_hazardous,
                                                                                      subset=["iaqi_category_co2",
                                                                                              "iaqi_category_tvoc"]))

    # Count the number of each category of IAQI category

    st.write("Jumlah Kategori IAQI CO2")
    good = df_filtered[df_filtered["iaqi_category_co2"] == 1].shape[0]
    moderate = df_filtered[df_filtered["iaqi_category_co2"] == 2].shape[0]
    hazardous = df_filtered[df_filtered["iaqi_category_co2"] == 3].shape[0]

    st.write(good, moderate, hazardous)

    st.write("Jumlah Kategori IAQI TVOC")
    good_tvoc = df_filtered[df_filtered["iaqi_category_tvoc"] == 1].shape[0]
    moderate_tvoc = df_filtered[df_filtered["iaqi_category_tvoc"] == 2].shape[0]
    hazardous_tvoc = df_filtered[df_filtered["iaqi_category_tvoc"] == 3].shape[0]

    st.write(good_tvoc, moderate_tvoc, hazardous_tvoc)

    # Features Engineering

    st.header("Features Engineering")

    df_transform = df_filtered.loc[:,
                   ["co2", "tvoc", "temperature", "iaqi_co2", "iaqi_tvoc", "iaqi_category_co2", "iaqi_category_tvoc"]].copy()

    # 75 data untuk training masing2 kategori

    df_transform = df_transform.groupby("iaqi_category_co2").head(75)

    df_transform = df_transform.groupby("iaqi_category_tvoc").head(75)

    # hitung jumlah data yang ada di masing-masing kategori untuk cek apakah data sudah dipisah dengan benar
    # atau belum

    st.write("Jumlah Kategori IAQI CO2")
    good = df_transform[df_transform["iaqi_category_co2"] == 1].shape[0]
    moderate = df_transform[df_transform["iaqi_category_co2"] == 2].shape[0]
    hazardous = df_transform[df_transform["iaqi_category_co2"] == 3].shape[0]

    st.write(good, moderate, hazardous)

    st.write("Jumlah Kategori IAQI TVOC")
    good_tvoc = df_transform[df_transform["iaqi_category_tvoc"] == 1].shape[0]
    moderate_tvoc = df_transform[df_transform["iaqi_category_tvoc"] == 2].shape[0]
    hazardous_tvoc = df_transform[df_transform["iaqi_category_tvoc"] == 3].shape[0]

    st.write(good_tvoc, moderate_tvoc, hazardous_tvoc)

    # Sisa 150 data untuk data testing

    df_transform_test = df_transform.groupby("iaqi_category_co2").tail(35)

    # Hitung jumlah data yang ada di masing-masing kategori untuk cek apakah data sudah dipisah dengan benar

    st.write("Jumlah Kategori IAQI CO2")

    good = df_transform_test[df_transform_test["iaqi_category_co2"] == 1].shape[0]
    moderate = df_transform_test[df_transform_test["iaqi_category_co2"] == 2].shape[0]
    hazardous = df_transform_test[df_transform_test["iaqi_category_co2"] == 3].shape[0]

    st.write(good, moderate, hazardous)

    st.write("Jumlah Kategori IAQI TVOC")

    good_tvoc = df_transform_test[df_transform_test["iaqi_category_tvoc"] == 1].shape[0]
    moderate_tvoc = df_transform_test[df_transform_test["iaqi_category_tvoc"] == 2].shape[0]
    hazardous_tvoc = df_transform_test[df_transform_test["iaqi_category_tvoc"] == 3].shape[0]

    st.write(good_tvoc, moderate_tvoc, hazardous_tvoc)

    X_test_co2 = df_transform_test[["co2", "iaqi_co2"]].values
    X_test_tvoc = df_transform_test[["tvoc", "iaqi_tvoc"]].values
    y_test_co2 = df_transform_test["iaqi_category_co2"].values
    y_test_tvoc = df_transform_test["iaqi_category_tvoc"].values

    df_transform.fillna(method="bfill", inplace=True)

    st.dataframe(df_transform)

    st.header("Data Preprocessing")

    feature_co2 = ["co2", "iaqi_co2"]
    feature_tvoc = ["tvoc", "iaqi_tvoc"]
    y_feature_co2 = "iaqi_category_co2"
    y_feature_tvoc = "iaqi_category_tvoc"

    # Splitting Data

    st.write("Pembagian Data Training dan Data Testing")

    # Normalisasi Data

    scaler_co2 = StandardScaler()
    scaler_tvoc = StandardScaler()
    X_co2 = scaler_co2.fit_transform(df_transform[feature_co2])
    X_tvoc = scaler_tvoc.fit_transform(df_transform[feature_tvoc])
    X_test_co2 = scaler_co2.transform(X_test_co2)
    X_test_tvoc = scaler_tvoc.transform(X_test_tvoc)
    y_co2 = df_transform[y_feature_co2]
    y_tvoc = df_transform[y_feature_tvoc]

    # One Hot Encoding

    y_co2 = to_categorical(y_co2)
    y_tvoc = to_categorical(y_tvoc)
    y_test_co2 = to_categorical(y_test_co2)
    y_test_tvoc = to_categorical(y_test_tvoc)
    y_co2 = np.delete(y_co2, 0, 1)
    y_tvoc = np.delete(y_tvoc, 0, 1)
    y_test_co2 = np.delete(y_test_co2, 0, 1)
    y_test_tvoc = np.delete(y_test_tvoc, 0, 1)
    num_classes = y_co2.shape[1]

    # Fungsi Data Augmentation
    def augment_data(X, noise_level=0.01):
        noise = np.random.normal(loc=0, scale=noise_level, size=X.shape)
        return X + noise

    X_train_co2, X_val_co2, y_train_co2, y_val_co2 = train_test_split(X_co2, y_co2, test_size=0.2, shuffle=True)
    X_train_tvoc, X_val_tvoc, y_train_tvoc, y_val_tvoc = train_test_split(X_tvoc, y_tvoc, test_size=0.2, shuffle=True)

    X_train_co2 = np.expand_dims(X_train_co2, 1)
    X_val_co2 = np.expand_dims(X_val_co2, 1)
    X_test_co2 = np.expand_dims(X_test_co2, 1)
    X_test_tvoc = np.expand_dims(X_test_tvoc, 1)

    X_train_tvoc = np.expand_dims(X_train_tvoc, 1)
    X_val_tvoc = np.expand_dims(X_val_tvoc, 1)

    X_augment_co2 = augment_data(X_train_co2, noise_level=0.5)
    X_augment_tvoc = augment_data(X_train_tvoc, noise_level=0.3)

    X_test_augment_co2 = augment_data(X_test_co2, noise_level=0.3)
    X_test_augment_tvoc = augment_data(X_test_tvoc, noise_level=0.1)

    st.write("Data Training Label")

    st.write(y_train_co2)

    st.write("Data Testing Label")

    st.write(y_val_co2)

    # Model Training

    st.header("Model Training")

    st.write("Model yang digunakan adalah LSTM Classifier")

    # Model Training
    def lstm_model(units, dropout, batch_size, input_size, learning_rate):
        model = Sequential()
        model.add(LSTM(units, input_shape=(batch_size, input_size), return_sequences=True))
        model.add(Dropout(dropout))
        model.add(LSTM(units))
        model.add(Dropout(dropout))
        model.add(Dense(num_classes, activation="softmax"))

        model.compile(optimizer=Adam(learning_rate=learning_rate), loss="categorical_crossentropy", metrics=["accuracy"])

        model.summary(print_fn=lambda x: st.text(x))

        return model

    model_co2 = lstm_model(64, 0.2, X_train_co2.shape[1], X_train_co2.shape[2], 0.02)

    model_tvoc = lstm_model(64, 0.2, X_train_tvoc.shape[1], X_train_tvoc.shape[2], 0.02)

    def callbacksUnits(patience_lr, min_lr, patience_es, min_delta_es):
        # definisikan ReduceLROnPlateau untuk mengurangi learning rate jika model tidak belajar lagi.
        lr_decay = ReduceLROnPlateau(monitor='loss',
                                     patience=patience_lr, verbose=1,
                                     factor=0.5, min_lr=min_lr)
        # definisikan EarlyStopping untuk menghentikan training jika model tidak belajar lagi.
        early_stop = EarlyStopping(monitor='val_accuracy', min_delta=min_delta_es,
                                   patience=patience_es, verbose=1, mode='auto',
                                   restore_best_weights=True)

        return lr_decay, early_stop

    lr_decay_co2, early_stop_co2 = callbacksUnits(5, 1e-3, 20, 0.01)
    lr_decay_tvoc, early_stop_tvoc = callbacksUnits(5, 2e-5, 30, 0.01)

    def plot_history(history):
        fig, ax = plt.subplots(1, 2, figsize=(20, 5))

        ax[0].plot(history.history["accuracy"], label="Training Accuracy")
        ax[0].plot(history.history["val_accuracy"], label="Validation Accuracy")
        ax[0].set_title("Accuracy")
        ax[0].set_xlabel("Epoch")
        ax[0].set_ylabel("Accuracy")
        ax[0].legend()

        ax[1].plot(history.history["loss"], label="Training Loss")
        ax[1].plot(history.history["val_loss"], label="Validation Loss")
        ax[1].set_title("Loss")
        ax[1].set_xlabel("Epoch")
        ax[1].legend()

        st.pyplot(fig)

        # Training accuracy and validation accuracy in percentage

        train_acc = history.history["accuracy"][-1] * 100

        val_acc = history.history["val_accuracy"][-1] * 100

        st.write(f"Training Accuracy: {train_acc:.2f}%")

        st.write(f"Validation Accuracy: {val_acc:.2f}%")

    st.write("Model Training Selesai")

    st.write("Model Evaluation")

    history_co2 = model_co2.fit(X_augment_co2, y_train_co2, epochs=100, batch_size=64,
                                validation_data=(X_val_co2, y_val_co2),
                                callbacks=[lr_decay_co2, early_stop_co2])

    history_tvoc = model_tvoc.fit(X_augment_tvoc, y_train_tvoc, epochs=100, batch_size=64,
                                  validation_data=(X_val_tvoc, y_val_tvoc),
                                  callbacks=[lr_decay_tvoc, early_stop_tvoc])

    st.subheader("CO2")

    plot_history(history_co2)

    st.subheader("TVOC")

    plot_history(history_tvoc)

    # Prediction

    st.header("Prediction")

    st.write("Prediksi kategori")

    def predict(model, test_data, actual_data):
        y_pred = model.predict(test_data)

        st.write(y_pred)

        y_pred = np.argmax(y_pred, axis=1)

        actual = np.argmax(actual_data, axis=1)

        # Classification Report
        st.text(classification_report(actual, y_pred, labels=[0, 1, 2], target_names=["Good", "Moderate", "Hazardous"]))

        # Time series plot from y_pred_co2 data per category

        st.write("Plot Prediksi per Kategori")

        fig, ax = plt.subplots(1, 1, figsize=(20, 5))
        for i in range(num_classes):
            if i == 0:
                ax.plot(y_pred == i, label=f"Category {i}", color='green')
            elif i == 1:
                ax.plot(y_pred == i, label=f"Category {i}", color='yellow')
            else:
                ax.plot(y_pred == i, label=f"Category {i}", color='red')
        ax.set_title("Prediksi Kategori per Waktu")
        ax.set_xlabel("Waktu")
        # X label 5minutes interval
        ax.set_xticks(np.arange(0, len(y_pred), 5))
        ax.set_ylabel("Predicted Value")
        ax.legend(["Good", "Moderate", "Hazardous"])
        st.pyplot(fig)

        # Confusion Matrix

        st.write("Confusion Matrix")

        fig, ax = plt.subplots(1, 1, figsize=(10, 5))
        sns.heatmap(confusion_matrix(actual, y_pred), annot=True, fmt='d', ax=ax)
        ax.set_title("Confusion Matrix")
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        # Untuk xlabel dan ylabel 1 = good, 2 = moderate, 3 = hazardous
        ax.set_xticklabels(["Good", "Moderate", "Hazardous"])
        ax.set_yticklabels(["Good", "Moderate", "Hazardous"])
        st.pyplot(fig)

    st.subheader("Prediksi CO2")

    predict(model_co2, X_test_augment_co2, y_test_co2)

    st.subheader("Prediksi TVOC")

    predict(model_tvoc, X_test_augment_tvoc, y_test_tvoc)

    # EDA

    st.header("Exploratory Data Analysis")

    st.write("Count CO2 per Category bar plot")

    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    sns.countplot(x='iaqi_category_co2', data=df_transform, ax=ax)
    ax.set_title("Count CO2 per Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Count")
    st.pyplot(fig)

    st.write("Count TVOC per Category bar plot")

    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    sns.countplot(x='iaqi_category_tvoc', data=df_transform, ax=ax)
    ax.set_title("Count TVOC per Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Count")
    st.pyplot(fig)

    # Save the model

    # model.save("model.h5")
    #
    # st.write("Model has been saved as model.h5")


page_names_to_funcs = {
    "Read Data": read_data,
    "Data Sensor": data_sensor,
}

tp_name = st.sidebar.selectbox("Pilih Menu", page_names_to_funcs)
page_names_to_funcs[tp_name]()
