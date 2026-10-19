import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(
    page_title="Asistente Comercial - Masas Delicias del Caribe",
    page_icon="🥟",
    layout="wide"
)

# --- LÓGICA DE NEGOCIO (PRECIOS Y COTIZADOR) ---
def obtener_precio_base(cantidad):
    if cantidad >= 1000:
        return 85.0
    elif cantidad >= 500:
        return 92.0
    elif cantidad >= 250:
        return 98.0
    elif cantidad >= 100:
        return 105.0
    elif cantidad >= 50:
        return 112.0
    elif cantidad >= 1:
        return 120.0
    return 0.0


def calcular_cotizacion(cantidad, forma_pago):
    precio_unitario = obtener_precio_base(cantidad)
    subtotal = cantidad * precio_unitario

    descuento_porcentaje = 0.0
    if forma_pago == "Al contado (3%)":
        descuento_porcentaje = 0.03
    elif forma_pago == "Crédito aprobado (1%)":
        descuento_porcentaje = 0.01

    descuento_monto = subtotal * descuento_porcentaje
    total = subtotal - descuento_monto
    ahorro_total = (120.0 * cantidad) - total if cantidad > 0 else 0.0

    return precio_unitario, subtotal, descuento_monto, total, ahorro_total


tab1, tab3 = st.tabs(["📊 Cotizador Mayorista", "📜 Lista de Precios y Políticas"])

# TAB 1: COTIZADOR
with tab1:
    st.header("Calculadora de Cotizaciones")
    col1, col2 = st.columns(2)

    with col1:
        cantidad = st.number_input(
            "Cantidad de paquetes (Cada paquete contiene 12 unidades):",
            min_value=1,
            max_value=100000,
            value=100,
            step=50
        )

        forma_pago = st.selectbox(
            "Forma de pago:",
            ["Ninguno / Regular", "Al contado (3%)", "Crédito aprobado (1%)"]
        )

    with col2:
        precio_unit, sub, desc, total, ahorro = calcular_cotizacion(cantidad, forma_pago)

        st.markdown(f"### Resumen de la Cotización")
        st.metric(label="Total a Pagar", value=f"RD$ {total:,.2f}")
        st.write(f"**Precio por paquete:** {precio_unit:,.2f}")
        st.write(f"**Subtotal inicial:** {sub:,.2f}")
        st.write(f"**Descuento aplicado:** {desc:,.2f}")
        if ahorro > 0:
            st.success(f"🎉 ¡Estás ahorrando RD$ {ahorro:,.2f} comparado con el precio base regular!")

        st.caption("Nota: Los precios son ficticios y no incluyen impuestos ni transporte.")

# TAB 3: LISTA DE PRECIOS Y POLÍTICAS
with tab3:
    st.header("Políticas Comerciales de Referencia")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("Precios por Volumen")
        df_precios = pd.DataFrame({
            "Rango de Paquetes": ["1-49", "50-99", "100-249", "250-499", "500-999", "1,000+"],
            "Precio por Unidad (RD$)": [120.00, 112.00, 105.00, 98.00, 92.00, 85.00]
        })
        st.table(df_precios)

    with col_t2:
        st.subheader("Descuentos Adicionales")
        st.markdown("""- **Al Contado:** 3% de descuento adicional.
- **Crédito Aprobado:** 1% de descuento adicional.
- *Ambos descuentos se aplican sobre el precio correspondiente a la escala de volumen.*""")

    st.info("""**Políticas Generales:**
- El precio de la cotización final se determina según la escala alcanzada por el total del pedido.
- Los créditos son autorizados única y exclusivamente por el departamento administrativo de la empresa.""")
