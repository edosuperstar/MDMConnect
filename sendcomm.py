import socket

host = "10.232.10.6"
port = 8234

hex_message = "A5C33C5AFF3605040101000AEE"

message = bytes.fromhex(hex_message)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.connect((host,port))
	print("Connesso")

	s.send(message)
	print("Inviato")

	response = s.recv(1024)
	print(f"Risposta ricevuta: {response.hex()}")
