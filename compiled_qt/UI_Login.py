# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_Login.ui'
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

class Ui_Login(object):
    def setupUi(self, Login):
        Login.setObjectName(_fromUtf8("Login"))
        Login.resize(372, 115)
        self.gridLayout = QtGui.QGridLayout(Login)
        self.gridLayout.setMargin(11)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setMargin(11)
        self.formLayout.setSpacing(3)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(Login)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label)
        self.label_2 = QtGui.QLabel(Login)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_2)
        self.password = QtGui.QLineEdit(Login)
        self.password.setEnabled(True)
        self.password.setEchoMode(QtGui.QLineEdit.Password)
        self.password.setObjectName(_fromUtf8("password"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.password)
        self.user = QtGui.QLineEdit(Login)
        self.user.setObjectName(_fromUtf8("user"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.user)
        self.remoteAccess = QtGui.QCheckBox(Login)
        self.remoteAccess.setObjectName(_fromUtf8("remoteAccess"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.remoteAccess)
        self.gridLayout.addLayout(self.formLayout, 1, 0, 1, 1)
        self.loginButton = QtGui.QPushButton(Login)
        self.loginButton.setObjectName(_fromUtf8("loginButton"))
        self.gridLayout.addWidget(self.loginButton, 2, 0, 1, 1)

        self.retranslateUi(Login)
        QtCore.QMetaObject.connectSlotsByName(Login)
        Login.setTabOrder(self.user, self.password)
        Login.setTabOrder(self.password, self.loginButton)

    def retranslateUi(self, Login):
        Login.setWindowTitle(_translate("Login", "Login", None))
        self.label.setText(_translate("Login", "User", None))
        self.label_2.setText(_translate("Login", "Password", None))
        self.remoteAccess.setText(_translate("Login", "Remote Access (Non-VPN)", None))
        self.loginButton.setText(_translate("Login", "Login", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Login = QtGui.QWidget()
    ui = Ui_Login()
    ui.setupUi(Login)
    Login.show()
    sys.exit(app.exec_())

