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
