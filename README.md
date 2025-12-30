# 🟢 Whatsython Chat

Whatsython is a terminal-based real-time chat application written in Python, designed to feel as close as possible to a real chat app — entirely inside the terminal.

It simulates a GUI-like experience using cursor control, colored text, and live message rendering, similar to WhatsApp or Discord — but running purely in a shell.

This project was created as a learning exercise to practice socket programming, concurrency, and terminal UI handling using only the Python standard library.

---

## ✨ Features

- Real-time chat over LAN using TCP sockets
- Multiple chat rooms
  - Create new chats
  - Join existing chats
- Terminal GUI behavior
  - Messages appear instantly while typing
  - Input line stays fixed at the bottom
  - Incoming messages scroll above
  - Join / leave messages rendered live
- Colored output
  - Users, system messages, errors, and DMs use different colors
- Direct Messages (DM)
- List users in the current chat
- Unique nicknames (global)
- Concurrent design
  - Server uses select()
  - Client uses threads
- Custom protocol
  - TCP framing with 2-byte length header
  - JSON payloads
- Cross-platform
  - Windows
  - Linux
  - macOS
- No external libraries required

---

## 🛠 Requirements

- Python 3.x
- Terminal with ANSI escape code support

---

## 🚀 How to Run

### Start the Server

```bash
python chat_server.py 5000
```

The server:
- Listens on the given port
- Accepts multiple clients
- Manages chats and users
- Broadcasts messages in real time

---

### Start the Client

```bash
python chat_client.py Alice 192.168.1.100 5000
```

Arguments:
- Alice → your nickname
- 192.168.1.100 → server IP
- 5000 → server port

---

## 🖥️ Terminal GUI (Real Behavior)

While running, the client behaves like a real chat app:

- Your typing stays at the bottom
- Incoming messages appear above without breaking input
- Cursor movement and line clearing simulate a GUI
- Messages scroll naturally

Example session:

```bash
---------- general ----------
Alice> hello everyone
Bob: hey alice!
Charlie: this feels like a real app
Alice> yeah, all in terminal
```

GitHub cannot render colors, cursor movement, or live updates.  
These effects are visible only when running the program locally.

---

## 💬 Commands

```bash
/help
```
Show available commands.

```bash
/users
```
List users in the current chat.

```bash
/dm Bob hello
```
Send a private message.

```bash
/quit
```
Exit the chat cleanly.

---

## ⚙️ Network Protocol

Each message sent over TCP uses this format:

```text
[2 bytes length][JSON payload]
```

Example payload:

```json
{
  "type": "message",
  "nick": "Alice",
  "message": "hello world"
}
```

---

## 🧠 Architecture

### Server

- Uses select() for non-blocking I/O
- Tracks:
  - Chats
  - Users per chat
  - Nickname mappings
- Cleans up disconnected clients automatically

### Client

- Thread for keyboard input
- Thread for server listener
- Uses threading.Event for synchronization
- Reads input character-by-character
- Redraws terminal dynamically

---

## ⚠️ Notes

- Server must be running before clients connect
- Designed for LAN usage
- Terminal behavior depends on ANSI support
- Educational project, not production-ready

---

## 📚 Learning Goals

- TCP socket communication
- Message framing
- Concurrency with threads and select()
- Terminal UI simulation
- Client-server architecture

---

🟢 Whatsython Chat  
A real-time chat application that turns the terminal into a GUI.
