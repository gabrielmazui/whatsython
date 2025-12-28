# 🟢 Whatsython Chat

A simple **LAN chat application** in Python using TCP sockets, allowing multiple users to communicate in a group.

> This project was created as a learning exercise to practice working with Python sockets.

---

## ✨ Features

- Real-time chat between multiple users on the same network
- Simple command-line interface
- Cross-platform: Windows, Linux, and macOS

---

## 🛠 Requirements

- Python 3.x

---

## 🚀 How to Run

### 1️⃣ Start the Server

The server listens for incoming connections from clients on a specific port.

To accept connections from any device in your LAN:

```bash
python chat_server.py PORT
```

Or equivalently:

```bash
python chat_server.py 0.0.0.0 PORT
```

> **Notes:**  
> - Replace `PORT` with the port number you want the server to listen on.  
> - `0.0.0.0` allows the server to accept connections from any IP in your LAN.  
> - You can also leave it as `""` in your code, which behaves the same as `0.0.0.0`.

---

### 2️⃣ Start the Client

Each user runs the client to connect to the server:

```bash
python chat_client.py NAME HOST PORT
```

- `NAME` → your username in the chat  
- `HOST` → the IP address of the server (e.g., `192.168.1.100`)  
- `PORT` → the same port used by the server

---

## 💬 Example

Start server:

```bash
python chat_server.py 5000
```

Connect two clients:

```bash
python chat_client.py Alice 192.168.1.100 5000
python chat_client.py Bob 192.168.1.100 5000
```

Example chat session:

```text
mazui: Hello everyone!
mazui: How are you doing today?
segat: I'm good, thanks! And you?
potter: Hey guys, what's up?
segat: Just working on a project.
potter: Sounds cool!
mazui: Nice! Let's catch up later.
mazui: See you all soon.

mazui> 
```

---

## ⚠️ Notes

- The server must be running before clients connect.  
- Works only on the local network (LAN).  
- Press **Ctrl+C** in the client to exit the chat.  
- This project is for educational purposes and to practice Python socket programming.
