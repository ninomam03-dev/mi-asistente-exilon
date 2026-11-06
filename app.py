
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from flask import Flask, Response, render_template_string, request

app = Flask(__name__)

PAGE = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Luna</title>
</head> 
<body>
  <h1>Luna</h1>
  <form method="post">
    <label for="message">¿Qué quieres preguntarle a Luna?</label><br>
    <textarea id="message" name="message" rows="4" cols="36"
              maxlength="2000" required>{{ message }}</textarea><br>
    <button type="submit">Enviar</button>
  </form>

  {% if error %}
    <p role="alert">{{ error }}</p>
  {% endif %}

  {% if reply %}
    <h2>Respuesta de Luna</h2>
    <p style="white-space: pre-wrap">{{ reply }}</p>
    <button type="button" id="listen">Escuchar con Bella</button>
    <p id="audio-status" role="status"></p>
    <audio id="luna-audio" controls hidden></audio>

    <script>
      const listen = document.getElementById("listen");
      const audio = document.getElementById("luna-audio");
      const audioStatus = document.getElementById("audio-status");
      const replyText = {{ reply | tojson }};

      listen.addEventListener("click", async () => {
        listen.disabled = true;
        audioStatus.textContent = "Preparando la voz de Bella…";

        try {
          if (!audio.hasAttribute("src")) {
            const response = await fetch({{ url_for("voz") | tojson }}, {
              method: "POST",
              body: new URLSearchParams({ text: replyText })
            });
            if (!response.ok) {
              throw new Error(await response.text());
            }
            audio.src = URL.createObjectURL(await response.blob());
            audio.hidden = false;
          }

          try {
            await audio.play();
            audioStatus.textContent = "";
          } catch {
            audioStatus.textContent = "Pulsa ▶ en el reproductor para escuchar.";
          }
        } catch (error) {
          audioStatus.textContent = error.message;
        } finally {
          listen.disabled = false;
        }
      });
    </script>
  {% endif %}
<button type="button" id="luna-mic">Activar micrófono</button>
<p id="mic-status" role="status"></p>

<script>
(() => {
  const mic = document.getElementById("luna-mic");
  const status = document.getElementById("mic-status");
  const field = document.getElementById("message");
  const listen = document.getElementById("listen");

  if (sessionStorage.getItem("luna-voice-request") === "1") {
    sessionStorage.removeItem("luna-voice-request");
    listen?.click();
  }

  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Recognition) {
    mic.disabled = true;
    status.textContent = "Este navegador no admite el reconocimiento de voz.";
    return;
  }

  const recognition = new Recognition();
  recognition.lang = "es-DO";
  recognition.continuous = true;
  let active = false;
  let waitingForQuestion = false;
  let failed = false;

  mic.onclick = () => {
    if (active) {
      recognition.abort();
      return;
    }

    failed = false;
    waitingForQuestion = false;

    try {
      recognition.start();
      active = true;
      mic.textContent = "Desactivar micrófono";
      status.textContent = "Di «Hola, Luna» o «Buenos días, Luna».";
    } catch {
      status.textContent = "No se pudo activar el micrófono. Intenta otra vez.";
    }
  };

  recognition.onresult = event => {
    for (let i = event.resultIndex; i < event.results.length; i++) {
      if (!event.results[i].isFinal) continue;

      const phrase = event.results[i][0].transcript.trim();
      status.textContent = "Escuché: «" + phrase + "»";
      const wake = /^[¡¿ ]*(?:hola|buenos d[ií]as)[ ,.]+luna\\b[ ,.:;!?¿¡]*/i;

      if (!waitingForQuestion && !wake.test(phrase)) continue;

      const question = phrase.replace(wake, "").trim();
      if (!question) {
        waitingForQuestion = true;
        status.textContent = "Te escucho. Haz tu pregunta.";
        continue;
      }

      field.value = question.slice(0, 2000);
      sessionStorage.setItem("luna-voice-request", "1");
      recognition.abort();
      field.form.requestSubmit();
      return;
    }
  };

  recognition.onerror = event => {
    if (event.error === "aborted") return;
    failed = true;
    status.textContent = "El micrófono se detuvo. Revisa los permisos y vuelve a activarlo.";
  };

  recognition.onend = () => {
    active = false;
    mic.textContent = "Activar micrófono";
    if (!failed) status.textContent += " (Micrófono desactivado).";
  };
})();
</script>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():
    message = request.form.get("message", "").strip()
    reply = ""
    error = ""

    if request.method == "POST":
        if not message or len(message) > 2000:
            error = "Escribe un mensaje de 1 a 2000 caracteres."
        else:
            reply, error = ask_gemini(message)

    return render_template_string(
        PAGE, message=message, reply=reply, error=error
    )


def ask_gemini(message):
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return "", "Falta configurar GEMINI_API_KEY en Render."

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-3.1-flash-lite:generateContent"
    )
    payload = {
        "systemInstruction": {
            "parts": [{
                "text": (
                    "Eres Luna, una asistente personal. "
                    "Preséntate como Luna si te preguntan tu nombre. "
                    "Responde en español salvo que te pidan otro idioma."
                )
            }]
        },
        "contents": [{"parts": [{"text": message}]}],
        "generationConfig": {"maxOutputTokens": 512},
    }
    api_request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urlopen(api_request, timeout=20) as response:
            result = json.load(response)

        candidates = result.get("candidates") or []
        parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
        answer = "".join(
            part.get("text", "") for part in parts if not part.get("thought")
        ).strip()
    except HTTPError as error:
        if error.code == 429:
            return "", "Gemini alcanzó un límite de uso. Intenta de nuevo más tarde."
        return "", f"Gemini devolvió el error HTTP {error.code}."
    except (URLError, TimeoutError):
        return "", "Luna no pudo conectar con Gemini. Intenta de nuevo."
    except (ValueError, AttributeError, TypeError, KeyError):
        return "", "Luna recibió una respuesta que no pudo leer."

    if not answer:
        return "", "Gemini no devolvió una respuesta de texto."

    return answer, ""


@app.post("/voz")
def voz():
    text = request.form.get("text", "").strip()
    if not text or len(text) > 4000:
        return "La respuesta debe tener entre 1 y 4000 caracteres.", 400

    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "").strip()
    if not api_key or not voice_id:
        return "Revisa la clave de ElevenLabs y el ID de Bella en Render.", 503

    url = (
        "https://api.elevenlabs.io/v1/text-to-speech/"
        f"{quote(voice_id, safe='')}?output_format=mp3_44100_128"
    )
    audio_request = Request(
        url,
        data=json.dumps({
            "text": text,
            "model_id": "eleven_multilingual_v2",
        }).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
            "xi-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urlopen(audio_request, timeout=20) as response:
            audio = response.read()
    except HTTPError as error:
        return f"ElevenLabs devolvió el error HTTP {error.code}.", 502
    except (URLError, TimeoutError):
        return "Luna no pudo conectarse a ElevenLabs. Intenta de nuevo.", 502

    return Response(
        audio,
        mimetype="audio/mpeg",
        headers={"Cache-Control": "no-store"},
    )
