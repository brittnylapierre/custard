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


class Example(QtGui.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()

        #clipboard = QtGui.QApplication.clipboard()
        #clipboard.text(self, QClipboard.Clipboard)

        #Create hookmanager
        self.hookman = pyxhook.HookManager()
        #Define our callback to fire when a key is pressed down
        self.hookman.KeyDown = self.kbevent
        #Hook the keyboard
        self.hookman.HookKeyboard()
        #Start our listener
        self.hookman.start()

        #Close the listener when we are done
        self.hookman.cancel()
        
        
    def initUI(self):
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Icon')
        self.setWindowIcon(QtGui.QIcon('web.png'))        
    
        self.show()

    #This function is called every time a key is presssed
    def kbevent(self, event):
        #print key info
        #print(event)
        
        #If the ascii value matches spacebar, terminate the while loop
        if event.Ascii == 32:
            self.hookman.cancel()

class ClipboardListener(QObject):   
    @pyqtSlot()  
    def changedSlot(self):
        if(QApplication.clipboard().mimeData().hasText()):
            QMessageBox.information(None,"ClipBoard Text Copy Detected!", "You Copied:"+QApplication.clipboard().text());      
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    #will need to multithread global key listener and clipboard chnage detection
    ex = Example()
    cl = ClipboardListener()
    QObject.connect(QApplication.clipboard(),SIGNAL("dataChanged()"),cl,SLOT("changedSlot()")) 
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

