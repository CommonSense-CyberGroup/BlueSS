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
    -Set up logging
    -Set up error checking and validation
    -Continue building out the UI

'''

### IMPORT LIBRARIES ###
import wx       # - Used for all things GUI
import time     # - Used for waiting on user input, and many other time activities
import threading    # - Used for threading different things outside of the main function


### CLASSES AND FUNCTIONS ###
#Class for the keypad
class keypad_panel(wx.Panel):

    #Init the UI and present to the user
    def __init__(self, parent):
        super().__init__(parent)
        self.last_button_pressed = None
        self.timer_started = False
        self.create_ui()

    #Function to actually create the UI for display within the main screen
    def create_ui(self):
        #Create the main window
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL)

        #Set up the user info panel
        self.code = wx.TextCtrl(self, style=wx.TE_RIGHT, value="Enter Security Code: ")
        self.code.SetFont(font)
        self.code.Disable()
        main_sizer.Add(self.code, 0, wx.EXPAND|wx.ALL, 0)
        self.running_code = wx.StaticText(self)
        main_sizer.Add(self.running_code, 0, wx.ALIGN_RIGHT)

        #Set up and configure the bottons/keypad
        buttons = [['7', '8', '9'],
                   ['4', '5', '6'],
                   ['1', '2', '3'],
                   ['*', '0', '#']]
        for label_list in buttons:
            btn_sizer = wx.BoxSizer()
            for label in label_list:
                button = wx.Button(self, label=label)
                btn_sizer.Add(button, 0, wx.ALIGN_CENTER, 0)
                button.Bind(wx.EVT_BUTTON, self.update_code)
            main_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER, 0)

        #Create the clear button
        clear_btn = wx.Button(self, label='Clear')
        clear_btn.Bind(wx.EVT_BUTTON, self.on_clear)

        #Set up the window sizer
        main_sizer.Add(clear_btn, 0, wx.EXPAND|wx.ALL, 3)
        self.SetSizer(main_sizer)

    #Function to output what the current code is to the user info screen
    def update_code(self, event):
        btn = event.GetEventObject()
        label = btn.GetLabel()
        current_code = self.code.GetValue()

        #Append the last button pressed to the running code
        self.code.SetValue(current_code + label)
        security_code = (current_code + label).split(": ")[1]

        #Set the last button pressed
        self.last_button_pressed = label

        #Start the clear timer in a thread so the user only has 10sec to enter the code
        if len(security_code) > 0 and not self.timer_started:
            clear_thread = threading.Thread(target=self.on_clear_timer, args=(self,))
            clear_thread.start()
            self.time_started = True

    #Function to clear the running code
    def on_clear(self, event):
        self.code.SetValue("Enter Security Code: ")
        self.running_code.SetLabel("")

    #Timer function clearing the user code after 10sec for security reasons (so it cannot get lseft filled out)
    def on_clear_timer(self, event):
        if self.last_button_pressed != None:
            time.sleep(10)
            self.code.SetValue("Enter Security Code: ")
            self.running_code.SetLabel("")
            self.last_button_pressed = None
            self.time_started = False


#Class for the main window to display
class ui_frame(wx.Frame):

    #Init the main window and set properties
    def __init__(self):
        super().__init__(
            None, title="BlueSS - CSCG",
            size=(250, 200))

        panel = keypad_panel(self)
        self.Show()

### THE THING ###
if __name__ == '__main__':
    app = wx.App(False)
    frame = ui_frame()
    app.MainLoop()
