#!/usr/bin/python
# *-* encoding: utf-8 *-*

import sqlite3
import string

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea
from PyQt5.QtCore import QObject, pyqtSignal, Qt

conn = sqlite3.connect('Lexique380.db')
c = conn.cursor()

def longestMnemo(num, lvl=[]):
	res=[]
	if len(num)==1: return [[num]]
	for i in range(2,len(num)+1):
		print(lvl+[i])
		c.execute("select ortho from lexique where cgram='NOM' and mnemo=?;",[num[:i]])
		r=c.fetchone()
		if r!=None:
			for x in longestMnemo(num[i:],lvl+[i]):
				res.append([num[:i]]+x)
	return res

class shortestMnemo(QWidget):
	def __init__(self,num):
		QWidget.__init__(self)
		print("Loading...")
		self.r=longestMnemo(num)
		self.m=len(min(self.r,key=len))
		print("Done")
		self.v={}
		self.initUI()

	def initUI(self):
		self.scroll = QScrollArea(self)
		self.scroll.setWidgetResizable(True)
		self.scroll.setFixedHeight(800)
		self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.scrollCont = QWidget(self.scroll)
		self.scroll.setWidget(self.scrollCont)
		self.vbox = QVBoxLayout()
		for y in self.r:
			if len(y)-self.m<2:
				hboxH = QHBoxLayout()
				hbox = QHBoxLayout()
				for x in y:
					L=QLabel(x)
					if len(y)==self.m:
						L.setStyleSheet("QLabel {color: red}")
					hboxH.addWidget(L)
					C=QComboBox()
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
		v=QVBoxLayout()
		v.addWidget(self.scroll)
		self.setLayout(v)
		self.show()

	def updateMnemo(self):
			sender = self.sender()
			c.execute("select mnemo from lexique where ortho=?;",[sender.currentText()])
			mnemo=c.fetchone()[0]
			c.execute("insert or replace into mnemo (nom,mnemo) values (?,?);",[sender.currentText(),mnemo])
			conn.commit()
			for x in self.v[mnemo]:
				x.setCurrentIndex(sender.currentIndex())
				x.setStyleSheet("background: none")

app=QApplication(sys.argv)
s=shortestMnemo(sys.argv[1])
sys.exit(app.exec_())
conn.close()
