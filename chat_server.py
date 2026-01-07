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

def drop_client(soc, read_set, users, buffers, users_by_name, users_chat, users_nicks):
    read_set.discard(soc)
    soc.close()

    chat = users_chat.pop(soc, None)
    if chat is None:
        buffers.pop(soc, None)
        return

    nick = None
    if chat in users and soc in users[chat]:
        nick = users[chat].pop(soc)

    if nick in users_nicks:
        users_nicks.discard(nick)
    if chat in users_by_name and nick in users_by_name[chat]:
        users_by_name[chat].pop(nick)

    buffers.pop(soc, None)

    if chat in users and not users[chat]:
        users.pop(chat)
        users_by_name.pop(chat)

def run(port):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", port))
    s.listen()
    read_set = {s}
    users = {} # CHAT -> SOCKET -> USER
    users_by_name = {} # CHAT -> USER ->SOCKET
    buffers = {} 
    users_chat = {} # SOCKET -> CHAT
    users_nicks = set()

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
                        chat = users_chat.get(soc,None)
                        chat_users = users.get(chat)
                        usuario = chat_users.get(soc) if chat_users else None
                        
                        drop_client(soc, read_set, users, buffers, users_by_name, users_chat, users_nicks)
                        if usuario != None:
                            json_to_send = json_create("leave", usuario, "").encode()
                            tamanho = len(json_to_send)
                            header = tamanho.to_bytes(2, byteorder="big")
                            packet = header + json_to_send
                            for u in users.get(chat, {}).keys():
                                try:
                                    u.sendall(packet)
                                except (BrokenPipeError, ConnectionResetError, OSError):
                                    drop_client(u, read_set, users, buffers, users_by_name, users_chat, users_nicks)
                            
             
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
                            
                            user_socket = None # usuario para enviar
                            json_to_reply = None

                            if json_dict["type"] == "hello":
                                if "chat" not in json_dict or "nick" not in json_dict:
                                    json_to_reply = json_create("error", "", "JSON must have nick and chat").encode()
                                    user_socket = soc
                                else: 
                                    if len(json_dict["chat"]) == 0 or len(json_dict["nick"]) == 0: 
                                        json_to_reply = json_create("error", "", "JSON must have nick and chat").encode()
                                        user_socket = soc
                                        buffers[soc] = data[2+json_sz:] 
                                        data = buffers[soc]
                                        continue
                                    
                                    else:
                                        if json_dict["nick"] not in users_nicks:
                                            chat = json_dict["chat"]
                                            if chat not in users:
                                                users[chat] = {}
                                                users_by_name[chat] = {}
                                            
                                            users_nicks.add(json_dict["nick"])
                                            users_chat[soc] = chat
                                            users[chat][soc] = json_dict["nick"]
                                            users_by_name[chat][json_dict["nick"]] = soc

                                            json_to_reply = json_create("ok", "", "").encode()
                                            # enviar o ok
                                            j_tamanho = len(json_to_reply)
                                            header = j_tamanho.to_bytes(2, byteorder="big")
                                            packet = header + json_to_reply
                                            try:
                                                soc.sendall(packet)
                                            except:
                                                drop_client(soc, read_set, users[chat], buffers, users_by_name[chat], users_chat, users_nicks)
                                                continue

                                            json_to_reply = json_create("join", json_dict["nick"], "").encode()
                                        else:
                                            json_to_reply = json_create("error", "", "User already exists").encode()
                                            user_socket = soc
      
                            elif json_dict["type"] == "chat_list":
                                
                                content = ""
                                chat_names = list(users.keys())
                                content = "\n".join(f"{i+1}- {chat}" for i, chat in enumerate(chat_names))
                                if len(content) == 0:
                                    # vai enviar um 0
                                    content = "0"
                                json_to_reply = json_create("chat_list", "", content).encode()
                                j_tamanho = len(json_to_reply)
                                header = j_tamanho.to_bytes(2, byteorder="big")
                                packet = header + json_to_reply
                                try:
                                    soc.sendall(packet)
                                except (ConnectionResetError, BrokenPipeError, OSError):
                                    # o cliente desconectou
                                    drop_client(soc, read_set, users, buffers, users_by_name, users_chat)
                                    

                                buffers[soc] = data[2+json_sz:]  
                                data = buffers[soc]  
                                continue

                            elif json_dict["type"] == "list":
                                chat = users_chat.get(soc, None)
                                content = ""
                                content = "\n".join(users[chat].values())
                                
                                json_to_reply = json_create("list", "", content).encode()
                                user_socket = soc

                            elif json_dict["type"] == "direct_message":
                                if "nick" not in json_dict or "message" not in json_dict:
                                    json_to_reply = json_create("error", "", "JSON must have message and chat").encode()
                                    user_socket = soc
                                elif len(json_dict["nick"]) == 0 or len(json_dict["message"]) == 0:
                                    json_to_reply = json_create("error", "", "JSON must have message and chat").encode()
                                    user_socket = soc
                                else:
                                    user = json_dict["nick"]
                                    chat = users_chat.get(soc, None)
                                    user_socket = users_by_name[chat].get(user, None)
                                    user2 = users[chat].get(soc,None)
                                    if user == user2:
                                        json_to_reply = json_create("error", "", "You cant message yourself").encode()
                                    else:

                                        if user_socket == None:
                                            #envia erro
                                            json_to_reply = json_create("error", "", "This message could not be sent, user is not in this chat").encode()
                                            user_socket = soc
                                            
                                        else:
                                            json_to_reply = json_create("direct_message", user2, json_dict["message"]).encode()
                            else:
                                if not "message" in json_dict:
                                    json_to_reply = json_create("error", "", "JSON must have message").encode()
                                    user_socket = soc
                                elif len(json_dict["message"]) == 0:
                                    json_to_reply = json_create("error", "", "empty message").encode()
                                    user_socket = soc
                                else:  
                                    chat = users_chat.get(soc, None)
                                    json_to_reply = json_create("message", users[chat].get(soc,"desconhecido"), json_dict["message"]).encode()

                            j_tamanho = len(json_to_reply)
                            header = j_tamanho.to_bytes(2, byteorder="big")
                            packet = header + json_to_reply

                            buffers[soc] = data[2+json_sz:]
                            data = buffers[soc]
                            chat_to_send = users_chat.get(soc, None)
                            if user_socket == None:
                                for u in list(users[chat_to_send].keys()):
                                    try:
                                        if u != soc:
                                            u.sendall(packet)
                                    except (BrokenPipeError, ConnectionResetError, OSError):
                                        drop_client(u, read_set, users[chat_to_send], buffers, users_by_name[chat_to_send], users_chat)
                                    
                            else:
                                try:
                                    user_socket.sendall(packet)
                                except (BrokenPipeError, ConnectionResetError, OSError):
                                    drop_client(user_socket, read_set, users[chat_to_send], buffers, users_by_name[chat_to_send], users_chat)
                                

    except KeyboardInterrupt:
        print("servidor interrompido")
    except Exception as e:
        print("deu erro\n")
        print(e)
    finally:
        for u in list(read_set):
            try:
                u.close()
            except:
                pass


def main(argv):
    try:
        port = int(argv[1])
        run(port)
    except:
        usage()


main(sys.argv)