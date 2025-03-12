import socket
import json
navn = input('navn: ')
alder = int(input('alder: '))
martin = {'navn':navn,'alder':alder}

martin_lugter = json.dumps(martin)

s = socket.socket()
host = 'localhost' # needs to be in quote
port = 1234
s.connect((host, port))

inpt = martin_lugter
s.send(inpt.encode())
print(s.recv(1024).decode())
print("the message has been sent")