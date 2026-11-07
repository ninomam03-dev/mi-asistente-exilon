
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from flask import Flask, Response, jsonify, render_template_string, request

app = Flask(__name__)

# ==========================================
# LUNA AI - INTERFAZ
# ==========================================

PAGE = """
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Luna AI</title>

<style>
body {
    margin: 0;
    min-height: 100vh;
    display: grid;
    place-items: center;
    background: #07111d;
    color: #eaf6ff;
    font: 16px Arial, sans-serif;
}

main {
    width: min(700px, 90vw);
    padding: 28px;
    border: 1px solid #16435a;
    border-radius: 20px;
    background: #0c1b2a;
    box-shadow: 0 0 40px #00c8ff22;
}

h1 {
    color: #55dcff;
    margin-top: 0;
}

textarea {
    box-sizing: border-box;
    width: 100%;
    min-height: 100px;
    padding: 12px;
    color: white;
    background: #07111d;
    border: 1px solid #27627b;
    border-radius: 10px;
    font: inherit;
}

button {
    margin: 10px 8px 0 0;
    padding: 10px 16px;
    border: 0;
    border-radius: 9px;
    cursor: pointer;
    color: #06121a;
    background: #55dcff;
    font-weight: bold;
}

button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

#reply {
    white-space: pre-wrap;
    line-height: 1.5;
}

#status {
    color: #9bb6c6;
    min-height: 24px;
}
</style>
</head>

<body>
<main>
    <h1>Luna AI</h1>

    <p>Pregúntame algo o activa el micrófono y habla.</p>

    <form id="form">
        <textarea
            id="message"
            maxlength="2000"
            placeholder="Escribe aquí..."></textarea>

        <div>
            <button id="send" type="submit">Enviar</button>

            <button id="mic" type="button">
                🎙 Activar micrófono
            </button>

            <button id="stop" type="button" hidden>
                Detener micrófono
            </button>
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
const sendButton = document.getElementById("send");
const micButton = document.getElementById("mic");
const stopButton = document.getElementById("stop");

let processing = false;
let recognition = null;
let elevenUnavailable = false;

// Evitar múltiples respuestas simultáneas

function updateButtons() {
    sendButton.disabled = processing;
    micButton.disabled = processing;
}

// Detener el micrófono antes de responder

function stopListening() {
    if (recognition) {
        const previous = recognition;
        recognition = null;
        previous.onresult = null;

        try {
            previous.stop();
        } catch (error) {
            // Ya estaba detenido
        }
    }

    micButton.hidden = false;
    stopButton.hidden = true;
}

// Voz gratuita de respaldo del navegador

function speakWithBrowser(text) {
    return new Promise((resolve, reject) => {
        if (!("speechSynthesis" in window)) {
            reject(new Error(
                "No hay una voz alternativa disponible."
            ));
            return;
        }

        const speech = new SpeechSynthesisUtterance(text);

        speech.lang = "es-DO";
        speech.rate = 1;
        speech.pitch = 1;

        const voices = speechSynthesis.getVoices();

        const selectedVoice =
            voices.find(v => v.lang.toLowerCase() === "es-do") ||
            voices.find(v => v.lang.toLowerCase().startsWith("es"));

        if (selectedVoice) {
            speech.voice = selectedVoice;
        }

        speech.onend = () => resolve();

        speech.onerror = () => {
            reject(new Error(
                "No se pudo reproducir la voz alternativa."
            ));
        };

        speechSynthesis.cancel();
        speechSynthesis.speak(speech);
    });
}

// Reproducir audio generado por ElevenLabs

function playAudio(blob) {
    return new Promise((resolve, reject) => {
        const audioUrl = URL.createObjectURL(blob);
        const audio = new Audio(audioUrl);

        audio.onended = () => {
            URL.revokeObjectURL(audioUrl);
            resolve();
        };

        audio.onerror = () => {
            URL.revokeObjectURL(audioUrl);
            reject(new Error(
                "No se pudo reproducir el audio."
            ));
        };

        audio.play().catch(error => {
            URL.revokeObjectURL(audioUrl);
            reject(error);
        });
    });
}

// Función principal de Luna

async function askLuna(text) {
    if (processing) return;

    const message = text.trim();

    if (!message) return;

    processing = true;
    updateButtons();
    stopListening();

    input.value = message;
    replyBox.textContent = "";
    statusBox.textContent = "Luna está pensando...";

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({message})
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "No se pudo obtener respuesta."
            );
        }

        replyBox.textContent = data.reply;

        const brain = data.brain || "IA";

        statusBox.textContent =
            "Respuesta generada con " + brain +
            ". Preparando la voz...";

        // Usar ElevenLabs si está disponible

        if (!elevenUnavailable) {
            const audioResponse = await fetch("/api/speak", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    text: data.reply
                })
            });

            if (audioResponse.ok) {
                const audioBlob = await audioResponse.blob();

                await playAudio(audioBlob);

                statusBox.textContent =
                    "Luna respondió usando " + brain + ".";
                return;
            }

            // Evita repetir intentos fallidos
            // durante esta sesión de la página.

            elevenUnavailable = true;
        }

        // Si ElevenLabs falla, usar voz alternativa

        statusBox.textContent =
            "ElevenLabs no está disponible. " +
            "Usando voz alternativa...";

        await speakWithBrowser(data.reply);

        statusBox.textContent =
            "Luna respondió usando " + brain +
            " con voz alternativa.";

    } catch (error) {
        statusBox.textContent =
            error.message || "Ocurrió un error.";

    } finally {
        processing = false;
        updateButtons();
    }
}

// Envío de mensajes

form.addEventListener("submit", event => {
    event.preventDefault();
    askLuna(input.value);
});

// Reconocimiento de voz

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

micButton.addEventListener("click", () => {
    if (processing || recognition) return;

    if (!SpeechRecognition) {
        statusBox.textContent =
            "Tu navegador no admite reconocimiento de voz.";
        return;
    }

    const rec = new SpeechRecognition();
    recognition = rec;

    rec.lang = "es-DO";
    rec.interimResults = false;
    rec.continuous = false;
    rec.maxAlternatives = 1;

    rec.onstart = () => {
        statusBox.textContent = "Te escucho...";
        micButton.hidden = true;
        stopButton.hidden = false;
    };

    rec.onresult = event => {
        if (processing) return;

        const spokenText =
            event.results[event.resultIndex][0].transcript;

        rec.onresult = null;
        askLuna(spokenText);
    };

    rec.onerror = event => {
        if (!processing) {
            statusBox.textContent =
                "Error del micrófono: " + event.error;
        }
    };

    rec.onend = () => {
        if (recognition === rec) {
            recognition = null;
        }

        micButton.hidden = false;
        stopButton.hidden = true;
    };

    try {
        rec.start();
    } catch (error) {
        recognition = null;
        statusBox.textContent =
            "No se pudo activar el micrófono.";
    }
});

stopButton.addEventListener("click", stopListening);
</script>
</body>
</html>
"""


