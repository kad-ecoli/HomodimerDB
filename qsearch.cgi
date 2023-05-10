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
order=form.getfirst("order",'').lower().strip().strip("'")
if not order:
    order="pdbid"
pdbid=form.getfirst("pdbid",'').lower().strip().strip("'")
uniprot=form.getfirst("uniprot",'').upper().strip().strip("'")
outfmt =form.getfirst("outfmt",'').strip().strip("'")

para_list=[]
if order:
    para_list.append("order=%s"%order)
if pdbid:
    para_list.append("pdbid=%s"%pdbid)
if uniprot:
    para_list.append("uniprot=%s"%uniprot)
para='&'.join(para_list)

#### read database data ####
fp=open(rootdir+"/data/nonredundant/dimers.txt")
dimer_list=fp.read().splitlines()
if pdbid:
    dimer_list=[dimer for dimer in dimer_list if dimer.startswith(pdbid+'-')]
fp.close()

fasta_dict=dict()
if outfmt=='txt':
    print("Content-type: text/plain\n")
    fp=open(rootdir+"/data/nonredundant/seq.fasta")
    for block in fp.read().split('>')[1:]:
        header,sequence=block.splitlines()
        fasta_dict[header.split()[0]]=sequence
    fp.close()
else:
    
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

#### parse page ####
pageLimit=200
html_txt=''
sort_line=[]
for entryid in dimer_list:
    chain1,chain2=entryid.split('_')
    pdb,assembly=chain1.split('-')[:2]

    reso = ''
    accession = ''
    
    items=(entryid,pdb,assembly[1:])
    if outfmt=='txt':
        html_txt+='\t'.join(items)+'\t'+fasta_dict[chain1]+ \
                                   '\t'+fasta_dict[chain2]+'\n'
    else:
        if order=="reso":
            sort_line.append((reso,items))
        elif order=="uniprot":
            sort_line.append((accession,items))
        else:
            sort_line.append((entryid,items))

if outfmt=="txt":
    #print("Content-type: text/plain\n")
    print(html_txt)
    exit()

sort_line.sort()
totalNum=len(sort_line)
totalPage=1+int(totalNum/pageLimit)
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

for l in range(totalNum):
    if l<pageLimit*(int(page)-1) or l>=pageLimit*(int(page)):
        continue
    items   =sort_line[l][1]

    entryid = items[0]
    pdb     = items[1]
    assembly= items[2]

    bgcolor=''
    if l%2:
        bgcolor='BGCOLOR="#DEDEDE"'
    html_txt+='''
<tr %s ALIGN=center>
    <td>%d</td>
    <td><a href=pdb.cgi?entryid=%s target=_blank>%s</a></td>
    <td><a href=https://www.rcsb.org/structure/%s target=_blank>%s</a></td>
    <td>%s</td>
</tr>
'''%(bgcolor,
    l+1,
    entryid, entryid,
    pdb,pdb,
    assembly
    )
fp.close()

print('''
Download all results in tab-seperated text for 
<a href="?outfmt=txt&%s" download="database.txt">%d dimeric interactions</a><br>
'''%(para,totalNum))

print(('''<p></p>
<form name="sform" action="qsearch.cgi">
Sort results by
<select name="order" onchange="this.form.submit()">
    <option value="pdbid">PDB ID</option>
    <option value="uniprot">UniProt ID</option>
    <option value="reso">Resolution</option>
<input type=hidden name=pdbid   value='%s'>
<input type=hidden name=uniprot value='%s'>
</form>'''%(pdbid,uniprot)
).replace('value="%s"'%order,
          'value="%s" selected="selected"'%order))


print('''<center> 
<a class='hover' href='?&page=1&%s'>&lt&lt</a>
<a class='hover' href='?&page=%d&%s'>&lt</a>
'''%(para,page-1,para))
for p in range(page-10,page+11):
    if p<1 or p>totalPage:
        continue
    elif p==page:
        print(' %d '%(p))
    else:
        print('''<a class='hover' href='?&page=%d&%s'>%d</a>'''%(p,para,p))
print('''
<a class='hover' href='?&page=%d&%s'>&gt</a>
<a class='hover' href='?&page=last&%s'>&gt&gt</a>
<form name="pform" action="qsearch.cgi">Go to page <select name="page" onchange="this.form.submit()">
'''%(page+1,para,para))
for p in range(1,totalPage+1):
    if p==page:
        print('<option value="%d" selected="selected">%d</option>'%(p,p))
    else:
        print('<option value="%d">%d</option>'%(p,p))
print('''</select>
<input type=hidden name=pdbid   value='%s'>
<input type=hidden name=uniprot value='%s'>
</form></center><br>'''%(pdbid,uniprot))


print('''
<style>
div.w {
  word-wrap: break-word;
}
</style>

<table border="0" align=center width=100%>    
<tr BGCOLOR="#FF9900">
    <th ALIGN=center><strong> # </strong></th>
    <th ALIGN=center><strong> Database entry </strong></th>
    <th ALIGN=center><strong> PDB ID </strong></th>
    <th ALIGN=center><strong> Assembly ID </strong></th>
</tr><tr ALIGN=center>
''')
print(html_txt)
print("</table>")
print("[<a href=.>Back to Home</a>]")
if len(html_footer):
    print(html_footer)
else:
    print("</body> </html>")
