from flask import Flask, render_template, request, jsonify, send_file
import edge_tts
import asyncio
import uuid
import os

app = Flask(__name__)

OUTPUT_DIR = "audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/tts", methods=["POST"])
def tts():
    try:
        text = request.form.get("text", "").strip()
        voice = request.form.get("voice", "vi-VN-HoaiMyNeural")
        rate = request.form.get("rate", "0")

        if not text:
            return jsonify({"error": "No text"}), 400

        filename = str(uuid.uuid4()) + ".mp3"
        filepath = os.path.join(OUTPUT_DIR, filename)

        async def run():
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=f"{rate}%"
            )
            await communicate.save(filepath)

        # FIX ỔN ĐỊNH CHO RENDER
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run())
        loop.close()

        return jsonify({
            "audio": f"/audio/{filename}",
            "file": filename
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/audio/<filename>")
def audio(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    return send_file(path, mimetype="audio/mpeg")


@app.route("/download/<filename>")
def download(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
