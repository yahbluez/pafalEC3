#!/usr/bin/python
""" 20191221
This is a cron job that reads energy values
with an optical IR interface from pafal counter
it stores the values at <tmp>
as raw data and as json

/?!
/PAF5EC3gr00006
000
0.0.0(71579625)
0.0.1(PAF)
F.F(00)
0.2.0(1.27)
1.8.0*00(019446.38)
2.8.0*00(023813.75)
C.2.1(000000000000)(                                                )
0.2.2(:::::G11)!
}
"""

import serial
import time
from io import open

tty = '/dev/ttyUSB0'
raw = '/dev/shm/pafalEC3.1'
json = '/dev/shm/pafalEC3.json'

idxDate = 0
idx180 = 8
idx280 = 9
posStart = 9
posEnd = 18

Identification_request_message = b'\x2f\x3f\x21\x0d\x0a' # "/?!" <cr><lf>  Identification request message 5 byte
Identification_response_message = b'\x06\x30\x30\x30\x0d\x0a'


pafal = serial.Serial()
pafal.port = tty
pafal.baudrate = 300
pafal.bytesize = 7
pafal.parity = serial.PARITY_EVEN
pafal.stopbits = serial.STOPBITS_ONE
pafal.xonxoff = True
pafal.rtscts = False
pafal.timeout = 3
pafal.write_timeout = 2
# pafal.exclusive = True

try:
    pafal.open()
except Exception as e:
    print("error open serial port: " + str(e))
    exit()

request = pafal.write(Identification_request_message)
if request != 5:
    print("error Identification_request_message: ", request)
    exit()

lines = []
lines.append(time.strftime('%Y %m %d %H %M', time.gmtime()) + '\r\n')
line = pafal.readline().decode('utf-8')
lines.append(line)
line = pafal.readline().decode('utf-8')
lines.append(line)
response = pafal.write(Identification_response_message)

while line:
    line = pafal.readline().decode('utf-8')
    lines.append(line)
pafal.close()

if len(lines) < 10:
    print("error to less lines from pafal: {}".format(len(lines)))
    exit()

with open(raw, 'w', encoding='utf-8') as raw_file:
    raw_file.writelines(lines)

vDate = lines[idxDate].replace(' ', '').strip()
v180 = lines[idx180][posStart:posEnd]
v280 = lines[idx280][posStart:posEnd]

jstr = "{" + '"date": {}, "180": {}, "280": {}'.format(vDate, v180, v280) + "}\n"
with open(json, 'w', encoding='utf-8') as json_file:
    json_file.writelines(jstr)

exit()
