
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Flask, render_template_string, request

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
  {% if reply %}
    <h2>Respuesta de Luna</h2>
    <p style="white-space: pre-wrap">{{ reply }}</p>
  {% endif %}
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():
    message = request.form.get("message", "").strip()
    reply = ""

    if request.method == "POST":
        if not message or len(message) > 2000:
            reply = "Escribe un mensaje de 1 a 2000 caracteres."
        else:
            reply = ask_gemini(message)

    return render_template_string(PAGE, message=message, reply=reply)


def ask_gemini(message):
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return "Falta configurar GEMINI_API_KEY en Render."

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
    except HTTPError as error:
        if error.code == 429:
            return "Gemini alcanzó un límite de uso. Intenta de nuevo más tarde."
        return f"Gemini devolvió el error HTTP {error.code}."
    except (URLError, TimeoutError):
        return "Luna no pudo conectar con Gemini. Intenta de nuevo."
    except (ValueError, UnicodeError):
        return "Luna recibió una respuesta que no pudo leer."

    if not isinstance(result, dict):
        return "Luna recibió una respuesta que no pudo leer."

    candidates = result.get("candidates") or []
    parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
    answer = "".join(
        part.get("text", "") for part in parts if not part.get("thought")
    )
    return answer.strip() or "Gemini no devolvió una respuesta de texto."
