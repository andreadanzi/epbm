# -*- coding: utf-8 -*-
"""
Created on Fri May 27 15:07:24 2016

@author: aghensi
"""

from PyQt4 import QtGui
import sys
import os
import logging

import gui
from helpers import get_immediate_subdirectories
from main import import_all_data
from process_calc import process_calc
from plot_data import plot_data as plt_data
from plot_data_ccg import plot_data as plt_data_ccg
from export_building_data import export_buildings_data as ebd


class guilogic(QtGui.QDialog, gui.Ui_MainWindow):
    '''
    classe che aggiunge la logica all'interfaccia grafica
    '''

    def __init__(self, parent=None):
        super(guilogic, self).__init__(parent)
        self.setupUi(parent)
        self.connectActions()
        # TODO: aggiungere possibilità di cambiare cartella di lavoro?
        self._project_code = None
        self.workingdir = os.path.join(os.path.dirname(__file__), "..", "data")
        self.get_projects()

    def get_projects(self):
        for project_name in get_immediate_subdirectories(self.workingdir):
            self.cbxProjectCode.addItem(project_name)


    def connectActions(self):
        """
        Connect the user interface controls to the logic
        """
        self.btnMain.clicked.connect(self.startmain)
        self.cbxProjectCode.activated[str].connect(self.set_projectcode)


    def set_projectcode(self, text):
        self._project_code = str(text)


    def startmain(self):
        """
        Even handler for the pushButton click
        """
        if (self._project_code):
            import_all_data(self._project_code)



class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super(QPlainTextEditLogger, self).__init__()

        self.widget = QtGui.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)


    def emit(self, record):
        msg = self.format(record)
        self.widget.textCursor().appendPlainText(msg)


    def write(self, m):
        pass

if __name__=='__main__':
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = guilogic(MainWindow)
    log_handler = QPlainTextEditLogger(MainWindow)
    logging.getLogger().addHandler(log_handler)
    MainWindow.show()
    sys.exit(app.exec_())



