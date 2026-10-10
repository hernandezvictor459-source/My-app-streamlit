import streamlit as st

st.title("¡Hola! ,IA 👋")
nombre = st.text_input("¿Como te llamas?")
if nombre:
   st.write(f"¡Hola, {nombre}!Mi primera app del master")
