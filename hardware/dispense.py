import serial
import time

from config import AppConfig


def dispense(n):
    """Dispenses a given amount of the given medicine and waits"""
    config = AppConfig()

    ser = serial.Serial(config.hardware.serial_port, 9600)

    if n < 10:
        ser.write('d0%d' % n)
    else:
        ser.write('d%d' % n)

    timeout_ctr = 20
    while True:
        if timeout_ctr == 0:
            raise Exception('Device failed to respond')

        timeout_ctr -= 1

        if ser.readline().rstrip() == 'ack':
            return
        time.sleep(0.1)

