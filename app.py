# TAB 2: ASISTENTE VIRTUAL CON IA
with tab2:
    st.header("Pregúntale al Asistente Comercial de IA")

    st.markdown("""
    Puedes consultarle dudas de precios, pedirle sugerencias de compra, o generar recordatorios de pago.

    *Ejemplos:*
    - ¿Cuánto me costarían 500 paquetes pagando al contado?
    - Redacta un recordatorio amable para un cliente con balance atrasado.
    - ¿Cuál es el precio para 1,000 paquetes?
    """)

    user_prompt = st.text_area(
        "¿En qué puedo ayudarte hoy?",
        height=100,
        placeholder="Escribe tu consulta aquí..."
    )

    if st.button("Enviar Consulta"):

        api_key = os.environ.get("GOOGLE_API_KEY", "")

        if not api_key:
            st.error(
                "⚠️ No se encontró la variable de entorno GOOGLE_API_KEY en el servidor."
            )

        elif not user_prompt.strip():
            st.warning("Por favor escribe una consulta.")
        else:
            with st.spinner("Procesando respuesta con Gemini..."):
                try:

                    client = genai.Client(api_key=api_key)

                    contexto_prompt = f"""
Eres el Asistente Comercial Virtual de la empresa 'Masas Delicias del Caribe, S.R.L.'.

Respondes siempre en español claro, cordial y profesional.

REGLAS IMPORTANTES:

1. NO inventes precios. Utiliza estrictamente la siguiente tabla de precios:

- 1 a 49 paquetes: RD$120 por paquete
- 50 a 99 paquetes: RD$112 por paquete
- 100 a 249 paquetes: RD$105 por paquete
- 250 a 499 paquetes: RD$98 por paquete
- 500 a 999 paquetes: RD$92 por paquete
- 1,000 o más paquetes: RD$85 por paquete

2. Descuentos adicionales:

- Al contado: 5%
- Crédito aprobado: 3%

3. Si preguntan por aprobación de crédito, explica que las aprobaciones son gestionadas exclusivamente por el departamento administrativo.

4. Si solicitan mensajes de cobro o recordatorios de pago, redacta textos muy cordiales, respetuosos y profesionales.

5. Cuando sea posible, realiza cálculos automáticamente utilizando la información suministrada.

Consulta del usuario:
{user_prompt}
"""

                    response = client.models.generate_content(
                        model="gemini-2.5-flash-lite",
                        contents=contexto_prompt
                    )

                    st.markdown("### Respuesta del Asistente")
                    st.write(response.text)

                except Exception as e:
                    st.error(
                        f"Ocurrió un error al contactar con Gemini: {str(e)}"
                    )
