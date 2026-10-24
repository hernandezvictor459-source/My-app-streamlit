from google.genai import types

# Prompt utilizando la base de conocimiento cargada
contexto_completo = "\n".join(documentos_docx[:15])  # Limitamos párrafos para evitar sobrecarga de tokens
prompt_llm = f"""Actúa como el asistente virtual experto de Masas Delicias del Caribe.
Usa el siguiente contexto para responder a la consulta del usuario de forma amable y profesional.

Contexto:
{contexto_completo}

Consulta del usuario: ¿Qué tipos de productos ofrece Masas Delicias del Caribe?
"""

response_llm = client.models.generate_content(
    model=MODELO,
    contents=prompt_llm
)

print("--- Respuesta directa del LLM ---")
print(response_llm.text)
