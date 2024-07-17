import firebase_admin
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from firebase_admin import db
from keras.utils import to_categorical
from sklearn.metrics import confusion_matrix, classification_report
from tensorflow import keras

st.set_page_config(page_title='Eksperimen Data', layout='wide')

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

# refGood = db.reference("/data/GoodData/")
# refModerate = db.reference("/data/testingData/")
# refHazard = db.reference("/data/testHazard/")
#
# data_ref_good = refGood.get()
# data_ref_moderate = refModerate.get()
# data_ref_hazard = refHazard.get()

data_ref = ref.get()


def reset_data():
    #     truncate_reference_data("data")
    ref.delete()


st.button("Reset Data", on_click=reset_data)

# dfGood = pd.DataFrame(data_ref_good.values())
# dfModerate = pd.DataFrame(data_ref_moderate.values())
# dfHazard = pd.DataFrame(data_ref_hazard.values())
#
# df = pd.concat([dfGood, dfModerate, dfHazard])

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
    if 450 <= co2 <= 500:
        iaqi_co2 = ((50 - 0) / (500 - 450)) * (co2 - 450) + 0
    elif 500 < co2 <= 1000:
        iaqi_co2 = ((100 - 51) / (1000 - 501)) * (co2 - 501) + 51
    elif 1000 < co2 <= 2000:
        iaqi_co2 = ((150 - 101) / (2000 - 1001)) * (co2 - 1001) + 101
    elif 2000 < co2 <= 5000:
        iaqi_co2 = ((200 - 151) / (5000 - 2001)) * (co2 - 2001) + 151
    elif 5000 < co2 <= 10000:
        iaqi_co2 = ((300 - 201) / (10000 - 5001)) * (co2 - 5001) + 201
    elif 10000 < co2 <= 15000:
        iaqi_co2 = ((500 - 301) / (15000 - 10001)) * (co2 - 10001) + 301
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
        iaqi_tvoc = ((500 - 301) / (10.0 - 5.0)) * (tvoc - 5.0) + 301
    else:
        iaqi_tvoc = 1000

    return iaqi_co2, iaqi_tvoc


st.write("Rumus yang terkandung dalam fungsi calculate_iaqi adalah sebagai berikut:")
st.latex(r'AQI_{CO2} = \frac{I_{H} - I_{L}}{C_{H} - C_{L}} \times (CO2 - C_{L}) + I_{L}')
st.latex(r'AQI_{TVOC} = \frac{I_{H} - I_{L}}{C_{H} - C_{L}} \times (TVOC - C_{L}) + I_{L}')

st.write("Parameter yang terdapat dalam rumus di atas adalah sebagai berikut:")
st.write("AQI = Indeks Kualitas Udara (Air Quality Index)")
st.write("CO2 = Konsentrasi CO2 dalam udara")
st.write("TVOC = Konsentrasi TVOC dalam udara")
st.write("I_H = Nilai Indeks tertinggi dalam rentang konsentrasi CO2 atau TVOC")
st.write("I_L = Nilai Indeks terendah dalam rentang konsentrasi CO2 atau TVOC")
st.write("C_H = Konsentrasi CO2 atau TVOC tertinggi dalam rentang konsentrasi CO2 atau TVOC")
st.write("C_L = Konsentrasi CO2 atau TVOC terendah dalam rentang konsentrasi CO2 atau TVOC")

st.write(
    "Setelah dihitung Nilai AQI akan di ambil nilai minimal dari kedua nilai AQI tersebut untuk mendapatkan nilai "
    "IAQI dengan rumus seperti dibawah ini:")

st.latex(r'IAQI = MIN(IAQI_{param})')

# Reference of the formula
st.link_button("Reference: Atmotube.com",
               "https://atmotube.com/atmocube-support/indoor-air-quality-index-iaqi#:~:text=To"
               "%20calculate%20the%20AQI%2C%20the%20EPA%20measured%20outdoor,"
               "individual%20index%20based%20on%20the%20EPA%E2%80%99s%20breakpoint%20table.")

