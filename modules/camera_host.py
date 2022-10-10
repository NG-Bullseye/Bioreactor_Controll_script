import socket
import threading


def runServer():

	print("Server Script Started")
	port = 8000  # Make sure it's within the > 1024 $$ <65535 range
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("0.0.0.0", port))
	s.listen(1)

	print("Waiting for incoming connection..")
	client_socket, adress = s.accept()
	print("Connection from: " + str(adress))
	while True:
		data = client_socket.recv(1024).decode('utf-8')
		if not data:
			break
		print('Recieved: ' + data)
		if data=="stop":
			client_socket.send(data.encode('utf-8'))
			client_socket.close()
			print("Client send Stop Command. Script will be terminated.")
			exit(4)
		elif data=="go":
			main.py
		elif data=="pause":


thread = threading.Thread(target=runServer)
thread.start()
