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
    -This first iteration / version of the script is meant to be called from a bash file (which is called from BlueIris upon detection). If this prooves to not work well, we will then
        change this to run continuously looking to pull any new file out of the saved videos location

Considerations:
    -The Haar Cascade and LBP models are used in this script for recognition. We use DLIB in order to create our dataset to run a face against
        *DLIB IS OUTSIDE THE SCOPE OF THIS SCRIPT AND WE USE A PRE-PROCESSED FILE FOR EVERYTHING AS THIS CAN TAKE A LONG TIME*
    -This script is specifically made to run against video files (mp4)
    -Any successful findings will get a rectangle drawn around the snapshot, a name if applicable, and then included in the email

To Do:
    -Add in files for human body detection
    -Integrate more logging
    -Integrate error catching
    -TESTING!!!!

"""

### IMPORT LIBRARIES ###
from cv2 import cv2     # - cv2 library for image and video processing
from datetime import datetime   #https://docs.python.org/3.8/library/datetime.html - Processing dates and times
from os.path import dirname   #https://docs.python.org/3.8/library/os.html - For using OS features on the local machine
import logging  #https://docs.python.org/3.8/library/logging.html - Used for logging issues and actions in the script
import argparse     #https://docs.python.org/3.8/library/argparse.html - Used for parsing through arguments handed to the script
import time     #https://docs.python.org/3.8/library/time.html - Used for waiting on different things
import face_recognition #https://pypi.org/project/face-recognition/ - For actually recognising and processing facial images
import pickle   #https://docs.python.org/3.8/library/pickle.html - For saving files to the local machine and later use
import smtplib  #https://docs.python.org/3.8/library/smtplib.html - For email using SSL and TLS
import ssl     #https://docs.python.org/3.8/library/ssl.html - For email using SSL and TLS

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
                        dlib = pickle.loads(open((row.split("dlib:")[1].replace("\n", "")), "rb").read())
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
                        save_location = f'{(row.split("save_location:")[1].replace("\n", ""))}{"%Y%m%d-%H%M%S%f_face.png"}'
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

#Class to do all the processing work on the files
class check_faces:
    """
        :param time:        Time to wait before running this script on the given file (seconds)
        :param file:        The file to process and look for bodies or faces (required)

        Example:    python3 blue_ss.py -t 15 -f alert1.mp4
    """
    def __init__(self, args):
        #Init and wait if the user asked us to. Then run 
        try:
            if args.time > 0:
                time.sleep(args.time)

        except:
            pass

        #Run the Haar processing to look for faces (then LBP if it doesnt find a match on detected face)
        self.lbp_processing(self, args.file)

        #Run the human processing function so we can look for human-forms
        self.human_processing(self, args.file)

    #If the script/class quits, close the connection cleanly
    def __del__(self):
        logger.info("Script has finished")

    #Function to use Haar against the video file. This usally works better so we use it first. If it doesnt get a face, we skip over to the LBP function
    def haar_processing(self, process_file):
        #Read the incoming video file and change colors to for processing
        ret, frame = cv2.VideoCapture(process_file).read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = haar_frontal.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60), flags=cv2.CASCADE_SCALE_IMAGE)
        profile_faces = haar_profile.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(60, 60),flags=cv2.CASCADE_SCALE_IMAGE)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #Define the facial embeddings for face in input
        encodings = face_recognition.face_encodings(rgb)
        names = []

        #Loop through the facial embeddings incase we have multiple embeddings for multiple fcaes
        for encoding in encodings:
            #Compare encodings with encodings in data["encodings"]
            #Matches contain array with boolean values and True for the embeddings it matches closely and False for rest
            matches = face_recognition.compare_faces(dlib["encodings"],encoding)

            #set name to "unknown" if no encoding matches
            name = "Unknown"

            #Check to see if we have found a match
            if True in matches:
                #Find positions at which we get True and store them
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                #Loop through the matched indexes and maintain a count for each recognized face face
                for i in matchedIdxs:
                    #Check the names at respective indexes we stored in matchedIdxs
                    name = dlib["names"][i]

                    #Increase count for the name we got
                    counts[name] = counts.get(name, 0) + 1

                #Set name which has highest count
                name = max(counts, key=counts.get)

            #Update the list of names
            names.append(name)

            #Loop through the recognized faces (frontal)
            for ((x, y, w, h), name) in zip(faces, names):
                if name == "Unknown":
                    #Call the LBP function to see if we get a match there. If we don't, call it unamed
                    name = self.lbp_processing(self, frame)

                #Rescale the face coordinates and draw the predicted face name on the image
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
                cv2.putText(frame, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
                cv2.putText(frame, str(datetime.now()),(10,30), cv2.FONT_HERSHEY_SIMPLEX, .5,(0,0,0),1,cv2.LINE_AA)

                #Save the image for processing later
                cv2.imwrite(datetime.now().strftime(save_location), frame)

                #Send an alert since we detected a face in the video
                self.send_alert(self, frame)

            #Loop through the recognized faces (profile)
            for ((a, b, c, d), name) in zip(profile_faces, names):
                if name == "Unknown":
                    #Call the LBP function to see if we get a match there. If we don't, call it unamed
                    name = self.lbp_processing(self, frame)

                #Rescale the face coordinates and draw the predicted face name on the image
                cv2.rectangle(frame, (a, b), (a + c, b + d), (0, 0, 255), 1)
                cv2.putText(frame, name, (a, b), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
                cv2.putText(frame, str(datetime.now()),(10,30), cv2.FONT_HERSHEY_SIMPLEX, .5,(0,0,0),1,cv2.LINE_AA)

                #Save the image for processing later
                cv2.imwrite(datetime.now().strftime(save_location), frame)

                #Send an alert since we detected a face in the video
                self.send_alert(self, frame)
        
    #Function to use LBP against the face snapshots captured to see if we can pull out a match (Use only the images that have faces detected so we do not have to process the whole file again)
    def lbp_processing(self, image):
        #Set name
        name = "Unknown"

        #Convert image to Greyscale for haarcascade
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = lbp_frontal.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(60, 60),flags=cv2.CASCADE_SCALE_IMAGE)
        profile_faces = lbp_profile.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(60, 60),flags=cv2.CASCADE_SCALE_IMAGE)
        
        #Define the facial embeddings for face in input
        encodings = face_recognition.face_encodings(rgb)
        names = []

        #Loop through the facial embeddings incase we have multiple faces detected
        for encoding in encodings:
            #Compare encodings with encodings in data["encodings"]
            #Matches contain array with boolean values and True for the embeddings it matches closely and False for rest
            matches = face_recognition.compare_faces(dlib["encodings"], encoding)

            #Check to see if we have found a match
            if True in matches:
                #Find positions at which we get True and store them
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                #Loop through the matched indexes and maintain a count for each recognized face face
                for i in matchedIdxs:
                    #Check the names at respective indexes we stored in matchedIdxs
                    name = dlib["names"][i]

                    #Increase count for the name we got
                    counts[name] = counts.get(name, 0) + 1

                    #Set name which has highest count
                    name = max(counts, key=counts.get)
        
                #Update the list of names
                names.append(name)

                #Loop through the recognized faces (frontal)
                for ((x, y, w, h), name) in zip(faces, names):
                    #If still an unknown name, pass so we continue
                    if name == "Unknown":
                        pass

                #Loop through the recognized faces (profile)
                for ((a, b, c, d), name) in zip(profile_faces, names):
                    #If still an unknown name, pass so we continue
                    if name == "Unknown":
                        pass

        #Return the name if one was found
        return name

    #Function to check the video for any human-forms
    def human_processing(self, process_file):
        print()

    #Function to send out email alerts in the case that a face or body was found
    def send_alert(self, image):
        #Create message to send
        message_beginning = """\
            BlueSS Alert! - A Face Or Body Was Detected!
            """

        message = f'{message_beginning}A Face or Body was detected at {datetime.now()}\n'

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

### THE THING ###
if __name__ == '__main__':
    #Set up and parse through the arguments in order to determine what we need to do
    parser = argparse.ArgumentParser()
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument("-t", dest="time", required=False, type=int) #Time to wait before tunning the script
    required_args.add_argument("-f", dest="file", required=True, type=str) #File that we are going to process

    args = parser.parse_args()

    #Parse through config file to get the info we need
    parse_config()