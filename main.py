import time
import json
import threading
import websocket

from waterQuality import read_tds
from temperature import read_temp
from sensorAPI import send_sensor_data

from waterPump import run_water_change
from feeder import run_feeding

DEVICE_ID = "SS501"
SERVER_WS = "ws://13.239.199.189:3000"


# --------------------
# 센서 전송
# --------------------
def sensor_loop():

    print("수질/수온 모니터링 시작")

    while True:

        try:

            tds = read_tds()
            temperature = read_temp()

            send_sensor_data(
                temperature=temperature,
                water_quality=tds
            )

            print(
                f"[전송] 수온={temperature}℃ | TDS={tds}"
            )

        except Exception as e:
            print("센서 전송 오류:", e)

        time.sleep(2)


# --------------------
# 웹소켓
# --------------------
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

        # 먹이주기
        if data["type"] == "feed":

            print("먹이 명령 수신")

            try:

                run_feeding()

                ws.send(json.dumps({
                    "type": "feedResult",
                    "success": True
                }))

            except Exception as e:

                print(e)

                ws.send(json.dumps({
                    "type": "feedResult",
                    "success": False
                }))

        # 환수
        elif data["type"] == "waterChange":

            print("환수 명령 수신")

            try:

                run_water_change()

                ws.send(json.dumps({
                    "type": "waterChangeResult",
                    "success": True
                }))

            except Exception as e:

                print(e)

                ws.send(json.dumps({
                    "type": "waterChangeResult",
                    "success": False
                }))

    except Exception as e:
        print("메시지 처리 오류:", e)


def websocket_loop():

    while True:

        try:

            ws = websocket.WebSocketApp(
                SERVER_WS,
                on_open=on_open,
                on_message=on_message
            )

            ws.run_forever()

        except Exception as e:

            print("웹소켓 재연결:", e)

        time.sleep(5)


# --------------------
# 시작
# --------------------
if __name__ == "__main__":

    threading.Thread(
        target=sensor_loop,
        daemon=True
    ).start()

    websocket_loop()

