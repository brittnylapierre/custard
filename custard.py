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
        import pythoncom
    except:
        print("install pyhook and pythoncom to run script")
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
        self.set_toggle_on_code = -1
        self.set_toggle_off_code = -1
        self.toggle_code = -1
        self.grid_layout    = QtGui.QGridLayout()
        self.central_widget = QtGui.QWidget()
        self.list_widget = ListWidget()

        #Resize width and height
        #self.list_widget.resize(300,120)

        self.list_widget.addItem("Item 1"); 
        self.list_widget.addItem("Item 2");
        self.list_widget.addItem("Item 3");
        self.list_widget.addItem("Item 4");

        self.grid_layout.addWidget(self.list_widget,0,0)
        #grid_layout.addWidget(QtGui.QPushButton("Button 2"),0,1)
        #grid_layout.addWidget(QtGui.QPushButton("Button 3"),0,2)
        #grid_layout.addWidget(QtGui.QPushButton("Button 4"),1,0)
        #grid_layout.addWidget(QtGui.QPushButton("Button 5"),1,1)

        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.grid_layout)

        self.resize(200,200)
        
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
            clipboard_content = QApplication.clipboard().text()
            #push to first index
            self.clipboard_history.insert(0, clipboard_content); 
            print(self.clipboard_history);

            #add clipboard contents to list widget
            self.list_widget.addItem(clipboard_content);


#List widget that stores clipboard history text
class ListWidget(QListWidget):
    def __init__(self):
        super(ListWidget, self).__init__()
        self.currentItemChanged.connect(self.copyToClipboard)

    def copyToClipboard(self, curr, prev):
        print('Selected: ', str(curr.text()))


#will need to multithread global key listener and clipboard chnage detection
class KeyListener(QThread):

    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.size = QSize(0, 0)
        self.signal = SIGNAL("signal")
        self.watching = True;

        #LINUX
        platform_name = platform.system()
        print "You are using " + platform_name;
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
        print(event.Ascii)
        #Disable watch for toggle on `
        if event.Ascii == 126:
            self.watching = False

        #Enable watch for toggle on ~
        if event.Ascii == 96:
            self.watching = True

        #toggle view on ]
        if self.watching and event.Ascii == 93: 
            self.emit(self.signal, "toggle");



    #This function is called every time a key is presssed
    def windows_kbevent(self, event):
        #TO DO
        print("to do")

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

