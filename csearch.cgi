#!/usr/bin/python3
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import os
import gzip
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

#### read cgi parameters ####

form = cgi.FieldStorage()
page =form.getfirst("page",'').strip().strip("'")
if not page:
    page='1'
elif page=='0':
    page='1'

#### read database data ####
print("Content-type: text/html\n")
if len(html_header):
    print(html_header)
else:
    print('''<html>
<head>
<link rel="stylesheet" type="text/css" href="page.css" />
<title>Database</title>
</head>
<body bgcolor="#F0FFF0">
<p><a href=.>[Back to Home]</a></p>
''')
print('''
This page describes membership of homodimers to sequence and structure clusters. The
database is built by first clustering by sequence and then by structural clustering within each
sequence cluster. As a result, one sequence cluster may include multiple structure clusters, while
each structural cluster may include multiple homodimers.
Homodimers that share membership to one structure cluster therefore exhibit both sequence and
structure similarity, while homodimers that have membership in different structure clusters but
the same sequence structure would exhibit sequence similarity but distinct structures.
''')

membership_dict=dict()
fp=open(rootdir+"/data/cluster/membership.tsv")
for line in fp.read().splitlines():
    dimer,seqclust,nonredundant=line.split('\t')
    if not seqclust in membership_dict:
        membership_dict[seqclust]=dict()
    if not nonredundant in membership_dict[seqclust]:
        membership_dict[seqclust][nonredundant]=[]
    membership_dict[seqclust][nonredundant].append(dimer)
fp.close()

#### parse page ####
pageLimit=200
totalPage=1+int(len(membership_dict)/pageLimit)
if not page:
    page=1
elif page=="last":
    page=totalPage
else:
    page=int(page)
if page<1:
    page=1
elif page>totalPage:
    page=totalPage

html_txt=''
for l,seqclust in enumerate(sorted(membership_dict.keys())):
    if l<pageLimit*(int(page)-1) or l>=pageLimit*(int(page)):
        continue
    members=''
    for nonredundant in sorted(membership_dict[seqclust].keys()):
        chain1,chain2=nonredundant.split('_')
        pdb,assembly,modelID1,chainID1=chain1.split('-')
        pdb,assembly,modelID2,chainID2=chain2.split('-')
        shortid='/'.join([pdb,assembly[1:],
            modelID1[1:]+':'+chainID1[1:],
            modelID2[1:]+':'+chainID2[1:]])
        members+='''<li><a href=pdb.cgi?entryid=$entryid>$shortid</a>:
        '''.replace('$entryid',nonredundant).replace('$shortid',shortid)
        for dimer in membership_dict[seqclust][nonredundant]:
            if dimer!=nonredundant:
                chain1,chain2=dimer.split('_')
                pdb,assembly,modelID1,chainID1=chain1.split('-')
                pdb,assembly,modelID2,chainID2=chain2.split('-')
                shortid='/'.join([pdb,assembly[1:],
                    modelID1[1:]+':'+chainID1[1:],
                    modelID2[1:]+':'+chainID2[1:]])
                #members+=dimer+'; '
                members+=shortid+'; '
        members+="</li>\n"

    chain1,chain2=seqclust.split('_')
    pdb,assembly,modelID1,chainID1=chain1.split('-')
    pdb,assembly,modelID2,chainID2=chain2.split('-')
    shortid='/'.join([pdb,assembly[1:],
        modelID1[1:]+':'+chainID1[1:],
        modelID2[1:]+':'+chainID2[1:]])

    bgcolor=''
    if l%2:
        bgcolor='BGCOLOR="#DEDEDE"'

    html_txt+='''
<tr %s ALIGN=center>
    <td>%d</td>
    <td>%s</td>
    <td>%s</td>
</tr>
'''%(bgcolor,
    l+1,
    shortid,#seqclust,
    members,
    )


navigation_html='''<center> 
<a class='hover' href='?&page=1'>&lt&lt</a>
<a class='hover' href='?&page=%d'>&lt</a>
'''%(page-1)
for p in range(page-10,page+11):
    if p<1 or p>totalPage:
        continue
    elif p==page:
        navigation_html+=' %d '%(p)
    else:
        navigation_html+=''' <a class='hover' href='?&page=%d'>%d</a> '''%(p,p)
navigation_html+='''
<a class='hover' href='?&page=%d'>&gt</a>
<a class='hover' href='?&page=last'>&gt&gt</a>
<form name="pform" action="csearch.cgi">Go to page <select name="page" onchange="this.form.submit()">
'''%(page+1)
for p in range(1,totalPage+1):
    if p==page:
        navigation_html+='<option value="%d" selected="selected">%d</option>'%(p,p)
    else:
        navigation_html+='<option value="%d">%d</option>'%(p,p)
navigation_html+='''</select>
</form></center><br>'''

print(navigation_html)
print('''
<style>
div.w {
  word-wrap: break-word;
}
</style>

<table border="0" align=center width=100%>    
<tr BGCOLOR="#FF9900">
    <th ALIGN=center><strong> # </strong></th>
    <th ALIGN=center><strong> Sequence cluster </strong></th>
    <th ALIGN=center><strong> Cluster members </strong></th>
</tr><tr ALIGN=center>
''')
print(html_txt)
print("</table>")
print(navigation_html)
print("[<a href=.>Back to Home</a>]")
if len(html_footer):
    print(html_footer)
else:
    print("</body> </html>")
