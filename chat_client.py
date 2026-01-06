import socket
import sys
import threading
import shutil
import os
import json

from utils import *

#global variables

buffer = ""
firstLine = True
localUser = ""
localChat = ""
types_functions = {}
commands_functions = {}
s = socket.socket()
stop_event = threading.Event()
chat_started = threading.Event()
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

def send_message_server(m):
    global s
    dir = {
        "type": "message",
        "message": m
    }
    try:    
        j = json.dumps(dir).encode()
        tamanho = len(j)
        header = tamanho.to_bytes(2, byteorder="big")
        content = header + j
        s.sendall(content)
    except:
        return False
    return True


def leave_chat():
    stop_event.set()
    print(f"\n{RED}[Saindo do chat]{RESET}", end="", flush=True)

def command_types(comm):
    global commands_functions
    def decorator(func):
        commands_functions[comm] = func
        return func
    return decorator

@command_types("help")
def help_command():
    print(F"{GREEN}List of commands:\n", end="", flush=True)
    print(f"{CYAN}/users\n", end="", flush=True)
    print(f"{CYAN}/quit\n", end="", flush=True)
    print(f"{CYAN}/dm (USER) (MESSAGE)", end="", flush=True)
    print(RESET, end="", flush=True)

@command_types("users")
def users_command():
    global s
    json_dir = {}
    json_dir["type"] = "list"
    
    try:
        json_to_send = json.dumps(json_dir).encode()
        tam = len(json_to_send)
        header = tam.to_bytes(2, byteorder="big")
        content = header + json_to_send
        s.sendall(content)
    except:
        print(f"{RED}An error ocurred, try again{RESET}", end="", flush=True)
    
    
@command_types("quit")
def quit_command():
    leave_chat()

@command_types("dm")
def dm_command(user, message):
    global localUser
    global s
    if user == localUser:
        print(f"{RED}You cant message yourself{RESET}", end="", flush=True)
        return
    json_dir = {}
    json_dir["type"] = "direct_message"
    json_dir["nick"] = user
    json_dir["message"] = message
    try:
        json_to_send = json.dumps(json_dir).encode()
        tam = len(json_to_send)
        header = tam.to_bytes(2, byteorder="big")
        content = header + json_to_send
        s.sendall(content)
        print(f"{CYAN}[DM] {GREEN}YOU {CYAN}to {BLUE}{user}{RESET}: {message}",end="", flush=True)
    except:
        print(f"{RED}An error occurred, try again{RESET}", end="", flush=True)
        return

    


def message_handle():
    global s
    global buffer
    global firstLine
    if len(buffer) > 0:
        clear_line()
        if firstLine == False:
            move_cursor(-1)
        else:
            firstLine = False

        if buffer[0] == '/':
            content = buffer.split('/', 1)[1]
            content = content.split(' ', 2)
            command = content[0]
            if command == "dm":
                # envia user e mensagem
                if len(content) >= 3:
                    commands_functions[command](content[1], content[2])
                else:
                    print(f"{RED}Invalid command. Usage: /dm <user> <message>{RESET}", end="", flush=True)

            elif commands_functions.get(command):
                commands_functions[command]()
            else:
                print(f"{RED}Command does not exist{RESET}", end="", flush=True)

        else:
            
            if send_message_server(buffer):

                print(f"{GREEN}{localUser}{RESET}: {buffer}", end="", flush=True)
            else:
                print(f"{RED}An error occurred while trying to send the message{RESET}", end="", flush=True)

        print(f"\n\n{localUser}> ", end="", flush=True)
        buffer = ""

    
def run_keyboard():
    global s
    global buffer
    global firstLine
    global localUser
    print(f"{GREEN}----------{CYAN}{localChat}{GREEN}----------{RESET}")
    print(f"{localUser}> ", end="", flush=True)
    try:
        chat_started.set()
        while not stop_event.is_set():
            ch = getch()
            if ch == '\x03':
                raise KeyboardInterrupt
            if ch in ("\r", "\n"):  # Enter
                message_handle()
                
            elif ch in ("\x08", "\x7f"):  # Backspace
                if buffer:
                    buffer = buffer[:-1]
                    print("\b \b", end="", flush=True)

            else:
                buffer += ch
                print(ch, end="", flush=True)
    except KeyboardInterrupt:
        stop_event.set()
        print(f"\n{RED}[Saindo do chat]{RESET}", end="", flush=True)
        


