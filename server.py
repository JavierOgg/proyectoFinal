# Echo server program
import socket
import json
import pdb

HOST = 'localhost'                 # Symbolic name meaning all available interfaces
PORT = 9999              # Arbitrary non-privileged port

from funciones import entrenarClasificador
from funciones import conexion
        
clasificador, word_features = entrenarClasificador()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
while True:
	print 'Esperando conexiones'
	conn, addr = s.accept()
	print 'Connected by', addr
	while 1:
	    data = conn.recv(1024)
	    if data: 
	    	print data
	    else: 
	    	break
		pdb.set_trace()
	    conn.sendall(json.dumps(word_features))
	conn.close()
