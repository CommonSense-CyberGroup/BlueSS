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

To Do:
    -Set up error checking and validation
    -Continue building out the UI

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
    def __init__(self, parent, title):
        super(main_panel, self).__init__(parent, title = title)

        self.timer_started = False

        #Create the main box that all the sub-boxes will sit in
        panel = wx.Panel(self)
        main_box = wx.BoxSizer(wx.HORIZONTAL)

        #Create the UI and run
        #Function variables for UI
        font = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL)

        #### KEYPAD SIZER / BOX SECTION ####
        #Create the keypad box and sizer
        keypad = wx.StaticBox(panel, 0)
        keypad_sizer = wx.StaticBoxSizer(keypad, wx.HORIZONTAL)
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

        #Add keypad box to the sizer
        keypad_sizer.Add(keypad_box, 0, wx.ALL|wx.CENTER, 10)
        
        #### INFO /STATUS SELECTOR BOX SECTION ###
        selection = wx.StaticBox(panel, 0) 
        selection_sizer = wx.StaticBoxSizer(selection, wx.HORIZONTAL)
        selection_box = wx.BoxSizer(wx.HORIZONTAL)

        #Set up the user info panel
        self.code = wx.TextCtrl(panel, style=wx.TE_LEFT, value="Enter Security Code: ")
        self.code.SetFont(font)
        self.code.Disable()
        selection_sizer.Add(self.code, 0, wx.EXPAND|wx.ALL, 0)
        self.running_code = wx.StaticText(panel)
        selection_sizer.Add(self.running_code, 0)

        #Add selection box to the sizer
        selection_sizer.Add(selection_box, 0, wx.ALL|wx.CENTER, 10)

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
        btn = event.GetEventObject()
        label = btn.GetLabel()
        current_code = self.code.GetValue()

        #Append the last button pressed to the running code
        self.code.SetValue(current_code + label)
        security_code = (current_code + label).split(": ")[1]

        #Start the clear timer in a thread so the user only has 10sec to enter the code
        if len(security_code) > 0 and not self.timer_started:
            threading.Thread(target=self.on_clear_timer, args=(self,)).start()
            self.timer_started = True

    #Function to clear the running code
    def on_clear(self, event):
        self.code.SetValue("Enter Security Code: ")
        self.running_code.SetLabel("")

    #Timer function clearing the user code after 10sec for security reasons (so it cannot get lseft filled out)
    def on_clear_timer(self, event):
            time.sleep(10)
            self.code.SetValue("Enter Security Code: ")
            self.running_code.SetLabel("")
            self.timer_started = False
            logger.info("Cleared Security Code due to input timeout")

            #Function to actually create the UI for display within the main screen
    

### THE THING ###
if __name__ == '__main__':
    app = wx.App(False)
    main_panel(None,  'BlueSS - CSCG')
    app.MainLoop()
