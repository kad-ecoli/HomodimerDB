#!/usr/bin/python3
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import os
import gzip
import subprocess
import textwrap

rootdir=os.path.dirname(os.path.abspath(__file__))

html_header=""
html_footer=""
if os.path.isfile(rootdir+"/index.html"):
    fp=open(rootdir+"/index.html")
    txt=fp.read()
    fp.close()
    html_header=txt.split('<!-- CONTENT START -->')[0]
    html_footer=txt.split('<!-- CONTENT END -->')[-1]

def ExitWithError(msg,html_footer):
    print("ERROR!")
    print(msg)
    print("<p></p><a href=.>[Back]</a>")
    if len(html_footer):
        print(html_footer)
    else:
        print("</body> </html>")
    exit()

#### read cgi parameters ####

form = cgi.FieldStorage()
sequence=form.getfirst("sequence",'').strip()

print("Content-type: text/html\n")
if len(html_header):
    print(html_header)
else:
    print('''<html>
<head>
<link rel="stylesheet" type="text/css" href="page.css" />
<title>Sequence search</title>
</head>
<body bgcolor="#F0FFF0">
<p><a href=.>[Back to Home]</a></p>
''')
header="protein"
txt=''
for line in sequence.splitlines():
    line=line.strip()
    if line.startswith('>'):
        if header[0]=='>':
            print("ERROR! only one sequence allowed per search")
            exit()
        else:
            header=line
    else:
        txt+=line.upper()
sequence=txt
if header[0]=='>':
    header=header[1:]
if len(set(txt).difference(set("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))):
    ExitWithError("Unknown residue type "+' '.join(set(txt
        ).difference(set("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))),html_footer)
if len(sequence)>1500:
    ExitWithError("Unable to handle sequence with %d &gt; 1500 residues"%len(sequence),html_footer)
print('&gt;'+header+'<br>')
print('<br>'.join(textwrap.wrap(sequence,60))+'<p></p>')

cmd="echo %s|%s/script/blastp -db %s/data/nonredundant/seqs.fasta -max_target_seqs 1000 -outfmt '6 sacc slen evalue nident length' "%(sequence,rootdir,rootdir)
score_name="E-value"
p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
stdout,stderr=p.communicate()
lines=stdout.decode().splitlines()
print('''
<table border="0" align=center width=100%>    
<tr BGCOLOR="#FF9900">
    <th ALIGN=center><strong> # </strong></th>
    <th ALIGN=center><strong> Hit </strong></th>
    <th ALIGN=center><strong> Hit<br>length </strong></th>
    <th ALIGN=center><strong> Aligned<br>length </strong></th>
    <th ALIGN=center><strong> Identity<br>(normalized by query)</strong> </th>           
    <th ALIGN=center><strong> Identity<br>(normalized by hit)</strong> </th>           
    <th ALIGN=center><strong> Identity (normalized<br>by aligned length)</strong> </th>           
    <th ALIGN=center><strong> '''+score_name+ '''</strong> </th>           
    <th ALIGN=center><strong> Dimers </strong> </th>           
</tr><tr ALIGN=center>
''')

dimer_dict=dict()
fp=open(rootdir+"/data/nonredundant/dimers.txt")
for line in fp.read().splitlines():
    entryid=line.strip()
    chain1,chain2=entryid.split('_')
    if not chain1 in dimer_dict:
        dimer_dict[chain1]=[]
    if not chain2 in dimer_dict:
        dimer_dict[chain2]=[]
    dimer_dict[chain1].append(entryid)
    dimer_dict[chain2].append(entryid)

fp.close()

totalNum=0
sacc_list=[]
for line in lines:
    sacc,slen,evalue,nident,Lali=line.split('\t')
    if sacc in sacc_list:
        continue
    totalNum+=1
    bgcolor=''
    if totalNum%2==0:
        bgcolor='BGCOLOR="#DEDEDE"'
    slen=int(slen)
    nident=float(nident)
    Lali=int(Lali)
    dimer_list=[]
    if sacc in dimer_dict:
        for entryid in dimer_dict[sacc]:
            dimer_list.append("<a href=pdb.cgi?entryid=%s target=_blank>%s</a>"%(entryid,entryid))
    print('''
<tr %s ALIGN=center>
    <td>%d</td>
    <td>%s</td>
    <td>%d</td>
    <td>%d</td>
    <td>%.4f</td>
    <td>%.4f</td>
    <td>%.4f</td>
    <td>%s</td>
    <td>%s</td>
</tr>
'''%(bgcolor,
    totalNum,
    sacc,
    slen,
    Lali,
    nident/len(sequence),
    nident/slen, 
    nident/Lali,
    evalue,
    ', '.join(dimer_list)))
print("</table><p></p><a href=.>[Back]</a>")
if len(html_footer):
    print(html_footer)
else:
    print("</body> </html>")
