import json
import time
import threading
import websocket

from waterPump import run_water_change
from feeder import run_feeding
from sensorAPI import send_sensor_data

SERVER_WS = "ws://13.239.199.189:3000"
DEVICE_ID = "SS501"


# ----------------------------
# 센서 전송
# ----------------------------

def sensor_loop():
    while True:
        try:
            # 실제 센서 읽기 코드로 변경
            temperature = 25.4
            water_quality = 320

            send_sensor_data(
                temperature,
                water_quality
            )

        except Exception as e:
            print("센서 전송 오류:", e)

        time.sleep(60)


# ----------------------------
# WebSocket 연결
# ----------------------------

def on_open(ws):
    print("AWS 연결 성공")

    ws.send(json.dumps({
        "type": "registerDevice",
        "device_id": DEVICE_ID
    }))


def on_message(ws, message):
    print("수신:", message)

    try:
        data = json.loads(message)

        # ------------------------
        # 먹이주기
        # ------------------------
        if data["type"] == "feed":

            print("먹이 명령 수신")

            try:
                run_feeding()

                ws.send(json.dumps({
                    "type": "feedResult",
                    "success": True
                }))

            except Exception as e:

                print("먹이 오류:", e)

                ws.send(json.dumps({
                    "type": "feedResult",
                    "success": False
                }))

        # ------------------------
        # 환수
        # ------------------------
        elif data["type"] == "waterChange":

            print("환수 명령 수신")

            try:
                run_water_change()

                ws.send(json.dumps({
                    "type": "waterChangeResult",
                    "success": True
                }))

            except Exception as e:

                print("환수 오류:", e)

                ws.send(json.dumps({
                    "type": "waterChangeResult",
                    "success": False
                }))

    except Exception as e:
        print("메시지 처리 오류:", e)


def on_error(ws, error):
    print("WebSocket 오류:", error)


def on_close(ws, code, msg):
    print("연결 종료")


def websocket_loop():

    while True:

        try:

            ws = websocket.WebSocketApp(
                SERVER_WS,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )

            ws.run_forever()

        except Exception as e:
            print("재연결:", e)

        time.sleep(5)


# ----------------------------
# 실행
# ----------------------------

if __name__ == "__main__":

    threading.Thread(
        target=sensor_loop,
        daemon=True
    ).start()

    websocket_loop()