# ==========================================
# PÁGINA PRINCIPAL
# ==========================================

@app.get("/")
def home():
    return render_template_string(PAGE)


# ==========================================
# CEREBRO PRINCIPAL: GEMINI
# RESPALDO: OPENROUTER GRATIS
# ==========================================

@app.post("/api/chat")
def chat():

    data = request.get_json(silent=True) or {}

    message = str(data.get("message", "")).strip()

    if not message or len(message) > 2000:
        return jsonify(
            error="Escribe un mensaje de hasta 2000 caracteres."
        ), 400

    # Fecha y hora de República Dominicana

    now = datetime.now(
        ZoneInfo("America/Santo_Domingo")
    )

    weekdays = [
        "lunes", "martes", "miércoles",
        "jueves", "viernes", "sábado", "domingo"
    ]

    months = [
        "enero", "febrero", "marzo", "abril",
        "mayo", "junio", "julio", "agosto",
        "septiembre", "octubre", "noviembre", "diciembre"
    ]

    fecha = (
        f"{weekdays[now.weekday()]} "
        f"{now.day} de {months[now.month - 1]} "
        f"de {now.year}"
    )

    hora = now.strftime("%H:%M")

    instrucciones = (
        "Eres Luna, una asistente personal femenina, "
        "amable, inteligente, tierna y comprensiva. "
        "Habla naturalmente en español. "
        "Responde de forma clara y normalmente breve. "
        "No repitas innecesariamente las respuestas. "
        "Tu personalidad es cercana y conversacional. "
        "No inventes información que desconozcas. "
        f"La fecha actual en República Dominicana es {fecha}. "
        f"La hora local es {hora}. "
        "Utiliza esa fecha para responder preguntas temporales."
    )

    # ======================================
    # INTENTAR GEMINI PRIMERO
    # ======================================

    gemini_key = os.environ.get(
        "GEMINI_API_KEY", ""
    ).strip()

    if gemini_key:

        gemini_url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            "models/gemini-3.1-flash-lite:generateContent"
        )

        gemini_payload = {
            "systemInstruction": {
                "parts": [
                    {"text": instrucciones}
                ]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": message}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 512
            }
        }

        gemini_request = Request(
            gemini_url,
            data=json.dumps(
                gemini_payload
            ).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": gemini_key
            },
            method="POST"
        )

        try:
            with urlopen(
                gemini_request,
                timeout=25
            ) as response:
                result = json.load(response)

            candidates = result.get("candidates") or []

            parts = (
                candidates[0]
                .get("content", {})
                .get("parts", [])
                if candidates else []
            )

            answer = "".join(
                part.get("text", "")
                for part in parts
                if isinstance(part, dict)
                and not part.get("thought")
            ).strip()

            if answer:
                return jsonify(
                    reply=answer,
                    brain="Gemini"
                )

            app.logger.warning(
                "Gemini devolvió una respuesta vacía."
            )

        except HTTPError as error:

            app.logger.warning(
                "Gemini devolvió HTTP %s.",
                error.code
            )

            # Errores que admiten respaldo
            if error.code not in (
                429, 500, 502, 503, 504
            ):
                return jsonify(
                    error=f"Gemini devolvió HTTP {error.code}."
                ), 502

        except (URLError, TimeoutError):
            app.logger.warning(
                "No fue posible conectar con Gemini."
            )

        except (ValueError, KeyError, TypeError):
            app.logger.warning(
                "Gemini devolvió datos inesperados."
            )

    # ======================================
    # RESPALDO: OPENROUTER
    # ======================================

    app.logger.info(
        "Intentando responder mediante OpenRouter."
    )

    router_key = os.environ.get(
        "OPENROUTER_API_KEY", ""
    ).strip()

    if not router_key:
        return jsonify(
            error=(
                "Gemini no está disponible y falta "
                "OPENROUTER_API_KEY en Render."
            )
        ), 503

    router_url = (
        "https://openrouter.ai/api/v1/chat/completions"
    )

    router_payload = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "system",
                "content": instrucciones
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "max_tokens": 512
    }

    router_request = Request(
        router_url,
        data=json.dumps(
            router_payload
        ).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {router_key}",
            "X-Title": "Luna AI"
        },
        method="POST"
    )

    try:
        with urlopen(
            router_request,
            timeout=40
        ) as response:
            result = json.load(response)

        choices = result.get("choices") or []

        if not choices:
            return jsonify(
                error="OpenRouter no devolvió respuestas."
            ), 502

        content = (
            choices[0]
            .get("message", {})
            .get("content", "")
        )

        if isinstance(content, str):
            answer = content.strip()

        elif isinstance(content, list):
            answer = "".join(
                item.get("text", "")
                for item in content
                if isinstance(item, dict)
            ).strip()

        else:
            answer = ""

        if not answer:
            return jsonify(
                error="OpenRouter devolvió una respuesta vacía."
            ), 502

        return jsonify(
            reply=answer,
            brain="OpenRouter",
            model=result.get(
                "model",
                "openrouter/free"
            )
        )

    except HTTPError as error:

        app.logger.error(
            "OpenRouter devolvió HTTP %s.",
            error.code
        )

        return jsonify(
            error=(
                f"OpenRouter devolvió HTTP {error.code}. "
                "Revisa los límites y permisos de la clave."
            )
        ), 502

    except (URLError, TimeoutError):
        return jsonify(
            error="No se pudo conectar con OpenRouter."
        ), 502

    except (ValueError, KeyError, TypeError):
        return jsonify(
            error="OpenRouter devolvió datos inesperados."
        ), 502


