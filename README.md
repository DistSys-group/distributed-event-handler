# distributed-event-handler
This is a University of Helsinki Distributed Systems course group project

# Project Plan 

The aim of the project is to create a distributed web server. The server contains of nodes which serve clients. Nodes share data and state and communicate over network with internet protocols. Detailed plan can be found at <Link>!

## Team

The project team consists of four members: Tuomas Konttinen, Sami Parkkinen, Sami Pulli and Tuuli Toivanen-Gripentrog. 

## Technologies 

Servers are implemented with python. Nodes will communicate over the network using socket or http requests. Nodes offer the same service for multiple users and share data needed to provide up to date information such as user likes. All nodes are identical and connect with all other nodes. It might be necessary to choose a leader among the nodes to work as load balancer and naming/node discovery.

## Comments about implementation

We are going to implement the basic functionality for nodes to be able to communicate with each other and share data e.g. number of user likes. The data should be as up to date as possible at all times.

## Working agreement

Project management is in Github Projects in this DistSys-group.
Project documents are at <Link to Shared drive>

## Project Deadlines

Project plan 21.11.2023 23:59  
Project Demo 13.12.2023  
Report 15.12.2023  

## Instructions

Developers should be able to develop the app either with Docker, or locally as previously.

When developing locally, remember to use host etc. variables provided by docker-compose.yaml when neccessary.

### Docker

It is highly recommended to use Docker Desktop app, which makes managing and inspecting containers very easy.

> **Note**: Client container needs to be run with options `-it`, or it will shut down immediately. Run up the services as below, and restart the client container with `docker compose run -it dist-sys-client`.

To build and run the containers, run `docker compose up -d`

`-d` is to detach from the containers. You can also omit this to see output from all containers in terminal. It is recommended to inspect the containers individually in Docker Desktop. If you forgot `-d` and are connected to the containers, use `Ctrl-c` to close the processes.

To bring the containers down, either run `docker compose down` or stop the in Docker Desktop.

#### Extra

If you make changes to leader, servers or clients, you need to rebuild the services for the changes to take effect.
This is done by using `docker compose up [options] --build <service-name>`, eg. `docker compose up -d --build dist-sys-server-1`.

Docker provides network aliases for the services automatically. Thus the service names can be used to refer to services host address, and let Docker manage host name resolution.

If you prefer to build individual images and containers using plain Docker, please refer to their [documentation](https://docs.docker.com/reference/) or [Cheat Sheet](https://docs.docker.com/get-started/docker_cheatsheet.pdf).

### Local development

1) Start the leader node in one terminal window:  
 `python3 leader.py`  
 Leader runs in port **5001** by default. Don't give 5001 to other nodes.

2) Start server nodes in separate windows:  
  `python3 server.py`
  * Give a port for client requests
  * Give a port for notifications
  * Note that the ports have to be individual for each server
3) Start clients in separate windows:
  `python3 client.py`
  * Leader will give the client a port number for an available server
4) Type `like` to send a like event which will be distributed across all server nodes. 

#### Virtual env, packages and code style

Run `python3 -m venv venv` to create a python virtual environment.  
Run `source venv/bin/activate` to start the virtual env.
Run `python3 -m pip install -r requirements.txt` to install dependencies.

If you install new packages run `python3 -m pip freeze > requirements.txt` after installing.  

To check for code style errors run `pylint <file or directory to check>`.  
To automatically lint the code run `black <file or directory to check>`. 