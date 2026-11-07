import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

PAGE = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Luna AI</title>
  <style>
    body {
      margin: 0; min-height: 100vh; display: grid; place-items: center;
      background: #07111d; color: #eaf6ff;
      font: 16px Arial, sans-serif;
    }
    main {
      width: min(700px, 90vw); padding: 28px; border: 1px solid #16435a;
      border-radius: 20px; background: #0c1b2a;
      box-shadow: 0 0 40px #00c8ff22;
    }
    h1 { color: #55dcff; margin-top: 0; }
    textarea {
      box-sizing: border-box; width: 100%; min-height: 100px; padding: 12px;
      color: white; background: #07111d; border: 1px solid #27627b;
      border-radius: 10px; font: inherit;
    }
    button {
      margin: 10px 8px 0 0; padding: 10px 16px; border: 0;
      border-radius: 9px; cursor: pointer; color: #06121a; background: #55dcff;
      font-weight: bold;
    }
    #reply { white-space: pre-wrap; line-height: 1.5; }
    #status { color: #9bb6c6; min-height: 24px; }
  </style>
</head>
<body>
<main>
  <h1>Luna AI</h1>
  <p>Pregúntame algo o activa el micrófono y habla.</p>
  <form id="form">
    <textarea id="message" maxlength="2000" placeholder="Escribe aquí…"></textarea>
    <div>
      <button type="submit">Enviar</button>
      <button type="button" id="mic">🎙 Activar micrófono</button>
      <button type="button" id="stop" hidden>Detener micrófono</button>
    </div>
  </form>
  <p id="status" aria-live="polite"></p>
  <h2>Respuesta</h2>
  <div id="reply"></div>
</main>
<script>
const form = document.getElementById("form");
const input = document.getElementById("message");
const replyBox = document.getElementById("reply");
const statusBox = document.getElementById("status");
let recognition = null;

async function askLuna(text) {
  const message = text.trim();
  if (!message) return;

  input.value = message;
  statusBox.textContent = "Luna está pensando…";
  replyBox.textContent = "";

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "No se pudo obtener respuesta.");

    replyBox.textContent = data.reply;
    statusBox.textContent = "Respuesta lista. Preparando la voz…";

    const audioResponse = await fetch("/api/speak", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({text: data.reply})
    });

    if (!audioResponse.ok) {
      const errorData = await audioResponse.json();
      statusBox.textContent = errorData.error || "La respuesta llegó, pero falló la voz.";
      return;
    }

    const audioUrl = URL.createObjectURL(await audioResponse.blob());
    const audio = new Audio(audioUrl);
    audio.onended = () => URL.revokeObjectURL(audioUrl);
    await audio.play();
    statusBox.textContent = "Luna respondió.";
  } catch (error) {
    statusBox.textContent = error.message || "Ocurrió un error.";
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  askLuna(input.value);
});

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
document.getElementById("mic").addEventListener("click", () => {
  if (!SpeechRecognition) {
    statusBox.textContent = "Este navegador no ofrece reconocimiento de voz. Prueba Chrome.";
    return;
  }

  recognition = new SpeechRecognition();
  recognition.lang = "es-DO";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    statusBox.textContent = "Te escucho…";
    document.getElementById("mic").hidden = true;
    document.getElementById("stop").hidden = false;
  };
  recognition.onresult = (event) => {
    const spokenText = event.results[0][0].transcript;
    input.value = spokenText;
    askLuna(spokenText);
  };
  recognition.onerror = () => {
    statusBox.textContent = "No pude reconocer lo que dijiste. Revisa el permiso del micrófono.";
  };
  recognition.onend = () => {
    document.getElementById("mic").hidden = false;
    document.getElementById("stop").hidden = true;
  };
  recognition.start();
});

document.getElementById("stop").addEventListener("click", () => {
  if (recognition) recognition.stop();
});
</script>
</body>
</html>
"""


@app.get("/")
def home():
    return render_template_string(PAGE)


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message or len(message) > 2000:
        return jsonify(error="Escribe un mensaje de hasta 2000 caracteres."), 400

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return jsonify(error="Falta configurar GEMINI_API_KEY en Render."), 500

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-3.1-flash-lite:generateContent"
    )
    payload = {
        "systemInstruction": {
            "parts": [{
                "text": (
                    "Eres Luna, una asistente personal. "
                    "Responde en español y de forma clara."
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
        with urlopen(api_request, timeout=30) as response:
            result = json.load(response)
    except HTTPError as error:
        if error.code == 429:
            return jsonify(error="Gemini alcanzó un límite de uso; inténtalo más tarde."), 429
        return jsonify(error=f"Gemini devolvió HTTP {error.code}."), 502
    except (URLError, TimeoutError):
        return jsonify(error="No se pudo conectar con Gemini."), 502

    candidates = result.get("candidates") or []
    parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
    answer = "".join(
        part.get("text", "") for part in parts if not part.get("thought")
    ).strip()

    if not answer:
        return jsonify(error="Gemini no devolvió una respuesta de texto."), 502
    return jsonify(reply=answer)


@app.post("/api/speak")
def speak():
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", "")).strip()

    if not text:
        return jsonify(error="No hay texto para convertir a voz."), 400

    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "").strip()

    if not api_key or not voice_id:
        return jsonify(error="Falta configurar la clave o el ID de voz de ElevenLabs en Render."), 500

    url = (
        "https://api.elevenlabs.io/v1/text-to-speech/"
        f"{quote(voice_id, safe='')}?output_format=mp3_44100_128"
    )
    payload = {
        "text": text[:2000],
        "model_id": "eleven_multilingual_v2",
    }
    api_request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
            "xi-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urlopen(api_request, timeout=30) as response:
            audio = response.read()
        from flask import Response
        return Response(audio, mimetype="audio/mpeg")
    except HTTPError as error:
        return jsonify(error=f"ElevenLabs rechazó la solicitud (HTTP {error.code}). Revisa el acceso de la clave al texto a voz y que el ID de voz sea correcto."), 502
    except (URLError, TimeoutError):
        return jsonify(error="No se pudo conectar con ElevenLabs."), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
