import socket
import select

HEADER_LENGTH = 10

IP = "0.0.0.0"
PORT = 1234

# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((IP, PORT))

# This makes server listen to new connections
server_socket.listen()

# List of sockets for select.select()
sockets_list = [server_socket]
#print(sockets_list)

# List of connected clients - socket as a key, user header and name as data
clients = {}

print(f'Listening for connections on {IP}:{PORT}...')

# Handles message receiving
def receive_message(client_socket):

    try:

        # Receive our "header" containing message length, it's size is defined and constant
        message_header = client_socket.recv(HEADER_LENGTH)

        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            return False

        # Convert header to int value
        message_length = int(message_header.decode('utf-8').strip())

        # Return an object of message header and message data
        return {'header': message_header, 'data': client_socket.recv(message_length) , 'status': client_socket.recv(7)}

    except:
        return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)


    # Iterate over notified sockets
    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket:

            # Accept new connection
            # That gives us new socket - client socket, connected to this given client only, it's unique for that client
            # The other returned object is ip/port set
            client_socket, client_address = server_socket.accept()
            print("Connection has been established! |" + " IP " + client_address[0] + " | Port" + str(client_address[1]))

            # Client should send his name right away, receive it
            user = receive_message(client_socket)
            print(user)

            # If False - client disconnected before he sent his name
            if user is False:
                continue

            # Add accepted socket to select.select() list
            sockets_list.append(client_socket)

            # Also save username and username header
            clients[client_socket] = user
            for client_socket in clients:
                client_socket.send(str.encode('update') + f"{len(clients):<10}".encode('utf-8'))
                for x in clients:
                    client_socket.send(clients[x]['header'] + clients[x]['data'] + clients[x]['status'])
            print('Accepted new connection from {}:{}, username: {}, status: {}'.format(*client_address, user['data'].decode('utf-8'),user['status'].decode('utf-8')))

        # Else existing socket is sending a message
        else:

            # Receive message
            message = receive_message(notified_socket)

            # If False, client disconnected, cleanup
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of users
                del clients[notified_socket]
                print(clients)
              #important
                for client_socket in clients:
                    client_socket.send(str.encode('update') + f"{len(clients):<10}".encode('utf-8'))
                    for x in clients:
                        client_socket.send(clients[x]['header'] + clients[x]['data'] + clients[x]['status'])
                #important
                continue

            # Get user by notified socket, so we will know who sent the message
            user = clients[notified_socket]

            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            # Iterate over connected clients and broadcast message
            if user["status"].decode('utf-8') == "Teacher":
                for client_socket in clients:
                    # But don't sent it to sender
                    if client_socket != notified_socket:

                        # Send user and message (both with their headers)
                        # We are reusing here message header sent by sender, and saved username header send by user when he connected
                        client_socket.send(str.encode('messag')+user['header'] + user['data'] + message['header'] + message['data'])
            elif user["status"].decode('utf-8') == "Student":
                for client_socket in clients:
                    if clients[client_socket]["status"].decode('utf-8') == "Teacher":
                        client_socket.send(str.encode('messag') + user['header'] + user['data'] + message['header'] + message['data'])

    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]
