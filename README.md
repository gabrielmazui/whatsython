# Whatsython Chat 🟢

A simple LAN chat application in Python using TCP sockets, allowing multiple users to communicate in a group.  

This project was created as a learning exercise to practice working with Python sockets.

---

## Features ✨

- Real-time chat between multiple users on the same network
- Simple command-line interface
- Works on Windows, Linux, and macOS

---

## Requirements 🛠️

- Python 3.x

---

## How to Run ▶️

### 1️⃣ Start the Server

The server listens for incoming connections from clients on a specific port.  

If you want it to accept connections from any device in your LAN, you can use:

python chat_server.py PORT

Or equivalently:

python chat_server.py 0.0.0.0 PORT

- Replace PORT with the port number you want the server to listen on.
- 0.0.0.0 means the server will accept connections from any IP in your LAN.
- You can also leave it as "" in your code, which behaves the same as 0.0.0.0.

---

### 2️⃣ Start the Client

Each user runs the client to connect to the server:

python chat_client.py NAME HOST PORT

- NAME → your username in the chat
- HOST → the IP address of the server (e.g., 192.168.1.100)
- PORT → the same port used by the server

---

## Example 💬

Start server:

python chat_server.py 5000

Connect two clients:

python chat_client.py Alice 192.168.1.100 5000
python chat_client.py Bob 192.168.1.100 5000

Now Alice and Bob can chat in real-time.

---

## Notes 📝

- The server must be running before clients connect.
- Works only on the local network (LAN).
- Press Ctrl+C in the client to exit the chat.
- This project was created for educational purposes to practice Python socket programming.
