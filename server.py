import socket
import pickle
import os
import random

HOST = '127.0.0.1'
PORT = 9090
SERVER_MESSAGE_HELLO = 'server_check_keys'
sock = socket.socket()
sock.bind(('', PORT))
sock.listen(1)
conn, addr = sock.accept()
b = 9
A, B, K = 0, 0, 0


def decrypt(s, private, public):
    return ''.join(map(chr, [(x-private-public) for x in map(ord, s)]))


def has_keys_in_storage():
    return os.path.isfile('client') and os.path.getsize('client') > 0


def check_key():
    global K, B, A
    msg = conn.recv(1024)
    p, g, A = pickle.loads(msg)
    B = g ** b % p
    K = A ** b % p
    with open('server', 'wb') as f:
        f.write(pickle.dumps((B, K)))
    print(f"[server] Generated private and public keys")
    conn.send(pickle.dumps(B))
    msg = conn.recv(1024)
    if decrypt(pickle.loads(msg), K, A) != SERVER_MESSAGE_HELLO:
        print("[server] Wrong client key. Closing connection...")
        conn.close()
    else:
        print("[server] Key validation success. Starting listening...")
        start_serving()


def start_serving():
    new_port = random.randint(1000, 65536)
    conn.send(pickle.dumps(decrypt(str(new_port), K, B)))
    conn.close()

    s1 = socket.socket()
    s1.bind(('', new_port))
    s1.listen(1)
    conn1, addr1 = s1.accept()

    while True:
        data = conn1.recv(1024)
        if not data:
            break
        print(f"[{addr1[0]}] {decrypt(pickle.loads(data), K, B)}")
    conn1.close()


if __name__ == '__main__':
    check_key()