def server_types(type):
    def decorator(func):
        types_functions[type] = func
        return func
    return decorator

@server_types("message")
def msg_srv(json_msg):
    global localUser
    global firstLine

    clear_line()
    if firstLine == False:
        move_cursor(-1)
    else:
        
        firstLine = False
    print(f"{json_msg['nick']}: {json_msg['message']}",end="", flush=True)
    print(f"\n\n{localUser}> {buffer}", end="", flush=True)

@server_types("join")
def join_srv(json_msg):
    global localUser
    global firstLine

    clear_line()
    if firstLine == False:
        move_cursor(-1)
    else:
        firstLine = False
    print(f"{BLUE}{json_msg['nick']} has joined the chat{RESET}",end="", flush=True)
    print(f"\n\n{localUser}> {buffer}", end="", flush=True)

@server_types("leave")
def leave_srv(json_msg):
    global localUser
    global firstLine

    clear_line()
    if firstLine == False:
        move_cursor(-1)
    else:
        firstLine = False
    print(f"{RED}{json_msg['nick']} has left the chat{RESET}",end="", flush=True)
    print(f"\n\n{localUser}> {buffer}", end="", flush=True)

@server_types("error")
def error_srv(json_msg):
    global localUser
    global firstLine

    clear_line()
    if firstLine == False:
        move_cursor(-1)
    else:
        firstLine = False
    print(f"{RED}[SERVER ERROR] {json_msg["message"]}{RESET}",end="", flush=True)
    print(f"\n\n{localUser}> {buffer}", end="", flush=True)

@server_types("direct_message")
def dm_srv(json_msg):
    global localUser
    global firstLine

    clear_line()
    if firstLine == False:
        move_cursor(-1)
    else:
        firstLine = False
    print(f"{CYAN}[DM] {BLUE}{json_msg["nick"]} {CYAN}to {GREEN}YOU{RESET}: {json_msg["message"]}",end="", flush=True)
    print(f"\n\n{localUser}> {buffer}", end="", flush=True)

@server_types("list")
def users_srv(json_msg):
    global localUser
    global firstLine

    clear_line()
    if firstLine == False:
        move_cursor(-2)
    else:
        move_cursor(-1)
        firstLine = False
    print(f"{GREEN}Users in this chat:\n{RESET}",end="", flush=True)
    print(f"{CYAN}{json_msg["message"]}{RESET}",end="", flush=True)
    print(f"\n\n{localUser}> {buffer}", end="", flush=True)

def listen_to_server():
    global s
    global firstLine
    global buffer
    global localUser
    global types_functions
    chat_started.wait()

    server_buffer = b""
    try:
        while stop_event.is_set() == False:
            data = s.recv(4096)
            if not data:
                if stop_event.is_set():
                    return  # saída limpa (/quit)
                print(f"\n{RED}[Servidor desconectado]{RESET}")
                return
            server_buffer += data
            if len(server_buffer) < 2:
                continue
            json_sz = int.from_bytes(server_buffer[:2], byteorder="big")
            tamanho = len(server_buffer)
            if tamanho - 2 < json_sz:
                continue
            server_msg = server_buffer[2:2+json_sz].decode()
            server_buffer = server_buffer[2+json_sz:]
            try:
                json_msg = json.loads(server_msg)
                if types_functions.get(json_msg["type"]):
                    types_functions[json_msg["type"]](json_msg)
            except:
                #talvez printar o erro em algum lugar
                continue
            

                
    except (ConnectionResetError, BrokenPipeError, OSError):
        s.close()
        print(f"\n{RED}[Servidor desconectado]{RESET}")
        return
    except KeyboardInterrupt:
        stop_event.set()
        s.close()
        print(f"\n{RED}[Saindo do chat]{RESET}")
        return

        
