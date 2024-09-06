import streamlit as st
import pandas as pd
import subprocess
import json

# Cargar clave de la API desde secrets
together_api_key = st.secrets["together"]["api_key"]

# Función para cargar el archivo Excel
def load_excel(file):
    df = pd.read_excel(file)
    return df

# Función para hacer preguntas a la API de Together usando curl
def ask_together_with_curl(api_key, question, context):
    url = "https://api.together.xyz/v1/chat/completions"
    model = "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"
    
    # Preparar los datos en formato JSON
    data = {
        "model": model,
        "messages": [{"role": "user", "content": f"Context: {context}\nQuestion: {question}"}],
        "max_tokens": 2512,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "stop": ["<|eot_id|>"],
        "stream": False
    }
    
    # Ejecutar el comando curl
    curl_command = [
        "curl", "-X", "POST", url,
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data)
    ]
    
    # Capturar la salida de curl
    result = subprocess.run(curl_command, capture_output=True, text=True)
    
    if result.returncode == 0:
        response = json.loads(result.stdout)
        return response.get("choices", [{}])[0].get("message", {}).get("content", "Sin respuesta")
    else:
        return f"Error: {result.stderr}"

# Título de la app
st.title("Preguntas sobre un archivo Excel")

# Cargar archivo Excel
uploaded_file = st.file_uploader("Carga un archivo Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Mostrar datos cargados
    df = load_excel(uploaded_file)
    st.write("Datos cargados:")
    st.dataframe(df)
    
    # Preguntar al usuario
    user_question = st.text_input("Haz una pregunta sobre los datos")
    
    if user_question:
        # Convertir el DataFrame en contexto en texto
        context = df.to_string()
        
        # Hacer la pregunta a la API
        answer = ask_together_with_curl(together_api_key, user_question, context)
        
        # Mostrar la respuesta
        st.write("Respuesta:")
        st.write(answer)
