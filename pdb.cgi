#!/usr/bin/python3
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import os
import gzip
import subprocess
import textwrap
import tarfile
import gzip
import re

rootdir=os.path.dirname(os.path.abspath(__file__))

def display_dimer(entryid):
    print('''
<tr><td><h1 align=center>$entryid</h1></td></tr>
'''.replace("$entryid",entryid))

    chain1,chain2=entryid.split('_')
    pdbid,assemblyid,modelid1,chainid1=chain1.split('-')
    pdbid,assemblyid,modelid2,chainid2=chain2.split('-')
    assemblyid=assemblyid[1:]
    modelid1  =modelid1[1:]
    chainid1  =chainid1[1:]
    modelid2  =modelid2[1:]
    chainid2  =chainid2[1:]
    divided   =pdbid[-3:-1]
    
    filename = rootdir+"/output/"+entryid+".pdb.gz"
    if not os.path.isfile(filename):
        pdbtxt=''
        tar = tarfile.open(rootdir+"/data/pdb/div/"+divided+".tar.gz", "r:gz")
        for c,chain in enumerate([chain1,chain2]):
            extract_filename = divided+"/"+chain+".pdb"
            if not extract_filename in tar.getnames():
                print("ERROR! No "+extract_filename1)
                return
            chainid='A'
            if c==1:
                chainid='B'
            fin  = tar.extractfile(extract_filename)
            for line in fin.read().decode().splitlines():
                if line.startswith('END'):
                    continue
                elif line.startswith('TER'):
                    pdbtxt+=line+'\n'
                elif line.startswith('ATOM  ') or line.startswith('HETATM'):
                    pdbtxt+=line[:21]+chainid+line[22:]+'\n'
            fin.close()
        tar.close()
        pdbtxt+='END\n'
        fp=gzip.open(filename,'wt')
        fp.write(pdbtxt)
        fp.close()


    sequence1=''
    sequence2=''
    cmd="zcat "+filename+"|"+rootdir+"/script/pdb2fasta -"
    p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout,stderr=p.communicate()
    print(stderr.decode())

    items = stdout.decode().splitlines()
    if len(items)!=4:
        print("ERROR! pdb2fasta <br>"+stdout.decode())
        return
    sequence1=items[1]
    sequence2=items[3]

    print('''
<tr><td>
<div id="headerDiv">
    <div id="titleText">Sequences</div>
</div>
<div style="clear:both;"></div>
<div id="contentDiv">
    <div id="RContent" style="display: block;">
    <table width=100% border="0" style="font-family:Monospace;font-size:14px;background:#F2F2F2;" >
    <tr><td><font color=blue>&gt;$chain1 (length=$L1) [<a href=ssearch.cgi?sequence=$sequence1 target=_blank>Search sequence</a>]</font></td></tr>
    <tr><td><span title="Only residues with experimentally determined coordinates are included. Residues unobserved in the structure are excluded."><font color=blue>$seq_txt1</font></span></td></tr>
    <tr><td><font color=red>&gt;$chain2 (length=$L2) [<a href=ssearch.cgi?sequence=$sequence2 target=_blank>Search sequence</a>]</font></td></tr>
    <tr><td><span title="Only residues with experimentally determined coordinates are included. Residues unobserved in the structure are excluded."><font color=red>$seq_txt2</font></span></td></tr>
    </table>
</div>
</td></tr>
'''.replace("$pdbid",pdbid
  ).replace("$assemblyid",assemblyid
  ).replace("$chain1",chain1
  ).replace("$chain2",chain2
  ).replace("$L1",str(len(sequence1))
  ).replace("$L2",str(len(sequence2))
  ).replace("$sequence1",sequence1
  ).replace("$sequence2",sequence2
  ).replace("$seq_txt1",'<br>'.join(textwrap.wrap(sequence1,60))
  ).replace("$seq_txt2",'<br>'.join(textwrap.wrap(sequence2,60))
  ))

    print('''
<tr><td>
<div id="headerDiv">
    <div id="titleText">3D structure</div>
</div>
<div style="clear:both;"></div>
<div id="contentDiv">
    <div id="RContent" style="display: block;">
    <table width=100% border="0" style="font-family:Monospace;font-size:14px;background:#F2F2F2;" >
    <tr><td>

<script type="text/javascript"> 
$(document).ready(function()
{
    Info = {
        width: 600,
        height: 600,
        j2sPath: "jsmol/j2s",
        script: "load output/$basename; color background black; cartoons; spacefill off; wireframe off; select :A; color blue; select :B; color red; spacefill off; wireframe off; "
    }
    $("#mydiv").html(Jmol.getAppletHtml("jmolApplet0",Info))
});
</script>
<span id=mydiv></span>
    </td></tr><tr><td>
    <table>
    <tr><td>Color:</td><td>
        [<a href="javascript:Jmol.script(jmolApplet0, 'select :A; color blue; select :B; color red;')">By chain</a>] &nbsp;
        [<a href="javascript:Jmol.script(jmolApplet0, 'select :A or :B; color group')">By residue index</a>] &nbsp;
    </td></tr>
    <tr><td>Spin:</td><td>
        [<a href="javascript:Jmol.script(jmolApplet0, 'spin off')">Spin off</a>] &nbsp;
        [<a href="javascript:Jmol.script(jmolApplet0, 'spin on')">Spin on</a>] &nbsp;
        [<a href="javascript:Jmol.script(jmolApplet0, 'Reset')">Reset</a>]
    </td></tr>
    <tr><td>Render:</td><td>
        [<a href="javascript:Jmol.script(jmolApplet0, 'set antialiasDisplay false')">Low quality</a>] &nbsp;
        [<a href="javascript:Jmol.script(jmolApplet0, 'set antialiasDisplay true')">High quality</a>] &nbsp;
    </td></tr>
    <tr><td>Background:</td><td>
        [<a href="javascript:Jmol.script(jmolApplet0, 'color background black')">Black quality</a>] &nbsp; 
        [<a href="javascript:Jmol.script(jmolApplet0, 'color background white')">White quality</a>] &nbsp;
    </td></tr>
    <tr><td>Download:</td><td>
        <a href=output/$basename download>$basename</a>
    </td></tr>
    </table>
    </td></tr>
    </table>
</div>
</td></tr>
'''.replace( "$basename",os.path.basename(filename)))

    return 

if __name__=="__main__":
    form   =cgi.FieldStorage()
    entryid=form.getfirst("entryid",'')
    

    print("Content-type: text/html\n")
    print('''<html>
<head>
<link rel="stylesheet" type="text/css" href="page.css" />
<title>'''+entryid+'''</title>
</head>
<body bgcolor="#F0FFF0">
<script type="text/javascript" src="jsmol/JSmol.min.js"></script>
<table style="table-layout:fixed;" width="100%" cellpadding="2" cellspacing="0">
<table width=100%>
''')
    

    if '_' in entryid:
        display_dimer(entryid)
    
    print('''</table>
<p></p>
[<a href=.>Back to Home</a>]
</body> </html>''')
