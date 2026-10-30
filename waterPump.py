import RPi.GPIO as GPIO
import time
import requests
from datetime import datetime
from sensorAPI import SERVER

SERVER_URL = f"{SERVER}/api/tank/water-change-log"
DEVICE_ID = "SS501"

DRAIN_RELAY = 6
FILL_RELAY = 16
FEEDER_PIN = 18
FLOAT_PIN = 25  # 플로트 스위치

DRAIN_TIME = 5 #어항>물통
FILL_TIME = 5 #물통>어항

feeder_pwm = None


def setup_gpio():
    global feeder_pwm

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # 플로트 스위치
    GPIO.setup(FLOAT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # 피더 정지 상태 유지
    GPIO.setup(FEEDER_PIN, GPIO.OUT)
    feeder_pwm = GPIO.PWM(FEEDER_PIN, 50)
    feeder_pwm.start(6.6)

    GPIO.setup(DRAIN_RELAY, GPIO.OUT)
    GPIO.setup(FILL_RELAY, GPIO.OUT)

    # 릴레이 OFF
    GPIO.output(DRAIN_RELAY, GPIO.HIGH)
    GPIO.output(FILL_RELAY, GPIO.HIGH)


def drain_on():
    GPIO.output(DRAIN_RELAY, GPIO.LOW)


def drain_off():
    GPIO.output(DRAIN_RELAY, GPIO.HIGH)


def fill_on():
    GPIO.output(FILL_RELAY, GPIO.LOW)


def fill_off():
    GPIO.output(FILL_RELAY, GPIO.HIGH)


def send_result(status, started_at, end_at):
    payload = {
        "deviceId": DEVICE_ID,
        "status": status,
        "startedAt": started_at.isoformat(),
        "endAt": end_at.isoformat()
    }

    try:
        requests.post(
            SERVER_URL,
            json=payload,
            timeout=5
        )
    except Exception as e:
        print("결과 전송 실패:", e)


def run_water_change():
    setup_gpio()

    start_time = datetime.now()

    try:
        print("배수 시작")
        drain_on()
        time.sleep(DRAIN_TIME)
        drain_off()

        time.sleep(0.5)

        print("급수 시작")
        fill_on()

        fill_start = time.time()

        while True:
            float_state = GPIO.input(FLOAT_PIN)

            # 물이 차서 플로트가 올라오면 급수 종료
            if float_state == 1:
                print("목표 수위 도달")
                break

            # 플로트 고장 대비 최대 급수시간 제한
            if time.time() - fill_start > FILL_TIME:
                print("최대 급수 시간 도달")
                break

            time.sleep(0.2)

        fill_off()

        end_time = datetime.now()

        send_result(
            "SUCCESS",
            start_time,
            end_time
        )

        print("환수 완료")

    except Exception as e:
        end_time = datetime.now()

        drain_off()
        fill_off()

        send_result(
            "FAIL",
            start_time,
            end_time
        )

        print("환수 중 오류 발생:", e)

    finally:
        global feeder_pwm

        if feeder_pwm:
            feeder_pwm.stop()

        GPIO.cleanup()


if __name__ == "__main__":
    run_water_change()