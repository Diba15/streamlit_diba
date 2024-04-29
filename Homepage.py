import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title='Home', layout='wide')

st.title('Test Streamlit')

st.write(
    "Website Test Streamlit, yang bertujuan untuk mempelajari bagaimana streamlit bekerja dan bagaimana cara "
    "menggunakan nya secara efektif.")

st.header("Test Macam-macam fitur dalam Streamlit", divider='red')

st.write("Disini kita akan mencoba beberapa fitur yang dapat digunakan dalam Streamlit.")

st.subheader("Data Frame")

st.write(pd.DataFrame({
    'Nama': ["Dimas Bagas", "Test1", "Test2", "Test3"],
    'NIM': ["1301228515", "1301228512", "1301228513", "1301228511"]
}))

st.subheader("Penulisan Derajat Temperature")

st.metric(label="Temperature", value="70 °F", delta="1.2 °F")

st.subheader("Test Forms")

with st.form(key="login_form"):
    username = st.text_input("Username")
    password = st.text_input("password", type="password")
    st.form_submit_button("Submit")

