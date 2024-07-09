import firebase_admin
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from firebase_admin import db
from keras import Input
from keras.callbacks import ReduceLROnPlateau, EarlyStopping
from keras.layers import Dense, LSTM, Dropout, BatchNormalization
from keras.models import Sequential, save_model
from keras.optimizers import Adam
from keras.regularizers import l1, l2, l1_l2
from keras.utils import to_categorical
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler

st.set_page_config(page_title='Training Data', layout='wide')

st.title("Data Training")

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

st.subheader("Pilih Data Ruangan")

option = st.selectbox("Select Room", list(data_ref.keys()))

with st.expander("Daftar Isi"):
    st.markdown("[Skenario](#scenario-pengambilan-data-sensor)")
    st.markdown("[Read Data From Firebase](#read-data-from-firebase)")
    st.markdown("[Data Summary](#data-summary)")
    st.markdown("[Data Missing Value](#data-missing-value)")
    st.markdown("[Correlation Matrix](#correlation-matrix)")
    st.markdown("[Filtered Data](#filtered-data)")
    st.markdown("[IAQI Calculation](#iaqi-calculation)")
    st.markdown("[Features Engineering](#features-engineering)")
    st.markdown("[Data Preprocessing](#data-preprocessing)")
    st.markdown("[Model Training](#model-training)")
    st.markdown("[Model Evaluation](#model-evaluation)")
    st.markdown("[Prediction](#prediction)")
    st.markdown("[Exploratory Data Analysis](#eda)")

st.header("Scenario Penelitian")

table_html = """
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4" crossorigin="anonymous"></script>
        <table class="table table-striped text-center table-dark">
            <thead>
                <tr>
                    <th scope='col'>#</th>
                    <th scope='col'>Good</th>
                    <th scope='col'>Moderate</th>
                    <th scope='col'>Hazardous</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <th scope='row'>1</th>
                    <td colspan='3'>Menyalakan sensor dengan menghubungkan nya dengan USB atau kepala charger.</td>
                </tr>
                <tr>
                    <th scope='row'>2</th>
                    <td colspan='3'>Menghubungkan sensor pada perangkat laptop/mobile menggunakan bluetooth</td>
                </tr>
                <tr>
                    <th scope='row'>3</th>
                    <td>Menempatkan sensor pada ruangan ber-AC dengan suhu 21 derajat celcius dan ruangan dengan saluran udara yang baik</td>
                    <td>Menempatkan sensor pada ruangan dan menyemprotkan parfum secara berkala.</td>
                    <td>Menempatkan sensor pada sebuah ruangan yang sudah di semprotkan racun nyamuk.</td>
                </tr>
                <tr>
                    <th scope='row'>4</th>
                    <td colspan='3'>Mengambil data sensor menggunakan aplikasi web yang sudah dibuat/disediakan</td>
                </tr>
                <tr>
                    <th scope='row'>5</th>
                    <td colspan='3'>Memasukkan data yang sudah diambil kedalam database NoSQL Firebase</td>
                </tr>
                <tr>
                    <th scope='row'>6</th>
                    <td colspan='3'>Membuat correlation matrix untuk melihat keterkaitan antar fitur.</td>
                </tr>
                <tr>
                    <th scope='row'>7</th>
                    <td colspan='3'>Featuring Engineer untuk menentukan data yang akan digunakan untuk menghitung skor IAQI.</td>
                </tr>
                <tr>
                    <th scope='row'>8</th>
                    <td colspan='3'>Menghitung skor IAQI menggunakan rumus yang sudah ada.</td>
                </tr
                <tr>
                    <th scope='row'>9</th>
                    <td colspan='3'>Membuat kategori IAQI pada data IAQI yang sudah dihitung.</td>
                </tr>
                <tr>
                    <th scope='row'>10</th>
                    <td>Skor <span class='fw-bold'>0-50</span> merupakan skor untuk mendapatkan IAQI kategori Good.</td>
                    <td>Skor <span class='fw-bold'>50-100</span> merupakan skor untuk mendapatkan IAQI kategori Moderate.</td>
                    <td><span class='fw-bold'>Skor > 100</span> merupakan skor untuk mendapatkan IAQI kategori Hazardous.</td>
                </tr>
                <tr>
                    <th scope='row'>11</th>
                    <td colspan='3'>Melakukan splitting data untuk data training, validasi data dan data testing.</td>
                </tr>
                <tr>
                    <th scope='row'>12</th>
                    <td colspan='3'>Melakukan One-Hot Encoding pada target kategori.</td>
                </tr>
                <tr>
                    <th scope='row'>13</th>
                    <td colspan='3'>Membuat model menggunakan metode LSTM.</td>
                </tr>
                <tr>
                    <th scope='row'>14</th>
                    <td colspan='3'>Melakukan training model menggunakan data training.</td>
                </tr>
                <tr>
                    <th scope='row'>15</th>
                    <td colspan='3'>Melakukan validasi model menggunakan data validasi.</td>
                </tr>
                <tr>
                    <th scope='row'>16</th>
                    <td colspan='3'>Membuat visualisasi validasi data untuk melihat akurasi dan loss yang didapatkan.</td>
                </tr>
                <tr>
                    <th scope='row'>17</th>
                    <td colspan='3'>Melakukan testing model menggunakan data testing.</td>
                </tr>
                <tr>
                    <th scope='row'>18</th>
                    <td colspan='3'>Membuat visualisasi testing data menggunakan time series dan confusion matrix.</td>
                </tr>
            </tbody>
        </table>
    """

