eimport streamlit as st
import pandas as pd
from google import genai
import os

# Configuración de página
st.set_page_config(
    page_title="Asistente Comercial - Masas Delicias del Caribe",
    page_icon="🥟",
    layout="wide"
)

# Inicializar session_state para API key e historial
if "GOOGLE_API_KEY" not in st.session_state:
    st.session_state.GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
if "history" not in st.session_state:
    st.session_state.history = []  # lista de (pregunta, respuesta)

# --- LÓGICA DE NEGOCIO (PRECIOS Y COTIZADOR) ---
def obtener_precio_base(cantidad_paquetes):
    # Retorna precio por paquete según escala
    if cantidad_paquetes >= 1000:
        return 85.0
    elif cantidad_paquetes >= 500:
        return 92.0
    elif cantidad_paquetes >= 250:
        return 98.0
    elif cantidad_paquetes >= 100:
        return 105.0
    elif cantidad_paquetes >= 50:
        return 112.0
    elif cantidad_paquetes >= 1:
        return 120.0
    return 0.0

def calcular_cotizacion(cantidad_paquetes, forma_pago):
    precio_unitario = obtener_precio_base(cantidad_paquetes)
    subtotal = cantidad_paquetes * precio_unitario

    descuento_porcentaje = 0.0
    if forma_pago == "Al contado (3%)":
        descuento_porcentaje = 0.03
    elif forma_pago == "Crédito aprobado (1%)":
        descuento_porcentaje = 0.01

    descuento_monto = subtotal * descuento_porcentaje
    total = subtotal - descuento_monto
    # Ahorro comparado con precio base "regular" (120 por paquete)
    ahorro_total = (120.0 * cantidad_paquetes) - total if cantidad_paquetes > 0 else 0.0

    return precio_unitario, subtotal, descuento_monto, total, ahorro_total

# --- INTERFAZ DE USUARIO DE STREAMLIT ---
st.title("🥟 Masas Delicias del Caribe, S.R.L.")
st.subheader("Asistente Comercial Inteligente y Cotizador Mayorista")

# Sidebar - Configuración e Información General
with st.sidebar:
    st.header("Sobre la Empresa")
    st.markdown("""**Actividad:** Fabricación y distribución al por mayor de masas para empanadas.
**Ubicación:** Santo Domingo, República Dominicana.
**Sitio web de referencia:** [anko.com.tw](https://anko.com.tw)

*Modelo enfocado exclusivamente a ventas al por mayor (B2B).*""")

    st.markdown("---")
    st.subheader("🔑 API Key de Gemini")
    st.caption("La API Key puede guardarse temporalmente durante la sesión (no se guarda en repositorios).")
    api_key_input = st.text_input(
        "Introduce tu GOOGLE_API_KEY:",
        value=st.session_state.GOOGLE_API_KEY,
        type="password"
    )
    if st.button("Guardar API Key"):
        st.session_state.GOOGLE_API_KEY = api_key_input.strip()
        st.success("API Key guardada en la sesión (temporal).")

    if st.session_state.GOOGLE_API_KEY:
        st.write("API Key cargada ✅")
    else:
        st.info("No hay API Key cargada. Proporciona una para usar el asistente IA.")

tab1, tab2, tab3 = st.tabs(["📊 Cotizador Mayorista", "🤖 Asistente Virtual con IA", "📜 Lista de Precios y Políticas"])

