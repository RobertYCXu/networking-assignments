# CS456 A1 - Socket Programming Basics
## University of Waterloo

### Summary:

Implement a simple message board server and client. The message server will store all client
messages, and, upon request send those messages to a client. First, the server and client will
negotiate, using TCP, a port over which all other communications will take place. Then, the
server will send all of its stored messages, over UDP, to the client who will display them. Next,
the client will send its own message (think of it as a reply) to the server---who will add this
message to its list of stored messages. See a1.pdf.

### Running:

Run the server and client through the shell scripts.
