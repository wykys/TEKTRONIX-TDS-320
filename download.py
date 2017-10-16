#!/usr/bin/python3
# wykys 2017
# program for download the image screen from TEKTRONIX TDS 320

import serial
import sys

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

        print('Waiting for dates...')

        while (not image_complate):
            byte = self.read_byte()
            img.append(byte)

            #img = (0x49,0x46,0x46,0x20,0x44,0x72,0x69,0x76,0x65,0x72,0x20,0x31,0x2E,0x30,0x00)
            #byte = 0

            i += 1

            print('\rReceive \t{:10d} B'.format(i), end='')

            # check end file
            if (byte == 0 and i > tiff_end_len):
                for j in range(tiff_end_len):
                    image_complate = True
                    if (img[-1*(j+1)] != tiff_end[-1*(j+1)]):
                        image_complate = False
                        break

        print('\n\nReceive Complate')
        self.close_serial_port()

        #fw = open('img_firt_test.tiff', 'wb')
        fw = open('data.txt', 'w')
        fw.write(str(img))
        fw.close()
        print('Image created!')

OsciloImageReader('COM11')
#OsciloImageReader('/dev/ttyUSB0')
