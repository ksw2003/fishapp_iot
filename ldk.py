
import RPi.GPIO as GPIO
import threading
import time
import signal

# ==========================================
# 기본 설정
# ==========================================

WATER_OUT_PIN = 6   # 물 빼기 펌프
WATER_IN_PIN = 16   # 물 넣기 펌프
FLOAT_PIN = 25      # 플로트 스위치

PUMP_ON = GPIO.LOW
PUMP_OFF = GPIO.HIGH

# 비상 안전장치: 최대 연속 작동 시간
MAX_RUN_TIME = 30

# 조원 코드와 동일한 플로트 감지 조건
FLOAT_FULL_STATE = 1

stop_event = threading.Event()
stop_reason = None
gpio_ready = False


# ==========================================
# GPIO 초기화
# ==========================================

def setup_gpio():
    global gpio_ready

    GPIO.setmode(GPIO.BCM)

    GPIO.setup(
        WATER_OUT_PIN,
        GPIO.OUT,
        initial=PUMP_OFF
    )

    GPIO.setup(
        WATER_IN_PIN,
        GPIO.OUT,
        initial=PUMP_OFF
    )

    GPIO.setup(
        FLOAT_PIN,
        GPIO.IN,
        pull_up_down=GPIO.PUD_UP
    )

    gpio_ready = True


# ==========================================
# 펌프 정지
# ==========================================

def stop_pumps():
    if gpio_ready:
        GPIO.output(WATER_OUT_PIN, PUMP_OFF)
        GPIO.output(WATER_IN_PIN, PUMP_OFF)


# ==========================================
# 사용자 입력 감지
# ==========================================

def wait_for_input():
    global stop_reason

    try:
        text = input(
            "\n멈추고 싶으시면 아무 문자나 입력하고 "
            "엔터를 누르세요 : "
        )

        if text.strip():
            stop_reason = "사용자 요청"
            stop_event.set()

    except (EOFError, OSError):
        stop_reason = "입력 연결 종료"
        stop_event.set()


# ==========================================
# SSH 종료 및 종료 신호 처리
# ==========================================

def handle_signal(signum, frame):
    global stop_reason

    stop_reason = "종료 신호 감지"
    stop_event.set()
    stop_pumps()


# ==========================================
# 펌프 실행
# ==========================================

def run_pump(pin, action):
    global stop_reason

    stop_event.clear()
    stop_reason = None

    stop_pumps()

    # 물 넣기 시작 전 플로트 확인
    if pin == WATER_IN_PIN:
        if GPIO.input(FLOAT_PIN) == FLOAT_FULL_STATE:
            print("\n이미 목표 수위에 도달했습니다.")
            return

    print(f"\n{action} 중입니다...", flush=True)

    input_thread = threading.Thread(
        target=wait_for_input,
        daemon=True
    )
    input_thread.start()

    start_time = time.monotonic()

    try:
        GPIO.output(pin, PUMP_ON)

        while not stop_event.is_set():

            # 물 넣기: 플로트가 1이면 자동 정지
            if pin == WATER_IN_PIN:
                if GPIO.input(FLOAT_PIN) == FLOAT_FULL_STATE:
                    stop_reason = "플로트 스위치 감지"
                    break

            # 최대 작동 시간 초과
            if time.monotonic() - start_time >= MAX_RUN_TIME:
                stop_reason = "최대 작동 시간 초과"
                break

            time.sleep(0.05)

    finally:
        stop_pumps()

    print(f"\n{action}가 중지되었습니다.")
    print(f"중지 사유: {stop_reason or '사용자 요청'}")


# ==========================================
# 메인 프로그램
# ==========================================

def main():
    signal.signal(signal.SIGHUP, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    try:
        setup_gpio()

        choice = input(
            "무엇을 하시겠습니까? "
            "(물넣기/물빼기) : "
        ).strip().replace(" ", "")

        if choice == "물넣기":
            run_pump(WATER_IN_PIN, "물넣기")

        elif choice == "물빼기":
            run_pump(WATER_OUT_PIN, "물빼기")

        else:
            print("잘못된 입력입니다.")

    except KeyboardInterrupt:
        print("\n사용자가 종료했습니다.")

    except Exception as e:
        print(f"\n오류 발생: {e}")

    finally:
        stop_pumps()

        if gpio_ready:
            GPIO.cleanup()

        print("\n프로그램을 종료합니다.")


if __name__ == "__main__":
    main()
