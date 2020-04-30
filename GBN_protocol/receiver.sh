# args:
#   host address of the network emulator
#   UDP port number used by the link emulator to receive ACKs from the receiver
#   UDP port number used by the receiver to receive data from the emulator
#   name of the file into which the received data is written

python3 receiver.py $1 $2 $3 $4
