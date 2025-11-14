Hotel Booking System (HTTP Client-Server Demo)
A simple Python project demonstrating HTTP client-server communication for hotel room booking management with basic authentication.

Features
Room management: Book, query, update, and checkout hotel rooms via RESTful endpoints.

Authentication: Secure password verification with SHA-256 hashing; immediate authentication before any user action.

HTTP methods: Supports GET, POST, PUT, and DELETE requests.

Command-line client: Interactive interface for users.

Technologies Used
Python 3

http.server (server-side)

requests (client-side)

hashlib (password hashing)

Usage
1. Install Dependencies
Make sure you have Python 3 installed.
Install the requests library:

bash
pip install requests
2. Run the Server
bash
python hotel_server.py
The server will listen on http://127.0.0.1:8000.

3. Run the Client
Open a new terminal and run:

bash
python hotel_client.py
Follow the prompts for username, password, and available actions.

API Endpoints
Method	Endpoint	Description
GET	/rooms	Get room status
POST	/book	Book available rooms
POST	/query	Query booked rooms
PUT	/update	Update booking
DELETE	/checkout	Release booked rooms
Security Notes
User passwords are stored as SHA-256 hashes, never in plaintext.

Users must authenticate before performing any action.

Invalid authentication causes the client to exit immediately.

Example Usage
text
=== Hotel Booking Client (HTTP + Auth Demo) ===
Username: user1
Password: mypassword

Actions: rooms | book | query | update | checkout | exit
License
This project is for educational demonstration purposes.
Actions: rooms | book | query | update | checkout | exit
