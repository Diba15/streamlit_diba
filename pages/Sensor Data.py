import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import db
import pandas as pd

st.set_page_config(page_title='Tugas Skripsi', layout='wide')

st.title("WP6003 Air Box Reader")

st.header("VSON WP6003 Bluetooth APP Air Quality Detector for PM Formaldehyde TVOC")


def read_data():
    html_string = """
        <fieldset>
          <legend>Read data:</legend>
          <button onclick="enableNotifications()">Enable notifications</button></br>
          <button onclick="readData()">Read sensor data</button></br>
          <button onclick="sendCommand()">Send command</button></br>
          <input type="checkbox" id="autoRefresh" name="autoRefresh" onclick="autoRefresh()">
          <label for="autoRefresh">Auto refresh values (30s)</label>
        </fieldset>

        <fieldset>
          <legend>Sensor calibration:</legend>
          <div style="font-size: 14px">
          Before sensor calibration procedure please follow these instructions:
          <ol>
            <li>Take the device to a place with fresh air (such as balcony, outdoor);
            <li>Keep the device runnin for more than 10 minutes; then take it indoor
          </ol>
          </div>
          <button onclick="calibrate()">Calibrate</button>
        </fieldset>

        <fieldset>
          <legend>Console:</legend>
          <p id="info">Info: </p>
          <p id="waktu"></p>
          <p id="temperature"></p>
          <p id="tvocs"></p>
          <p id="hchos"></p>
          <p id="co2s"></p>
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
              element.innerHTML = "Info: " + message;
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
          const test = ref(database, 'test');
          get(test).then((snapshot) => {
            if (snapshot.exists()) {
                console.log(snapshot.val());
            }
          });

          function addData(time, temperature, tvocs, hcho, co2) {
            push(ref(database, 'data/'), {
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


          window.addData = addData;
        </script>

        <style>
        html{
            height: 900px;
        }
        body {
          max-width: 400px;
          margin: 0 auto;
          color: white;
          font-family: Lato,'Helvetica Neue',Arial,Helvetica,sans-serif;
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

    df = pd.DataFrame(data_ref.values())

    st.dataframe(df,
                 column_config={
                     "time": st.column_config.Column(
                         width="large",
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

    st.write(df.describe())

    st.write(df.isna().sum())


page_names_to_funcs = {
    "Read Data": read_data,
    "Data Sensor": data_sensor,
}

tp_name = st.sidebar.selectbox("Pilih Menu", page_names_to_funcs)
page_names_to_funcs[tp_name]()

