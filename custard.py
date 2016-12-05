#!/usr/bin/python2
# -*- coding: utf-8 -*-

"""

This is a clipboard manager for Linux and Windows.

"""

import sys
import re
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
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.initUI()

        self.pause_toggle = False

        self.thread = None
        self.toggle_settings_widget = None

        #Signal for sending toggle codes change
        self.signal = SIGNAL("signal")

        #Watch for changes in clipboard if change occurs run changeSlot function
        self.connect(QApplication.clipboard(),SIGNAL("dataChanged()"),self,SLOT("changedSlot()"))

        self.clipboard_history = [] #might come in handy?
        
        
    def initUI(self):
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Custard')
        self.setWindowIcon(QtGui.QIcon(''))

        self.list_widget = ListWidget()

        self.grid_layout = QtGui.QGridLayout()
        self.central_widget = QtGui.QWidget()
        self.grid_layout.addWidget(self.list_widget,0,0)
        self.setCentralWidget(self.central_widget)
        self.grid_layout.setMargin(0)
        self.central_widget.setLayout(self.grid_layout)

        #Menu
        main_menu = self.menuBar()
        toggle_settings_action = QtGui.QAction("&Toggle Settings", self)
        toggle_settings_action.setShortcut("Ctrl+E")
        toggle_settings_action.setStatusTip('Edit the keys used to toggle.')
        toggle_settings_action.triggered.connect(self.openToggleSettings)
        settings_menu = main_menu.addMenu('&Settings')
        settings_menu.addAction(toggle_settings_action)

        self.resize(400,150)

        #Keeps it staying on top when not active window
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        #Styling
        self.stylesheet = """ /*Begin Stylesheet*/

        QScrollBar:vertical {
            border: 2px solid #333333;
            background-color: #333333;
            opacity: 1.0;
            width: 14px;
            margin: 0px 0px 0px 0px;
        }

        QScrollBar:handle:vertical {
            background-color: #5F5F5F;
            border-radius: 5px;
            width: 10px;
        }

        QScrollBar:sub-page:vertical {
            background: #333333;
        }

        QScrollBar:add-page:vertical {
            background: #333333;
        }

        QScrollBar:horizontal {
            border: 2px solid #333333;
            background-color: #333333;
            opacity: 1.0;
            height: 14px;
            margin: 0px 0px 0px 0px;
        }

        QScrollBar:handle:horizontal {
            background-color: #5F5F5F;
            border-radius: 5px;
            height: 10px;
        }

        QScrollBar:sub-page:horizontal {
            background: #333333;
        }

        QScrollBar:add-page:horizontal {
            background: #333333;
        }

        QScrollBar:add-line {
            background: none;
            height: 0px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }

        QScrollBar::sub-line {
            background: none;
            height: 0px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }

        QWidget {
            background-color: #333333;
        }

        QGridLayout {
            background-color: #333333;
        }

        QMainWindow {
            background-color: #333333;
        } 

        QListWidget {
            border: none;
            background-color: #464646;
            padding: 0;
            outline: 0;
        } 

        QListWidget::item {
            color: white;
            height: 24px;
            padding: 10px;
            background-color: #464646;
            border-bottom: 1px dashed #5F5F5F;
        }

        QListWidget::item::selected {
            color: #00A8B2;
            background-color: #404040;
        }

        """
        
        self.setStyleSheet(self.stylesheet)

        self.show()
        self.hidden = False


    def setWorkerThread(self, thread):
        #Create key listening thread for toggle view and attach signal for communicating to this main window
        self.thread = thread
        self.connect(self.thread, self.thread.signal, self.handleKey)


    def handleKey(self, command):
        if command == "toggle" and self.hidden == False and self.pause_toggle == False:
            print(command)
            self.hide()
            print(self.isActiveWindow())
            self.hidden = True
            
        elif command == "toggle" and self.hidden == True and self.pause_toggle == False:
            print(command)
            self.show()

            #This sequence fixes a bug for debian systems
            self.showMaximized()
            self.showNormal()

            # this will activate the window
            self.window().raise_()
            self.window().activateWindow()
            self.window().setWindowState(Qt.WindowActive)
            
            self.window().setFocus()
            print(self.window().isActiveWindow())
            self.hidden = False


    def keyPressEvent(self, event):
        key = event.key()
        print(event, "\nkey:\n", key)
        
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
                print(self.list_widget.currentItem().text(), "copied to clipboard")

                #Remove newly added from list 
                matching_items = self.list_widget.findItems(self.list_widget.currentItem().text(), Qt.MatchExactly)

                i = 0
                for item in matching_items:
                    if i != 0:
                        self.list_widget.takeItem(self.list_widget.row(item))
                    i += 1
                    #print("removed", item.text())


    @pyqtSlot()
    def changedSlot(self):
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


    def openToggleSettings(self):
        print("toggle settings open")
        self.pause_toggle = True

        self.toggle_settings_widget = PopupMenuWidget()
        self.connect(self.toggle_settings_widget, self.toggle_settings_widget.signal, self.handlePauseToggle)

        #Keeps it above the main window
        self.toggle_settings_widget.setFocusPolicy(Qt.StrongFocus)
        self.toggle_settings_widget.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.mouse = QtGui.QCursor()
        self.toggle_settings_widget.move(self.mouse.pos())
        self.toggle_settings_widget.resize(300,200)
        self.stylesheet = """ /* Start Style */
            QWidget {
                background-color: #464646;
                color: white;
            }

            QTextEdit {
                background-color: white;
                color: black;
                border: 1px solid black;
            }

            QScrollArea {
                height:0px;
                width:0px;
            }
            
            QScrollBar:vertical {
                height:0px;
                width:0px;
            }

            QScrollBar:horizontal {
                height:0px;
                width:0px;
            }

            QPushButton {
                background-color: #333333;
            }

            QPushButton:pressed {
                background-color: #3E3E3E;
            }

        """

        self.toggle_grid_layout = QtGui.QGridLayout()

        #Add inputs
        self.toggle_enabled_label = QLabel('Enable Toggle Key:')
        self.toggle_grid_layout.addWidget(self.toggle_enabled_label,0,0)

        self.toggle_enabled_input = QTextEdit();
        self.toggle_enabled_input.setMaximumHeight(self.toggle_enabled_label.sizeHint().height())
        self.toggle_grid_layout.addWidget(self.toggle_enabled_input,0,1)

        self.toggle_disabled_label = QLabel('Disable Toggle Key:')
        self.toggle_grid_layout.addWidget(self.toggle_disabled_label,1,0)

        self.toggle_disabled_input = QTextEdit()
        self.toggle_disabled_input.setMaximumHeight(self.toggle_disabled_label.sizeHint().height())
        self.toggle_grid_layout.addWidget(self.toggle_disabled_input,1,1)

        self.toggle_label = QLabel('Toggle Key:')
        self.toggle_grid_layout.addWidget(self.toggle_label,2,0)

        self.toggle_input = QTextEdit()
        self.toggle_input.setMaximumHeight(self.toggle_label.sizeHint().height())
        self.toggle_grid_layout.addWidget(self.toggle_input,2,1)

        self.toggle_settings_button = QPushButton('Ok')
        self.toggle_settings_button.clicked.connect(self.changeSettingsFromOnToggleMenu)
        self.toggle_grid_layout.addWidget(self.toggle_settings_button,3,1)

        self.toggle_settings_widget.setLayout(self.toggle_grid_layout);

        #Change settings on button press

        self.toggle_settings_widget.setStyleSheet(self.stylesheet)
        self.toggle_settings_widget.show()


    def changeSettingsFromOnToggleMenu(self):
        print("widget ", self.toggle_settings_widget)
        enable_text = str(self.toggle_enabled_input.toPlainText())
        disable_text = str(self.toggle_disabled_input.toPlainText())
        toggle_text = str(self.toggle_input.toPlainText())
        print(enable_text, "\n", disable_text, "\n", toggle_text)

        if re.match('$^', enable_text) == None:
            enable_code = ord(enable_text)
            self.changeToggleVar('enabled', enable_code)

        if re.match('$^', disable_text) == None:
            disable_code = ord(disable_text)
            self.changeToggleVar('disabled', disable_code)

        if re.match('$^', toggle_text) == None:
            toggle_code = ord(toggle_text)
            self.changeToggleVar('toggle', toggle_code)

        if self.toggle_settings_widget:
            self.toggle_settings_widget.close()


    def changeToggleVar(self, toggle_event_name, ascii_code):
        self.emit(self.signal, toggle_event_name, ascii_code);


    def handlePauseToggle(self, data):
        if self.pause_toggle == False:
            self.pause_toggle = True
            print("toggle paused")

        elif self.pause_toggle == True:
            self.pause_toggle = False
            print("toggle unpaused")


    def closeEvent(self, event):
        print(self.thread)
        self.thread.stopListening()
        if self.toggle_settings_widget != None:
            self.toggle_settings_widget.close()


