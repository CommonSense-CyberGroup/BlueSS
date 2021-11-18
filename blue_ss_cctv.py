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
    -It could also be manually run from the cli for any ad-hoc commands/control that may be needed
    -This script was initially be used as a module in a larger security system program suite in order to interact with BlueIris based on events/alrms from that security system

Considerations:
    -This is just a POC script that is being tested on a BlueIris 4 Server Install on Windows 10
        -This has NOT been tested on BlueIris 5 but should work
    -Arguments need to be entered from the user for the username, password, host, protocol, and command to keep this script from hardcoding anything that may be compormised
    -Python 3.6+ is required for this script

Arguments:
    --The process for invoking this script: 'python blue_ss.py -hn <host> -p <protocol> -u <user> -t <token> -c <command> -a <command args>'
        -This would be: 'python3 blue_ss.py -hn 192.168.1.2 -p http -u admin -t password123 -c list_cameras
        -Note that some commands may take additional arguments to get the expected result! Refer to the README in order to determine when to use these 

To Do:
<<<<<<< HEAD
    -Start adding other script calls to activate the security system
    -Find a way to change color/bold of system status reading
    -Testing!!
    -Create requirements file using pipreqs - https://blog.jcharistech.com/2020/11/02/how-to-create-requirements-txt-file-in-python/
=======
    -See if we are able to use HTTPS for this....
    -Set up more error checking
    -Set up more logging
>>>>>>> parent of 7a783bf (Update blue_ss_cctv.py)

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
        :param host:        IP or FQDN of the BlueIris server to be controlled (required)
        :param user:        The user to log into the host with (required)
        :param token:       The password for the user to log into the host with (required)
        :param protocol:    The connection protocol (either HTTP or HTTPS) (required)
        :param command:     The command to run on the CCTV host (required)
        :param arguments:   Arguments for the given command if needed

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
    def execute(self, command, argvs):
        """
        Required possible commands - 

        :list_cameras:          List the connected cameras to the host. Does not take additional arguments
        :camera_details:        List the details for a given camera name (needs arguments passed)
        :pause_camera_time:     Pause a given camera for a given amount of time (needs arguments passed)
        :pause_camera_indef:    Indefinitely pause a given camera (needs arguments passed)
        :unpause_camera:        Unpause a given camera (needs arguments passed)
        :set_status:            Set the profile status on BlueIris by using profile name (needs arguments passed)

        """
        #Determine the command that we received and run it
        #List all cameras and send it to the alert users on file
        if command == "list_cameras":
            self.send_alert(self.bi_server.cameras)

        #Requires command args to be '-a camera=<camera name>'
        if command == "camera_details":
            try:
                self.send_alert(self.bi_server.get_camera_details(argvs))
                logger.info("Sent camera details!")
            except:
                logger.error("Unable to gather information for requested camera: %s", argvs)

        #Requires command args to be '-a camera=<camera name>, seconds=<seconds to pause camera>'
        if command == "pause_camera_time":
            try:
                self.bi_server.pause_camera(argvs)
                logger.info("Paused camera with following params: %s", argvs)
                self.send_alert("Pased camera with following params: ", argvs)
            except:
                logger.error("Unable to pause camera: %s", argvs)

        #Requires command args to be '-a camera=<camera name>'
        if command == "pause_camera_indef":
            try:
                self.bi_server.pause_camera_indefinitely(argvs)
                logger.info("Paused camera indefinitely: %s", argvs)
                self.send_alert("Indefinitely paused camera: ", argvs)
            except:
                logger.error("Unable to indefinitely pause camera: %s", argvs)
        
        #Requires command args to be '-a camera=<camera name>'
        if command == "unpause_camera":
            try:
                self.bi_server.unpause_camera(argvs)
                logger.info("Unpaused camera: %s", argvs)
                self.send_alert("Unpaused camera: ", argvs)
            except:
                logger.error("Unable to unpause camera: %s", argvs)

        #Requires command args to be '-a profile_index=<profile name>'
        if command == "set_status":
            try:
                self.bi_server.set_status_profile_by_name(argvs)
                logger.info("Set profile status to: %s", argvs)
                self.send_alert("Set camera profile to: ", argvs)
            except:
                logger.error("Unable to set profile to: %s", argvs)

