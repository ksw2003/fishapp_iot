import requests

SERVER = "http://13.239.199.189:3000"
DEVICE_ID = "SS501"

def send_sensor_data(temperature, water_quality):

    url = f"{SERVER}/api/tank/Sensor"

    payload = {
        "device_id": DEVICE_ID,
        "temperature": temperature,
        "water_quality": water_quality
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=5
        )

        print("응답 :", response.status_code)

        if response.status_code == 204:
            print("센서 데이터 전송 성공")
        elif response.ok:
            print(response.json())
        else:
            print(response.text)

    except Exception as e:
        print("전송 실패 :", e)


if __name__ == "__main__":
    send_sensor_data(25.4, 320)