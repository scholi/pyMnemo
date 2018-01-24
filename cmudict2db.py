import sqlite3

filename = "cmudict-0.7b"

d = {'Z':0,
     'S':0,
     'T':1,
     'D':1,
     'TH':1,
     'DH':1,
     'N':2,
     'M':3,
     'R':4,
     'ER1':4,
     'ER0':4,
     'L':5,
     'CH':6,
     'SH':6,
     'JH':6,
     'ZH':6,
     'K':7,
     'G':7,
     'V':8,
     'F':8,
     'B':9,
     'P':9,
     'NG':27}

conn = sqlite3.connect('cmudict07b.db')
c = conn.cursor()
c.execute("CREATE TABLE mnemo (name text, phonem text, mnemo text)")

with open(filename, 'r') as f:
    for line in f:
        line = line.strip().split()
        if line[0].startswith(';;;'):
            continue
        name = line[0].lower()
        phonems = ' '.join(line[1:])
        mnemo = ''.join([str(d[x]) for x in line[1:] if x in d])
        c.execute("INSERT INTO mnemo VALUES (?,?,?)", (name, phonems, mnemo) )
conn.commit()
conn.close()
