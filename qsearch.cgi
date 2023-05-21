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
fp=open(rootdir+"/data/nonredundant/dimers_info.tsv")
lines=fp.read().splitlines()
fp.close()

fasta_dict=dict()
fp=open(rootdir+"/data/nonredundant/seqs.fasta")
for block in fp.read().split('>')[1:]:
    header,sequence=block.splitlines()
    fasta_dict[header.split()[0]]=sequence
fp.close()
if outfmt=='txt':
    print("Content-type: text/plain\n")
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

membership_dict=dict()
fp=open(rootdir+"/data/cluster/membership.tsv")
for line in fp.read().splitlines():
    dimer,seqclust,nonredundant=line.split('\t')
    if dimer==nonredundant:
        continue
    if not nonredundant in membership_dict:
        membership_dict[nonredundant]=[]
    membership_dict[nonredundant].append(dimer)
fp.close()

#### parse page ####
pageLimit=200
html_txt=''
sort_line=[]
for line in lines:
    items=line.split('\t')
    if len(items)<10:
        continue
    entryid    =items[0]
    #title      =items[1]
    accession  =items[2].strip()
    accession2 =items[3].strip()
    reso       =items[4]
    #method     =items[5]
    #contactnum =items[6]
    #seqid      =items[7]
    #species    =items[8]
    #species2   =items[9]
        
    chain1,chain2=entryid.split('_')
    pdb,assembly=chain1.split('-')[:2]
    if uniprot and accession!=uniprot and accession2!=uniprot:
        continue
    
    member_list=[]
    if entryid in membership_dict:
        member_list=membership_dict[entryid]
    if pdbid and pdb!=pdbid and sum(
        [dimer.split('-')[0]==pdbid for dimer in member_list])==0:
        continue

    seq1       =''
    seq2       =''
    if chain1 in fasta_dict:
        seq1   =fasta_dict[chain1]
    if chain2 in fasta_dict:
        seq2   =fasta_dict[chain2]
    L1         =str(len(seq1))
    L2         =str(len(seq2))
    items.append(L1)
    items.append(L2)
    items.append(' '.join(member_list))

    if ',' in reso:
        reso=reso.split(',')[0]
        items[4]=reso
    if reso=='':
        reso="NOT"
        items[4]=reso
    if reso=="NOT":
        reso=-1
    else:
        reso=float(reso)

    if outfmt=='txt':
        html_txt+='\t'.join(items)+'\t'+seq1+'\t'+seq2+'\n'
    else:
        if order=="reso":
            sort_line.append((reso,items))
        elif order=="uniprot":
            sort_line.append((accession+accession2,items))
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

    entryid    =items[0]
    title      =items[1]
    accession  =items[2].strip()
    accession2 =items[3].strip()
    reso       =items[4]
    method     =items[5]
    contactnum =items[6]
    seqid      =items[7]
    species    =items[8]
    species2   =items[9]
    L1         =items[10]
    L2         =items[11]
    member_list=items[12].split(' ')
    members    =''
    for i in range(int(len(member_list)/1)):
        members+='<br>'+' '.join(member_list[i:(i+1)])
    if len(members):
        members=members[4:]
    chain1,chain2=entryid.split('_')
    pdb,assembly=chain1.split('-')[:2]
    title=title.replace('"',"'")
    accession_list=["<a href=https://uniprot.org/uniprot/%s target=_blank>%s</a>"%(accession,accession)]
    if accession!=accession2:
        accession_list.append(
            "<a href=https://uniprot.org/uniprot/%s target=_blank>%s</a>"%(accession2,accession2))
    method=method.lower(
        ).replace('electron microscopy','EM'
        ).replace('solution nmr','NMR'
        ).replace('x-ray diffraction','X-ray')
    species_list=[species]
    if species!=species2:
        species_list.append(species)

    bgcolor=''
    if l%2:
        bgcolor='BGCOLOR="#DEDEDE"'

    html_txt+='''
<tr %s ALIGN=center>
    <td>%d</td>
    <td><a href=pdb.cgi?entryid=%s target=_blank>%s</a></td>
    <td><a href=https://www.rcsb.org/structure/%s target=_blank><span title="%s">%s</span></a></td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s/%s</td>
    <td>%s</td>
</tr>
'''%(bgcolor,
    l+1,
    entryid, entryid,
    pdb,title,pdb,
    '<br>'.join(accession_list),
    reso,
    method,
    contactnum,
    seqid,
    '<br>'.join(species_list),
    L1,L2,
    members,
    )

print('''
Download all results in tab-seperated text for 
<a href="?outfmt=txt&%s" download="database.txt">%d dimeric interactions</a>
(<a href=readme_database.txt>format explanation</a>)<br>
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


navigation_html='''<center> 
<a class='hover' href='?&page=1&%s'>&lt&lt</a>
<a class='hover' href='?&page=%d&%s'>&lt</a>
'''%(para,page-1,para)
for p in range(page-10,page+11):
    if p<1 or p>totalPage:
        continue
    elif p==page:
        navigation_html+=' %d '%(p)
    else:
        navigation_html+=''' <a class='hover' href='?&page=%d&%s'>%d</a> '''%(p,para,p)
navigation_html+='''
<a class='hover' href='?&page=%d&%s'>&gt</a>
<a class='hover' href='?&page=last&%s'>&gt&gt</a>
<form name="pform" action="qsearch.cgi">Go to page <select name="page" onchange="this.form.submit()">
'''%(page+1,para,para)
for p in range(1,totalPage+1):
    if p==page:
        navigation_html+='<option value="%d" selected="selected">%d</option>'%(p,p)
    else:
        navigation_html+='<option value="%d">%d</option>'%(p,p)
navigation_html+='''</select>
<input type=hidden name=pdbid   value='%s'>
<input type=hidden name=uniprot value='%s'>
</form></center><br>'''%(pdbid,uniprot)

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
    <th ALIGN=center><strong> Database<br>entry </strong></th>
    <th ALIGN=center><strong> PDB<br>ID </strong></th>
    <th ALIGN=center><strong> UniProt<br>accession </strong></th>
    <th ALIGN=center><strong> Resolution</strong></th>
    <th ALIGN=center><strong> Method</strong></th>
    <th ALIGN=center><strong> Contacts</strong></th>
    <th ALIGN=center><strong> Identity</strong></th>
    <th ALIGN=center><strong> Species</strong></th>
    <th ALIGN=center><strong> Length</strong></th>
    <th ALIGN=center><strong> Homologs with similar<br>sequences and structures</strong></th>
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