<<<<<<< HEAD
            else:
                #Shut off the alarm if it is running
                if self.alarm_started:
                    self.stop_alarm = True
                    self.thread_alarm.join()

                #Call scripts to disarm security system

                #Set variables to disarm alarm sound
                self.stop_alarm = True
                self.alarm_started = False

                self.status = "HOME"

                self.stat.SetValue("System Status:  HOME")
                self.code.SetValue("Enter Code: ")

        #Error checking if user enters wrong passcode when trying to disarm system
        else:
            if self.status != "HOME" or self.status != "DISARMED":
                self.disarm_try += 1

                if self.disarm_try < 3:
                    playsound(error_sound)
                    self.code.SetValue("Incorrect Code! Try again! \n[!] 2 attempts remaining!! [!]")
                    logger.error("Incorrect passcode entered while setting to HOME! Attempt: %s", self.disarm_try)
                    self.security_code = ""

                else:
                    logger.critical("3 Incorrect disarm attempts made!!!")

                    #Set off alarm here!
                    self.stop_alarm = False
                    if not self.alarm_started:
                        self.thread_alarm = threading.Thread(target=self.threaded_alarm_sound, args=(self,))
                        self.thread_alarm.start()
                        self.alarm_started = True

                    #Send alerts
                    #self.send_alert()

            
            #Error checking for incorrect passcode, but not in an armed state
            else:
                playsound(error_sound)
                self.code.SetValue("Incorrect Code! Try again!")
                logger.error("Incorrect passcode entered")

                #Start clear thread to clear the screen
                if not self.timer_started:
                    threading.Thread(target=self.on_clear_timer, args=(self,)).start()
                    self.timer_started = True

                self.security_code = ""  

    #Function for setting system status to "CCTV"
    def cctv_system(self, event):
        #Verify that a passcode has been entered
        if self.security_code == "":
            playsound(error_sound)
            self.code.SetValue("You must enter a code to arm!")

            #Start the clear thread to clear the screen
            if not self.timer_started:
                threading.Thread(target=self.on_clear_timer, args=(self,)).start()
                self.timer_started = True

        #Verify that the passcode the user input is correct, and countdown to arming CCTV
        if self.security_code == self.passcode:

            #Error checking if the system is already in the CCTV state
            if self.status == "CCTV":
                playsound(error_sound)
                self.code.SetValue("System is already in CCTV mode!")

                if not self.timer_started:
                    threading.Thread(target=self.on_clear_timer, args=(self,)).start()
                    self.timer_started = True

            #Arm to CCTV state
            else:
                #Set status to armed
                self.status = "CCTV"

                #Stop the clear_timer
                self.button_success = True
                self.clear_wait_thread.join()

                #Run the thread to countdown and then actually arm things
                self.countdown = True
                self.thread_countdown = threading.Thread(target=self.threaded_countdown, args=(self,))
                self.thread_countdown.start()

        #Error checking for incorrect passcode
=======
>>>>>>> parent of 7a783bf (Update blue_ss_cctv.py)
        else:
            logger.error("Invalid command given! %s", command)

