import streamlit as st

st.title("¡Hola! ,Soy Estudiante de Machine Learning 👋")
nombre = st.text_input("¿Como te llamas?")
if nombre:
    st.write(f"¡Hola, {nombre}! Esta es mi primera app del master.")
