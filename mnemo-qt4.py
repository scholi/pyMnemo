#!/usr/bin/python
# *-* encoding: utf-8 *-*

import sqlite3
import string

import sys
from PyQt4 import QtGui, QtCore

conn = sqlite3.connect('Lexique380.db')
c = conn.cursor()

def longestMnemo(num, lvl=[]):
	res=[]
	if len(num)==1: return [[num]]
	if len(num)==0: return [[]]
	for i in range(2,len(num)+1):
		print lvl+[i]
		c.execute("select ortho from lexique where cgram='NOM' and mnemo=?;",[num[:i]])
		r=c.fetchone()
		if r!=None:
			for x in longestMnemo(num[i:],lvl+[i]):
				res.append([num[:i]]+x)
	return res

class shortestMnemo(QtGui.QWidget):
	def __init__(self,num):
		QtGui.QWidget.__init__(self)
		print "Loading..."
		self.r=longestMnemo(num)
		self.m=len(min(self.r,key=len))
		print "Done"
		self.v={}
		self.initUI()

	def initUI(self):
		self.scroll = QtGui.QScrollArea(self)
		self.scroll.setWidgetResizable(True)
		self.scroll.setFixedHeight(800)
		self.scroll.setHorizontalScrollBarPolicy(1)
		self.scrollCont = QtGui.QWidget(self.scroll)
		self.scroll.setWidget(self.scrollCont)
		self.vbox = QtGui.QVBoxLayout()
		for y in self.r:
			if len(y)-self.m<2:
				hboxH = QtGui.QHBoxLayout()
				hbox = QtGui.QHBoxLayout()
				for x in y:
					L=QtGui.QLabel(x)
					if len(y)==self.m:
						L.setStyleSheet("QLabel {color: red}")
					hboxH.addWidget(L)
					C=QtGui.QComboBox()
					c.execute("select ortho from lexique where cgram='NOM' and mnemo=? order by ortho;",[x])
					for s in c:
						C.addItem(s[0])
					c.execute("select nom from mnemo where mnemo=?;",[x]);
					r=c.fetchone()
					if r!=None:
						C.setCurrentIndex(C.findText(r[0]))
					else:
						C.setStyleSheet("background: blue")
					C.activated.connect(self.updateMnemo)
					if not x in self.v:
						self.v[x]=[]
					self.v[x].append(C)
					hbox.addWidget(C)
				self.vbox.addLayout(hboxH)
				self.vbox.addLayout(hbox)
		self.scrollCont.setLayout(self.vbox)
		v=QtGui.QVBoxLayout()
		v.addWidget(self.scroll)
		self.setLayout(v)
		self.show()

	def updateMnemo(self):
			sender = self.sender()
			c.execute("select mnemo from lexique where ortho=?;",[str(sender.currentText())])
			mnemo=c.fetchone()[0]
			c.execute("insert or replace into mnemo (nom,mnemo) values (?,?);",[str(sender.currentText()),mnemo])
			conn.commit()
			for x in self.v[mnemo]:
				x.setCurrentIndex(sender.currentIndex())
				x.setStyleSheet("background: none")

app=QtGui.QApplication(sys.argv)
diag=QtGui.QWidget()
if len(sys.argv)<2:
	num, ok = QtGui.QInputDialog.getText(diag,'Number', 'Enter the number you want to mnemonize:')
	if ok: s=shortestMnemo(str(num))
else:
	s=shortestMnemo(sys.argv[1])
sys.exit(app.exec_())
conn.close()
