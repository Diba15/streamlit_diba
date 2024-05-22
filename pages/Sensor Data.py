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
from keras.layers import Dense, LSTM, BatchNormalization
from keras.models import Sequential
from keras.optimizers import Adam
from keras.regularizers import l2
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
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
    df_filtered = df[["co2", "tvoc"]]

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
        elif 10000 < co2 <= 20000:
            iaqi_co2 = ((400 - 301) / (20000 - 10001)) * (co2 - 10001) + 301
        elif 20000 < co2 <= 50000:
            iaqi_co2 = ((500 - 401) / (50000 - 20001)) * (co2 - 20001) + 401
        elif 50000 < co2 <= 100000:
            iaqi_co2 = ((600 - 501) / (100000 - 50001)) * (co2 - 50001) + 501
        elif 100000 < co2 <= 200000:
            iaqi_co2 = ((700 - 601) / (200000 - 100001)) * (co2 - 100001) + 601
        elif 200000 < co2 <= 400000:
            iaqi_co2 = ((800 - 701) / (400000 - 200001)) * (co2 - 200001) + 701
        elif 400000 < co2 <= 1000000:
            iaqi_co2 = ((900 - 801) / (1000000 - 400001)) * (co2 - 400001) + 801
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
            return 0
        else:
            return -1

    df_filtered["iaqi_category_co2"] = df_filtered["iaqi_co2"].apply(iaqi_category)
    df_filtered["iaqi_category_tvoc"] = df_filtered["iaqi_tvoc"].apply(iaqi_category)

    def highlight_good(s):
        return ['background-color: green' if v == 1 else '' for v in s]

    def highlight_moderate(s):
        return ['background-color: yellow' if v == 0 else '' for v in s]

    def highlight_hazardous(s):
        return ['background-color: red' if v == -1 else '' for v in s]

    st.dataframe(df_filtered.style.apply(highlight_good, subset=["iaqi_category_co2", "iaqi_category_tvoc"]).apply(
        highlight_moderate, subset=["iaqi_category_co2", "iaqi_category_tvoc"]).apply(highlight_hazardous,
                                                                                      subset=["iaqi_category_co2",
                                                                                              "iaqi_category_tvoc"]))

    # Features Engineering

    st.header("Features Engineering")

    df_transform = df_filtered.loc[:, ["iaqi_co2", "iaqi_tvoc", "iaqi_category_co2", "iaqi_category_tvoc"]].copy()

    st.dataframe(df_transform)

    df_transform.fillna(method="bfill", inplace=True)

    st.dataframe(df_transform)

    st.header("Data Preprocessing CO2")

    # Splitting Data

    st.write("Pembagian Data Training dan Data Testing")

    X = df_transform[["iaqi_co2"]]
    y = df_transform["iaqi_category_co2"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    st.write("Data Training")

    st.write(X_train)

    st.write("Data Testing")

    st.write(X_test)

    st.write("Data Training Label")

    st.write(y_train)

    st.write("Data Testing Label")

    st.write(y_test)

    # Model Training

    st.header("Model Training")

    st.write("Model yang digunakan adalah LSTM Classifier")

    model = Sequential()
    model.add(LSTM(8, activation='tanh', input_shape=(X_train.shape[1], 1), recurrent_activation='hard_sigmoid'
                   , return_sequences=True, return_state=False, stateful=False, unroll=False))

    model.add(BatchNormalization())
    model.add(LSTM(units=8,
                   activation='tanh', recurrent_activation='hard_sigmoid',
                   return_sequences=True, return_state=False,
                   stateful=False, unroll=False
                   ))
    model.add(BatchNormalization())
    model.add(LSTM(units=8,
                   activation='tanh', recurrent_activation='hard_sigmoid',
                   return_sequences=False, return_state=False,
                   stateful=False, unroll=False
                   ))
    model.add(BatchNormalization())
    model.add(Dense(1, activation='sigmoid'))

    model.compile(optimizer=Adam(lr=5e-2), loss="binary_crossentropy", metrics=["acc"])

    # Print Model Summary

    model.summary(print_fn=lambda x: st.text(x))

    # definisikan ReduceLROnPlateau untuk mengurangi learning rate jika model tidak belajar lagi.
    lr_decay = ReduceLROnPlateau(monitor='loss',
                                 patience=1, verbose=0,
                                 factor=0.5, min_lr=1e-8)
    # definisikan EarlyStopping untuk menghentikan training jika model tidak belajar lagi.
    early_stop = EarlyStopping(monitor='val_acc', min_delta=0,
                               patience=30, verbose=1, mode='auto',
                               baseline=0, restore_best_weights=True)

    # Train the model.
    # The dataset is small for NN - let's use test_data for validation
    M_TEST = X_test.shape[0]
    M_TRAIN = X_train.shape[0]

    start = time()
    History = model.fit(X_train, y_train,
                        epochs=50,
                        batch_size=M_TRAIN,
                        validation_split=0.0,
                        validation_data=(X_test[:M_TEST], y_test[:M_TEST]),
                        shuffle=True, verbose=0,
                        callbacks=[lr_decay, early_stop])
    st.write('-' * 65)
    st.write(f'Training was completed in {time() - start:.2f} secs')
    st.write('-' * 65)
    # Evaluate the model:
    train_loss, train_acc = model.evaluate(X_train, y_train,
                                           batch_size=M_TRAIN, verbose=0)
    test_loss, test_acc = model.evaluate(X_test[:M_TEST], y_test[:M_TEST],
                                         batch_size=M_TEST, verbose=0)
    st.write('-' * 65)
    st.write(f'train accuracy = {round(train_acc * 100, 4)}%')
    st.write(f'test accuracy = {round(test_acc * 100, 4)}%')
    st.write(f'test error = {round((1 - test_acc) * M_TEST)} out of {M_TEST} examples')

    st.write(History.history.keys())

    # Plot the loss and accuracy curves over epochs:
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(18, 6))
    axs[0].plot(History.history['loss'], color='b', label='Training loss')
    axs[0].plot(History.history['val_loss'], color='r', label='Validation loss')
    axs[0].set_title("Loss curves")
    axs[0].legend(loc='best', shadow=True)
    axs[1].plot(History.history['acc'], color='b', label='Training accuracy')
    axs[1].plot(History.history['val_acc'], color='r', label='Validation accuracy')
    axs[1].set_title("Accuracy curves")
    axs[1].legend(loc='best', shadow=True)
    st.pyplot(fig)

    # Model Evaluation

    st.header("Model Evaluation")

    y_pred = model.predict(X_test)

    st.write("Prediksi CO2")

    # Compare Prediction with Actual Data

    st.write("Perbandingan Prediksi dengan Data Asli")

    df_compare = pd.DataFrame({"iaqi_category_co2": y_test, "iaqi_category_co2_pred": y_pred.flatten()})

    # Round the prediction to the nearest integer
    df_compare['iaqi_category_co2_pred'] = df_compare['iaqi_category_co2_pred'].apply(lambda x: round(x))

    st.dataframe(df_compare)

    # Give an expected and not expected column in dataframe
    df_compare['expected'] = df_compare['iaqi_category_co2'] == df_compare['iaqi_category_co2_pred']

    st.dataframe(df_compare)

    # EDA

    st.header("Exploratory Data Analysis (EDA)")

    # Ubah iaqi_category_co2 menjadi katregori ketika -1 adalah hazardous, 0 adalah moderate dan 1 adalah good

    df_transform['iaqi_category_co2'] = df_transform['iaqi_category_co2'].apply(
        lambda x: "hazardous" if x == -1 else "moderate" if x == 0 else "good")

    st.write("Distribusi Kategori CO2")

    fig = px.histogram(df_transform, x="iaqi_category_co2", title="Distribusi Kategori CO2")

    st.plotly_chart(fig)

    st.write("Line Plot Timeseries CO2")

    fig = px.line(df_transform, y="iaqi_co2", color="iaqi_category_co2", title="Line Plot Timeseries CO2")

    st.plotly_chart(fig)

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
