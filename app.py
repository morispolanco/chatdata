import streamlit as st
import pandas as pd
import requests
import json

# Configuración de la página
st.set_page_config(page_title="Excel Q&A App", page_icon="📊", layout="wide")

# Título de la aplicación
st.title("Excel Q&A App")

# Función para realizar la consulta a la API de Together
def query_together_api(prompt, api_key):
    url = "https://api.together.xyz/inference"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "togethercomputer/llama-2-70b-chat",
        "prompt": prompt,
        "max_tokens": 512,
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Esto lanzará una excepción para códigos de estado HTTP no exitosos
        response_json = response.json()
        
        # Añadir depuración
        st.write("Respuesta completa de la API:", response_json)
        
        if 'output' in response_json and 'choices' in response_json['output'] and len(response_json['output']['choices']) > 0:
            return response_json['output']['choices'][0]['text']
        else:
            st.error("La respuesta de la API no tiene el formato esperado.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error al hacer la solicitud a la API: {e}")
        return None
    except json.JSONDecodeError:
        st.error("Error al decodificar la respuesta JSON de la API.")
        return None
    except Exception as e:
        st.error(f"Error inesperado: {e}")
        return None

# Función para leer el archivo Excel
def read_excel_file(file):
    try:
        # Intenta leer el archivo como .xlsx
        return pd.read_excel(file, engine='openpyxl')
    except Exception as e:
        try:
            # Si falla, intenta leer como .xls
            return pd.read_excel(file, engine='xlrd')
        except Exception as e:
            st.error(f"No se pudo leer el archivo. Error: {e}")
            return None

# Cargar el archivo Excel
uploaded_file = st.file_uploader("Carga tu archivo Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Leer el archivo Excel
    df = read_excel_file(uploaded_file)
    if df is not None:
        st.success("Archivo cargado correctamente!")

        # Mostrar las primeras filas del DataFrame
        st.subheader("Vista previa de los datos:")
        st.dataframe(df.head())

        # Área para ingresar la pregunta
        user_question = st.text_input("Haz una pregunta sobre los datos:")

        if user_question:
            # Preparar el prompt para la API
            prompt = f"""Basado en los siguientes datos:

{df.head().to_string()}

Por favor, responde a la siguiente pregunta:
{user_question}

Proporciona una respuesta concisa y precisa basada únicamente en la información disponible en los datos proporcionados."""

            # Obtener la clave API de los secrets de Streamlit
            api_key = st.secrets["TOGETHER_API_KEY"]

            # Realizar la consulta a la API
            with st.spinner("Analizando tu pregunta..."):
                response = query_together_api(prompt, api_key)

            # Mostrar la respuesta
            if response:
                st.subheader("Respuesta:")
                st.write(response)

else:
    st.info("Por favor, carga un archivo Excel para comenzar.")

# Instrucciones de uso
st.sidebar.header("Instrucciones de uso")
st.sidebar.markdown("""
1. Carga tu archivo Excel (.xlsx o .xls) usando el botón de carga.
2. Una vez cargado, verás una vista previa de los datos.
3. Escribe tu pregunta en el campo de texto.
4. La aplicación analizará los datos y responderá a tu pregunta.
5. ¡Explora tus datos haciendo múltiples preguntas!
""")

# Nota sobre la privacidad
st.sidebar.header("Nota de privacidad")
st.sidebar.markdown("""
Esta aplicación utiliza la API de Together para procesar tus preguntas.
No almacenamos ningún dato de tu archivo Excel. Toda la información se procesa de forma temporal y se elimina después de cada sesión.
""")
