#!/usr/bin/python
# *-* encoding: utf-8 *-*

import sqlite3
import string

import sys
from PyQt4 import QtGui, QtCore

conn = sqlite3.connect('Lexique380.db')
c = conn.cursor()


class shortestMnemo(QtGui.QWidget):
	def __init__(self,num):
		QtGui.QWidget.__init__(self)
		print "Loading..."
		self.r=self.longestMnemo(num)
		self.mnemo={}
		self.m=len(min(self.r,key=len))
		print "Done"
		self.v={}
		self.initUI()
		
	def longestMnemo(self, num, lvl=[]):
		res=[]
		one=True
		if len(lvl) and lvl[-1]==1: one=False
		if len(num)==1: return [[num]]
		if len(num)==2: return [[num]]
		for i in range([2,1][one],len(num)+1):
			print lvl+[i]
			if i>2:
				c.execute("select ortho from lexique where cgram='NOM' and mnemo=?;",[num[:i]])
				r=c.fetchone()
				if r!=None:
					for x in self.longestMnemo(num[i:],lvl+[i]):
						res.append([num[:i]]+x)
			else:
				for x in self.longestMnemo(num[i:],lvl+[i]):
						res.append([num[:i]]+x)
		return res


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
					if x in self.mnemo:
						for s in self.mnemo[x]['list']:
								C.addItem(s)
						if self.mnemo[x]['default']!=None:
								C.setCurrentIndex(C.findText(self.mnemo[x]['default']))
						else:
								C.setStyleSheet("background: blue")
					else:
							c.execute("select ortho from lexique where cgram='NOM' and mnemo=? order by ortho;",[x])
							self.mnemo[x]={'default':None,'list':[]}
							for s in c:
											self.mnemo[x]['list'].append(s[0])
											C.addItem(s[0])
							c.execute("select nom from mnemo where mnemo=?;",[x]);
							r=c.fetchone()
							if r!=None:
								self.mnemo[x]['default']=r[0]
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
			c.execute("select mnemo from lexique where ortho=?;",[str(sender.currentText().toUtf8()).decode('utf-8')])
			mnemo=c.fetchone()[0]
			c.execute("insert or replace into mnemo (nom,mnemo) values (?,?);",[str(sender.currentText().toUtf8()).decode('utf-8'),mnemo])
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
