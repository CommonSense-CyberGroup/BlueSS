#!/bin/python3

'''
NAME: BlueSS
BY:
    Some Guy they call Scooter
    Common Sense Cyber Group

Created: 11/12/2021
Updated: 11/12/2021

Version: 1.0.1

License: MIT


Purpose:
    -This is a POC script to test out the functionality of pyBlueIris to see how we can control a BlueIris CCTV Server
    -The initial intended use case of this script is for it to be called/triggered from a BlueIris server upon an event/trigger/alert using the 'run script' functionality
    -It could also be manually run from the cli for any ad-hoc commands/control that may be needed
    -This script can also be used as a module in a larger security system program suite in order to interact with BlueIris based on events/alrms from that security system

Considerations:
    -This is just a POC script that is being tested on a BlueIris 4 Server Install on Windows 10
    -Arguments need to be entered from the user for the username, password, host, protocol, and command to keep this script from hardcoding anything that may be compormised
    -Python 3.6+ is required for this script

Arguments:
    --The process for invoking this script: 'python blue_ss.py -hn <host> -p <protocol> -u <user> -t <token> -c <command> >
        -This would be: 'python3 blue_ss.py -hn 192.168.1.2 -p http -u admin -t password123 -c list_cameras

To Do:
    -See if we are able to use HTTPS for this....
    -Set up more error checking
    -Set up more logging
    -Work on additional commands, and where output should be displayed/sent

'''

### IMPORT LIBRARIES ###
import logging      #https://docs.python.org/3.8/library/logging.html - Used to log errors and other script information
import pyblueiris   #https://pypi.org/project/pyblueiris/ - Used to interface with BlueIris
from aiohttp import ClientSession   #https://docs.python.org/3.8/library/aiohttp.html - This is for making the connection to the BlueIris server (in this script's case, localhost)
import argparse     #https://docs.python.org/3.8/library/argparse.html - Used for parsing through arguments handed to the script


### DEFINE VARIABLES ###

#Set up logging for user activities
logging_file = "blue_ss.log"         #Define log file location for windows
logger = logging.getLogger('blue_ss CCTV Script Log')  #Define log name
logger.setLevel(logging.DEBUG)              #Set logger level
fh = logging.FileHandler(logging_file)      #Set the file handler for the logger
fh.setLevel(logging.DEBUG)                  #Set the file handler log level
logger.addHandler(fh)                       #Add the file handler to logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')   #Format how the log messages will look
fh.setFormatter(formatter)                  #Add the format to the file handler


### CLASSES AND FUNCTIONS ###
class ssblue_iris:
    """
        :param host: IP of rFQDN of the BlueIris server to be controlled
        :param user: The user to log into the host with
        :param token: The password for the user to log into the host with
        :param protocol: The connection protocol (either HTTP or HTTPS)
        :param command: The command to run on the CCTV host

        Example:    python3 blue_ss.py -hn 192.168.1.2 -p http -u admin -t password123 -c list_cameras    
    """

    #Open the session to the server
    async def __init__(self, BI_HOST, BI_USER, BI_PASS, PROTOCOL):
        try:
            async with ClientSession(raise_for_status=True) as self.session:
                self.bi_server = pyblueiris.BlueIris(self.session, BI_USER, BI_PASS, PROTOCOL, BI_HOST)
                logger.info("Connected to the host server!")
        except:
            logger.critical("Unable to connect to host server!")

    #If the script/class quits, close the connection cleanly
    def __del__(self):
        self.session.close()
        logger.info("Closed session to the host server")

    #Execute the command that the user/server requested
    def execute(self, command):
        """
        Required possible commands - 

        :list_cameras:    List the connected cameras to the host
        """
        #Determine the command that we received
        if command == "list_cameras":
            print(self.bi_server.cameras)

        else:
            logger.error("Invalid command given! %s", command)
        

### THE THING ###
if __name__ == '__main__':
    #Set up and parse through the arguments in order to determine what we need to do
    parser = argparse.ArgumentParser()
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument("-hn", dest="host", required=True, type=str) #host arg
    required_args.add_argument("-p", dest="protocol",required=True, type=int) #port arg
    required_args.add_argument("-u", dest="user",required=True, type=str) #username arg
    required_args.add_argument("-t", dest="token",required=True, type=str) #token/pw arg
    required_args.add_argument("-c", dest="command",required=True, type=str) #Connecter version arg

    args = parser.parse_args()

    #Connect to the BlueIris server
    server_session = ssblue_iris(args.host, args.user, args.token, args.protocol)

    #Execute what we need to based on the arg we were called with
    ssblue_iris.execute(server_session, args.command)
