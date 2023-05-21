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
    html_header=txt.split('<!-- CONTENT START -->')[0]
    html_footer=txt.split('<!-- CONTENT END -->')[-1]

print("Content-type: text/html\n")
if len(html_header):
   print(html_header)
else:
    print('''<html>
<head>
<title>Download database</title>
</head>
<body bgcolor="#F0FFF0">
<p><a href=.>[Back to Home]</a></p>
''')

print('''
<h1>Download database</h1>
<li>Download all database entries: 
    <a href=qsearch.cgi?outfmt=txt download="database.txt">Table for detailed information of the dimers</a> 
    (<a href=readme_database.txt>format explanation</a>),
    <a href=data/nonredundant/seqs.fasta download>FASTA sequence of individual chains</a>
</li>
<li>Download sequence clusters:
    <a href=data/cluster/clusters.txt download>List of clusters</a>,
    <a href=data/cluster/membership.tsv download>Membership of the cluster</a>
</li>
<li>Download database entries further clustered down to more stringent sequence identity cutoffs:<br>
    &nbsp;&nbsp;&nbsp;&nbsp; 
    80% sequence identity cutoff:
    <a href=data/extra/cluster80_dimers.txt download>List of dimers</a>
    <a href=data/extra/cluster80_chains.txt download>List of individual chains</a>
    <a href=data/extra/cluster80_seqs.fasta download>FASTA sequence of individual chains</a><br>
    &nbsp;&nbsp;&nbsp;&nbsp; 
    70% sequence identity cutoff:
    <a href=data/extra/cluster70_dimers.txt download>List of dimers</a>
    <a href=data/extra/cluster70_chains.txt download>List of individual chains</a>
    <a href=data/extra/cluster70_seqs.fasta download>FASTA sequence of individual chains</a><br>
    &nbsp;&nbsp;&nbsp;&nbsp; 
    60% sequence identity cutoff:
    <a href=data/extra/cluster60_dimers.txt download>List of dimers</a>
    <a href=data/extra/cluster60_chains.txt download>List of individual chains</a>
    <a href=data/extra/cluster60_seqs.fasta download>FASTA sequence of individual chains</a><br>
    &nbsp;&nbsp;&nbsp;&nbsp; 
    50% sequence identity cutoff:
    <a href=data/extra/cluster50_dimers.txt download>List of dimers</a>
    <a href=data/extra/cluster50_chains.txt download>List of individual chains</a>
    <a href=data/extra/cluster50_seqs.fasta download>FASTA sequence of individual chains</a><br>
    &nbsp;&nbsp;&nbsp;&nbsp; 
    40% sequence identity cutoff:
    <a href=data/extra/cluster40_dimers.txt download>List of dimers</a>
    <a href=data/extra/cluster40_chains.txt download>List of individual chains</a>
    <a href=data/extra/cluster40_seqs.fasta download>FASTA sequence of individual chains</a><br>
    &nbsp;&nbsp;&nbsp;&nbsp; 
    30% sequence identity cutoff:
    <a href=data/extra/cluster30_dimers.txt download>List of dimers</a>
    <a href=data/extra/cluster30_chains.txt download>List of individual chains</a>
    <a href=data/extra/cluster30_seqs.fasta download>FASTA sequence of individual chains</a><br>
</li>

<li>Download PDB files for individual chains of all database entries:
(We provide <a href=download.sh download=download.sh>a script</a> to download all PDB files listed below. The script can be run by:
bash <a href=download.sh download=download.sh>download.sh</a>)
<ul>
<table>
''')

cmd='ls data/pdb/div/|grep -F .tar.gz'
p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
stdout,stderr=p.communicate()
for line in stdout.decode().splitlines():
    print("<tr><td><a href=data/pdb/div/%s>%s</a></td></tr>"%(line,line))
print('''
</ul>
</table>
</li>

<p></p>
<p><a href=.>[Back to Home]</a></p>
''')

if len(html_footer):
    print(html_footer)
else:
    print("</body> </html>")
