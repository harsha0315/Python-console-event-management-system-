# Event Registration System

A simple console app built with Python and MySQL. It lets you create events, register participants, enforce seat limits and cancel registrations.

## Features
- Add, view and delete events (name, date, location, seat limit)
- Register a participant for an event
- Block registration when the event is full (checked inside a database transaction)
- Prevent the same person registering twice for one event
- View the participant list for an event
- Cancel a registration

## Database (3 tables)
- `events`
- `participants`
- `registrations` (links events and participants)

## Setup
1. Install Python 3 and MySQL 8.
2. Install the dependency:
   ```
   pip install -r requirements.txt
   ```
3. Create the database: open `schema.sql` in MySQL Workbench and run the whole script.
4. Set your MySQL password (PowerShell):
   ```
   $env:DB_PASSWORD = "your_mysql_password"
   ```
   On Mac/Linux: `export DB_PASSWORD="your_mysql_password"`
5. Run:
   ```
   python main.py
   ```

Do not commit your real password to GitHub.
