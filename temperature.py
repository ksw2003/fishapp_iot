import glob
import time

base_dir = "/sys/bus/w1/devices/"

def get_device_file():
    devices = glob.glob(base_dir + "28-*")

    if not devices:
        raise Exception("DS18B20 센서를 찾을 수 없습니다.")

    return devices[0] + "/w1_slave"


def read_temp():
    device_file = get_device_file()

    while True:
        with open(device_file, "r") as f:
            lines = f.readlines()

        if lines[0].strip().endswith("YES"):
            break

        time.sleep(0.2)

    equals_pos = lines[1].find("t=")

    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        return int(float(temp_string) / 1000.0)

    return None