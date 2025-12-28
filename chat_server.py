import select
import socket
import sys
import json

def usage():
    print("py chat_server.py PORT")

def json_create(type, user , content):
    d = {
        "type": f"{type}"
    }
    if len(user) > 0:
        d["nick"] = user 
    if len(content) > 0:
        d["message"] = content
    return json.dumps(d)


def json_handle(json_string):
    try:
        json_dict = json.loads(json_string)
    except:
        raise
    if json_dict["type"] == "hello":
        return json_create("join", json_dict["nick"], "").encode()
    return json_create("message", json_dict["nick"], json_dict["message"]).encode()

def drop_client(soc, read_set, users, buffers):
    read_set.discard(soc)
    soc.close()
    users.pop(soc, None)
    buffers.pop(soc, None)

def run(port):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", port))
    s.listen()
    read_set = {s}
    users = {}
    buffers = {}

    print(f"funcionando na porta {port}")
    try:
        while True:
            ready_to_read, _, _ = select.select(read_set, [], [], 1)
            for soc in ready_to_read:
                
                if soc == s:
                    conn, _ = soc.accept()
                    read_set.add(conn)
                    buffers[conn] = b""
                else:

                    try:
                        d = soc.recv(4096)
                    except (ConnectionResetError, OSError):
                        d = b""
                    
                    if not d:
                        # alguem saiu
                        read_set.discard(soc)
                        usuario = users.get(soc, "desconhecido")
                        json_to_send = json_create("leave", usuario, "").encode()
                        soc.close()
                        tamanho = len(json_to_send)
                        header = tamanho.to_bytes(2, byteorder="big")
                        packet = header + json_to_send

                        buffers.pop(soc, None)
                        users.pop(soc, None)

                        for u in list(users):
                            try:
                                u.sendall(packet)
                            except (BrokenPipeError, ConnectionResetError, OSError):
                                drop_client(soc, read_set, users, buffers)
                            


                        print(f"{usuario} saiu")
                    else:
                        buffers[soc] += d
                        data = buffers[soc]
                        
                        # pode vir mais de uma mensagem
                        while True:

                            tamanho = len(data)
                            if tamanho < 2:
                                break
                            json_sz = int.from_bytes(data[:2], byteorder="big")
                            if tamanho - 2 < json_sz:
                                break
                            
                            try:
                                json_dict = json.loads(data[2:2+json_sz].decode())
                            except json.JSONDecodeError:
                                buffers[soc] = b""
                                break
                                
                            if json_dict["type"] == "hello":
                                users[soc] = json_dict["nick"]

                            user_socket = None # usuario para enviar
                            json_to_reply = None
                            if json_dict["type"] == "hello":
                                json_to_reply = json_create("join", json_dict["nick"], "").encode()
                            elif json_dict["type"] == "list":
                                content = ""
                                for _, u in users.items():
                                    content += u + "\n"
                                
                                json_to_reply = json_create("list", "", content).encode()
                                user_socket = soc

                            elif json_dict["type"] == "direct_message":
                                user = json_dict["user"]
                                
                                for u in users:
                                    if users[u] == user:
                                        user_socket = u
                                        break
                                if user_socket == None:
                                    #envia erro
                                    json_to_reply = json_create("error", "", "User does not Exist").encode()
                                    user_socket = soc
                            else:
                                print("mensagem recebida")
                                json_to_reply = json_create("message", users.get(soc,"desconhecido"), json_dict["message"]).encode()

                            j_tamanho = len(json_to_reply)
                            header = j_tamanho.to_bytes(2, byteorder="big")
                            packet = header + json_to_reply

                            buffers[soc] = data[2+json_sz:]
                            data = buffers[soc]
                            if user_socket == None:
                                for u in list(users):
                                    try:
                                        if u != soc:
                                            u.sendall(packet)
                                    except (BrokenPipeError, ConnectionResetError, OSError):
                                        drop_client(soc, read_set, users, buffers)
                                    

                            else:
                                try:
                                    user_socket.sendall(packet)
                                except (BrokenPipeError, ConnectionResetError, OSError):
                                    drop_client(soc, read_set, users, buffers)
                                

    except KeyboardInterrupt:
        print("servidor interrompido")
    except Exception as e:
        print("deu erro\n")
        print(e)
    finally:
        for u in list(read_set):
            u.close()
        s.close()

def main(argv):
    try:
        port = int(argv[1])
        run(port)
    except:
        usage()


main(sys.argv)