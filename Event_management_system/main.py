"""Simple Event Registration System (Python + MySQL)."""

import os
from datetime import datetime

import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "ROOT"),  # change this
    "database": "event_registration",
}


def connect():
    return mysql.connector.connect(**DB_CONFIG)


# ---------- input helpers ----------

def ask_int(prompt):
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Please enter a number.")


def ask_text(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def ask_date(prompt):
    while True:
        value = input(prompt).strip()
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("Use the format YYYY-MM-DD, e.g. 2026-12-25.")


# ---------- event features ----------

def add_event(conn):
    name = ask_text("Event name: ")
    date = ask_date("Date (YYYY-MM-DD): ")
    location = ask_text("Location: ")
    capacity = ask_int("Seat limit: ")
    if capacity <= 0:
        print("Seat limit must be greater than 0.")
        return
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO events (name, event_date, location, capacity) VALUES (%s, %s, %s, %s)",
        (name, date, location, capacity),
    )
    conn.commit()
    print(f"Event added with ID {cur.lastrowid}.")


def view_events(conn):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT e.id, e.name, e.event_date, e.location, e.capacity,
               e.capacity - COUNT(r.id) AS seats_left
        FROM events e
        LEFT JOIN registrations r ON r.event_id = e.id
        GROUP BY e.id
        ORDER BY e.event_date
        """
    )
    rows = cur.fetchall()
    if not rows:
        print("No events found.")
        return
    print(f"\n{'ID':<4}{'Name':<25}{'Date':<12}{'Location':<18}{'Seats':<7}{'Left':<5}")
    print("-" * 71)
    for eid, name, date, loc, cap, left in rows:
        print(f"{eid:<4}{name:<25}{str(date):<12}{loc:<18}{cap:<7}{left:<5}")


def delete_event(conn):
    event_id = ask_int("Event ID to delete: ")
    cur = conn.cursor()
    cur.execute("DELETE FROM events WHERE id = %s", (event_id,))
    conn.commit()
    if cur.rowcount:
        print("Event deleted (its registrations were removed too).")
    else:
        print("No event with that ID.")


# ---------- registration features ----------

def register_participant(conn):
    event_id = ask_int("Event ID: ")
    name = ask_text("Participant name: ")
    email = ask_text("Email: ")
    phone = input("Phone (optional): ").strip() or None

    cur = conn.cursor()
    try:
        # Lock the event row so two people can't take the last seat at once.
        cur.execute("SELECT capacity FROM events WHERE id = %s FOR UPDATE", (event_id,))
        row = cur.fetchone()
        if row is None:
            conn.rollback()
            print("No event with that ID.")
            return
        capacity = row[0]

        cur.execute("SELECT COUNT(*) FROM registrations WHERE event_id = %s", (event_id,))
        taken = cur.fetchone()[0]
        if taken >= capacity:
            conn.rollback()
            print("Sorry, this event is full.")
            return

        # Reuse the participant if the email already exists.
        cur.execute("SELECT id FROM participants WHERE email = %s", (email,))
        person = cur.fetchone()
        if person:
            participant_id = person[0]
        else:
            cur.execute(
                "INSERT INTO participants (name, email, phone) VALUES (%s, %s, %s)",
                (name, email, phone),
            )
            participant_id = cur.lastrowid

        cur.execute(
            "SELECT id FROM registrations WHERE event_id = %s AND participant_id = %s",
            (event_id, participant_id),
        )
        if cur.fetchone():
            conn.rollback()
            print("This participant is already registered for the event.")
            return

        cur.execute(
            "INSERT INTO registrations (event_id, participant_id) VALUES (%s, %s)",
            (event_id, participant_id),
        )
        conn.commit()
        print(f"Registered! Registration ID: {cur.lastrowid}. Seats left: {capacity - taken - 1}")
    except Error as err:
        conn.rollback()
        print("Registration failed:", err)


def view_participants(conn):
    event_id = ask_int("Event ID: ")
    cur = conn.cursor()
    cur.execute("SELECT name FROM events WHERE id = %s", (event_id,))
    event = cur.fetchone()
    if event is None:
        print("No event with that ID.")
        return

    cur.execute(
        """
        SELECT r.id, p.name, p.email, p.phone
        FROM registrations r
        JOIN participants p ON p.id = r.participant_id
        WHERE r.event_id = %s
        ORDER BY r.registered_at
        """,
        (event_id,),
    )
    rows = cur.fetchall()
    print(f"\nParticipants for '{event[0]}':")
    if not rows:
        print("No one has registered yet.")
        return
    print(f"{'Reg ID':<8}{'Name':<22}{'Email':<28}{'Phone':<15}")
    print("-" * 73)
    for rid, name, email, phone in rows:
        print(f"{rid:<8}{name:<22}{email:<28}{phone or '-':<15}")
    print(f"\nTotal: {len(rows)}")


def cancel_registration(conn):
    reg_id = ask_int("Registration ID to cancel: ")
    cur = conn.cursor()
    cur.execute("DELETE FROM registrations WHERE id = %s", (reg_id,))
    conn.commit()
    if cur.rowcount:
        print("Registration cancelled. The seat is free again.")
    else:
        print("No registration with that ID.")


# ---------- menu ----------

MENU = """
===== Event Registration System =====
1. Add event
2. View events
3. Delete event
4. Register participant
5. View participants of an event
6. Cancel registration
0. Exit
"""

ACTIONS = {
    "1": add_event,
    "2": view_events,
    "3": delete_event,
    "4": register_participant,
    "5": view_participants,
    "6": cancel_registration,
}


def main():
    try:
        conn = connect()
    except Error as err:
        print("Could not connect to MySQL:", err)
        print("Check your password (DB_PASSWORD) and that schema.sql has been run.")
        return

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        action = ACTIONS.get(choice)
        if action is None:
            print("Invalid option.")
            continue
        try:
            action(conn)
        except Error as err:
            conn.rollback()
            print("Database error:", err)

    conn.close()


if __name__ == "__main__":
    main()
