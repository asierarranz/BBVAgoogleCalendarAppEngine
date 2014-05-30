import socket

HOST = '23.97.218.60'   
PORT = 7777              
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
raw_input("Pulsa ENTER para enviar datos")
f = open('accion.txt', 'r')
accion=f.readline()
s.sendall(accion)
data = s.recv(1024)
s.close()
print 'Received', str(data)
raw_input()
