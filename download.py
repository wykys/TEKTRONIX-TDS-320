#!/usr/bin/python3
# wykys 2017
# program for download the image screen from TEKTRONIX TDS 320

import serial
import time
import sys
import os

IMG_DIR = 'img'

class OsciloImageReader():
    def __init__(self, port):
        """ initialization """
        self.port = port
        self.ser = serial.Serial()
        self.open_serial_port()
        self.read_TIFF()

    def open_serial_port(self):
        """ open connection """
        self.ser.port = self.port
        self.ser.baudrate = 19200
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.parity = serial.PARITY_NONE
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.timeout = None
        try:
            self.ser.open()
            print('Port {} is open.'.format(self.port))
        except serial.SerialException:
            print('Port {} opening error!'.format(self.port))
            sys.exit()

    def read_byte(self):
        """ read one byte """
        return int.from_bytes(self.ser.read(1), byteorder='little', signed=False)

    def send_byte(self, byte):
        """ write one byte """
        self.ser.write(bytes((byte,)))
        time.sleep(0.01)

    def send_cmd(self, cmd):
        """ send command """
        if type(cmd) == str:
            for c in cmd:
                self.send_byte(ord(c))
            self.send_byte(10) # LF
            print('Send command {}.'.format(cmd))

    def close_serial_port(self):
        """ end connection """
        self.ser.close()
        print('Close port')

    def read_TIFF(self):
        tiff_end = (0x49,0x46,0x46,0x20,0x44,0x72,0x69,0x76,0x65,0x72,0x20,0x31,0x2E,0x30,0x00)
        tiff_end_len = len(tiff_end)
        image_complate = False

        img = []
        i = 0

        self.send_cmd('HARDCopy:PORT RS232')
        self.send_cmd('HARDCopy:FORMat TIFf')
        self.send_cmd('HARDCopy:LAYout PORTRait')
        self.send_cmd('HARDCopy STARt')

        print('Waiting for dates...')

        while (not image_complate):
            byte = self.read_byte()
            img.append(byte)
            i += 1

            print('\rReceive{:71d} B'.format(i), end='')

            # check end file
            if (byte == 0 and i > tiff_end_len):
                for j in range(tiff_end_len):
                    image_complate = True
                    if (img[-1*(j+1)] != tiff_end[-1*(j+1)]):
                        image_complate = False
                        break

        print('\nReceive Complate')
        self.close_serial_port()

        if not os.path.exists(IMG_DIR):
            os.makedirs(IMG_DIR)

        img_url = IMG_DIR + '/'
        img_url += time.strftime('%Y-%m-%d_%H-%M-%S_', time.localtime())
        img_url += input('Enter image name >>> ') + '.tiff'

        fw = open(img_url, 'wb')
        fw.write(bytes(img))
        fw.close()
        print('Image created!')


if sys.platform == 'win32':
    OsciloImageReader('COM11')
else:
    OsciloImageReader('/dev/ttyUSB0')
