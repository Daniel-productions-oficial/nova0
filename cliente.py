import requests
import json
import os
import pygame
import time
from gtts import gTTS
import tempfile
# Configuración
API_URL = "http://localhost:8000/v1/completions"

def hablar(texto):
    """Convierte texto a audio localmente y lo reproduce."""
    if not texto.strip():
        return

    try:
        # 1. Crear el objeto TTS
        tts = gTTS(text=texto, lang="es", tld="com.mx") # TLD de México para mejor acento
        
        # 2. Guardar en un archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            temp_path = fp.name
            tts.save(temp_path)

        # 3. Reproducir con Pygame
        pygame.mixer.init()
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()

        # Esperar a que termine de hablar
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        pygame.mixer.quit()

        # 4. Limpieza: Borrar archivo temporal
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    except Exception as e:
        print(f"\n[Error de Voz] No se pudo generar el audio: {e}")

def chat():
    print("--- KAMUTINI CLIENT (Local TTS) ---")
    while True:
        prompt = input("\n\nTú: ")
        if prompt.lower() in ["salir", "exit"]: break

        payload = {"prompt": prompt}
        respuesta_completa = ""

        print("\nKamutini: ", end="", flush=True)

        try:
            with requests.post(API_URL, json=payload, stream=True) as r:
                for line in r.iter_lines():
                    if line:
                        chunk_data = json.loads(line.decode("utf-8"))
                        if "choices" in chunk_data:
                            texto = chunk_data["choices"][0]["text"]
                            print(texto, end="", flush=True)
                            respuesta_completa += texto
            
            # Al terminar el texto, Kamutini habla
            hablar(respuesta_completa)

        except requests.exceptions.ConnectionError:
            print("\n[Error] No se pudo conectar con el servidor. ¿Está encendido?")

if __name__ == "__main__":
    chat()
