import os, sys, socket
from dotenv import load_dotenv
from struct import pack


class MixnetClient:

    def __init__(self, entry, port, group = 0):
        self.entry = entry
        self.port = port
        self.group = group
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((entry, port))

    def send(self, m):
        payload = m.encode()
        length = len(payload)
        packet_format= f'!I{length}s'
        packet = pack(packet_format, length, payload)
        self.s.send(packet)

        if self.s.recv(2) == b'\x06':
            print("Respuesta correcta")
            sys.exit(0)
        elif self.s.recv(2) == b'\x15':
            print("Algo salió mal")
            sys.exit(1)
    
    def __prepare_message(self, m):
        # TODO: Implement message encryption
        pass


load_dotenv()

mixnet_entry = os.getenv('MIXNET_ENTRY')
r_port = int(os.getenv('PORT'))
m_group = os.getenv('GROUP')

client = MixnetClient(mixnet_entry, r_port, m_group)

client.send("Esto es una prueba")



