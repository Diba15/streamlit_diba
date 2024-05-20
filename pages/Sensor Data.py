import firebase_admin
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
import streamlit.components.v1 as components
import tensorflow as tf
from firebase_admin import db
from keras.layers import Dense, LSTM
from keras.models import Sequential
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

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

    # add text below the image
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
            return "Good"
        elif 51 <= iaqi <= 100:
            return "Moderate"
        else:
            return "Hazardous"

    df_filtered["iaqi_category_co2"] = df_filtered["iaqi_co2"].apply(iaqi_category)
    df_filtered["iaqi_category_tvoc"] = df_filtered["iaqi_tvoc"].apply(iaqi_category)

    st.dataframe(df_filtered)

    # Buat sebuah plot yang menunjukkan IAQI category dari CO2 yang sudah dipisah menjadi 3 line yaitu hijau untuk Good,
    # kuning untuk Moderate, dan merah untuk Hazardous. dan y juga berdasarkan category yang sudah diubah menjadi
    # kategori Good = 1, Moderate = 0, dan Hazardous = -1 dan x nya adalah waktu setiap 5 menit

    fig = go.Figure()

    for category in df_filtered["iaqi_category_co2"].unique():
        df_category = df_filtered[df_filtered["iaqi_category_co2"] == category]
        if category == "Good":
            color = "green"
        elif category == "Moderate":
            color = "yellow"
        else:
            color = "red"
        fig.add_trace(go.Scatter(y=[1] * len(df_category), mode="markers", marker=dict(color=color), name=category))

    fig.update_layout(title="IAQI Category CO2", xaxis_title="Time", yaxis_title="Category", showlegend=True)
    st.plotly_chart(fig)

    st.header("Data Preprocessing")

    # Splitting the dataset into training and testing set

    X = df_filtered[["co2", "tvoc"]].values
    y = df_filtered[["iaqi_category_co2"]].values

    y = pd.DataFrame(y).replace({"Good": 1, "Moderate": 2, "Hazardous": 3}).values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    st.write("X_train shape:", X_train.shape)

    st.write("X_test shape:", X_test.shape)

    st.write("y_train:", y_train)

    st.header("Modeling")

    # Create a model using LSTM classification

    model = Sequential()
    model.add(LSTM(50, activation="relu", input_shape=(X_train.shape[1], 1)))
    model.add(Dense(1))
    # Bisakah kamu jelaskan kenapa menggunakan activation relu?
    # Jawaban: Karena activation relu merupakan activation function yang paling sering digunakan dan memiliki performa
    # yang baik dalam model deep learning. Activation relu juga memiliki kelebihan yaitu mengatasi masalah vanishing
    # gradient yang sering terjadi pada activation function sigmoid dan tanh.

    model.compile(optimizer="adam", loss="mse")
    # Bisakah kamu jelaskan kenapa menggunakan loss mse?
    # Jawaban: Karena loss mse merupakan loss function yang paling sering digunakan untuk regression problem dan
    # memiliki performa yang baik dalam model deep learning. Loss mse juga memiliki kelebihan yaitu menghitung
    # error antara prediksi dan target dengan cara menghitung squared error.
    # Bisakah kamu jelaskan kenapa menggunakan optimizer adam?
    # Jawaban: Karena optimizer adam merupakan optimizer yang paling sering digunakan dan memiliki performa yang baik
    # dalam model deep learning. Optimizer adam juga memiliki kelebihan yaitu menghitung learning rate secara adaptif
    # dan menghitung momentum secara adaptif.

    # Fit the model

    model.fit(X_train, y_train, epochs=200, batch_size=32, verbose=1)

    # Evaluate the model

    y_pred = model.predict(X_test)

    st.write("y_pred:", y_pred)

    # Konversi prediksi menjadi kategori
    # menggunakan np.where untuk check kondisi jika prediksi kurang dari atau sama dengan 1, maka kategori adalah 1,
    # jika prediksi kurang dari atau sama dengan 2, maka kategori adalah 2, jika tidak keduanya,
    # maka kategori adalah 3
    y_pred_category = np.where(y_pred <= 1, 1, np.where(y_pred <= 2, 2, 3))

    st.write("y_pred_category:", y_pred_category)

    # Evaluate the model

    accuracy = accuracy_score(y_test, y_pred_category)

    st.write("Accuracy:", accuracy)

    # Print MSE

    mse = mean_squared_error(y_test, y_pred_category)

    st.write("MSE:", mse)

    # Compare the actual and prediction

    df_compare = pd.DataFrame({"Actual": y_test.flatten(), "Prediction": y_pred_category.flatten()})

    df_compare["Accuracy"] = np.where(df_compare["Actual"] == df_compare["Prediction"], "Accurate", "Not Accurate")

    df_compare["Actual"] = pd.DataFrame(df_compare["Actual"]).replace({1: "Good", 2: "Moderate", 3: "Hazardous"})

    df_compare["Prediction"] = pd.DataFrame(df_compare["Prediction"]).replace({1: "Good", 2: "Moderate", 3: "Hazardous"})

    st.dataframe(df_compare)

    # Save the model

    model.save("model.h5")

    st.write("Model has been saved as model.h5")


page_names_to_funcs = {
    "Read Data": read_data,
    "Data Sensor": data_sensor,
}

tp_name = st.sidebar.selectbox("Pilih Menu", page_names_to_funcs)
page_names_to_funcs[tp_name]()
