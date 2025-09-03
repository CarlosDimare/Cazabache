# cazabache.py
# Este programa monitorea la entrada de audio y detecta periodos de silencio prolongados.
# Dependencias: sounddevice, numpy, colorama, requests

import sounddevice as sd
import numpy as np
import time
import sys
import colorama
import requests
import json
from datetime import datetime

# --- Configuración ---
# Umbral de RMS para ser considerado silencio. Este valor requiere ajuste y depende
# del nivel de ruido de fondo de tu sistema. Un valor entre 100 y 1000 es un buen punto de partida.
UMBRAL_SILENCIO = 50

# Duración en segundos para que un silencio dispare la alerta.
DURACION_SILENCIO_SEGUNDOS = 59

# Parámetros de audio
SAMPLERATE = 44100
CANALES = 1
TIPO_DATO = 'int16'
BLOQUE_MS = 200  # Procesar audio en bloques de 200ms

# --- Configuración VU Meter ---
VU_METER_WIDTH = 50     # Ancho del VU meter en caracteres

# --- Configuración Telegram ---
# TODO: Configurar estos valores con tus datos reales de Telegram
TELEGRAM_BOT_TOKEN = "8496537219:AAGqbSa0OTOgNgQ5-TqN_tGZ0vMWjLL7_BE"  # Obtener de @BotFather
TELEGRAM_CHAT_ID = "-4950998662"      # ID del chat donde enviar mensajes

# --- Variables de Estado ---
estado = {
    'tiempo_inicio_silencio': None,
    'alerta_enviada': False,
    'ultimo_rms': 0
}

def mostrar_banner():
   """Muestra el banner de Cazabache al iniciar el programa.""" 
   banner = """
╔══════════════════════════════════════════════════╗
║                                                  ║
║     ██████╗ █████╗ ███████╗ █████╗               ║
║    ██╔════╝██╔══██╗╚══███╔╝██╔══██╗              ║
║    ██║     ███████║  ███╔╝ ███████║              ║
║    ██║     ██╔══██║ ███╔╝  ██╔══██║              ║
║    ╚██████╗██║  ██║███████╗██║  ██║              ║
║     ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝              ║
║                                                  ║
║    ██████╗  █████╗  ██████╗██╗  ██╗███████╗      ║
║    ██╔══██╗██╔══██╗██╔════╝██║  ██║██╔════╝      ║
║    ██████╔╝███████║██║     ███████║█████╗        ║
║    ██╔══██╗██╔══██║██║     ██╔══██║██╔══╝        ║
║    ██████╔╝██║  ██║╚██████╗██║  ██║███████╗      ║
║    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝      ║
║                                                  ║
║                            🎶 Dimare             ║
╚══════════════════════════════════════════════════╝
"""
   
   RED = '\033[91m'
   RESET = '\033[0m'
   print(f"{RED}{banner}{RESET}")

