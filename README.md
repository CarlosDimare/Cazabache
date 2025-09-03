# cazabache.py 📻

*Un guardián contra el silencio para radios libres, podcasters y cualquier proyecto a pulmón que no quiera quedarse mudo.*

Este humilde script es un "cazabache", una herramienta pensada para monitorear una señal de audio y avisarte cuando las cosas se quedan en silencio por demasiado tiempo. ¿Se cayó el reproductor? ¿Se colgó la compu del operador? ¿El invitado se quedó sin palabras? El cazabache te manda un Telegram para que salgas a solucionar el quilombo.

Hecho con software libre, para gente libre.

## ¿Cómo funciona esta magia?

El script escucha el audio de tu sistema (lo que sea que le configures como entrada). Calcula el volumen en tiempo real (el famoso RMS) y si ese volumen cae por debajo de un umbral que vos definís, empieza a contar. Si el silencio dura más de la cuenta, ¡PUM! Alerta por Telegram.

No es un sistema de broadcast de miles de dólares, es una solución de trinchera. Eficaz, gratuita y nuestra.

## Puesta en marcha

Esto corre con Python. Si no lo tenés, es hora de amigarse. Lo que sigue asume que tenés Python y `pip` listos para la acción.

**1. Dependencias:**

El cazabache necesita algunos compañeros para funcionar. Los instalás desde tu terminal con:

```bash
pip install sounddevice numpy colorama requests
```

**2. Configuración:**

Abrí el archivo `cazabache.py` con cualquier editor de texto. Arriba de todo, vas a ver la sección de `Configuración`.

*   `UMBRAL_SILENCIO`: Este es el número mágico. Define qué tan bajo tiene que ser el volumen para que se considere "silencio". Depende mucho de tu micrófono y del ruido de fondo. Un buen punto de partida es `50` o `100`. Si te saltan falsas alarmas, subilo. Si no detecta los silencios, bajalo.
*   `DURACION_SILENCIO_SEGUNDOS`: ¿Cuántos segundos de silencio aguantamos antes de mandar la alerta? Por defecto está en `59`, casi un minuto.
*   `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID`: La parte más "complicada".
    1.  Hablale a `@BotFather` en Telegram y creá un bot nuevo. Te va a dar un "token", que es como la contraseña de tu bot. Copialo y pegalo en `TELEGRAM_BOT_TOKEN`.
    2.  Necesitás saber el ID del chat donde querés que lleguen los mensajes. Puede ser un chat con vos mismo o un grupo. Hay varios bots como `@userinfobot` que te ayudan a conseguir este ID. Pegalo en `TELEGRAM_CHAT_ID`.

## Uso

Una vez configurado, es una pavada. Abrí una terminal y corré:

```bash
python cazabache.py
```

Vas a ver un vúmetro medio psicodélico mostrando el nivel de audio. Dejalo corriendo en su propia terminal y él se encargará del resto.

### Comandos útiles

*   **Ver tu configuración y dispositivos de audio:**
    ```bash
    python cazabache.py --config
    ```
    Esto es clave si tenés varias placas de sonido o micrófonos y querés asegurarte de que está escuchando la correcta.

*   **Probar si Telegram funciona:**
    ```bash
    python cazabache.py --test-telegram
    ```
    Te manda un mensaje de prueba para ver si configuraste bien el bot.

## Filosofía y Licencia

Este código es tuyo. Usalo, modificalo, compartilo. Si le encontrás una mejora, genial. Si te ahorró un dolor de cabeza, me alegro. No hay una licencia formal de esas que escriben los abogados de traje.

Esto se rige por la **Licencia "Hacete Cargo"**: si lo usás y algo sale mal, es parte del juego. Si lo mejorás y no lo compartís, allá vos con tu conciencia. La idea es que nos sirva a todos los que remamos en dulce de leche para mantener nuestros proyectos a flote.

¡Salud y buena radio!
