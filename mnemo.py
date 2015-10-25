#!/usr/bin/python
# *-* encoding: utf-8 *-*

import sqlite3
import string

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea

conn = sqlite3.connect('Lexique380.db')
c = conn.cursor()

def longestMnemo(num):
	res=[]
	if len(num)==1: return [[num]]
	for i in range(1,len(num)+1):
		c.execute("select ortho from lexique where cgram='NOM' and mnemo=?;",[num[:i]])
		r=c.fetchone()
		if r!=None:
			for x in longestMnemo(num[i:]):
				res.append([num[:i]]+x)
	return res

def shortestMnemo(num):
	r=longestMnemo(num)
	m=len(min(r,key=len))
	app = QApplication(sys.argv)
	w = QWidget()
	scroll = QScrollArea()
	scroll.setWidget(w)
	scroll.setWidgetResizable(True)
	scroll.setFixedHeight(600)
	vbox = QVBoxLayout()
	for y in r:
		if len(y)-m<2:
			hboxH = QHBoxLayout()
			hbox = QHBoxLayout()
			for x in y:
				C=QComboBox()
				hboxH.addWidget(QLabel(x))
				c.execute("select ortho from lexique where cgram='NOM' and mnemo=?;",[x])
				for s in c:
					C.addItem(s[0])
				hbox.addWidget(C)
			vbox.addLayout(hboxH)
			vbox.addLayout(hbox)
	w.setLayout(vbox)
	scroll.show()
	sys.exit(app.exec_())

shortestMnemo(sys.argv[1])

conn.close()
