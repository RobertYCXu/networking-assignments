# args:
#   host address of the network emulator
#   UDP port number used by the emulator to receive data from the sender
#   UDP port number used by the sender to receive ACKs from the emulator
#   name of the file to be transferred

python3 sender.py $1 $2 $3 $4