#List widget that stores clipboard history text
class ListWidget(QListWidget):
    def __init__(self):
        super(ListWidget, self).__init__()


class PopupMenuWidget(QWidget):
    def __init__(self):
        super(PopupMenuWidget, self).__init__()
        self.signal = SIGNAL("signal")

    def closeEvent(self, event):
        self.emit(self.signal, "unpause toggle");


#Multithread global key listener to toggle our program even when it doesnt have keyboard focus
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
        self.set_toggle_enabled_code = 126 #`
        self.set_toggle_disabled_code = 96 #~
        self.toggle_code = 9 #TAB #93 #]

        #LINUX
        platform_name = platform.system()
        print "You are using " + platform_name;
        if platform_name == "Linux":
            #Create hookmanager
            self.hookman = pyxhook.HookManager()

            #Define our callback to fire when a key is pressed down
            self.hookman.KeyDown = self.linuxKeyEvent

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
            self.hookman.KeyDown = self.linuxKeyEvent # see if works self.windowsKeyEvent
            # set the hook
            self.hookman.HookKeyboard()
            # wait forever
            #pythoncom.PumpMessages()


    #This function is called every time a key is presssed
    def linuxKeyEvent(self, event):
        #print key info
        print(event.Ascii)

        #Disable watch for toggle on `
        if event.Ascii == self.set_toggle_enabled_code:
            self.watching = False

        #Enable watch for toggle on ~
        if event.Ascii == self.set_toggle_disabled_code:
            self.watching = True

        #toggle view on ]
        if self.watching and event.Ascii == self.toggle_code: 
            self.emit(self.signal, "toggle");


    def connectToMain(self, main):
        #Create key listening thread for toggle view and attach signal for communicating to this main window
        self.main = main
        self.connect(self.main, self.main.signal, self.changeToggleEventValue)


    def changeToggleEventValue(self, toggle_event_name, ascii_code):
        print('Toggle event name: ', toggle_event_name, " ascii: ", ascii_code)
        if toggle_event_name == "enable":
            self.set_toggle_enabled_code = ascii_code

        if toggle_event_name == "disable":
            self.set_toggle_disabled_code = ascii_code

        if toggle_event_name == "toggle":
            self.toggle_code = ascii_code


    #This function is called every time a key is presssed
    def windowsKeyEvent(self, event):
        #TO DO
        print("to do")


    def stopListening(self):
        print("stopping key listen thread")
        #LINUX
        platform_name = platform.system()
        print "You are using " + platform_name;
        if platform_name == "Linux":
            self.hookman.cancel()



def main():
    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()

    #Create key listening thread for toggle view 
    key_thread = KeyListener()

    #and attach signal for communicating to this main window
    main_window.setWorkerThread(key_thread)

    #Set signal for customizing toggle codes 
    key_thread.connectToMain(main_window)

    #Test main window to worker thread connections
    main_window.changeToggleVar("toggle on", 1234)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()