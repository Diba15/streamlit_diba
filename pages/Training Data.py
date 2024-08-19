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
from keras.layers import Dense, LSTM, BatchNormalization, Activation
from keras.models import Sequential, save_model
from keras.optimizers import Adam
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import MinMaxScaler

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

# features = ["time", "temperature", "tvoc", "hcho", "co2"]

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

refTraining = db.reference("/data/testData/")
refTraining2 = db.reference("/data/Training2/")

data_ref = refTraining.get()

data_ref2 = refTraining2.get()

df = pd.DataFrame(data_ref.values())

df2 = pd.DataFrame(data_ref2.values())

df = pd.concat([df, df2])

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


def highlight_good(s):
    return ['background-color: green' if v == 0 else '' for v in s]


def highlight_moderate(s):
    return ['background-color: yellow' if v == 1 else '' for v in s]


def highlight_hazardous(s):
    return ['background-color: red' if v == 2 else '' for v in s]


st.dataframe(df_filtered.style.apply(highlight_good, subset=["iaqi_category"]).apply(
    highlight_moderate, subset=["iaqi_category"]).apply(highlight_hazardous,
                                                        subset=["iaqi_category"]))

# Count the number of each category of IAQI category

st.write("Jumlah Kategori IAQI")
good = df_filtered[df_filtered["iaqi_category"] == 0].shape[0]
moderate = df_filtered[df_filtered["iaqi_category"] == 1].shape[0]
hazardous = df_filtered[df_filtered["iaqi_category"] == 2].shape[0]

st.write(good, moderate, hazardous)

# Features Engineering

st.header("Features Engineering")

df_transform = df_filtered.loc[:,
               ["co2", "tvoc", "iaqi_co2", "iaqi_tvoc", "iaqi_min", "iaqi_category"]].copy()

st.write("Jumlah Kategori IAQI")
good = df_transform[df_transform["iaqi_category"] == 0].shape[0]
moderate = df_transform[df_transform["iaqi_category"] == 1].shape[0]
hazardous = df_transform[df_transform["iaqi_category"] == 2].shape[0]

st.write(good, moderate, hazardous)

df_transform.fillna(method="bfill", inplace=True)

st.dataframe(df_transform)

st.header("Data Preprocessing")

feature = ["co2", "iaqi_co2", "tvoc", "iaqi_tvoc", "iaqi_min"]
y_feature = "iaqi_category"

# Splitting Data

st.write("Pembagian Data Training dan Data Testing")

X = df_transform[feature].values
y = df_transform[y_feature]

# One Hot Encoding
st.write(np.unique(y))

y = to_categorical(y, num_classes=3)


# Fungsi Data Augmentation
def augment_data(X, noise_level=0.01):
    noise_level = abs(noise_level)
    noise = np.random.normal(loc=0, scale=noise_level, size=X.shape)
    return X + noise


# Augment Data
X_augment_co2 = augment_data(X)

# Splitting Data
X_train, X_val, y_train, y_val = train_test_split(X_augment_co2, y, test_size=0.35, stratify=y, shuffle=True,
                                                  random_state=42)

# Normalisasi Data
scaler = MinMaxScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)

joblib.dump(scaler, "scaler.pkl")

X_train = np.expand_dims(X_train, 1)
X_val = np.expand_dims(X_val, 1)

st.write("Data Training Label")
st.write(y_train)

st.write("Data Validasi Label")
st.write(y_val)

# Hitung jumlah data training dan data validasi yang memiliki label 0, 1, dan 2

st.write("Jumlah Data Training")
st.write(np.unique(np.argmax(y_train, axis=1), return_counts=True))

st.write("Jumlah Data Validasi")
st.write(np.unique(np.argmax(y_val, axis=1), return_counts=True))

# Model Training
st.header("Model Training", anchor="model-training")
st.write("Model yang digunakan adalah LSTM Classifier")


# Model Training
# b = batch, dp = dropout, rdp = recurrent dropout, alpha = learning rate
# in: b, dp, rdp, alpha
# out: LSTM

