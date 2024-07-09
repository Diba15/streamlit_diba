import firebase_admin
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from tensorflow import keras
from firebase_admin import db
from keras.saving.saving_api import load_model
from keras.utils import to_categorical
from pandas import DataFrame
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title='Testing Data', layout='wide')

st.title("Data Testing")
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
        return 0
    elif 51 <= iaqi <= 100:
        return 1
    else:
        return 2


df_filtered["iaqi_category_co2"] = df_filtered["iaqi_co2"].apply(iaqi_category)
df_filtered["iaqi_category_tvoc"] = df_filtered["iaqi_tvoc"].apply(iaqi_category)


def highlight_good(s):
    return ['background-color: green' if v == 0 else '' for v in s]


def highlight_moderate(s):
    return ['background-color: yellow' if v == 1 else '' for v in s]


def highlight_hazardous(s):
    return ['background-color: red' if v == 2 else '' for v in s]


st.dataframe(df_filtered.style.apply(highlight_good, subset=["iaqi_category_co2", "iaqi_category_tvoc"]).apply(
    highlight_moderate, subset=["iaqi_category_co2", "iaqi_category_tvoc"]).apply(highlight_hazardous,
                                                                                  subset=["iaqi_category_co2",
                                                                                          "iaqi_category_tvoc"]))

df_transform = df_filtered.loc[:,
               ["co2", "tvoc", "iaqi_co2", "iaqi_tvoc", "iaqi_category_co2", "iaqi_category_tvoc"]].copy()

st.dataframe(df_transform)

# Splitting Data
x_co2 = df_transform[["co2", "iaqi_co2"]].values
x_tvoc = df_transform[["tvoc", "iaqi_tvoc"]].values
y_co2 = df_transform[["iaqi_category_co2"]].values
y_tvoc = df_transform[["iaqi_category_tvoc"]].values

# Normalisasi Data
scaler_co2 = joblib.load("scaler_co2.pkl")
scaler_tvoc = joblib.load("scaler_tvoc.pkl")

x_co2 = scaler_co2.transform(x_co2)
x_tvoc = scaler_tvoc.transform(x_tvoc)

# One Hot Encoding

y_co2 = to_categorical(y_co2, num_classes=3)
y_tvoc = to_categorical(y_tvoc, num_classes=3)

# Expand Dims

x_co2 = np.expand_dims(x_co2, 1)
x_tvoc = np.expand_dims(x_tvoc, 1)

# Load h5 Model

model_co2 = keras.models.load_model("model_co2.h5")
model_tvoc = keras.models.load_model("model_tvoc.h5")

# Evaluate Model

loss_co2, acc_co2 = model_co2.evaluate(x_co2, y_co2)
loss_tvoc, acc_tvoc = model_tvoc.evaluate(x_tvoc, y_tvoc)

st.write("Loss CO2: ", loss_co2)
st.write("Accuracy CO2: ", acc_co2)

st.write("Loss TVOC: ", loss_tvoc)
st.write("Accuracy TVOC: ", acc_tvoc)

# Predict Data

y_pred_co2 = model_co2.predict(x_co2)
y_pred_tvoc = model_tvoc.predict(x_tvoc)

st.write(y_pred_co2)
st.write(y_pred_tvoc)

# Convert Prediction to Categorical

y_pred_cate_co2 = np.argmax(y_pred_co2, axis=1)
y_pred_cate_tvoc = np.argmax(y_pred_tvoc, axis=1)
actual_co2_test = np.argmax(y_co2, axis=1)
actual_tvoc_test = np.argmax(y_tvoc, axis=1)


# Plot

def plot(actual, prediction, labels, prediction_cate):
    st.text(classification_report(actual, prediction_cate, labels=[0, 1, 2],
                                  target_names=["Good", "Moderate", "Hazardous"], zero_division=0))

    # Confusion Matrix

    st.write("Confusion Matrix")

    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    cm = confusion_matrix(actual, prediction_cate)
    cmn = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    sns.heatmap(cmn, annot=True, fmt='.2f', ax=ax, xticklabels=labels, yticklabels=labels)
    ax.set_title("Confusion Matrix")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    st.pyplot(fig)

    # Time series plot

    st.write("Plot Prediksi per Kategori")

    fig, ax = plt.subplots(1, 1, figsize=(20, 5))
    colors = ['green', 'yellow', 'red']

    for i in range(prediction.shape[1]):
        ax.plot(prediction[:, i], label=f"Category {i}", color=colors[i])

    ax.set_title("Prediksi Kategori per Waktu")
    ax.set_xlabel("Waktu")
    # X label 5minutes interval
    ax.set_xticks(np.arange(0, len(prediction), 5))
    ax.set_ylabel("Predicted Value")
    ax.legend(labels)
    st.pyplot(fig)


labels = ["Good", "Moderate", "Hazardous"]

st.write("CO2")
plot(actual_co2_test, y_pred_co2, labels, y_pred_cate_co2)

st.write("TVOC")
plot(actual_tvoc_test, y_pred_tvoc, labels, y_pred_cate_tvoc)