# ==========================================
# VOZ DE LUNA: ELEVENLABS
# ==========================================

@app.post("/api/speak")
def speak():

    data = request.get_json(silent=True) or {}
    text = str(data.get("text", "")).strip()

    if not text:
        return jsonify(
            error="No hay texto para convertir a voz."
        ), 400

    api_key = os.environ.get(
        "ELEVENLABS_API_KEY", ""
    ).strip()

    voice_id = os.environ.get(
        "ELEVENLABS_VOICE_ID", ""
    ).strip()

    if not api_key or not voice_id:
        return jsonify(
            error="Falta configurar ElevenLabs."
        ), 503

    url = (
        "https://api.elevenlabs.io/v1/text-to-speech/"
        f"{quote(voice_id, safe='')}"
        "?output_format=mp3_44100_128"
    )

    payload = {
        "text": text[:2000],
        "model_id": "eleven_multilingual_v2"
    }

    api_request = Request(
        url,
        data=json.dumps(
            payload
        ).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
            "xi-api-key": api_key
        },
        method="POST"
    )

    try:
        with urlopen(
            api_request,
            timeout=30
        ) as response:
            audio = response.read()

        return Response(
            audio,
            mimetype="audio/mpeg"
        )

    except HTTPError as error:

        raw = error.read().decode(
            "utf-8",
            errors="replace"
        )

        try:
            error_data = json.loads(raw)
        except json.JSONDecodeError:
            error_data = {}

        if not isinstance(error_data, dict):
            error_data = {}

        detail = error_data.get("detail", {})

        if isinstance(detail, dict):
            error_code = (
                detail.get("status")
                or detail.get("code")
                or "desconocido"
            )

            error_message = (
                detail.get("message")
                or "Sin detalles"
            )

        elif isinstance(detail, str):
            error_code = "desconocido"
            error_message = detail

        else:
            error_code = "desconocido"
            error_message = "Sin detalles"

        app.logger.error(
            "ElevenLabs HTTP %s | %s | %s",
            error.code,
            error_code,
            str(error_message)[:200]
        )

        return jsonify(
            error=f"ElevenLabs: {error_code}"
        ), 502

    except (URLError, TimeoutError):
        return jsonify(
            error="No se pudo conectar con ElevenLabs."
        ), 502


# ==========================================
# INICIAR LUNA AI
# ==========================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000"))
    )