st.markdown(table_html, unsafe_allow_html=True)

st.title("Read Data from Firebase")

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
        return 0
    elif 51 <= iaqi <= 100:
        return 1
    else:
        return 2


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
               ["co2", "tvoc", "iaqi_co2", "iaqi_tvoc", "iaqi_category_co2", "iaqi_category_tvoc"]].copy()

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

df_transform.fillna(method="bfill", inplace=True)

st.dataframe(df_transform)

st.header("Data Preprocessing")

feature_co2 = ["co2", "iaqi_co2"]
feature_tvoc = ["tvoc", "iaqi_tvoc"]
y_feature_co2 = "iaqi_category_co2"
y_feature_tvoc = "iaqi_category_tvoc"

# Splitting Data

st.write("Pembagian Data Training dan Data Testing")

X_co2 = df_transform[feature_co2].values
X_tvoc = df_transform[feature_tvoc].values
y_co2 = df_transform[y_feature_co2]
y_tvoc = df_transform[y_feature_tvoc]

# One Hot Encoding

st.write(np.unique(y_co2))
st.write(np.unique(y_tvoc))

y_co2 = to_categorical(y_co2, num_classes=3)
y_tvoc = to_categorical(y_tvoc, num_classes=3)


# Fungsi Data Augmentation
def augment_data(X, noise_level=0.01):
    noise_level = abs(noise_level)
    noise = np.random.normal(loc=0, scale=noise_level, size=X.shape)
    return X + noise


# Augment Data
X_augment_co2 = augment_data(X_co2)
X_augment_tvoc = augment_data(X_tvoc)

# Splitting Data
X_train_co2, X_val_co2, y_train_co2, y_val_co2 = train_test_split(X_co2, y_co2, test_size=0.3, stratify=y_co2)
X_train_tvoc, X_val_tvoc, y_train_tvoc, y_val_tvoc = train_test_split(X_tvoc, y_tvoc, test_size=0.3, stratify=y_tvoc)

# Normalisasi Data
scaler_co2 = MinMaxScaler()
X_train_co2 = scaler_co2.fit_transform(X_train_co2)
X_val_co2 = scaler_co2.transform(X_val_co2)

scaler_tvoc = MinMaxScaler()
X_train_tvoc = scaler_tvoc.fit_transform(X_train_tvoc)
X_val_tvoc = scaler_tvoc.transform(X_val_tvoc)

joblib.dump(scaler_co2, "scaler_co2.pkl")
joblib.dump(scaler_tvoc, "scaler_tvoc.pkl")

X_train_co2 = np.expand_dims(X_train_co2, 1)
X_val_co2 = np.expand_dims(X_val_co2, 1)

X_train_tvoc = np.expand_dims(X_train_tvoc, 1)
X_val_tvoc = np.expand_dims(X_val_tvoc, 1)

st.write("Data Training Label")

st.write(y_train_co2)

st.write("Data Testing Label")

st.write(y_val_co2)

# Model Training

st.header("Model Training", anchor="model-training")

st.write("Model yang digunakan adalah LSTM Classifier")


# Model Training
def lstm_model(units, dropout, input_shape, learning_rate, rdp):
    model = Sequential()

    model.add(Input(shape=input_shape))
    model.add(LSTM(units, return_sequences=True, dropout=dropout, recurrent_dropout=rdp, activation='tanh',
                   return_state=False,
                   stateful=False, unroll=False))
    model.add(LSTM(units, return_sequences=True, dropout=dropout, recurrent_dropout=rdp, activation='tanh',
                   return_state=False,
                   stateful=False, unroll=False))
    model.add(LSTM(units, return_sequences=False, dropout=dropout, recurrent_dropout=rdp, activation='tanh',
                   return_state=False,
                   stateful=False, unroll=False))
    model.add(Dense(3, activation="softmax"))

    model.compile(optimizer=Adam(learning_rate=learning_rate), loss="categorical_crossentropy",
                  metrics=["accuracy"])

    model.summary(print_fn=lambda x: st.text(x))

    return model


st.write(X_train_co2.shape)
st.write(X_train_tvoc.shape)

input_co2 = (X_train_co2.shape[1], X_train_co2.shape[2])
input_tvoc = (X_train_tvoc.shape[1], X_train_tvoc.shape[2])

