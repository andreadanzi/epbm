# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\users\Andrea\dev\SmartTunneling\epbm\smt\gui\gui.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(282, 205)
        MainWindow.setMinimumSize(QtCore.QSize(282, 205))
        MainWindow.setMaximumSize(QtCore.QSize(282, 205))
        MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        MainWindow.setAnimated(True)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.layoutWidget = QtGui.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 261, 170))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.layoutWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox = QtGui.QGroupBox(self.layoutWidget)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.layoutWidget1 = QtGui.QWidget(self.groupBox)
        self.layoutWidget1.setGeometry(QtCore.QRect(10, 20, 237, 24))
        self.layoutWidget1.setObjectName(_fromUtf8("layoutWidget1"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.rbStandardCalc = QtGui.QRadioButton(self.layoutWidget1)
        self.rbStandardCalc.setObjectName(_fromUtf8("rbStandardCalc"))
        self.horizontalLayout.addWidget(self.rbStandardCalc)
        self.rbCustomCalc = QtGui.QRadioButton(self.layoutWidget1)
        self.rbCustomCalc.setObjectName(_fromUtf8("rbCustomCalc"))
        self.horizontalLayout.addWidget(self.rbCustomCalc)
        self.lblSamples = QtGui.QLabel(self.layoutWidget1)
        self.lblSamples.setObjectName(_fromUtf8("lblSamples"))
        self.horizontalLayout.addWidget(self.lblSamples)
        self.sbSamples = QtGui.QSpinBox(self.layoutWidget1)
        self.sbSamples.setMinimum(1)
        self.sbSamples.setObjectName(_fromUtf8("sbSamples"))
        self.horizontalLayout.addWidget(self.sbSamples)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        self.gridLayout.addWidget(self.groupBox, 1, 0, 3, 2)
        self.btnMain = QtGui.QPushButton(self.layoutWidget)
        self.btnMain.setObjectName(_fromUtf8("btnMain"))
        self.gridLayout.addWidget(self.btnMain, 4, 0, 1, 1)
        self.lblProjectCode = QtGui.QLabel(self.layoutWidget)
        self.lblProjectCode.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lblProjectCode.setObjectName(_fromUtf8("lblProjectCode"))
        self.gridLayout.addWidget(self.lblProjectCode, 0, 0, 1, 1)
        self.cbxProjectCode = QtGui.QComboBox(self.layoutWidget)
        self.cbxProjectCode.setObjectName(_fromUtf8("cbxProjectCode"))
        self.gridLayout.addWidget(self.cbxProjectCode, 0, 1, 1, 1)
        self.btnProcessCalc = QtGui.QPushButton(self.layoutWidget)
        self.btnProcessCalc.setObjectName(_fromUtf8("btnProcessCalc"))
        self.gridLayout.addWidget(self.btnProcessCalc, 5, 0, 1, 1)
        self.btnExportData = QtGui.QPushButton(self.layoutWidget)
        self.btnExportData.setObjectName(_fromUtf8("btnExportData"))
        self.gridLayout.addWidget(self.btnExportData, 4, 1, 1, 1)
        self.btnExportBuilding = QtGui.QPushButton(self.layoutWidget)
        self.btnExportBuilding.setObjectName(_fromUtf8("btnExportBuilding"))
        self.gridLayout.addWidget(self.btnExportBuilding, 5, 1, 1, 1)
        self.btnStrataQgis = QtGui.QPushButton(self.layoutWidget)
        self.btnStrataQgis.setObjectName(_fromUtf8("btnStrataQgis"))
        self.gridLayout.addWidget(self.btnStrataQgis, 6, 1, 1, 1)
        self.pushButton = QtGui.QPushButton(self.layoutWidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.gridLayout.addWidget(self.pushButton, 6, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.cbxProjectCode, self.rbStandardCalc)
        MainWindow.setTabOrder(self.rbStandardCalc, self.rbCustomCalc)
        MainWindow.setTabOrder(self.rbCustomCalc, self.sbSamples)
        MainWindow.setTabOrder(self.sbSamples, self.btnMain)
        MainWindow.setTabOrder(self.btnMain, self.btnProcessCalc)
        MainWindow.setTabOrder(self.btnProcessCalc, self.pushButton)
        MainWindow.setTabOrder(self.pushButton, self.btnExportData)
        MainWindow.setTabOrder(self.btnExportData, self.btnExportBuilding)
        MainWindow.setTabOrder(self.btnExportBuilding, self.btnStrataQgis)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "EPBM", None))
        self.groupBox.setTitle(_translate("MainWindow", "Tipologia calcolo", None))
        self.rbStandardCalc.setText(_translate("MainWindow", "Standard", None))
        self.rbCustomCalc.setText(_translate("MainWindow", "Custom", None))
        self.lblSamples.setText(_translate("MainWindow", "Campioni:", None))
        self.btnMain.setToolTip(_translate("MainWindow", "Importa i file contenuti nalla cartella \"in\" del progetto", None))
        self.btnMain.setText(_translate("MainWindow", "Inizializza", None))
        self.lblProjectCode.setText(_translate("MainWindow", "Project Code:", None))
        self.btnProcessCalc.setText(_translate("MainWindow", "Calcola", None))
        self.btnExportData.setText(_translate("MainWindow", "Esporta dati tracciato", None))
        self.btnExportBuilding.setText(_translate("MainWindow", "Esporta dati Edifici", None))
        self.btnStrataQgis.setText(_translate("MainWindow", "Esporta SHP strati", None))
        self.pushButton.setText(_translate("MainWindow", "Estrapola Grafici", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

