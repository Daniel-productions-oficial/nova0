import requests
import json
import os
import time
import pyttsx3

# Configuración
API_URL = "http://localhost:8000/v1/completions"

# --- INICIALIZACIÓN GLOBAL DEL MOTOR ---
engine = pyttsx3.init()

def configurar_voz_espanol():
    """Busca una voz en español disponible en el sistema."""
    try:
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'es' in voice.id.lower() or 'spanish' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                return True
    except Exception as e:
        print(f"Error configurando voz: {e}")
    return False

# Aplicar configuración inicial
configurar_voz_espanol()
engine.setProperty('rate', 155) # Un poco más rápido para fluidez en streaming
engine.setProperty('volume', 1.0)

def hablar(texto):
    """Función atómica para procesar un fragmento de texto."""
    texto = texto.strip()
    if not texto:
        return
    try:
        # Nota: pyttsx3 es síncrono, detendrá el print hasta que termine de hablar
        engine.say(texto)
        engine.runAndWait()
    except Exception as e:
        print(f"\n[Error de Voz] {e}")

def chat():
    print("--- KAMUTINI CLIENT (Voz por Párrafos) ---")
    while True:
        prompt = input("\n\nTú: ")
        if prompt.lower() in ["salir", "exit", "quit"]: 
            break

        payload = {"prompt": prompt, "stream": True} # Aseguramos modo stream
        
        print("\nKamutini: ", end="", flush=True)
        
        # Búfer para acumular texto hasta encontrar un salto de línea
        bufer_voz = ""

        try:
            with requests.post(API_URL, json=payload, stream=True) as r:
                for line in r.iter_lines():
                    if line:
                        # Limpiamos el prefijo 'data: ' si el servidor lo envía (estándar SSE)
                        decoded_line = line.decode("utf-8")
                        if decoded_line.startswith("data: "):
                            decoded_line = decoded_line[6:]
                        
                        try:
                            chunk_data = json.loads(decoded_line)
                            if "choices" in chunk_data:
                                texto_chunk = chunk_data["choices"][0]["text"]
                                
                                # 1. Mostrar en consola inmediatamente
                                print(texto_chunk, end="", flush=True)
                                
                                # 2. Acumular para la voz
                                bufer_voz += texto_chunk
                                
                                # 3. Si detectamos un salto de línea, hablamos ese párrafo
                                if "\n" in bufer_voz:
                                    # Dividimos por si hay múltiples saltos
                                    parrafos = bufer_voz.split("\n")
                                    # Hablamos todos menos el último (que podría estar incompleto)
                                    for p in parrafos[:-1]:
                                        hablar(p)
                                    # El último fragmento vuelve al búfer
                                    bufer_voz = parrafos[-1]
                        
                        except json.JSONDecodeError:
                            continue

            # Hablar el remanente final después de que el stream cierre
            if bufer_voz.strip():
                hablar(bufer_voz)

        except requests.exceptions.ConnectionError:
            print("\n[Error] El servidor no responde. ¿Iniciaste el backend?")

if __name__ == "__main__":
    chat()
