import socket

class MdmConnect:
	def __init__(self, host, port):
		self.host = host
		self.port = port

	def setHost(self, host):
		self.host = host

	def setPort(self, port):
		self.port = port 

	def getAllInputGains(self):
		return_list = []
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect((self.host,self.port))
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
				return_list.append(result)
			s.close()
		return return_list

	def getGainOfInputFader(self, faderNum: int):
		if (1 <= faderNum <= 16): #controllo il valore in ingresso, che deve essere compreso tra 1 e 16
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
				s.connect((self.host,self.port))
				comp="A5C33C5AFF63040201"+"{:02x}".format(faderNum)+"EE" #compongo la stringa hex con il valore del ciclo for
				tosend=bytes.fromhex(comp) #converto in byte la stringa esadecimale
				s.send(tosend)

				response = s.recv(1024) #ricevo la risposta in hex
				byt_1 = response[-3] # strippo i byte che mi servono
				byt_2 =response[-2]
				invert = bytes([byt_2,byt_1]) #compongo la stringa hex invertendo i byte
				convert = int.from_bytes(invert, byteorder="big", signed=True) #converto in intero la stringa esadecimale col complemento a due (signed integer)
				result = (convert / 10.0) # risultato divido per 10
				s.close()
			return result
		else:
			raise ValueError(f"Il valore {faderNum} è fuori dall'intervallo consentito (1-16).")

	def getAllInputMuteStatus(self):
		return_list = []
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect((self.host,self.port))
			for i in range(1,17):
				comp="A5C33C5AFF63030201"+"{:02x}".format(i)+"EE" #compongo la stringa hex con il valore del ciclo for
				tosend=bytes.fromhex(comp) #converto in byte la stringa esadecimale
				s.send(tosend)

				response = s.recv(1024) #ricevo la risposta in hex
				byt =response[-2]
				result = True if byt == 0x01 else False
				return_list.append(result)
			s.close()
		return return_list

	def getMuteStatusOfInputChannel(self, channel: int):
		if (1 <= channel <= 16): #controllo il valore in ingresso, che deve essere compreso tra 1 e 16
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
				s.connect((self.host,self.port))
				comp="A5C33C5AFF63030201"+"{:02x}".format(channel)+"EE" #compongo la stringa hex con il valore del ciclo for
				tosend=bytes.fromhex(comp) #converto in byte la stringa esadecimale
				s.send(tosend)

				response = s.recv(1024) #ricevo la risposta in hex
				byt =response[-2]
				result = True if byt == 0x01 else False
				s.close()
			return result
		else:
			raise ValueError(f"Il valore {channel} è fuori dall'intervallo consentito (1-16).")

	def setGainOfInputFader(self, gainLevel, faderNum):
		gainLevel = round(gainLevel, 1)  # Arrotondo il gain alla prima cifra decimale
		if (1 <= faderNum <= 16):  # Controllo che i dati di input stiano all'interno del range
			if (-60 <= gainLevel <= 15):
				scaled_value = int(gainLevel * 10)
				convert = scaled_value.to_bytes(2, byteorder="big", signed=True)
				invert = convert[::-1]
				stringaXXYY = ''.join(f'{byte:02X}' for byte in invert)
				to_send = bytes.fromhex("A5C33C5AFF36040401""{:02x}".format(faderNum) + stringaXXYY + "EE")

				try:
					with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
						s.settimeout(0.5)  # Timeout di mezzo secondo
						s.connect((self.host, self.port))
						s.send(to_send)
						response = s.recv(1024)  # Ricevo la risposta in hex
						if response != b'\x00':
							raise ConnectionError("Errore. MDM ha risposto con un errore. Comando non inviato.")
						s.close()
				except socket.timeout:
					print(f"Timeout: Il dispositivo non ha risposto in tempo per il fader {faderNum}.")
				except Exception as e:
					print(f"Errore durante l'invio del comando per il fader {faderNum}: {e}")
			else:
				raise ValueError(f"Il valore {gainLevel} è fuori dall'intervallo consentito (-60 / +15).")
		else:
			raise ValueError(f"Il valore {faderNum} è fuori dall'intervallo consentito (1-16).")

	def setMuteOfInputChannel(self, channel, set):
		if (1 <= channel <= 16): #controllo il valore in ingresso, che deve essere compreso tra 1 e 16
			if set:
				with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
					s.connect((self.host,self.port))
					comp="A5C33C5AFF36030301"+"{:02x}".format(channel)+"01EE" #compongo la stringa hex con il valore del ciclo for
					tosend=bytes.fromhex(comp) #converto in byte la stringa esadecimale
					s.send(tosend)
					response = s.recv(1024) #ricevo la risposta in hex
					if response != b'\x00':
						raise ConnectionError(f"Errore. MDM ha risposto con un errore. Comando non inviato.")
					s.close()
			else:
				with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
					s.connect((self.host,self.port))
					comp="A5C33C5AFF36030301"+"{:02x}".format(channel)+"00EE" #compongo la stringa hex con il valore del ciclo for
					tosend=bytes.fromhex(comp) #converto in byte la stringa esadecimale
					s.send(tosend)
					response = s.recv(1024) #ricevo la risposta in hex
					if response != b'\x00':
						raise ConnectionError(f"Errore. MDM ha risposto con un errore. Comando non inviato.")
					s.close()
			return 0
		else:
			raise ValueError(f"Il valore {channel} è fuori dall'intervallo consentito (1-16).")

	def recallScene(self,sceneNum):
		if (1 <= sceneNum <= 80): #controllo il valore in ingresso, che deve essere compreso tra 1 e 16
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
				s.connect((self.host,self.port))
				comp="A5C33C5AFF360201"+"{:02x}".format(sceneNum)+"EE" #compongo la stringa hex con il valore del ciclo for
				tosend=bytes.fromhex(comp) #converto in byte la stringa esadecimale
				s.send(tosend)
				s.close()
			return 0
		else:
			raise ValueError(f"Il valore {sceneNum} è fuori dall'intervallo consentito (1-16).")

	def getCurrentScene(self):
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect((self.host, self.port))
			tosend = bytes.fromhex("A5C33C5AFF630200EE")  # converto in byte la stringa esadecimale
			s.send(tosend)
			response = s.recv(1024)  # ricevo la risposta in hex
			result = response[-2]
			s.close()
		return result

