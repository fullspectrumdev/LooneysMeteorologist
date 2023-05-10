# LooneysMeteorologist

First Iteration of ChatGPT Generated HTTP/S Beaconing Implant.

All the code was generated with ChatGPT and then hand-fixed as needed to get a minimum viable proof of concept working.

This is version 1, which is entirely Python for now, intended purely as a playground/testbench.

You can find the writeup on this iteration on my blog: www.fullspectrum.dev/chatgpt-assisted-implant-dev-part-1/



This is probably going to be "frozen in time" after a followup blog post, with a new repo for the next "version" in this experiment.

Works only on Linux targets. 

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

1. Run mkdb.py to create the database.

2. Run c2.py to launch the command and control server. 

3. Edit bot.py to point to your command and control server. 

4. Edit control.py to point to your command and control server.

5. Run bot.py on your target.

6. Run control.py and use the arguments to list agents, list tasks, add tasks for agents, get output from tasks, cancel tasks... 



Licence: WTFPL

Bugs? I guess make an issue, I'll probably be interested. 