def enviar_mensaje_telegram(mensaje):
    """
    Envía un mensaje a través de Telegram Bot API.
    
    Args:
        mensaje (str): El mensaje a enviar
    
    Returns:
        bool: True si el mensaje se envió correctamente, False en caso contrario
    """
    # Verificar si los datos de Telegram están configurados
    if TELEGRAM_BOT_TOKEN == "TU_BOT_TOKEN_AQUI" or TELEGRAM_CHAT_ID == "TU_CHAT_ID_AQUI":
        print(f"\n⚠️  TELEGRAM NO CONFIGURADO - Mensaje que se enviaría:")
        print(f"📱 {mensaje}")
        print("💡 Para configurar Telegram, edita las variables TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': mensaje,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"\n✅ Mensaje enviado por Telegram")
            return True
        else:
            print(f"\n❌ Error al enviar mensaje por Telegram: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error de conexión con Telegram: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error inesperado al enviar mensaje: {e}")
        return False

def print_vumetro(rms_level, width=VU_METER_WIDTH):
    """
    Imprime una barra de vúmetro ASCII en la consola estilo am.py.
    
    Args:
        rms_level (float): Nivel RMS actual del audio
        width (int): Ancho de la barra en caracteres
    """
    if rms_level < 1:
        rms_level = 1

    # Convertir RMS a dBFS (similar a am.py)
    dbfs = 20 * np.log10(rms_level / 32767)
    min_db, max_db = -60, 0
    level = max(0.0, min(1.0, (dbfs - min_db) / (max_db - min_db)))

    # Crear la barra
    bar_length = int(level * width)
    bar = '█' * bar_length
    empty_bar = ' ' * (width - bar_length)
    
    # Determinar color basado en el nivel
    color = '\033[91m'  # Rojo (always red)
    
    RESET = '\033[0m'
    
    # Imprimir todo en una línea que se sobrescribe
    line = f'Vol: |{color}{bar}{RESET}{empty_bar}|'
    print(line, end='\r', flush=True)

def callback_audio(indata, frames, time_info, status):
    """
    Esta función es llamada por sounddevice para cada nuevo bloque de audio.
    Toda la lógica de detección de silencio ocurre aquí.
    """
    if status:
        print(status, file=sys.stderr)

    # Calcular el volumen (RMS) del bloque actual
    volumen_rms = np.sqrt(np.mean(indata.astype(np.float64)**2))
    estado['ultimo_rms'] = volumen_rms
    
    # Mostrar el VU meter
    print_vumetro(volumen_rms)

    # Lógica de detección de silencio
    if volumen_rms < UMBRAL_SILENCIO:
        # El audio está por debajo del umbral de silencio.
        if estado['tiempo_inicio_silencio'] is None:
            # El silencio acaba de empezar. Guardamos cuándo.
            estado['tiempo_inicio_silencio'] = time.time()
        else:
            # El silencio continúa. Verificamos si ha superado la duración configurada.
            tiempo_silencio_actual = time.time() - estado['tiempo_inicio_silencio']
            if tiempo_silencio_actual > DURACION_SILENCIO_SEGUNDOS:
                if not estado['alerta_enviada']:
                    # Si ha superado la duración y no hemos enviado una alerta para este
                    # periodo de silencio, la enviamos ahora.
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    mensaje_alerta = f"🚨 <b>ALERTA CAZABACHE - QUILOMBO EN PUERTA !</b>\n\n" \
                                   f"⏰ Hora: {timestamp}\n" \
                                   f"🔇 Silencio detectado por más de {DURACION_SILENCIO_SEGUNDOS} segundos\n" \
                                   f"📊 Último RMS: {volumen_rms:.0f} (umbral: {UMBRAL_SILENCIO})"
                    
                    print(f"\n🚨 ¡ALERTA! Silencio detectado por más de {DURACION_SILENCIO_SEGUNDOS} segundos!")
                    enviar_mensaje_telegram(mensaje_alerta)
                    estado['alerta_enviada'] = True  # Marcamos que la alerta fue enviada.
    else:
        # El audio está por encima del umbral (hay sonido).
        if estado['tiempo_inicio_silencio'] is not None:
            # El silencio se ha roto. Reseteamos el estado.
            tiempo_silencio_total = time.time() - estado['tiempo_inicio_silencio']
            estado['tiempo_inicio_silencio'] = None
            estado['alerta_enviada'] = False

def mostrar_configuracion():
    """Muestra la configuración actual del programa."""
    print("📋 CONFIGURACIÓN:")
    print(f"   • Umbral de silencio (RMS): {UMBRAL_SILENCIO}")
    print(f"   • Alerta tras: {DURACION_SILENCIO_SEGUNDOS} segundos de silencio")
    print(f"   • Sample rate: {SAMPLERATE} Hz")
    print(f"   • Canales: {CANALES}")
    
    # Estado de configuración de Telegram
    telegram_configurado = (TELEGRAM_BOT_TOKEN != "TU_BOT_TOKEN_AQUI" and 
                           TELEGRAM_CHAT_ID != "TU_CHAT_ID_AQUI")
    
    if telegram_configurado:
        print(f"   • Telegram: ✅ Configurado")
    else:
        print(f"   • Telegram: ❌ No configurado")
        print(f"     💡 Para configurar:")
        print(f"        1. Crear bot con @BotFather")
        print(f"        2. Editar TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID")
    
    print()

def test_telegram():
    """Función para probar la conectividad con Telegram."""
    print("🧪 Probando conexión con Telegram...")
    mensaje_test = f"🧪 Test de Cazabache - {datetime.now().strftime('%H:%M:%S')}"
    
    if enviar_mensaje_telegram(mensaje_test):
        print("✅ Test de Telegram exitoso")
    else:
        print("❌ Test de Telegram falló")

def mostrar_dispositivos_audio():
    """Muestra los dispositivos de audio disponibles."""
    print("🎤 DISPOSITIVOS DE AUDIO:")
    try:
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:  # Solo mostrar dispositivos de entrada
                device_type = "🎤"
                default_marker = " (DEFAULT)" if i == sd.default.device[0] else ""
                print(f"   {i}: {device_type} {device['name']}{default_marker}")
    except Exception as e:
        print(f"   ❌ Error al obtener dispositivos: {e}")
    print()

def main():
    """Función principal que configura y ejecuta el stream de audio."""
    colorama.init()  # Initialize colorama
    mostrar_banner()
    
    # Opción para test de Telegram
    if len(sys.argv) > 1 and sys.argv[1] == "--test-telegram":
        test_telegram()
        return
    
    # Opción para mostrar configuración detallada
    if len(sys.argv) > 1 and sys.argv[1] == "--config":
        mostrar_configuracion()
        mostrar_dispositivos_audio()
        return

    try:
        with sd.InputStream(
            samplerate=SAMPLERATE,
            blocksize=int(SAMPLERATE * BLOQUE_MS / 1000),
            channels=CANALES,
            dtype=TIPO_DATO,
            callback=callback_audio
        ):
            while True:
                # El callback hace todo el trabajo en segundo plano.
                # El bucle principal solo necesita mantenerse vivo.
                time.sleep(1)
                
    except KeyboardInterrupt:
        print(f"\n\n🛑 Finalizando...")
        
    except sd.PortAudioError as e:
        print(f"\n❌ Error de audio: {e}")
        print("💡 Usa: python cazabache.py --config para ver dispositivos")
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()