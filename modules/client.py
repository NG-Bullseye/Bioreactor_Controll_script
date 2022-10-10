import socket


host = "10.6.51.140"  # "127.0.1.1"
port = 8000  # Make sure it's within the > 1024 $$ <65535 range

s = socket.socket()
s.connect((host, port))

message = input('Message: ')
while message != 'q':
    s.send(message.encode('utf-8'))
    data = s.recv(1024).decode('utf-8')
    print('Received from server: ' + data)
    message = input('Message: ')
s.close()








