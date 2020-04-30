# CS456 A2 - GBN PROTOCOL
## University of Waterloo

### Summary:

This is a python implementation of the Go Back N transport layer protocol built on top of UDP for
CS456. It consists of a multithreaded sender and a receiever. The sender sends data as a bytearray
and received acks from the receiver. Data sent from the sender and receiver go through the emulator
which serves to delay and delete packets. See a2.pdf for more info.

### Running:

Run the emulator executable with the following command line args:

    emulator's receiving UDP port number in the forward (sender) direction,
    receiver’s network address,
    receiver’s receiving UDP port number,
    emulator's receiving UDP port number in the backward (receiver) direction,
    sender’s network address,
    sender’s receiving UDP port number,
    maximum delay of the link in units of millisecond,
    packet discard probability 0 <= p <= 1 ,
    verbose-mode (Boolean: if 1, the network emulator outputs its internal processing)

Run receiver.sh with the following command line args:

    host address of the network emulator
    UDP port number used by the link emulator to receive ACKs from the receiver
    UDP port number used by the receiver to receive data from the emulator
    name of the file into which the received data is written

Run sender.sh with the following command line args:

    host address of the network emulator
    UDP port number used by the emulator to receive data from the sender
    UDP port number used by the sender to receive ACKs from the emulator
    name of the file to be transferred
