#!/usr/bin/python

# Make sure to have the server side running in CoppeliaSim
# Run setNodePosition.py to update station location
# If there is an error to connect to the socket run sudo pkill -9 -f python

import sys
import time
import os

from mininet.log import info

try:
    import sim
except ImportError:
    info('--------------------------------------------------------------')
    info('"sim.py" could not be imported. This means very probably that')
    info('either "sim.py" or the remoteApi library could not be found.')
    info('Make sure both are in the same folder as this file,')
    info('or appropriately adjust the file "sim.py"')
    info('--------------------------------------------------------------')
    info('')


def drone_position(args):
    if len(args) <= 1:
        info("No nodes defined")
        exit()

    num_drones = len(args) - 1
    drones = [[] for _ in range(num_drones)]
    drones_names = [f'Quadricopter_base#{i}' if i > 0 else 'Quadricopter_base' for i in range(num_drones)]
    nodes = args[1:num_drones + 1]
    data = [[] for _ in range(num_drones)]

    info('Program started')
    sim.simxFinish(-1)  # just in case, close all opened connections
    clientID = sim.simxStart('127.0.0.1', 19999, True, True, 5000, 5)  # Connect to CoppeliaSim

    if clientID != -1:
        info('Connected to remote API server')
        # Getting the ID of the drones from the simulation
        for i in range(num_drones):
            res, drones[i] = sim.simxGetObjectHandle(clientID,
                                                     drones_names[i],
                                                     sim.simx_opmode_oneshot_wait)
            if res != sim.simx_return_ok:
                info('Remote API function call returned with error code: ', res)
                exit()

        info('Connected with CoppeliaSim')
        time.sleep(2)
        # Starting the getPosition function streaming
        for i in range(num_drones):
            sim.simxGetObjectPosition(clientID,
                                      drones[i],
                                      -1,
                                      sim.simx_opmode_streaming)

        while True:
            # Getting the positions as buffers
            for i in range(num_drones):
                # Try to retrieve the streamed data
                returnCode, data[i] = sim.simxGetObjectPosition(clientID,
                                                                drones[i],
                                                                -1,
                                                                sim.simx_opmode_buffer)
                if returnCode == sim.simx_return_ok:
                    send_file(data[i], nodes[i])

            time.sleep(1)

        # Now close the connection to CoppeliaSim:
        sim.simxFinish(clientID)
    else:
        info('Failed connecting to remote API server')
    info('Program ended')


def send_file(data, node):
    path = os.path.dirname(os.path.abspath(__file__))
    data_dir = "{}/data".format(path)

    # Ensure the data directory exists
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    file_name = "{}/{}.txt".format(data_dir, node)
    with open(file_name, "w") as f:
        file_position = ','.join(map(str, data))
        f.write(file_position)

    # Log the file creation
    print(f"Data for node {node} written to {file_name}")

def wait_for_files(nodes, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        all_files_exist = all(os.path.exists(f"data/{node}.txt") for node in nodes)
        if all_files_exist:
            return True
        time.sleep(1)  # Wait for 1 second before checking again
    return False

if __name__ == '__main__':
    nodes = sys.argv[1:]
    if wait_for_files(nodes):
        print("All files are created, proceeding with reading data.")
        # Proceed with reading the data from the files
    else:
        print("Error: Not all files were created in time.")
