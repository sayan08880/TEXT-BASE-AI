# Terminal AI Chatbot (Groq + LLaMA 3)

A modern **terminal-based AI chatbot** built in Python using the **Groq API** and **LLaMA-3.3-70B model**.
This project provides a visually rich command-line chat interface with chat bubbles, typing effects, token tracking, and animated status indicators.

---

## Features

* Clean **terminal UI with chat bubbles**
* **AI response typing animation**
* **Thinking spinner animation**
* **Conversation history management**
* **Token usage estimation**
* **Status bar showing messages and tokens**
* **Commands for clearing and resetting the session**
* Powered by **Groq API + LLaMA 3.3 70B**

---

## Demo

```
You › Hello

╭──────────────────────────────────────────────╮
│ 👤 YOU                                      │
├──────────────────────────────────────────────┤
│ Hello                                       │
╰──────────────────────────────────────────────╯

🤖 AI ASSISTANT
Hello! How can I help you today?
```

---

## Requirements

* Python **3.8+**
* Groq Python SDK

Install dependencies:

```bash
pip install groq
```

---

## Setup

1. Clone the repository

```bash
git clone https://github.com/yourusername/terminal-ai-chatbot.git
cd terminal-ai-chatbot
```

2. Open the Python file and replace the API key:

```python
API_KEY = "your_groq_api_key_here"
```

3. Run the chatbot:

```bash
python chatbot.py
```

---

## Commands

| Command                 | Function                   |
| ----------------------- | -------------------------- |
| `clear`                 | Clear the terminal screen  |
| `reset`                 | Reset conversation history |
| `exit` / `quit` / `bye` | Exit the chatbot           |

---

## Project Structure

```
terminal-ai-chatbot
│
├── chatbot.py
├── README.md
└── requirements.txt
```

---

## How It Works

1. User enters a prompt in the terminal.
2. The message is stored in conversation history.
3. The program sends the conversation to the **Groq API**.
4. The LLaMA model generates a response.
5. The response is printed with a **typing animation inside a chat bubble UI**.

---

## Technologies Used

* Python
* Groq API
* LLaMA-3.3-70B Model
* ANSI Terminal Styling

---

## Future Improvements

* Streaming responses
* Voice input
* Save chat history
* Plugin support
* Web interface

---

## License

This project is open-source and available under the **MIT License**.

---

## Author

**Sayan**
BCA Student | Programming & AI Enthusiast
