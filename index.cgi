#!/usr/bin/python3
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import os
import subprocess

rootdir=os.path.dirname(os.path.abspath(__file__))

html_header=""
html_footer=""
if os.path.isfile(rootdir+"/index.html"):
    fp=open(rootdir+"/index.html")
    txt=fp.read()
    fp.close()
    html_header=txt.split('<!-- CONTENT REFRESH START -->')[0]
    html_footer=txt.split('<!-- CONTENT REFRESH END -->')[-1]

print("Content-type: text/html\n")
if len(html_header):
   print(html_header)
else:
    print('''<html>
<head>
<title>Database</title>
</head>
<body bgcolor="#F0FFF0">
<p><a href=.>[Back to Home]</a></p>
''')

filename=rootdir+"/data/summary.txt"
if os.path.isfile(filename):
    LAST_UPDATE_UTC=""
    FULL_SET_NUM_CHAIN=""
    FULL_SET_NUM_DIMER=""
    NONRED_NUM_CHAIN=""
    NONRED_NUM_DIMER=""
    fp=open(filename,'r')
    for line in fp.read().splitlines():
        if line.startswith("LAST_UPDATE"):
            LAST_UPDATE_UTC=line.split()[1]
        elif line.startswith("FULL_SET_NUM_CHAIN"):
            FULL_SET_NUM_CHAIN=line.split()[-1]
        elif line.startswith("FULL_SET_NUM_DIMER"):
            FULL_SET_NUM_DIMER=line.split()[-1]
        elif line.startswith("NONRED_NUM_CHAIN"):
            NONRED_NUM_CHAIN=line.split()[-1]
        elif line.startswith("NONRED_NUM_DIMER"):
            NONRED_NUM_DIMER=line.split()[-1]
    fp.close()
    print('''
    The current database, which was updated on %s, contains a non-redundant set of
    <a href=qsearch.cgi>
    %s chains involved in %s homodimeric interactions</a>
    curated from all %s chains in %s homodimers from PDB.
    '''%(LAST_UPDATE_UTC,
        NONRED_NUM_CHAIN, NONRED_NUM_DIMER,
        FULL_SET_NUM_CHAIN, FULL_SET_NUM_DIMER,
    ))

cmd='ls -rt output/|grep -F .pdb.gz|cut -f1 -d.|tail -1'
p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
stdout,stderr=p.communicate()
entryid=stdout.decode().strip()
if len(entryid):
    print("<li><a href=pdb.cgi?entryid=%s>View an example entry</a></li>"%entryid)

if len(html_footer):
    print(html_footer)
else:
    print("</body> </html>")
