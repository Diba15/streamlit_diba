import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import paho.mqtt.client as mqtt
import time
import datetime

st.title("WP6003 Air Box Reader")

st.header("VSON WP6003 Bluetooth APP Air Quality Detector for PM Formaldehyde TVOC")

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
      <div id="console"></div>
    </fieldset>
    
    <script language='javascript'>
    
    const SENSOR_SERVICE = '0000fff0-0000-1000-8000-00805f9b34fb';
    const SENSOR_WRITE   = '0000fff1-0000-1000-8000-00805f9b34fb';
    const SENSOR_READ    = '0000fff4-0000-1000-8000-00805f9b34fb';
    
    var service;
    var readChar;
    var writeChar;
    var autoRefreshInterval;
    
    async function initConnection() {
      if(service != null) 
        return;
      
      try {
        service = await getService(SENSOR_SERVICE);
    
        writeChar = await service.getCharacteristic(SENSOR_WRITE);
        readChar = await service.getCharacteristic(SENSOR_READ);
      } catch(error) {
        console.error(error);
        log('BT connection error. Please retry or refresh the browser.');
      }
    }
    
    async function enableNotifications() {
      await initConnection();
        
      log('Enabaling notifications');
      await readChar.startNotifications();
      readChar.addEventListener('characteristicvaluechanged', handleNotifications);
    
      log('Waiting on data... may take some time on a first read');
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
      log('Calabration started');
    }
    
    function autoRefresh() {
      if(autoRefreshInterval) {
        clearTimeout(autoRefreshInterval);
        log('Auto refresh disabled');
      } else {
        autoRefreshInterval = setInterval(() => readData(), 30000);
        log('Auto refresh enabled');
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
        
        log(`Time: ${time} <br/>
             Temp: ${temp} <br/>
             TVOC: ${tvoc} <br/>
             HCHO: ${hcho} <br/>
             CO2 : ${co2} <br/>`);
        } catch(error) {
          console.error(error);
          log('Value parsing faild!');
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
        log('Connecting...')
          return device.gatt.connect();
        })
        .then(function (server) {
        log('Getting primary service...')
          return server.getPrimaryService(service);
        });
    }
    
    function log(message) {
      let element = document.getElementById('console');
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
