import sqlite3
import string

import sys
from PyQt4 import QtGui, QtCore

conn = sqlite3.connect('Lexique380.db')
c = conn.cursor()


class shortestMnemo(QtGui.QWidget):
    def __init__(self, num):
        QtGui.QWidget.__init__(self)
        self.pb = QtGui.QProgressBar()
        self.scroll = QtGui.QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(1)
        self.scrollCont = QtGui.QFrame(self.scroll)
        self.scroll.setWidget(self.scrollCont)
        self.Vlayout = QtGui.QVBoxLayout()
        self.Vlayout.addWidget(self.pb)
        self.Vlayout.addWidget(self.scroll)
        self.setLayout(self.Vlayout)
        self.show()
        
        self.pb.setMaximum(2**(len(num)-1))
        self.mnemoSeq = []
        self.r = self.longestMnemo(num)
        self.mnemo = {}
        self.m = len(min(self.r, key=len))
        self.v = {}
        self.initUI()
        
    def longestMnemo(self, num, lvl=[]):
        res = []
        one = True
        if len(lvl) and lvl[-1]==1: one=False
        if len(num)==1:
            return [[num]]
        if len(num)==2:
            return [[num]]
        for i in range([2, 1][one], len(num)+1):
            L = lvl+[i]
            OK = i<3 or num[:i] in self.mnemoSeq
            if not OK:
                c.execute("select ortho from lexique where cgram='NOM' and mnemo=?;", [num[:i]])
                r = c.fetchone()
                if r!= None:
                    OK = True
                    self.mnemoSeq.append(num[:i])
            if OK:
                for x in self.longestMnemo(num[i:], L):
                        R = [num[:i]]+x
                        if lvl == []:
                            V = [len(z) for z in R]
                            v = sum([2**(sum(V[j:])-1)-2**(sum(V[(j+1):])) for j in range(len(V))])
                            self.pb.setValue(v)
                        res.append(R)
        return res


    def initUI(self):
        self.scroll.setFixedHeight(800)
        self.vbox = QtGui.QVBoxLayout(self.scrollCont)
        self.pb.setValue(0)
        self.pb.setMaximum(len(self.r)-1)
        self.pb.setStyleSheet('QProgressBar::chunk {background: blue;}')
        for i, y in enumerate(self.r):
            self.pb.setValue(i)
            if len(y)-self.m<2:
                hboxH = QtGui.QHBoxLayout()
                hbox = QtGui.QHBoxLayout()
                for x in y:
                    L = QtGui.QLabel(x)
                    if len(y) == self.m:
                        L.setStyleSheet("QLabel {color: red}")
                    hboxH.addWidget(L)
                    C = QtGui.QComboBox()
                    if x in self.mnemo:
                        for s in self.mnemo[x]['list']:
                                C.addItem(s)
                        if self.mnemo[x]['default'] != None:
                                C.setCurrentIndex(C.findText(self.mnemo[x]['default']))
                        else:
                                C.setStyleSheet("background: blue")
                    else:
                            c.execute("select ortho from lexique where cgram='NOM' and mnemo=? order by ortho;", [x])
                            self.mnemo[x] = {'default':None, 'list':[]}
                            for s in c:
                                self.mnemo[x]['list'].append(s[0])
                                C.addItem(s[0])
                            c.execute("select nom from mnemo where mnemo=?;", [x]);
                            r = c.fetchone()
                            if r != None:
                                self.mnemo[x]['default'] = r[0]
                                C.setCurrentIndex(C.findText(r[0]))
                            else:
                                C.setStyleSheet("background: blue")
                    C.activated.connect(self.updateMnemo)
                    if not x in self.v:
                        self.v[x] = []
                    self.v[x].append(C)
                    hbox.addWidget(C)
                self.vbox.addLayout(hboxH)
                self.vbox.addLayout(hbox)
        self.scrollCont.setLayout(self.vbox)
        self.Vlayout.removeWidget(self.pb)
        self.pb.deleteLater()
        self.setMinimumWidth(self.sizeHint().width())

    def updateMnemo(self):
            sender = self.sender()
            c.execute("select mnemo from lexique where ortho=?;", [str(sender.currentText().toUtf8()).decode('utf-8')])
            mnemo = c.fetchone()[0]
            c.execute("insert or replace into mnemo (nom,mnemo) values (?,?);",[str(sender.currentText().toUtf8()).decode('utf-8'),mnemo])
            conn.commit()
            for x in self.v[mnemo]:
                x.setCurrentIndex(sender.currentIndex())
                x.setStyleSheet("background: none")

app = QtGui.QApplication(sys.argv)
diag = QtGui.QWidget()
if len(sys.argv)<2:
    num, ok = QtGui.QInputDialog.getText(diag, 'Number', 'Enter the number you want to mnemonize:')
    if ok:
        s = shortestMnemo(str(num))
else:
    s=shortestMnemo(sys.argv[1])
sys.exit(app.exec_())
del s.window
conn.close()
