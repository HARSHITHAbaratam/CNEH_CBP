import requests
import json
import sys

BASE = "http://127.0.0.1:8000"

def print_rooms():
    r = requests.get(f"{BASE}/rooms")
    data = r.json()
    print("\nRooms status:")
    for r in data.get("rooms", []):
        status = "Occupied" if r["is_occupied"] else "Free"
        print(f" Room {r['room_number']}: {status}")
    print()

def interactive():
    print("=== Hotel Booking Client (HTTP + Auth Demo) ===")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    # -------- Immediate authentication check -----------
    payload = {"username": username, "password": password}
    resp = requests.post(f"{BASE}/query", json=payload)
    data = resp.json()
    # Allow for 'User not found' to register new user lazily by booking later
    if "error" in data and data["error"] == "Invalid password.":
        print("Invalid password. Exiting.")
        sys.exit(1)

    while True:
        print("\nActions: rooms | book | query | update | checkout | exit")
        cmd = input("Action: ").strip().lower()
        if cmd == "rooms":
            print_rooms()
        elif cmd == "book":
            try:
                n = int(input("Number of rooms to book: "))
            except ValueError:
                print("Enter a valid integer.")
                continue
            payload = {"username": username, "password": password, "num_rooms": n}
            r = requests.post(f"{BASE}/book", json=payload)
            print(r.json())
        elif cmd == "query":
            payload = {"username": username, "password": password}
            r = requests.post(f"{BASE}/query", json=payload)
            print(r.json())
        elif cmd == "update":
            try:
                new_room = int(input("Enter new room number to assign: "))
            except ValueError:
                print("Enter a valid integer.")
                continue
            payload = {"username": username, "password": password, "new_room": new_room}
            r = requests.put(f"{BASE}/update", json=payload)
            print(r.json())
        elif cmd == "checkout":
            payload = {"username": username, "password": password}
            r = requests.delete(f"{BASE}/checkout", json=payload)
            print(r.json())
        elif cmd == "exit":
            print("Goodbye.")
            break
        else:
            print("Unknown action.")

if __name__ == "__main__":
    interactive()
