import bluetooth
import time
import os
import subprocess
import signal
import select
from gpiozero import MCP3008

# Fixed application commands
READ_CMD = "r"     # To read ADC channels
RELEASE_CMD = "b"  # To release actual connection
EXIT_CMD = "x"     # To stop program
START_CMD = "s"    # To start and keep running the program

# Configure ADC
load_cell1 = MCP3008(0)     # Channel 0
load_cell2 = MCP3008(1)     # Channel 1




# Configure connection to bluetooth driver
cmd = START_CMD
while cmd != EXIT_CMD:
    serviceName = "Droid Plate Server"
    print "Searching service \"%s\"" % serviceName
    service_matches = bluetooth.find_service( name = serviceName )

    # Check if no server was encountered
    print "Services matches: ", len(service_matches)
    serviceFound = False
    if len(service_matches) != 0:
        # See if some of the services is the one we are looking for
        
        for elem in service_matches:
            if elem['name'] == serviceName:
                serviceFound = True
                port = elem["port"]
                name = elem["name"]
                host = elem["host"]
                break

    # Create a comm socket and conect to server
    if serviceFound == True:
        print "Connecting to \"%s\" on %s" % (name, host)
        sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
        time.sleep(1)
        sock.connect((host, port))
        time.sleep(1)


    # Wait for commands
    while serviceFound == True:
        cmd = sock.recv(1) # Wait for one byte command
        print "command is: %s" % cmd
        if cmd == READ_CMD:
            # Take ADC measurements
            # Send meassurements back to client
            #lcv1 = int(0.12*10000)
            #lcv2 = int(1.0*10000)
            # Scale the values to decimal places on the Android app
            lcv1 = int((load_cell1.value)*10000.0) 
            lcv2 = int((load_cell2.value)*10000.0)
            s = "c%04x%04x" % (lcv1,lcv2) # 8 characters 
            sock.send(s)
        if cmd == RELEASE_CMD:
            # Release connection from actual client and wait for another
            sock.close()
            print "Disconnected from: ", host
            break
        if cmd == EXIT_CMD:
            # Exit program, stop executing
            sock.close()
            print "Disconnected from: ", host
            break
        if len(cmd) == 0:
            # Connection lost or closed from client
            break
    # Close actual communication sockets and wait for
    # another connection



# If last command was EXIT_CMD then terminate execution of the program

print("Program termitated")
