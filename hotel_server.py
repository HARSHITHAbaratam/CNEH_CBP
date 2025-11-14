from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse
import hashlib  # <--- Added for password hashing

HOST = "127.0.0.1"
PORT = 8000
MAX_ROOMS = 10

rooms = [{"room_number": i + 1, "is_occupied": False} for i in range(MAX_ROOMS)]
user_info = {}

# ---- Added: Password Hashing Function ----
def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def assign_rooms_to_user(username, password, room_numbers):
    hashed = hash_password(password)  # <--- Store hashed password
    if username not in user_info:
        user_info[username] = {"password": hashed, "room_numbers": []}
    user_info[username]["room_numbers"].extend(room_numbers)

def book_rooms(num_rooms, username, password):
    if username in user_info and user_info[username]["password"] != hash_password(password):  # <--- Check hashed
        return {"error": "Invalid password."}, 401
    booked = []
    for room in rooms:
        if not room["is_occupied"]:
            room["is_occupied"] = True
            booked.append(room["room_number"])
            if len(booked) == num_rooms:
                break
    if not booked:
        return {"error": "No rooms available."}, 409
    assign_rooms_to_user(username, password, booked)  # always uses hashed inside
    return {"message": f"Rooms booked successfully: {booked}"}, 200

def checkout_rooms(username, password):
    if username not in user_info:
        return {"error": "User not found."}, 404
    if user_info[username]["password"] != hash_password(password):  # <--- Check hashed
        return {"error": "Invalid password."}, 401
    booked = user_info[username].get("room_numbers", [])
    if not booked:
        return {"message": "You have no booked rooms."}, 400
    for rn in booked:
        for room in rooms:
            if room["room_number"] == rn:
                room["is_occupied"] = False
    user_info[username]["room_numbers"] = []
    return {"message": f"Checked out successfully. Released rooms: {booked}"}, 200

def query_rooms(username, password):
    if username not in user_info:
        return {"error": "User not found."}, 404
    if user_info[username]["password"] != hash_password(password):  # <--- Check hashed
        return {"error": "Invalid password."}, 401
    booked = user_info[username].get("room_numbers", [])
    if booked:
        return {"message": f"Your booked rooms: {booked}"}, 200
    else:
        return {"message": "You have not booked any rooms."}, 200

def update_booking(username, password, new_room):
    if username not in user_info:
        return {"error": "User not found."}, 404
    if user_info[username]["password"] != hash_password(password):  # <--- Check hashed
        return {"error": "Invalid password."}, 401
    if not (1 <= new_room <= MAX_ROOMS):
        return {"error": "Invalid room number."}, 400
    # check occupancy
    for room in rooms:
        if room["room_number"] == new_room and room["is_occupied"]:
            if new_room in user_info[username]["room_numbers"]:
                return {"message": f"You already have room {new_room}."}, 200
            return {"error": f"Room {new_room} is already occupied."}, 409
    user_rooms = user_info[username].get("room_numbers", [])
    if not user_rooms:
        return {"error": "You have no booking to update."}, 400
    old_room = user_rooms.pop(0)
    for room in rooms:
        if room["room_number"] == old_room:
            room["is_occupied"] = False
    for room in rooms:
        if room["room_number"] == new_room:
            room["is_occupied"] = True
            break
    user_info[username]["room_numbers"].append(new_room)
    return {"message": f"Updated booking: released {old_room}, assigned {new_room}."}, 200

class HotelHTTPRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/rooms":
            status = [{"room_number": r["room_number"], "is_occupied": r["is_occupied"]} for r in rooms]
            self._send_json({"rooms": status}, 200)
        else:
            self._send_json({"error": "Endpoint not found."}, 404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(content_length).decode("utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON."}, 400)
            return
        username = data.get("username")
        password = data.get("password")
        if parsed.path == "/book":
            num_rooms = int(data.get("num_rooms", 0))
            if not username or not password or num_rooms <= 0:
                self._send_json({"error": "username, password, and num_rooms required."}, 400)
                return
            result, status = book_rooms(num_rooms, username, password)
            self._send_json(result, status)
        elif parsed.path == "/query":
            if not username or not password:
                self._send_json({"error": "username and password required."}, 400)
                return
            result, status = query_rooms(username, password)
            self._send_json(result, status)
        else:
            self._send_json({"error": "Endpoint not found."}, 404)

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/update":
            self._send_json({"error": "Endpoint not found."}, 404)
            return
        content_length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(content_length).decode("utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON."}, 400)
            return
        username = data.get("username")
        password = data.get("password")
        try:
            new_room = int(data.get("new_room"))
        except (TypeError, ValueError):
            self._send_json({"error": "new_room must be integer."}, 400)
            return
        if not username or not password:
            self._send_json({"error": "username and password required."}, 400)
            return
        result, status = update_booking(username, password, new_room)
        self._send_json(result, status)

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/checkout":
            self._send_json({"error": "Endpoint not found."}, 404)
            return
        content_length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(content_length).decode("utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON."}, 400)
            return
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            self._send_json({"error": "username and password required."}, 400)
            return
        result, status = checkout_rooms(username, password)
        self._send_json(result, status)

def run_server():
    print(f"Starting HTTP Hotel Server at http://{HOST}:{PORT}")
    server = HTTPServer((HOST, PORT), HotelHTTPRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopping...")
        server.server_close()

if __name__ == "__main__":
    run_server()
