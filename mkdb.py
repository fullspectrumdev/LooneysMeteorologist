#!/usr/bin/env python3
import sqlite3
import uuid
import datetime

# Create a connection to the database
conn = sqlite3.connect('my_database.db')

# Create a cursor object
c = conn.cursor()

# Create the "implants" table
c.execute('''CREATE TABLE implants (
                implant_machine_id TEXT(32) PRIMARY KEY,
                implant_build_id TEXT(32),
                implant_uname TEXT,
                implant_user TEXT,
                first_seen TIMESTAMP,
                last_seen TIMESTAMP
            )''')

# Create the "tasks" table
c.execute('''CREATE TABLE tasks (
                implant_machine_id TEXT(32) REFERENCES implants(implant_machine_id),
                task_uuid TEXT(36),
                task_data TEXT,
                task_created_time TIMESTAMP,
                task_status INTEGER,
                task_executed_time TIMESTAMP,
                task_result TEXT,
                PRIMARY KEY (implant_machine_id, task_uuid)
            )''')


# Commit the changes to the database
conn.commit()

# Close the cursor and the connection
c.close()
conn.close()