# TAB 1: COTIZADOR
with tab1:
    st.header("Calculadora de Cotizaciones")
    st.markdown("Nota: cada paquete contiene 12 unidades. Los precios se muestran por paquete.")
    col1, col2 = st.columns([1, 1])

    with col1:
        cantidad = st.number_input(
            "Cantidad de paquetes:",
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

        st.markdown("### Resumen de la Cotización")
        st.metric(label="Total a Pagar (RD$)", value=f"RD$ {total:,.2f}")
        st.write(f"**Precio por paquete:** RD$ {precio_unit:,.2f}")
        st.write(f"**Subtotal inicial:** RD$ {sub:,.2f}")
        st.write(f"**Descuento aplicado:** RD$ {desc:,.2f}")
        if ahorro > 0:
            st.success(f"🎉 ¡Estás ahorrando RD$ {ahorro:,.2f} comparado con RD$ 120 por paquete!")
        st.caption("Los precios son referenciales, no incluyen impuestos ni transporte. Contacta al departamento comercial para cotizaciones formales.")

# TAB 2: ASISTENTE VIRTUAL CON IA
with tab2:
    st.header("Pregúntale al Asistente Comercial de IA")
    st.markdown(
        "Puedes consultarle dudas de precios, pedir sugerencias de compra o generar recordatorios de pago. " +
        "Ejemplos: '¿Cuánto me costarían 500 paquetes pagando al contado?' o 'Redacta un recordatorio amable para un cliente con balance atrasado'."
    )

    user_prompt = st.text_area("¿En qué puedo ayudarte hoy?", height=120, placeholder="Escribe tu consulta aquí...")
    send_col, clear_col = st.columns([1, 1])
    with send_col:
        if st.button("Enviar Consulta"):
            final_key = st.session_state.GOOGLE_API_KEY or os.environ.get("GOOGLE_API_KEY", "")
            if not final_key:
                st.error("⚠️ Por favor, introduce y guarda tu GOOGLE_API_KEY en la barra lateral para usar el asistente con IA.")
            elif not user_prompt.strip():
                st.warning("Escribe una consulta antes de enviar.")
            else:
                with st.spinner("Procesando respuesta con Gemini..."):
                    try:
                        client = genai.Client(api_key=final_key)

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
   - Al contado: 3% adicional.
   - A crédito aprobado: 1% adicional.
3. Si el usuario pregunta sobre la aprobación de créditos, aclara que la IA no aprueba créditos ni confirma pagos; debe remitirse al personal autorizado.
4. Redacta mensajes de cobro de forma cordial, respetuosa y profesional.

Consulta del usuario:
{user_prompt}
"""
                        response = client.models.generate_content(
                            model='gemini-2.5-flash-lite',
                            contents=contexto_prompt,
                        )

                        # Mostrar respuesta (depende de la forma en que la API devuelva el texto)
                        respuesta_texto = getattr(response, "text", None) or str(response)
                        st.markdown("### Respuesta del Asistente:")
                        st.write(respuesta_texto)

                        # Guardar en historial
                        st.session_state.history.insert(0, (user_prompt, respuesta_texto))
                    except Exception as e:
                        st.error(f"Ocurrió un error al contactar con la API de Gemini: {e}")

    with clear_col:
        if st.button("Limpiar historial"):
            st.session_state.history = []
            st.success("Historial limpiado.")

    # Mostrar historial
    if st.session_state.history:
        st.markdown("#### Historial de consultas (últimas primero)")
        for i, (q, r) in enumerate(st.session_state.history[:20], start=1):
            with st.expander(f"#{i} — {q[:80]}"):
                st.write("**Pregunta:**")
                st.write(q)
                st.write("**Respuesta:**")
                st.write(r)

# TAB 3: LISTA DE PRECIOS Y POLÍTICAS
with tab3:
    st.header("Políticas Comerciales de Referencia")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("Precios por Volumen (por paquete)")
        df_precios = pd.DataFrame({
            "Rango de Paquetes": ["1-49", "50-99", "100-249", "250-499", "500-999", "1,000+"],
            "Precio por Paquete (RD$)": [120.00, 112.00, 105.00, 98.00, 92.00, 85.00]
        })
        st.table(df_precios)

    with col_t2:
        st.subheader("Descuentos Adicionales")
        st.markdown("""
- **Al Contado:** 3% de descuento adicional.
- **Crédito Aprobado:** 1% de descuento adicional.
- *Ambos descuentos se aplican sobre el precio correspondiente a la escala de volumen.*
""")

    st.info("""
**Políticas Generales:**
- El precio final de la cotización se determina según la escala alcanzada por el total del pedido (en paquetes).
- Los créditos son autorizados única y exclusivamente por el departamento administrativo de la empresa.
- Las cotizaciones informales aquí generadas son referenciales; para cotizaciones formales y condiciones comerciales, contacte al área comercial.
""")
