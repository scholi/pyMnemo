#!/usr/bin/python
# *-* encoding: utf-8 *-*

import sqlite3
import string

import sys
from PySide6.QtWidgets import QApplication, QWidget, QComboBox, QHBoxLayout
from PySide6.QtWidgets import QVBoxLayout, QLabel, QScrollArea, QInputDialog
from PySide6.QtWidgets import QProgressBar, QFrame, QLineEdit, QPushButton
from PySide6.QtCore import QObject, Qt

langs = {
    'French': dict(
        db='Lexique380.db',
        query="select ortho from lexique where mnemo=? order by ortho;",
        default="select nom from mnemo where mnemo=?;",
        mnemo="select mnemo from lexique where ortho=?;",
        update="insert or replace into mnemo (nom,mnemo) values (?,?);"),
    'English': dict(
        db='cmudict07b.db',
        query="select name from mnemo where mnemo=? order by name",
        default="select name from `default` where mnemo=?",
        mnemo="select mnemo from mnemo where name=?",
        update="insert or replace into `default` (name, mnemo) values (?,?);"),
    }
class shortestMnemo(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.conn = None
        self.c = None
        self.mnemoSeq = {x:[] for x in langs}
        self.initUI()
        
    def mnemonize(self):
        num = self.num.text()
        lang = self.lang.currentText()
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
        self.conn = sqlite3.connect(langs[lang]['db'])
        c = self.conn.cursor()
        
        self.pb.setMaximum(2**(len(num)-1))
        self.pb.setValue(0)
        self.pb.setStyleSheet('QProgressBar::chunk {background: blue;}')
        
        r = self.longestMnemo(num)
        m = len(min(r, key=len))
        self.v = {}
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(800)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollCont = QWidget(self.scroll)
        self.scroll.setWidget(self.scrollCont)
        self.vbox = QVBoxLayout()
        
        self.pb.setValue(0)
        self.pb.setStyleSheet('QProgressBar::chunk {background: green;}')
        self.pb.setMaximum(len(r)-1)
        
        for i, y in enumerate(r):
            self.pb.setValue(i)
            if len(y)-m<2:
                hboxH = QHBoxLayout()
                hbox = QHBoxLayout()
                for x in y:
                    L = QLabel(x)
                    if len(y) == m:
                        L.setStyleSheet("QLabel {color: red}")
                    hboxH.addWidget(L)
                    C = QComboBox()
                    c.execute(langs[lang]['query'], [x])
                    for s in c:
                        C.addItem(s[0])
                    c.execute(langs[lang]['default'], [x]);
                    r = c.fetchone()
                    if r != None:
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
        self.pb.setValue(0)
       
    def initUI(self):
        self.pb = QProgressBar()
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollCont = QFrame(self.scroll)
        self.scroll.setWidget(self.scrollCont)
        self.num = QLineEdit()
        self.Lnum = QLabel("Number")
        self.hnum = QHBoxLayout()
        self.hnum.addWidget(self.Lnum)
        self.hnum.addWidget(self.num)
        self.lang = QComboBox()
        self.lang.addItem("French")
        self.lang.addItem("English")
        self.Llang = QLabel("Language")
        self.hlang = QHBoxLayout()
        self.hlang.addWidget(self.Llang)
        self.hlang.addWidget(self.lang)
        self.btgo = QPushButton("Mnemonize")
        self.Vlayout = QVBoxLayout()
        self.Vlayout.addLayout(self.hnum)
        self.Vlayout.addLayout(self.hlang)
        self.Vlayout.addWidget(self.btgo)
        self.Vlayout.addWidget(self.pb)
        self.Vlayout.addWidget(self.scroll)
        self.setLayout(self.Vlayout)
        
        self.btgo.clicked.connect(self.mnemonize)
        self.num.returnPressed.connect(self.mnemonize)
        self.num.setFocus()
        self.show()

    def longestMnemo(self, num, lvl=[]):
        c = self.conn.cursor()
        lang = self.lang.currentText()
        res = []
        one = True
        if len(lvl) and lvl[-1]==1:
            one=False
        if len(num) in [1, 2]: # There is a solution for all numbers with 1 & 2 digits
            return [[num]]
            
        for i in range([2, 1][one], len(num)+1):
            L = lvl+[i]
            OK = i<3 or num[:i] in self.mnemoSeq[lang]
            if not OK:
                c.execute(langs[lang]['query'], [num[:i]])
                r = c.fetchone()
                if r != None:
                    OK = True
                    self.mnemoSeq[lang].append(num[:i])
            if OK:
                if i == len(num):
                    res.append([num])
                else:
                    for x in self.longestMnemo(num[i:], L):
                        R = [num[:i]]+x
                        if lvl == []:
                            V = [len(z) for z in R]
                            v = sum([2**(sum(V[j:])-1)-2**(sum(V[(j+1):])) for j in range(len(V))])
                            self.pb.setValue(v)
                        res.append(R)
        return res

    def updateMnemo(self):
        lang = self.lang.currentText()
        c = self.conn.cursor()
        sender = self.sender()
        c.execute(langs[lang]['mnemo'], [sender.currentText()])
        mnemo = c.fetchone()[0]
        c.execute(langs[lang]['update'], [sender.currentText(), mnemo])
        self.conn.commit()
        for x in self.v[mnemo]:
            x.setCurrentIndex(sender.currentIndex())
            x.setStyleSheet("background: none")

    def closeEvent(self, event):
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
        event.accept()
            
app = QApplication(sys.argv)
s = shortestMnemo()
sys.exit(app.exec_())
