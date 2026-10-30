
import glob
import time

BASE_DIR = "/sys/bus/w1/devices/"

def read_temp():
    devices = glob.glob(BASE_DIR + "28-*")

    if not devices:
        print("오류: DS18B20 센서를 찾을 수 없습니다.")
        return None

    device_file = devices[0] + "/w1_slave"

    try:
        with open(device_file, "r") as f:
            lines = f.readlines()

        if not lines[0].strip().endswith("YES"):
            print("오류: 센서 데이터 검증 실패")
            return None

        pos = lines[1].find("t=")

        if pos == -1:
            print("오류: 온도 데이터가 없습니다.")
            return None

        temp_c = int(lines[1][pos + 2:]) / 1000.0
        return temp_c

    except Exception as e:
        print("센서 읽기 오류:", e)
        return None


while True:
    temp = read_temp()

    if temp is not None:
        print(f"[수온 센서] 현재 온도: {temp:.2f}°C")

    time.sleep(2)