def wait_for_ok():
    global s

    buffer_temp = b""
    buffer_sz = None
    while True:
        data = s.recv(4096)
        if not data:
            print(f"{RED}Could not connect to server{RESET}")
            s.close()
            return False
        buffer_temp+=data
        if len(buffer_temp) >= 2:
            buffer_sz = int.from_bytes(buffer_temp[:2], byteorder="big")
            break
    while len(buffer_temp) - 2 < buffer_sz:
        data = s.recv(4096)
        if not data:
            print(f"{RED}Could not connect to server{RESET}")
            s.close()
            return False
        buffer_temp+=data
    try:
        buffer_temp = buffer_temp[2:2+buffer_sz]
        j = json.loads(buffer_temp.decode())
        if j["type"] == "ok":
            return True
        else:
            print(f"{RED}{j["message"]}{RESET}")
            s.close()
            return False
    except json.JSONDecodeError:
        print(f"{RED}Error decoding server message{RESET}")
        s.close()
        return False


def choose_chat():
    global s
    global localChat
    try:
        json_dict = {}
        json_dict["type"] = "chat_list"
        j = json.dumps(json_dict).encode()
        json_sz = len(j)
        header = json_sz.to_bytes(2, byteorder="big")
        packet = header + j
        s.sendall(packet)

        buffer = b""
        buffer_sz = None
        j = None
        while True:
            data = s.recv(4096)
            if not data:
                raise ConnectionError
            buffer += data
            if len(buffer) >= 2 and buffer_sz == None:
                buffer_sz = int.from_bytes(buffer[:2],byteorder="big")

            if len(buffer) - 2 >= buffer_sz:
                js = buffer[2:2+buffer_sz]
                json_dir = js.decode()
                j = json.loads(json_dir)
                if j["type"] == "chat_list":
                    break
                else:
                    buffer = buffer[:2+buffer_sz]
                    buffer_sz = None


        running = 1
        while running:
            clear()
            if j["message"] == "0":
                #vazio
                choose = input("There are no available chats. Please enter a name for a new chat: ")
                if len(choose) == 0:
                    continue
                localChat = choose
                break
            print(f"{GREEN}{j["message"]}{RESET}", flush=True)

            choose = None
            existing_chats = [] if j["message"] == "0" else j["message"].split('\n')
            while True:
                
                try:
                    choose = input("Pick the number of the chat you want to join (pick 0 to create a new one): ")
                    if len(choose) == 0:
                        continue
                    choose = int(choose)
                    if choose > len(existing_chats) or choose < 0: 
                        move_cursor(-1)
                        clear_line()
                        continue
                except ValueError:
                    print(f"{RED}Please enter a valid number{RESET}")
                    move_cursor(-1)
                    clear_line()
                    continue
                break
            existing_chats = [] if j["message"] == "0" else j["message"].split('\n')
            if choose == 0:
                clear()
                while True:
                    chat_create = input("Enter a name for the new chat: ")
                    if len(chat_create) == 0:
                        continue
                    break
                
                if chat_create in existing_chats:
                    clear()
                    while True:
                        i = input(f"{chat_create} already exists, do you want to join it? (y/n): ")
                        if len(i) == 0:
                            continue
                        break
                    if i == 'y':
                        localChat = chat_create
                        running = 0
                        break
                    continue
                else:
                    running = 0
                    localChat = chat_create
                    break
            else:   
                running = 0           
                localChat = existing_chats[choose - 1].split('-', 1)[1].strip()
                break

    except:
        raise ConnectionError
    
    
def main(argv):
    global localUser
    global localChat
    global s
    try:
        localUser = argv[1]
        host = argv[2]
        port = int(argv[3])
    except:
        usage()
        return
    
    s.connect((host, port))
    clear()
    choose_chat()
    clear()
    try:
        
        hello_dir = {
            "type": "hello",
            "chat": localChat,
            "nick": localUser
        }
        json_tosend = json.dumps(hello_dir).encode()
        tamanho = len(json_tosend)
        header = tamanho.to_bytes(2, byteorder="big")
        content = header + json_tosend
      
        s.sendall(content)
    except:
        print(f"{RED}Could not connect to server, try again{RESET}")
        s.close()
        return

    if wait_for_ok() == False:
        return
    
    t1 = threading.Thread(target=listen_to_server, daemon=True)
    
    t1.start()

    run_keyboard()

main(sys.argv)