#!/usr/bin/python2
# -*- coding: utf-8 -*-

"""

This is a clipboard manager for Linux and Windows.

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
        self.init_UI()

        self.thread = None

        #Signal for sending toggle codes change
        self.signal = SIGNAL("signal")

        #Watch for changes in clipboard if change occurs run changeSlot function
        self.connect(QApplication.clipboard(),SIGNAL("dataChanged()"),self,SLOT("changed_slot()"))

        self.clipboard_history = [] #might come in handy?
        
        
    def init_UI(self):
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Icon')
        self.setWindowIcon(QtGui.QIcon('web.png')) 
        self.grid_layout    = QtGui.QGridLayout()
        self.central_widget = QtGui.QWidget()
        self.list_widget = ListWidget()
        self.grid_layout.addWidget(self.list_widget,0,0)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.grid_layout)
        self.resize(600,350)

        #Styling
        self.stylesheet = """ /*Begin Stylesheet*/
        QWidget {
            background-color: #333333;
        } 

        QListWidget {
            border: none;
            background-color: #464646;
            padding: 0;
        } 

        QListWidget::item {
            color: white;
            height: 24px;
            padding: 10px;
            background-color: #464646;
            outline: 0;
            border: none;
        }

        QListWidget::item::selected {
            color: #00A8B2;
            background-color: #404040;
        }
        """
        self.setStyleSheet(self.stylesheet)

        self.show()
        self.hidden = False


    def set_worker_thread(self, thread):
        #Create key listening thread for toggle view and attach signal for communicating to this main window
        self.thread = thread
        self.connect(self.thread, self.thread.signal, self.handle_key)


    def closeEvent(self, event):
        print(self.thread)
        self.thread.stop_listening()


    def handle_key(self, command):
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


    def key_press_event(self, event):
        key = event.key()
        print(event, "\nkey: ", key)
        
        #Check for control modifier
        if int(event.modifiers()) == Qt.ControlModifier:
            #On x remove the curr selected item from item list and copy to clipboard via CUT
            if key == Qt.Key_X:
                #Copy to clipboard
                QApplication.clipboard().setText(self.list_widget.currentItem().text())
                print(self.list_widget.currentItem().text(), " removed from list and copied to clipboard")

                #Remove all from list 
                matching_items = self.list_widget.findItems(self.list_widget.currentItem().text(), Qt.MatchExactly)
                for item in matching_items:
                    self.list_widget.takeItem(self.list_widget.row(item))
                    #print("removed", item.text())

            #TO DO: On c copy, don't remove from list
            if key == Qt.Key_C:
                #Copy to clipboard
                QApplication.clipboard().setText(self.list_widget.currentItem().text())
                print(self.list_widget.currentItem().text(), " removed from list and copied to clipboard")

                #Remove newly added from list 
                matching_items = self.list_widget.findItems(self.list_widget.currentItem().text(), Qt.MatchExactly)

                i = 0
                for item in matching_items:
                    if i != 0:
                        self.list_widget.takeItem(self.list_widget.row(item))
                    i += 1
                    #print("removed", item.text())


    @pyqtSlot()
    def changed_slot(self):
        if(QApplication.clipboard().mimeData().hasText()):
            clipboard_content = QApplication.clipboard().text()
            #Remove from list

            #Check if already in list, not in list if no mathcing items
            matching_items = self.list_widget.findItems(clipboard_content, Qt.MatchExactly)

            if len(matching_items) == 0:
                #add clipboard contents to top of list in list widget
                item = QListWidgetItem(clipboard_content)
                self.list_widget.insertItem(0, item);
            else: 
                #TODO: make item first in list?
                print("Selected text already in history.")

    def change_toggle_var(self, toggle_event_name, ascii_code):
        self.emit(self.signal, toggle_event_name, ascii_code);



#List widget that stores clipboard history text
class ListWidget(QListWidget):
    def __init__(self):
        super(ListWidget, self).__init__()
        #self.stylesheet = """ """
        #self.setStyleSheet(self.stylesheet)



#Will need to multithread global key listener to toggle our program even when it doesnt have keyboard focus
class KeyListener(QThread):

    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.size = QSize(0, 0)
        self.signal = SIGNAL("signal")
        self.watching = True
        print("parent: ", self.parent)

        #Default values
        #TODO: find a way to set within gui then pass to key listen thread
        #TODO: in gui have disable all toggle functionalty button
        self.set_toggle_on_code = 126 #`
        self.set_toggle_off_code = 96 #~
        self.toggle_code = 93 #]

        #LINUX
        platform_name = platform.system()
        print "You are using " + platform_name;
        if platform_name == "Linux":
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

        #Windows    
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
        #print(event.Ascii)

        #Disable watch for toggle on `
        if event.Ascii == self.set_toggle_on_code:
            self.watching = False

        #Enable watch for toggle on ~
        if event.Ascii == self.set_toggle_off_code:
            self.watching = True

        #toggle view on ]
        if self.watching and event.Ascii == self.toggle_code: 
            self.emit(self.signal, "toggle");


    def connect_to_main(self, main):
        #Create key listening thread for toggle view and attach signal for communicating to this main window
        self.main = main
        self.connect(self.main, self.main.signal, self.change_toggle_event_value)


    def change_toggle_event_value(self, toggle_event_name, ascii_code):
        print('Toggle event name: ', toggle_event_name, " ascii: ", ascii_code)


    #This function is called every time a key is presssed
    def windows_kbevent(self, event):
        #TO DO
        print("to do")


    def stop_listening(self):
        print("stopping key listen thread")
        self.hookman.cancel()



def main():
    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()

    #Create key listening thread for toggle view 
    key_thread = KeyListener()

    #and attach signal for communicating to this main window
    main_window.set_worker_thread(key_thread)

    #Set signal for customizing toggle codes 
    key_thread.connect_to_main(main_window)

    #Test main window to worker thread connections
    main_window.change_toggle_var("toggle on", 1234)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

