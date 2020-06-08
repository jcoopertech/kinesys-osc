import socket
import uuid
import os

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('iow.jcooper.tech', 10124)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)

returnstring = ""
try:

    # Send data
    uuid_4 = uuid.uuid4()
    email = input("Please enter your email address - it's encrypted on your machine, but used as your ID.")
    message = bytes("kinesys-osc:licencerequest_public-key:{0}".format(str(uuid_4),str(email)),"ascii")
    print('sending {!r}'.format(message))
    sock.sendall(message)

    print(message)
    # Look for the response
    amount_received = 0
    amount_expected = len(message)

    while amount_received < amount_expected:
        data = sock.recv(16)
        decoded = data.decode("ascii")
        amount_received += len(data)
        print('received {!r}'.format(decoded))
        returnstring += "{0}".format(decoded)

finally:
    print('closing socket')
    sock.close()

print(returnstring)
