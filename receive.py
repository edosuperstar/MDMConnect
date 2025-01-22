import socket

def calculate_percentage(value):
    # Range di input: -60 a +15
    x_min, x_max = -60, 15
    # Range di output: 0% a 100%
    y_min, y_max = 0, 100
    
    # Calcolo della percentuale
    percentage = (value - x_min) / (x_max - x_min) * (y_max - y_min) + y_min
    return percentage

host = "10.232.10.6"
port = 8234

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.connect((host,port))
	print("Connesso")

	for i in range(1,17):
		comp="A5C33C5AFF63040201"+"{:02x}".format(i)+"EE" #compongo la stringa hex con il valore del ciclo for
		tosend=bytes.fromhex(comp) #converto in byte la stringa esadecimale
		s.send(tosend)

		response = s.recv(1024) #ricevo la risposta in hex
		byt_1 = response[-3] # strippo i byte che mi servono
		byt_2 =response[-2]
		invert = bytes([byt_2,byt_1]) #compongo la stringa hex invertendo i byte
		convert = int.from_bytes(invert, byteorder="big", signed=True) #converto in intero la stringa esadecimale col complemento a due (signed integer)
		result = (convert / 10.0) # risultato divido per 10
		percentuale=calculate_percentage(result)

		print("Risposta ricevuta: Input {} {}db - {}%".format(i,result,percentuale))