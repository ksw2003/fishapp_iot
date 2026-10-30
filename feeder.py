import RPi.GPIO as GPIO
import time

SERVO_PIN = 18

def run_feeding():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(SERVO_PIN, GPIO.OUT)

    pwm = GPIO.PWM(SERVO_PIN, 50)
    pwm.start(7.5)

    try:
        print("먹이 배급 시작")

        pwm.ChangeDutyCycle(10)
        time.sleep(3)

        pwm.ChangeDutyCycle(7.5)

        print("먹이 배급 완료")

    finally:
        pwm.stop()
        GPIO.cleanup()


if __name__ == "__main__":
    run_feeding()