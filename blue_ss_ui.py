#!/bin/python3

'''
TITLE: BlueSS UI
BY:
    Some Guy they call Scooter
    Common Sense Cyber Group

Created: 11/17/2021
Updated: 11/17/2021

Version: 1.0.1

License: MIT

Purpose:
    -This is meant to be the control panel UI for the BlueSS Security Suite

Considerations:
    -This is meant to be run on a Raspberry PI, but has been coded so it can run on a variety of different OS versions
    -Depending on what the user hits/selects, this UI script will call other functions to do things within the security system
    -When armed and user is trying to change to 'home' or 'disarm', they get 3 attempts before the alarm sets off

To Do:
    -Start adding other script calls to activate the security system
    -Find a way to change color of system status reading
    *-If 'clear' button is hit, close the thread so it doesnt wipe what the user is typing again
    -Determine how/where we will store the passcode (most likely a locked config file)
    -Set up beeping / alarm noises to come from local speaker
    -Figure out how we are going to tell if an alert was triggered
    -Add logic for switching between modes

'''

### IMPORT LIBRARIES ###
import wx       #https://pypi.org/project/wxPython/ - Used for all things GUI
import time     #https://docs.python.org/3.8/library/time.html - Used for waiting on user input, and many other time activities
import threading    #https://docs.python.org/3.8/library/threading.html - Used for threading different things outside of the main function
import logging      #https://docs.python.org/3.8/library/logging.html - Used to log errors and other script information

### DEFINE VARIABLES ###
#Set up logging for user activities
logging_file = "blue_ss_UI.log"         #Define log file location for windows
logger = logging.getLogger('blue_ss UI Script Log')  #Define log name
logger.setLevel(logging.DEBUG)              #Set logger level
fh = logging.FileHandler(logging_file)      #Set the file handler for the logger
fh.setLevel(logging.DEBUG)                  #Set the file handler log level
logger.addHandler(fh)                       #Add the file handler to logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')   #Format how the log messages will look
fh.setFormatter(formatter)                  #Add the format to the file handler