<<<<<<< HEAD
            #Error checking for if system is already in disarmed state
            if self.status == "DISARMED":
                playsound(error_sound)
                self.code.SetValue("System is already Disarmed")

                #Run clear thread to clear the screen
                if not self.timer_started:
                    threading.Thread(target=self.on_clear_timer, args=(self,)).start()
                    self.timer_started = True

            #If the arming countdown has started but the user hits disarm to stop it, do so
            if self.countdown:
                self.button_success = True
                self.thread_countdown.join()

                self.code.SetValue("Stopped system from arming!")

                #Run clear thread to clear the screen
                if not self.timer_started:
                    threading.Thread(target=self.on_clear_timer, args=(self,)).start()
                    self.timer_started = True

            #Disarm the system
            else:
                #Shut off the alarm if it is running
                if self.alarm_started:
                    self.stop_alarm = True
                    self.thread_alarm.join()

                #Call scripts to disarm security system

                #Set variables to disarm alarm sound
                self.stop_alarm = True
                self.alarm_started = False

                #Set statuses
                self.status = "DISARMED"
                self.stat.SetValue("System Status:  DISARMED")
                self.code.SetValue("Enter Code: ")

        #If the passcode is entered incorrectly
        else:
            #Error checking if the system is armed and user is entering wrong passcodes
            if self.status != "HOME" or self.status != "DISARMED":
                self.disarm_try += 1

                if self.disarm_try < 3:
                    playsound(error_sound)
                    self.code.SetValue("Incorrect Code! Try again! \n[!] 2 attempts remaining!! [!]")
                    logger.error("Incorrect passcode entered while disarming! Attempt: %s", self.disarm_try)
                    self.security_code = ""

                else:
                    logger.critical("3 Incorrect disarm attempts made!!!")

                    #Set off alarm here!
                    self.stop_alarm = False
                    if not self.alarm_started:
                        self.thread_alarm = threading.Thread(target=self.threaded_alarm_sound, args=(self,))
                        self.thread_alarm.start()
                        self.alarm_started = True

                    #Send alerts
                    #self.send_alert()
            
            #Error checking for if system is not armed, and trying to enter the unarmed state but bad passcode
            else:
                playsound(error_sound)
                self.code.SetValue("Incorrect Code! Try again!")
                logger.error("Incorrect passcode entered")

                #Start the clear function to clear the screen for the user
                if not self.timer_started:
                    threading.Thread(target=self.on_clear_timer, args=(self,)).start()
                    self.timer_started = True

                self.security_code = ""

    #Function for setting system status to "EMERGENCY"
    def emergency_system(self, event):
        #Set off alarm here!
        self.stop_alarm = False
        if not self.alarm_started:
            self.thread_alarm = threading.Thread(target=self.threaded_alarm_sound, args=(self,))
            self.thread_alarm.start()
            self.alarm_started = True

        #Run scripts to arm system

        #Set statuses
        self.stat.SetValue("System Status:  EMERGENCY")
        self.status = "EMERGENCY"

        #Send alerts
        #self.send_alert()

    #Function for setting system status to "SILENT"
    def silent_system(self, event):
        #Run scripts to arm system

        #Set statuses
        self.stat.SetValue("System Status:  SILENT")
        self.status = "SILENT"

        #Send alerts
        #self.send_alert()

    #Function to send out email alerts in the case that an alarm was triggered
    def send_alert(self, event):
        #Create message to send
        message_beginning = """\
            BlueSS Alert! - Alarm was triggered on main console!
            """

        message = f'{message_beginning}Alarm was triggered at {datetime.now()}\nSystem was in {self.status} when the alert was triggered!'

        #Create a secure SSL context
        context = ssl.create_default_context()

        #Try to log in to server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(alert_email, alert_password)

            #Iterate through the list of contacts from the config file and send them the email
            for email in alert_list:
                try:
                    server.sendmail(alert_email, email, message)
                    logger.info("Sent notification to: %s", email)
                except:
                    logger.error("Error sending alert email!!!")

        return
=======
    #Send alerts if needed based on the action that was done so the user gets a confirmation or a notification of what happened
    def send_alert(msg_data):
        print("SEND ALERTS NOT YET IMPLIMENTED")
        
>>>>>>> parent of 7a783bf (Update blue_ss_cctv.py)

### THE THING ###
if __name__ == '__main__':
    #Set up and parse through the arguments in order to determine what we need to do
    parser = argparse.ArgumentParser()
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument("-hn", dest="host", required=True, type=str) #host arg
    required_args.add_argument("-p", dest="protocol",required=True, type=int) #protocol arg
    required_args.add_argument("-u", dest="user",required=True, type=str) #username arg
    required_args.add_argument("-t", dest="token",required=True, type=str) #token/pw arg
    required_args.add_argument("-c", dest="command",required=True, type=str) #Command arg
    required_args.add_argument("-a", dest="arguments",required=False, type=str) #Arguments for command if required

    args = parser.parse_args()

    #Connect to the BlueIris server
    server_session = ssblue_iris(args.host, args.user, args.token, args.protocol)

    #Execute what we need to based on the arg we were called with
    ssblue_iris.execute(server_session, args.command, args.arguments)
