# LooneysMeteorologist

First Iteration of ChatGPT Generated HTTP/S Beaconing Implant.

All the code was generated with ChatGPT and then hand-fixed as needed to get a minimum viable proof of concept working.

This is version 1, which is entirely Python for now, intended purely as a playground/testbench.

You can find the writeup on this iteration on my blog: 

## Features:
* Command Execution
* Beacons every minute (you can change this in code)
* Nothing else

## Anti-Features:
* No encryption
* No authentication
* Literally a proof of concept
* Full of bugs.

## Usage
Install flask, sqlite, requests - see requirements.txt

Run mkdb.py to create the database.

Run c2.py to launch the command and control server. 

Edit bot.py to point to your command and control server. 

Edit control.py to point to your command and control server.

Run bot.py on your target.

Run control.py to list agents, list tasks, add tasks for agents, get output from tasks, cancel tasks... 



Licence: WTFPL

Bugs? I guess make an issue, I'll probably be interested. 
