# CS456 A3: P2P Network
## University of Waterloo

## Running:

### Tracker:

Run with `./tracker.sh`

The port of the tracker used for communicating with peers will be saved in `port.txt`

### Peer:

Run with `./peer.sh <tracker_addr> <tracker_port> <min_time_alive>`

All file(s) for the peer will be saved in the Shared/ directory. Each peer starts with one unique
file, however, the system supports multiple files. Each file in the system must have a unique
filename.

See a3.pdf for more info.
