import streamlit as st
import pandas as pd
import os

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

# --- INTERFAZ DE USUARIO DE STREAMLIT ---
st.title("🥟 Masas Delicias del Caribe, S.R.L.")
st.subheader("Asistente Comercial Inteligente y Cotizador Mayorista")

# Sidebar - Configuración e Información General
with st.sidebar:
    st.header("Sobre la Empresa")
    st.markdown("""**Actividad:** Fabricación y distribución al por mayor de masas para empanadas.
**Vision:** Ser una empresa líder en la fabricación y distribución al por mayor de masas para empanadas en la República Dominicana, reconocida por la calidad de sus productos, la innovación y la confianza de sus clientes comerciales.
**Mision:** Fabricar masas para empanadas de alta calidad, utilizando ingredientes seleccionados y procesos higiénicos que garanticen productos frescos, seguros y uniformes, satisfaciendo las necesidades de supermercados, restaurantes, cafeterías, distribuidores y otros negocios de alimentos.
**Ubicación:** Santo Domingo, República Dominicana.


 tab1, tab2, tab3 = st.tabs(["📊 Cotizador Mayorista", "🤖 Asistente Virtual con IA", "📜 Lista de Precios y Políticas"])

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
            ["Ninguno / Regular", "Al contado (5%)", "Crédito aprobado (3%)"]
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

# TAB 2: ASISTENTE VIRTUAL CON IA
with tab2:
    st.header("Pregúntale al Asistente Comercial de IA")
    st.markdown(
        """Puedes consultarle dudas de precios, pedirle sugerencias de compra, o generar recordatorios de pago.
        *Ejemplo: '¿Cuánto me costarían 500 paquetes pagando al contado?' o 'Redacta un recordatorio amable para un cliente con balance atrasado'.*"""
    )

    user_prompt = st.text_area("¿En qué puedo ayudarte hoy?", height=100, placeholder="Escribe tu consulta aquí...")

    if st.button("Enviar Consulta"):
       

                    contexto_prompt = f"""
                    Eres el Asistente Comercial Virtual de la empresa 'Masas Delicias del Caribe, S.R.L.'.
                    Respondes en español claro y profesional.

                    REGLAS IMPORTANTES:
                    1. NO inventes precios. Utiliza estrictamente la siguiente tabla de precios de referencia:
                       - 1 a 49 paquetes: RD$ 120 por paquete
                       - 50 a 99 paquetes: RD$ 112 por paquete
                       - 100 a 249 paquetes: RD$ 105 por paquete
                       - 250 a 499 paquetes: RD$ 98 por paquete
                       - 500 a 999 paquetes: RD$ 92 por paquete
                       - 1,000 o más paquetes: RD$ 85 por paquete
                    2. Descuentos por forma de pago (adicionales):
                       - Al contado: 5% adicional.
                       - A crédito aprobado: 3% adicional.
                    3. Si el usuario te pregunta sobre la aprobación de créditos, aclara amablemente que tú, como IA, no apruebas créditos ni confirmas pagos directos, y que deben comunicarse con el personal autorizado.
                    4. Si te piden redactar un mensaje de cobro o recordatorio de pago atrasado, hazlo de forma sumamente cordial, respetuosa y profesional.

                    Consulta del usuario: {user_prompt}
                    """

                    response = client.models.generate_content(
                        model='gemini-2.5-flash-lite',
                        contents=contexto_prompt,
                    )
                    st.markdown("### Respuesta del Asistente:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Ocurrió un error al contactar con la API de Gemini: {e}")

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
        st.markdown("""- **Al Contado:** 5% de descuento adicional.
- **Crédito Aprobado:** 3% de descuento adicional.
- *Ambos descuentos se aplican sobre el precio correspondiente a la escala de volumen.*""")

    st.info("""**Políticas Generales:**
- El precio de la cotización final se determina según la escala alcanzada por el total del pedido.
- Los créditos son autorizados única y exclusivamente por el departamento administrativo de la empresa.""")