# LSTM_Model(in: b, dp, rdp, alpha; out: LSTM)
# BEGIN
# 1. LSTM_Input(in: input_shape; out: Input_Layer)
# 2. FOR i = 1 to 2 DO {
#       LSTM(in: b, dp, rdp, rs; out: LSTM_Layer)
# }
# 3. LSTM(in: b, dp, rdp, rs; out: LSTM_Layer)
# 3. LSTM_Dense(in: n_output, activation; out: Output_layer)
# 4. LSTM_Compiler(in: alpha; out: Model)
# END

def lstm_model(units, dropout, input_shape, learning_rate, rdp):
    model = Sequential()

    model.add(Input(shape=input_shape))
    for i in range(2):
        model.add(LSTM(units, return_sequences=True, dropout=dropout, recurrent_dropout=rdp, activation=None,
                       return_state=False, stateful=False, unroll=False))
        model.add(BatchNormalization())
        model.add(Activation("tanh"))
    model.add(LSTM(units, return_sequences=False, dropout=dropout, activation=None, return_state=False,
                   stateful=False, unroll=False))
    model.add(BatchNormalization())
    model.add(Activation("tanh"))
    model.add(Dense(3, activation="softmax"))

    model.compile(optimizer=Adam(learning_rate=learning_rate), loss="categorical_crossentropy",
                  metrics=["accuracy"])

    model.summary(print_fn=lambda x: st.text(x))

    return model


st.write(X_train.shape)

input = (X_train.shape[1], X_train.shape[2])

st.write(input)


def callbacksUnits(patience_lr, min_lr, patience_es, min_delta_es):
    # definisikan ReduceLROnPlateau untuk mengurangi learning rate jika model tidak belajar lagi.
    lr_decay = ReduceLROnPlateau(monitor='val_accuracy',
                                 patience=patience_lr, verbose=1,
                                 factor=0.5, min_lr=min_lr)
    # definisikan EarlyStopping untuk menghentikan training jika model tidak belajar lagi.
    early_stop = EarlyStopping(monitor='val_loss', min_delta=min_delta_es,
                               patience=patience_es, verbose=1, mode='auto',
                               restore_best_weights=True)

    return lr_decay, early_stop


def plot_history(history):
    fig, ax = plt.subplots(1, 2, figsize=(20, 5))

    for i, histories in enumerate(history):
        ax[0].plot(histories.history["accuracy"], label="Training Fold {}".format(i + 1))
        ax[0].plot(histories.history["val_accuracy"], label="Validation Fold {}".format(i + 1), linestyle="--")
    ax[0].set_title("Accuracy")
    ax[0].set_xlabel("Epoch")
    ax[0].set_ylabel("Accuracy")
    ax[0].legend()

    for i, histories in enumerate(history):
        ax[1].plot(histories.history["loss"], label="Training Fold {}".format(i + 1))
        ax[1].plot(histories.history["val_loss"], label="Validation Fold {}".format(i + 1), linestyle="--")
    ax[1].set_title("Loss")
    ax[1].set_xlabel("Epoch")
    ax[1].legend()

    st.pyplot(fig)


st.write("Model Training Selesai")

st.header("Model Evaluation", anchor="model-evaluation")

kf = KFold(n_splits=5, shuffle=True, random_state=42)

all_scores = []
scores = []
histories = []

for train_index, val_index in kf.split(X_train):
    model = lstm_model(32, 0.2, input, 0.001, 0.2)
    lr_decay, early_stop = callbacksUnits(5, 0.01, 20, 0.01)

    history = model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=100, batch_size=32)
    histories.append(history)

    accuracy = history.history['accuracy'][-1]
    val_accuracy = history.history['val_accuracy'][-1]
    all_scores.append(val_accuracy)
    scores.append(accuracy)

    save_model(model, "model.h5")

st.write("Average Training Accuracy: ", np.mean(scores))
st.write("Average Validation Accuracy: ", np.mean(all_scores))

# Plot Learning Curves

plot_history(histories)

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

st.write("Model Saved")
