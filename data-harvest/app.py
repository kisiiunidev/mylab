from flask import Flask, request, jsonify
import subprocess
import json

app = Flask(__name__)


@app.route("/search", methods=["POST"])
def search_username():
    data = request.get_json()

    username = data.get("username")

    if not username:
        return jsonify({
            "error": "Username is required"
        }), 400

    result = subprocess.run(
        [
            "maigret",
            username,
            "--json",
            "simple"
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return jsonify({
            "error": result.stderr
        }), 500

    try:
        results = json.loads(result.stdout)
    except json.JSONDecodeError:
        return jsonify({
            "error": "Could not parse Maigret output",
            "output": result.stdout
        }), 500

    return jsonify({
        "username": username,
        "results": results
    })


if __name__ == "__main__":
    app.run(debug=True, port=6700)