### CLASSES AND FUNCTIONS ###
#Class for the main GUI panel
class main_panel(wx.Frame):

    #Init the UI
    def __init__(self, parent, title, size):
        super(main_panel, self).__init__(parent, title=title, size=size)

        #Define class specific variables
        self.timer_started = False #Timer for clearing passcode input
        self.passcode = "24682" #TEST PASSCODE - NON PRODUCTION USE
        self.security_code = ""  #Sets blank security code for validation
        self.disarm_try = 0 #Holds the number of unsuccessful disarm attempts made

        #Create the main box that all the sub-boxes will sit in
        panel = wx.Panel(self)
        main_box = wx.BoxSizer(wx.HORIZONTAL)

        #Create the UI and run
        #Function variables for UI
        font = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL)

        #### KEYPAD SIZER / BOX SECTION ####
        #Create the keypad box and sizer
        keypad = wx.StaticBox(panel, 0)
        keypad_sizer = wx.StaticBoxSizer(keypad, wx.VERTICAL)
        keypad_box = wx.BoxSizer(wx.VERTICAL)

        #Set up and configure the bottons/keypad for the keypad box, and add it to the sizer
        buttons = [['7', '8', '9'], ['4', '5', '6'], ['1', '2', '3'], ['*', '0', '#']]

        for label_list in buttons:
            btn_sizer = wx.BoxSizer()
            for label in label_list:
                button = wx.Button(panel, label=label)
                btn_sizer.Add(button, 0, wx.ALIGN_CENTER, 0)
                button.Bind(wx.EVT_BUTTON, self.update_code)
            keypad_box.Add(btn_sizer, 0, wx.ALIGN_CENTER, 0)

        #Create the clear button in the keypad box, and add it to the sizer
        clear_btn = wx.Button(panel, label='Clear')
        clear_btn.Bind(wx.EVT_BUTTON, self.on_clear)
        keypad_box.Add(clear_btn, 0, wx.EXPAND|wx.ALL, 3)

        #Line for seperation
        seperator = wx.StaticLine(panel, -1, style=wx.LI_HORIZONTAL)
        keypad_box.Add(seperator, 0, wx.EXPAND|wx.ALL, 12)

        #Create the emergency mode buttons, and add it to the sizer
        emergency_box = wx.BoxSizer(wx.HORIZONTAL)

        emergency_btn = wx.Button(panel, label='Emergency')
        emergency_btn.Bind(wx.EVT_BUTTON, self.emergency_system)
        emergency_btn.SetBackgroundColour("orange")
        emergency_box.Add(emergency_btn, 0, 10)
        silent_btn = wx.Button(panel, label='Silent')
        silent_btn.Bind(wx.EVT_BUTTON, self.silent_system)
        silent_btn.SetBackgroundColour("gold")
        emergency_box.Add(silent_btn, 0, 10)

        #Add keypad box to the sizer
        keypad_sizer.Add(keypad_box, 0, wx.ALL|wx.CENTER, 5)
        keypad_sizer.Add(emergency_box, 0, wx.ALL|wx.CENTER, 5)
        

        #### INFO /STATUS SELECTOR BOX SECTION ###
        selection = wx.StaticBox(panel, 0) 
        selection_sizer = wx.StaticBoxSizer(selection, wx.VERTICAL)
        selection_box = wx.BoxSizer(wx.VERTICAL)

        #Set up the system status panel
        self.stat = wx.TextCtrl(panel, size=(200,25), style=wx.TE_READONLY, value="System Status: ")
        self.stat.SetFont(font)
        self.stat.Disable()
        selection_sizer.Add(self.stat, 0, wx.EXPAND|wx.ALL, 0)
        self.running_status = wx.StaticText(panel)
        selection_sizer.Add(self.running_status, 0)

        #Set up the user info panel
        self.code = wx.TextCtrl(panel, size=(200,100), style=wx.TE_MULTILINE, value="Enter Code: ")
        self.code.SetFont(font)
        self.code.Disable()
        selection_sizer.Add(self.code, 0, wx.EXPAND|wx.ALL, 0)
        self.running_code = wx.StaticText(panel)
        selection_sizer.Add(self.running_code, 0)

        #Add buttons for selecting system modes
        mode_row_1 = wx.BoxSizer(wx.HORIZONTAL)
        mode_row_2 = wx.BoxSizer(wx.HORIZONTAL)

        arm_btn = wx.Button(panel, label='Arm')
        arm_btn.Bind(wx.EVT_BUTTON, self.arm_system)
        arm_btn.SetForegroundColour("orange")
        mode_row_1.Add(arm_btn, 0, 10)
        home_btn = wx.Button(panel, label='Home')
        home_btn.Bind(wx.EVT_BUTTON, self.home_system)
        home_btn.SetForegroundColour("blue")
        mode_row_1.Add(home_btn, 0, 10)
        cctv_btn = wx.Button(panel, label='CCTV')
        cctv_btn.Bind(wx.EVT_BUTTON, self.cctv_system)
        cctv_btn.SetForegroundColour("gold")
        mode_row_1.Add(cctv_btn, 0, 10)
        disarm_btn = wx.Button(panel, label='Disarm')
        disarm_btn.Bind(wx.EVT_BUTTON, self.disarm_system)
        mode_row_1.Add(disarm_btn, 0, 10)

        #Add selection box to the sizer
        selection_sizer.Add(selection_box, 0, wx.ALL|wx.CENTER, 0)
        selection_sizer.Add(mode_row_1, 0, wx.ALL|wx.CENTER, 5)
        selection_sizer.Add(mode_row_2, 0, wx.ALL|wx.CENTER, 5)
        

        #### MAIN SECTION ####
        #Add all of the panels into the main box
        main_box.Add(selection_sizer, 0, wx.ALL|wx.CENTER, 5)
        main_box.Add(keypad_sizer, 0, wx.ALL|wx.CENTER, 5)

        #Set up the main sizer and panel, display
        panel.SetSizer(main_box) 
        self.Centre() 
        panel.Fit() 
        self.Show()

    #Function to output what the current code is to the user info screen
    def update_code(self, event):
        global security_code

        btn = event.GetEventObject()
        label = btn.GetLabel()
        current_code = self.code.GetValue()

        #Append the last button pressed to the running code
        self.print_code = (current_code + label)[12:]
        self.code.SetValue(("Enter Code: " + "*" * (len(self.print_code) - 1) + label))

        #Create the actual code the user is entering
        self.security_code += str(label)
        
        #Start the clear timer in a thread so the user only has 10sec to enter the code
        if len(self.security_code) > 0 and not self.timer_started:
            threading.Thread(target=self.on_clear_timer, args=(self,)).start()
            self.timer_started = True

    #Function to clear the running code
    def on_clear(self, event):
        self.code.SetValue("Enter Code: ")
        self.running_code.SetLabel("")
        self.security_code = ""

    #Timer function clearing the user code after 10sec for security reasons (so it cannot get lseft filled out)
    def on_clear_timer(self, event):
            time.sleep(10)
            self.code.SetValue("Enter Code: ")
            self.running_code.SetLabel("")
            self.timer_started = False
            self.security_code = ""
            logger.info("Cleared Security Code due to input timeout")
    
    #Function for threading the countdown and notification to users (so it doesnt lock the application)
    def threaded_countdown(self, event, status):
        #60sec notice
        self.code.SetValue("System Arming in 60 seconds!")
        i = 0
        while i <= 30:
            time.sleep(1)
            i += 1

        #30sec notice
        self.code.SetValue("System Arming in 30 seconds!")
        i = 0
        while i <= 20:
            time.sleep(1)
            i += 1

        #10sec notice
        self.code.SetValue("System Arming in 10 seconds!")
        i = 0
        while i <= 10:
            time.sleep(1)
            i += 1

        #Call the scripts to actually arm the system

        #Set the system status appropriately
            self.stat.SetValue("System Status:  " + status)
            self.code.SetValue("Enter Code: ")
            logger.info("System has been armed! Status: %s", status)

    #Function for setting system status to "Armed"
    def arm_system(self, event):
        #Verify that a passcode has been entered
        if self.security_code == "":
            self.code.SetValue("You must enter a code to arm!")

        status = "ARMED"

        #Verify that the passcode the user input is correct, and countdown to arming
        if self.security_code == self.passcode:

            #Run the thread to countdown and then actually arm things
            threading.Thread(target=self.threaded_countdown, args=(self,status,)).start()

        else:
            self.code.SetValue("Incorrect Code! Try again!")
            logger.error("Incorrect passcode entered")
            self.security_code = ""
    
    #Function for setting system status to "Home"
    def home_system(self, event):
        #Verify that a passcode has been entered
        if self.security_code == "":
            self.code.SetValue("You must enter a code to set system to Home!")

        #Verify that the passcode the user input is correct, and countdown to arming
        if self.security_code == self.passcode:

            self.stat.SetValue("System Status:  HOME")

        else:
            self.code.SetValue("Incorrect Code! Try again!")
            logger.error("Incorrect passcode entered")
            self.security_code = ""  

    #Function for setting system status to "CCTV"
    def cctv_system(self, event):
        #Verify that a passcode has been entered
        if self.security_code == "":
            self.code.SetValue("You must enter a code to arm!")

        status = "CCTV"
        
        #Verify that the passcode the user input is correct, and countdown to arming
        if self.security_code == self.passcode:

            #Run the thread to countdown and then actually arm things
            threading.Thread(target=self.threaded_countdown, args=(self,status,)).start()

        else:
            self.code.SetValue("Incorrect Code! Try again!")
            logger.error("Incorrect passcode entered")
            self.security_code = "" 

    #Function for setting system status to "Disarmed"
    def disarm_system(self, event):
        #Verify that a passcode has been entered
        if self.security_code == "":
            self.code.SetValue("You must enter a code to disarm!")

        #Verify that the passcode the user input is correct, and countdown to arming
        if self.security_code == self.passcode:
            #Call scripts to disarm security system

            self.stat.SetValue("System Status:  DISARMED")
            self.code.SetValue("Enter Code: ")

        else:
            self.disarm_try += 1

            if self.disarm_try < 3:
                self.code.SetValue("Incorrect Code! Try again! \n[!] 2 attempts remaining!! [!]")
                logger.error("Incorrect passcode entered while disarming! Attempt: %s", self.disarm_try)
                self.security_code = ""

            else:
                logger.critical("3 Incorrect disarm attempts made!!!")
                print("GET FUCKED")

                #Set off alarm here!

    #Function for setting system status to "EMERGENCY"
    def emergency_system(self, event):
        self.stat.SetValue("System Status:  EMERGENCY")

    #Function for setting system status to "SILENT"
    def silent_system(self, event):
        self.stat.SetValue("System Status:  SILENT")

### THE THING ###
if __name__ == '__main__':
    app = wx.App(False)
    main_panel(None, 'BlueSS - CSCG', (600, 300))
    app.MainLoop()
