#!/usr/bin/python2
# -*- coding: utf-8 -*-

"""

"""

import sys

try:
    import pyxhook
except:
    print("Not on linux")
    try:
        import pyHook
    except:
        print("install pyHook to run script")

import pythoncom
import time
import os
import platform

from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class MainWindow(QMainWindow): #QWidget
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
        self.thread = KeyListener()
        self.connect(self.thread, self.thread.signal, self.handleKey)
        self.clipboard_history = []
        
    def initUI(self):
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Icon')
        self.setWindowIcon(QtGui.QIcon('web.png'))        
    
        self.show()
        self.connect(QApplication.clipboard(),SIGNAL("dataChanged()"),self,SLOT("changedSlot()"))
        self.hidden = False

    def closeEvent(self, evnt):
        self.thread.stopListening()

    def handleKey(self, command):
        print(command)
        if command == "toggle" and self.hidden == False:
            self.hide()
            self.hidden = True
        elif command == "toggle" and self.hidden == True: 
            self.show()

            #This sequence fixes a bug for debian systems
            self.showMaximized()
            self.showNormal()

            self.activateWindow()
            self.raise_()
            self.setFocus()
            self.hidden = False

    @pyqtSlot()
    def changedSlot(self):
        #print("change")
        if(QApplication.clipboard().mimeData().hasText()):
            self.clipboard_history.insert(0, QApplication.clipboard().text()); #push
            print(self.clipboard_history);

#will need to multithread global key listener and clipboard chnage detection
class KeyListener(QThread):

    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.size = QSize(0, 0)
        self.signal = SIGNAL("signal")
        self.key_combo = []

        #LINUX
        platform_name = platform.system()
        if platform_name == "Linux":
            #will need to multithread global key listener and clipboard chnage detection
            #Create hookmanager
            self.hookman = pyxhook.HookManager()

            #Define our callback to fire when a key is pressed down
            self.hookman.KeyDown = self.linux_kbevent

            #Hook the keyboard
            self.hookman.HookKeyboard()

            #Start our listener
            self.hookman.start()

            #Close the listener when we are done
            #self.hookman.cancel()
        elif platform_name == "Windows":
            # create a hook manager
            self.hookman = pyHook.HookManager()
            # watch for all mouse events
            self.hookman.KeyDown = self.windows_kbevent
            # set the hook
            self.hookman.HookKeyboard()
            # wait forever
            pythoncom.PumpMessages()


    #This function is called every time a key is presssed
    def linux_kbevent(self, event):
        #print key info
        #print(event)
        
        #If the ascii value matches spacebar, terminate the while loop
        #if event.Ascii == 32:
        if len(self.key_combo) >= 2:
            self.key_combo = []

        self.key_combo.append(event.Ascii)
        #print("Combo arr: ", self.key_combo)
        if len(self.key_combo) == 2:
            check_space = (self.key_combo[0] == 99 or self.key_combo[1] == 99)
            check_alt = (self.key_combo[0] == 233 or self.key_combo[1] == 233)
            if check_space and check_alt: 
                self.emit(self.signal, "toggle");


    #This function is called every time a key is presssed
    def windows_kbevent(self, event):
        #print key info
        print(event.Ascii)
        if len(self.key_combo) >= 2:
            self.key_combo = []

        self.key_combo.append(event.Ascii)
        #print("Combo arr: ", self.key_combo)
        if len(self.key_combo) == 2:
            check_space = (self.key_combo[0] == 32 or self.key_combo[1] == 32)
            check_alt = (self.key_combo[0] == 0 or self.key_combo[1] == 0)
            if check_space and check_alt: 
                self.emit(self.signal, "toggle");
        #If the ascii value matches spacebar, terminate the while loop
        #if event.Ascii == 32:
        #if len(self.key_combo) >= 2:
        #    self. key_combo = []

        #self.key_combo.append(event.Ascii)
        #print("Combo arr: ", self.key_combo)
        #if len(self.key_combo) == 2:
        #    check_space = (self.key_combo[0] == 99 or self.key_combo[1] == 99)
        #    check_alt = (self.key_combo[0] == 233 or self.key_combo[1] == 233)
        #    if check_space and check_alt: 
        #        self.emit(self.signal, "toggle");

        

    def stopListening(self):
        print("stopping key listen thread")
        self.hookman.cancel()

    def notifyMain(self):
        self.emit(SIGNAL("output(QRect, QImage)"), QRect(x - self.outerRadius, y - self.outerRadius, self.outerRadius * 2, self.outerRadius * 2), image)

def main():
    
    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

