#!/usr/bin/python2
# -*- coding: utf-8 -*-

"""
TODO : https://wiki.python.org/moin/PyQt/Threading,_Signals_and_Slots
"""

import sys
import pyxhook
import time

import sys
from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class MainWindow(QMainWindow): #QWidget
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
        self.thread = KeyListener()
        self.connect(self.thread, self.thread.signal, self.handleKey)
        
    def initUI(self):
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Icon')
        self.setWindowIcon(QtGui.QIcon('web.png'))        
    
        self.show()
        self.connect(QApplication.clipboard(),SIGNAL("dataChanged()"),self,SLOT("changedSlot()"))
        self.hidden = False

    def closeEvent(self, evnt):
        self.thread.stopListening()

    def handleKey(self, key):
        print(key)
        if key == "space" and self.hidden == False:
            self.hide()
            self.hidden = True
        elif key == "space" and self.hidden == True: 
            self.show()
            self.activateWindow()
            self.raise_()
            self.setFocus()
            self.hidden = False

    @pyqtSlot()
    def changedSlot(self):
        #print("change")
        if(QApplication.clipboard().mimeData().hasText()):
            QMessageBox.information(self,"ClipBoard Text Copy Detected!", "You Copied:"+QApplication.clipboard().text());


#will need to multithread global key listener and clipboard chnage detection
class KeyListener(QThread):

    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.size = QSize(0, 0)
        self.signal = SIGNAL("signal")

        #will need to multithread global key listener and clipboard chnage detection
        #Create hookmanager
        self.hookman = pyxhook.HookManager()

        #Define our callback to fire when a key is pressed down
        self.hookman.KeyDown = self.kbevent

        #Hook the keyboard
        self.hookman.HookKeyboard()

        #Start our listener
        self.hookman.start()

        #Close the listener when we are done
        #self.hookman.cancel()

    #This function is called every time a key is presssed
    def kbevent(self, event):
        #print key info
        #print(event)
        
        #If the ascii value matches spacebar, terminate the while loop
        if event.Ascii == 32:
            self.emit(self.signal, "space"); 

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

