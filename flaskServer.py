from flask import Flask, jsonify
from waterPump import run_water_change
from feeder import run_feeding

app = Flask(__name__)

# 환수
@app.route('/waterchange', methods=['POST'])
def waterchange():
    try:
        run_water_change()

        return jsonify({
            "success": True
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# 먹이주기
@app.route('/feed', methods=['POST'])
def feed():
    try:
        run_feeding()

        return jsonify({
            "success": True
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


app.run(
    host="0.0.0.0",
    port=5000
)