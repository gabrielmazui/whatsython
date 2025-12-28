import socket
import sys
import threading
import shutil
import os
import json


if os.name == "nt":
    import msvcrt
    def getch():
        return msvcrt.getch().decode(errors="ignore")
else:
    import sys, termios, tty
    def getch():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

def usage():
    print("usage: py chat_client.py NAME HOST PORT")

def clear():
    os.system("cls")

def clear_line():
    """
    Limpa a linha atual no terminal e move o cursor para o início.
    """
    print("\r\033[K", end="", flush=True)

def move_cursor(lines):
    """
    Move o cursor verticalmente.
    - lines > 0 : desce `lines` linhas
    - lines < 0 : sobe `abs(lines)` linhas
    """
    if lines > 0:
        print(f"\033[{lines}B", end="", flush=True)  # desce
    elif lines < 0:
        print(f"\033[{abs(lines)}A", end="", flush=True)  # sobe


def send_message_server(s, m, user):
    dir = {
        "type": "message",
        "message": m
    }
    j = json.dumps(dir).encode()
    tamanho = len(j)
    header = tamanho.to_bytes(2, byteorder="big")
    content = header + j
    s.sendall(content)

buffer = ""
firstLine = True

def run_keyboard(user, s):
    global buffer
    global firstLine

    print(f"{user}> ", end="", flush=True)
    try:

        while True:
            ch = getch()
            if ch == '\x03':
                raise KeyboardInterrupt
            if ch in ("\r", "\n"):  # Enter
                clear_line()
                if firstLine == False:
                    move_cursor(-1)
                else:
                    firstLine = False
                print(f"{user}: {buffer}", end="", flush=True)
                print(f"\n\n{user}> ", end="", flush=True)

                send_message_server(s, buffer, user)
                buffer = ""
                

            elif ch in ("\x08", "\x7f"):  # Backspace
                if buffer:
                    buffer = buffer[:-1]
                    print("\b \b", end="", flush=True)

            else:
                buffer += ch
                print(ch, end="", flush=True)
    except KeyboardInterrupt:
        print("\n[Saindo do chat]")
        s.close()
        os._exit(0)

def listen_to_server(s, name):
    global firstLine
    global buffer
    server_buffer = b""
    try:
        while True:
            data = s.recv(4096)
            if not data:
                print("\n[Servidor desconectado]")
                s.close()
                os._exit(1)
            server_buffer += data
            if len(server_buffer) < 2:
                break
            json_sz = int.from_bytes(server_buffer[:2], byteorder="big")
            tamanho = len(server_buffer)
            if tamanho - 2 < json_sz:
                break
            server_msg = server_buffer[2:2+json_sz].decode()
            server_buffer = server_buffer[2+json_sz:]
            json_msg = json.loads(server_msg)
            if json_msg["type"] == "message":
                clear_line()
                if firstLine == False:
                    move_cursor(-1)
                else:
                    firstLine = False
                print(f"{json_msg['nick']}: {json_msg['message']}",end="", flush=True)
                print(f"\n\n{name}> {buffer}", end="", flush=True)
                
                
    except (ConnectionResetError, BrokenPipeError, OSError):
        s.close()
        print("\n[Servidor desconectado]")
        os._exit(1)
    except KeyboardInterrupt:
        s.close()
        print("\n[Saindo do chat]")
        os._exit(0)

        
        
def main(argv):
    try:
        name = argv[1]
        host = argv[2]
        port = int(argv[3])
    except:
        usage()
        return
    clear()

    s = socket.socket()
    s.connect((host, port))
    hello_dir = {
        "type": "hello",
        "nick": name
    }
    json_tosend = json.dumps(hello_dir).encode()
    tamanho = len(json_tosend)
    header = tamanho.to_bytes(2, byteorder="big")
    content = header + json_tosend
    s.sendall(content)

    t1 = threading.Thread(target=listen_to_server, daemon=True, args=(s, name))
    
    t1.start()

    run_keyboard(name, s)

main(sys.argv)