df_filtered["iaqi_co2"], df_filtered["iaqi_tvoc"] = zip(
    *df_filtered.apply(lambda x: calculate_iaqi(x["co2"], x["tvoc"]), axis=1))


# After IAQI Calculation make a new column that show category of IAQI Score of Good, Moderate, and Hazardous

def iaqi_category(iaqi):
    if 0 <= iaqi <= 50:
        return 0
    elif 51 <= iaqi <= 100:
        return 1
    else:
        return 2


# Buat kolom yang menampilkan minimal dari iaqi_co2 dan iaqi_tvoc
df_filtered["iaqi_min"] = df_filtered[["iaqi_co2", "iaqi_tvoc"]].min(axis=1)

# Tambahkan kolom yang menampilkan kategori dari nilai IAQI terendah
df_filtered["iaqi_category"] = df_filtered["iaqi_min"].apply(iaqi_category)

st.dataframe(df_filtered)


def highlight_good(s):
    return ['background-color: green' if v == 0 else '' for v in s]


def highlight_moderate(s):
    return ['background-color: yellow' if v == 1 else '' for v in s]


def highlight_hazardous(s):
    return ['background-color: red' if v == 2 else '' for v in s]


st.dataframe(df_filtered.style.apply(highlight_good, subset=["iaqi_category"]).apply(
    highlight_moderate, subset=["iaqi_category"]).apply(highlight_hazardous,
                                                        subset=["iaqi_category"]))

# Hitung jumlah data yang masuk ke dalam kategori baik, sedang, dan berbahaya
good = df_filtered[df_filtered["iaqi_category"] == 0].shape[0]
moderate = df_filtered[df_filtered["iaqi_category"] == 1].shape[0]
hazardous = df_filtered[df_filtered["iaqi_category"] == 2].shape[0]

st.write("Jumlah data yang masuk ke dalam kategori baik adalah", good)
st.write("Jumlah data yang masuk ke dalam kategori sedang adalah", moderate)
st.write("Jumlah data yang masuk ke dalam kategori berbahaya adalah", hazardous)

df_transform = df_filtered.loc[:,
               ["co2", "tvoc", "iaqi_co2", "iaqi_tvoc", "iaqi_min", "iaqi_category"]].copy()

st.dataframe(df_transform)

# Splitting Data
x = df_transform[["co2", "iaqi_co2", "tvoc", "iaqi_tvoc", "iaqi_min"]].values
y = df_transform[["iaqi_category"]].values

# Eksperimen 1: Memahami Pengaruh CO2 dan TVOC terhadap IAQI

st.write("Eksperimen 1: Memahami Pengaruh CO2 dan TVOC terhadap IAQI")

st.write("Pada eksperimen ini, akan dilakukan analisis terhadap pengaruh CO2 dan TVOC terhadap nilai IAQI. "
         "Analisis ini dilakukan dengan menggunakan scatter plot.")

fig, ax = plt.subplots(1, 2, figsize=(20, 10))

# Scatter plot CO2 terhadap IAQI
ax[0].scatter(df_transform["co2"], df_transform["iaqi_co2"], color="blue")
ax[0].set_title("CO2 vs IAQI CO2")
ax[0].set_xlabel("CO2")
ax[0].set_ylabel("IAQI CO2")

# Scatter plot TVOC terhadap IAQI
ax[1].scatter(df_transform["tvoc"], df_transform["iaqi_tvoc"], color="red")
ax[1].set_title("TVOC vs IAQI TVOC")
ax[1].set_xlabel("TVOC")
ax[1].set_ylabel("IAQI TVOC")

st.pyplot(fig)

# Selanjutnya akan dibuat plot correlation matrix untuk melihat hubungan antara CO2 dan TVOC terhadap IAQI
st.write("Selanjutnya akan dibuat correlation matrix untuk melihat hubungan antara CO2 dan TVOC terhadap IAQI")

correlation_matrix = df_transform[["co2", "tvoc", "iaqi_co2", "iaqi_tvoc", "iaqi_min"]].corr()

st.write(correlation_matrix)

fig, ax = plt.subplots(figsize=(10, 10))

sns.heatmap(correlation_matrix, annot=True, ax=ax)

st.pyplot(fig)