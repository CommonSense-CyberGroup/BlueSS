"""
TITLE: BlueSS Facial
BY:
    Some Guy they call Scooter
    Common Sense Cyber Group

Created: 11/20/2021
Updated: 11/20/2021

Version: 1.0.1

License: MIT

Purpose:
    -The purpose of this script is to run facial and human recognition on alerts and recordings from the BlueIris CCTV System
    -Upon seeing a face (positive ID or unknown) or a human body, an alert will be sent to the configured list of recipients via Email
    -This script was built intended to be used in Windoes, buut is written in such a way that it should work on most platforms

Considerations:
    -The Haar Cascade and LBP models are used in this script for recognition. We use DLIB in order to create our dataset to run a face againse
        *DLIB IS OUTSIDE THE SCOPE OF THIS SCRIPT AND WE USE A PRE-PROCESSED FILE FOR EVERYTHING AS THIS CAN TAKE A LONG TIME*
    -This script is specifically made to run against video files (mp4)
    -Any successful findings will get a rectangle drawn around the snapshot, a name if applicable, and then included in the email

To Do:
    -Add in files for human body detection

"""

### IMPORT LIBRARIES ###
from cv2 import cv2     # - cv2 library for image and video processing
from datetime import datetime   #https://docs.python.org/3.8/library/datetime.html - Processing dates and times
import os   #https://docs.python.org/3.8/library/os.html - OS related things
from os.path import dirname   #https://docs.python.org/3.8/library/os.html - For using OS features on the local machine
import logging  #https://docs.python.org/3.8/library/logging.html - Used for logging issues and actions in the script

### DEFINE VARIABLES ###
project_root = dirname(__file__)   #Defines the root directory the script is currently in

#Set up logging for user activities
logging_file = project_root + "\\blue_ss_facial.log"         #Define log file location for windows
logger = logging.getLogger("blue_ss Face Recognition Log")  #Define log name
logger.setLevel(logging.DEBUG)              #Set logger level
fh = logging.FileHandler(logging_file)      #Set the file handler for the logger
fh.setLevel(logging.DEBUG)                  #Set the file handler log level
logger.addHandler(fh)                       #Add the file handler to logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')   #Format how the log messages will look
fh.setFormatter(formatter) 

### CLASSES AND FUNCTIONS ###
#Function to parse through config to script related dependencies
def parse_config():
    #Set global variables
    global smtp_server, smtp_port, alert_email, alert_password, alert_list, dlib, haar_frontal, haar_profile, lbp_frontal, lbp_profile, save_location

    alert_list = [] #List to hold users to send out alerts to

    #Open the config file
    try:
        with open(project_root + '\\blue_ss_facial.conf') as file:
            rows = file.readlines()

            for row in rows:
                #Pull out files we need for recognition
                try:
                    if "dlib:" in row:
                        dlib = (row.split("dlib:")[1].replace("\n", ""))
                except:
                        logger.error("Unable to read dlib file from config file! Please check syntax!")
                        quit()

                try:
                    if "haar_frontal:" in row:
                        haar_frontal = cv2.CascadeClassifier((row.split("haar_frontal:")[1].replace("\n", "")))
                except:
                        logger.error("Unable to read haar_frontal file from config file! Please check syntax!")
                        quit()

                try:
                    if "haar_profile:" in row:
                        haar_profile = cv2.CascadeClassifier((row.split("haar_profile:")[1].replace("\n", "")))
                except:
                        logger.error("Unable to read haar_profile file from config file! Please check syntax!")
                        quit()

                try:
                    if "lbp_frontal:" in row:
                        lbp_frontal = cv2.CascadeClassifier((row.split("lbp_frontal:")[1].replace("\n", "")))
                except:
                        logger.error("Unable to read lbp_frontal file from config file! Please check syntax!")
                        quit()

                try:
                    if "lbp_profile:" in row:
                        lbp_profile = cv2.CascadeClassifier((row.split("lbp_profile:")[1].replace("\n", "")))
                except:
                        logger.error("Unable to read lbp_profile file from config file! Please check syntax!")
                        quit()

                try:
                    if "save_location:" in row:
                        save_location = (row.split("save_location:")[1].replace("\n", ""))
                except:
                        logger.error("Unable to read save_location file from config file! Please check syntax!")
                        quit()



                #Pull out notification settings
                try:
                    if "smtp_server:" in row:
                        smtp_server = (row.split("smtp_server:")[1].replace("\n", ""))
                except:
                        logger.error("Unable to read smtp_server from config file! Please check syntax!")
                        quit()

                try:
                    if "smtp_port:" in row:
                        smtp_port = (row.split("smtp_port:")[1].replace("\n", ""))
                except:
                        logger.error("Unable to read smtp_port from config file! Please check syntax!")
                        quit()

                try:
                    if "alert_email:" in row:
                        alert_email = (row.split("alert_email:")[1].replace("\n", ""))
                except:
                        logger.error("Unable to read alert_email from config file! Please check syntax!")
                        quit()

                try:
                    if "alert_passwrd:" in row:
                        alert_password = (row.split("alert_passwrd:")[1].replace("\n", ""))
                except:
                        logger.error("Unable to read alert_passwrd from config file! Please check syntax!")
                        quit()

                try:
                    if "alert_contact_" in row:
                        alert_list.append(row.split(":")[1].replace("\n", ""))
                except:
                        logger.error("Unable to read alert_contacts from config file! Please check syntax!")
                        quit()

    except:
        logger.critical("Error Occurred when opening config file! Closing!")
        quit()


### THE THING ###
if __name__ == '__main__':
    #Parse through config file to get the info we need
    parse_config()