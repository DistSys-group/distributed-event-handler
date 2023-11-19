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
