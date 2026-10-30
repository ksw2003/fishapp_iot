import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000


def read_adc(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    return ((adc[1] & 3) << 8) + adc[2]


def read_tds():
    values = []

    # 5번 읽어서 평균값 사용
    for _ in range(5):
        values.append(read_adc(0))
        time.sleep(0.05)

    return int(sum(values) / len(values))