st.write(input_co2)
st.write(input_tvoc)

model_co2 = lstm_model(32, 0.2, input_co2, 0.001, 0.2)

model_tvoc = lstm_model(32, 0.2, input_tvoc, 0.002, 0.2)


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

st.header("Model Evaluation", anchor="model-evaluation")

history_co2 = model_co2.fit(X_train_co2, y_train_co2, epochs=50, batch_size=32,
                            validation_data=(X_val_co2, y_val_co2),
                            callbacks=[lr_decay_co2, early_stop_co2])

history_tvoc = model_tvoc.fit(X_train_tvoc, y_train_tvoc, epochs=50, batch_size=64,
                              validation_data=(X_val_tvoc, y_val_tvoc),
                              callbacks=[lr_decay_tvoc, early_stop_tvoc])

st.subheader("CO2")

plot_history(history_co2)

st.subheader("TVOC")

plot_history(history_tvoc)

# Prediction

# st.header("Prediction", anchor="prediction")
#
# st.write("Prediksi kategori")
#
# def predict_prob(number):
#     return [number[0], 1 - number[0]]
#
# def predict(model, test_data, actual_data):
#     y_pred = model.predict(test_data)
#     y_pred_proba = np.array(list(map(predict_prob, y_pred)))
#
#     st.write(y_pred)
#
#     st.write(y_pred_proba)
#
#     y_sum = np.sum(y_pred, axis=1)
#
#     st.write(y_sum)
#
#     y_pred_cate = np.argmax(y_pred, axis=1)
#
#     actual = np.argmax(actual_data, axis=1)
#
#     st.write(y_pred.shape)
#
#     # Threshold
#     threshold = 0.7
#     y_pred_classes = (y_pred_proba > threshold).astype(int)
#
#     # Confidence Estimation
#     for i in range(len(y_pred_proba)):
#         print(f"Sample {i}: Class={y_pred_classes[i]}, Probability={y_pred_proba[i]}")
#
#     # Classification Report
#     st.text(classification_report(actual, y_pred_cate, labels=[0, 1, 2],
#                                   target_names=["Good", "Moderate", "Hazardous"]))
#
#     # Confusion Matrix
#
#     st.write("Confusion Matrix")
#
#     fig, ax = plt.subplots(1, 1, figsize=(10, 5))
#     cm = confusion_matrix(actual, y_pred_cate)
#     cmn = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
#     sns.heatmap(cmn, annot=True, fmt='.2f', ax=ax)
#     ax.set_title("Confusion Matrix")
#     ax.set_xlabel("Predicted")
#     ax.set_ylabel("Actual")
#     # Untuk xlabel dan ylabel 1 = good, 2 = moderate, 3 = hazardous
#     ax.set_xticklabels(["Good", "Moderate", "Hazardous"])
#     ax.set_yticklabels(["Good", "Moderate", "Hazardous"])
#     st.pyplot(fig)
#
#     # Time series plot
#
#     st.write("Plot Prediksi per Kategori")
#
#     fig, ax = plt.subplots(1, 1, figsize=(20, 5))
#     colors = ['green', 'yellow', 'red']
#     labels = ["Good", "Moderate", "Hazardous"]
#
#     for i in range(y_pred.shape[1]):
#         ax.plot(y_pred[:, i], label=f"Category {i}", color=colors[i])
#
#     ax.set_title("Prediksi Kategori per Waktu")
#     ax.set_xlabel("Waktu")
#     # X label 5minutes interval
#     ax.set_xticks(np.arange(0, len(y_pred), 5))
#     ax.set_ylabel("Predicted Value")
#     ax.legend(labels)
#     st.pyplot(fig)
#
#
# st.subheader("Prediksi CO2")
#
# predict(model_co2, X_test_augment_co2, y_test_co2)
#
# st.subheader("Prediksi TVOC")
#
# predict(model_tvoc, X_test_augment_tvoc, y_test_tvoc)
#
# # EDA
#
# st.header("Exploratory Data Analysis", anchor="eda")
#
# st.write("Count CO2 per Category bar plot")
#
# fig, ax = plt.subplots(1, 1, figsize=(10, 5))
# sns.countplot(x='iaqi_category_co2', data=df_transform, ax=ax)
# ax.set_title("Count CO2 per Category")
# ax.set_xlabel("Category")
# ax.set_ylabel("Count")
# st.pyplot(fig)
#
# st.write("Count TVOC per Category bar plot")
#
# fig, ax = plt.subplots(1, 1, figsize=(10, 5))
# sns.countplot(x='iaqi_category_tvoc', data=df_transform, ax=ax)
# ax.set_title("Count TVOC per Category")
# ax.set_xlabel("Category")
# ax.set_ylabel("Count")
# st.pyplot(fig)

# Save the model

st.header("Save Model", anchor="save-model")

save_model(model_co2, "model_co2.h5")
save_model(model_tvoc, "model_tvoc.h5")

st.write("Model Saved")
