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

def display_dimer(entryid,viewer):
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
    
    #### display sequence ####
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
    <tr><td><font color=red>&gt;$chain1 (length=$L1) [<a href=ssearch.cgi?sequence=$sequence1 target=_blank>Search sequence</a>]</font></td></tr>
    <tr><td><span title="Only residues with experimentally determined coordinates are included. Residues unobserved in the structure are excluded."><font color=red>$seq_txt1</font></span></td></tr>
    <tr><td><font color=blue>&gt;$chain2 (length=$L2) [<a href=ssearch.cgi?sequence=$sequence2 target=_blank>Search sequence</a>]</font></td></tr>
    <tr><td><span title="Only residues with experimentally determined coordinates are included. Residues unobserved in the structure are excluded."><font color=blue>$seq_txt2</font></span></td></tr>
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

    #### structure information ####
    title      =""
    accession1 =""
    accession2 =""
    reso       =""
    method     =""
    contactnum =""
    seqid      =""
    species1   =""
    species2   =""
    fp=open("data/nonredundant/dimers_info.tsv")
    for line in fp.read().splitlines():
        if not line.startswith(entryid):
            continue
        items=line.split('\t')
        if entryid!=items[0] or len(items)<=9:
            continue
        title      =items[1]
        accession1 =items[2]
        accession2 =items[3]
        reso       =items[4]
        method     =items[5]
        contactnum =items[6]
        seqid      =items[7]
        species1   =items[8]
        species2   =items[9]

        if species1:
            taxonid1=species1.split()[0]
            species1="<a href=https://ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id="+taxonid1+">"+taxonid1+"</a>"+species1[(len(taxonid1)):]
        if species2:
            taxonid2=species2.split()[0]
            species2="<a href=https://ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id="+taxonid2+">"+taxonid2+"</a>"+species2[(len(taxonid2)):]
        if reso=='NOT':
            reso="Not applicable"
        elif reso:
            reso+="&#8491;"
    fp.close()
    
    BioLiP_html=""
    pubmed_html=""
    if os.path.isfile("../BioLiP/data/pdb_all.tsv.gz"):
        BioLiP_dict=dict()
        fp=gzip.open("../BioLiP/data/pdb_all.tsv.gz",'rt')
        for line in fp.read().splitlines():
            if not line.startswith(pdbid+'\t'):
                continue
            items=line.split('\t')
            #pdb    chain   resolution      csa     csa(Renumbered) ec      go      uniprot pubmed
            if items[1]!=chainid1 and items[1]!=chainid2:
                continue
            chainid=items[1]
            ec=items[5]
            go=items[6]
            pubmed=items[8]
            BioLiP_dict[pdbid+chainid]=[ec,go]
            pubmed_html='''
    <tr align=center>
        <td><b>PubMed citation</b></td>
        <td><a href=https://pubmed.ncbi.nlm.nih.gov/$pubmed target=_blank>$pubmed</a></td>
    </tr>
    '''.replace("$pubmed",pubmed)
        fp.close()
        if len(BioLiP_dict):
            BioLiP1=''
            BioLiP2=''
            if pdbid+chainid1 in BioLiP_dict:
                BioLiP1='''
        <td><font color=red>BioLiP:<a href="../BioLiP/pdb.cgi?pdb=$pdbid&chain=$chainid1" 
            target=_blank>$pdbid$chainid1</a></font></td>
            '''.replace("$pdbid",pdbid).replace("$chainid1",chainid1)
            if pdbid+chainid2 in BioLiP_dict:
                BioLiP2='''
        <td><font color=blue>BioLiP:<a href="../BioLiP/pdb.cgi?pdb=$pdbid&chain=$chainid2" 
            target=_blank>$pdbid$chainid2</a></font></td>
            '''.replace("$pdbid",pdbid).replace("$chainid2",chainid2)
            BioLiP_html+='''
    <tr align=center>
        <td><b>Function annotation</b></td> $BioLiP1 $BioLiP2
    </tr>
    '''.replace("$BioLiP1",BioLiP1).replace("$BioLiP2",BioLiP2)

    print('''
<tr><td>
<div id="headerDiv">
    <div id="titleText">Structure information</div>
</div>
<div style="clear:both;"></div>
<div id="contentDiv">
    <div id="RContent" style="display: block;">
    <table border="0" style="font-family:Monospace;font-size:14px;background:#F2F2F2;" >
    <tr bgcolor="#DEDEDE" align=center>
        <td><b>PDB ID</b></td>
        <td>$pdbid (database links:
            <a href=https://rcsb.org/structure/$pdbid target=_blank>RCSB PDB</a>
            <a href=https://ebi.ac.uk/pdbe/entry/pdb/$pdbid target=_blank>PDBe</a>
            <a href=https://pdbj.org/mine/summary/$pdbid target=_blank>PDBj</a>
            <a href=http://ebi.ac.uk/pdbsum/$pdbid target=_blank>PDBsum</a>)</td>
    </tr>
    <tr align=center>
        <td><b>Title</b></td>
        <td>$title</td>
    </tr>
    <tr bgcolor="#DEDEDE" align=center>
        <td><b>Assembly ID</b></td>
        <td>$assemblyid</td>
    </tr>
    <tr align=center>
        <td><b>Resolution</b></td>
        <td>$reso</td>
    </tr>
    <tr bgcolor="#DEDEDE" align=center>
        <td><b>Method of structure determination</b></td>
        <td>$method</td>
    </tr>
    <tr align=center>
        <td><b>Number of inter-chain contacts</b></td>
        <td>$contactnum</td>
    </tr>
    <tr bgcolor="#DEDEDE" align=center>
        <td><b>Sequence identity between the two chains</b></td>
        <td>$seqid</td>
    </tr>
$pubmed_html
    </table>
</div>
</td></tr>
'''.replace("$pdbid",pdbid
  ).replace("$reso",reso
  ).replace("$assemblyid",assemblyid
  ).replace("$method",method
  ).replace("$contactnum",contactnum
  ).replace("$seqid",seqid
  ).replace("$title",title
  ).replace("$pubmed_html",pubmed_html
  ))

    print('''
<tr><td>
<div id="headerDiv">
    <div id="titleText">Chain information</div>
</div>
<div style="clear:both;"></div>
<div id="contentDiv">
    <div id="RContent" style="display: block;">
    <table border="0" style="font-family:Monospace;font-size:14px;background:#F2F2F2;" >
    <tr bgcolor="#DEDEDE" align=center>
        <th></th>
        <th><b><font color=red>Chain 1</font></b></th>
        <th><b><font color=blue>Chain 2</font></b></th>
    </tr>
    <tr align=center>
        <td><b>Model ID</b></td>
        <td><font color=red>$modelid1</font></td>
        <td><font color=blue>$modelid2</font></td>
    </tr>
    <tr bgcolor="#DEDEDE" align=center>
        <td><b>Chain ID</b></td>
        <td><font color=red>$chainid1</font></td>
        <td><font color=blue>$chainid2</font></td>
    </tr>
    <tr align=center>
        <td><b>UniProt accession</b></td>
        <td><a href=https://uniprot.org/uniprot/$accession1 target=_blank>$accession1</a></td>
        <td><a href=https://uniprot.org/uniprot/$accession2 target=_blank>$accession2</a></td>
    </tr>
    <tr bgcolor="#DEDEDE" align=center>
        <td><b>Species</b></td>
        <td><font color=red>$species1</font></td>
        <td><font color=blue>$species2</font></td>
    </tr>
$BioLiP_html
    </table>
</div>
</td></tr>
'''.replace("$pdbid",pdbid
  ).replace("$modelid1",modelid1).replace("$modelid2",modelid2
  ).replace("$chainid1",chainid1).replace("$chainid2",chainid2
  ).replace("$accession1",accession1).replace("$accession2",accession2
  ).replace("$species1",species1).replace("$species2",species2
  ).replace("$BioLiP_html",BioLiP_html
  ))

    #### display structure ####
    assembly_name=pdbid+"-assembly"+assemblyid+".cif.gz"
    assembly_filename=rootdir+"/output/"+assembly_name
    if not os.path.isfile(assembly_filename):
        divided=pdbid[-3:-1]
        cmd="curl -s https://files.wwpdb.org/pub/pdb/data/assemblies/mmCIF/divided/%s/%s-assembly%s.cif.gz -o %s"%(divided,pdbid,assemblyid,assembly_filename)
        os.system(cmd)

    if not viewer:
        cmd="zcat "+assembly_filename+"|"+rootdir+"/script/pdb2fasta - |grep -F '>'|cut -f2 -d:|cut -f1"
        p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout,stderr=p.communicate()
        chainid_list=stdout.decode().splitlines()
        if max([len(chainid) for chainid in chainid_list])>1:
            viewer="ngl"
        else:
            viewer="jmol"

    if viewer=="ngl":
        if modelid1!='1':
            chainid1+='-'+modelid1
        if modelid2!='1':
            chainid2+='-'+modelid2
        print('''
<tr><td>
<div id="headerDiv">
    <div id="titleText">3D structure</div>
</div>
Switch viewer: [NGL] <a href="?entryid=$entryid&viewer=jmol">[JSmol]</a>
<div style="clear:both;"></div>
<div id="contentDiv">
<div id="RContent" style="display: block;">
<table width=100% border="0" style="font-family:Monospace;font-size:14px;background:#F2F2F2;" >
<tr><td>
    Dimer structure: 
    <font color=red>Chain 1 in red</font>;
    <font color=blue>Chain 2 in blue</font>.

    <script src="ngl/dist/ngl.js"></script>
    <script type="text/javascript"> 

    document.addEventListener("DOMContentLoaded", function () {
        var stage = new NGL.Stage("mydiv0");
        var schemeId = NGL.ColormakerRegistry.addSelectionScheme([
            ["red", ":A"],
            ["blue", ":B"],
            ["grey", "*"]
        ], "$assembly_name");
        stage.loadFile("output/$basename").then( function( o ){
            o.addRepresentation("cartoon", {color: schemeId }); 
            o.autoView();
        });
    });

    </script>
    <div id="mydiv0" style="width:400px; height:400px;"></div>
    <table>
        <tr><td>Download:</td><td>
            <a href=output/$basename download>$basename</a>
        </td></tr>
    </table>

</td><td>
    Full biological assembly

    <script type="text/javascript"> 
    document.addEventListener("DOMContentLoaded", function () {
        var stage = new NGL.Stage("mydiv1");
        var schemeId = NGL.ColormakerRegistry.addSelectionScheme([
            ["red", ":$chainid1"],
            ["blue", ":$chainid2"],
            ["grey", "nucleic"],
            ["grey", "*"]
        ], "$assembly_name");
        stage.loadFile("output/$assembly_name").then( function( o ){
            o.addRepresentation( "licorice", {
                sele: "hetero and not water",
                multipleBond: true
            } );
            o.addRepresentation("cartoon", {color: schemeId }); 
            o.autoView();
        });
    });
    </script>
    <div id="mydiv1" style="width:400px; height:400px;"></div>
    <table>
        <tr><td>Download:</td><td>
            <a href=output/$assembly_name download>$assembly_name</a>
        </td></tr>
    </table>

</td></tr>
</table>
</div>
</td></tr>
'''.replace( "$basename",os.path.basename(filename)
  ).replace( "$entryid",entryid
  ).replace( "$assembly_name",assembly_name
  ).replace( "$chainid1",chainid1).replace( "$chainid2",chainid2
  ))
    else:
        print('''
<tr><td>
<div id="headerDiv">
    <div id="titleText">3D structure</div>
</div>
Switch viewer: <a href="?entryid=$entryid&viewer=ngl">[NGL]</a> [JSmol]
<div style="clear:both;"></div>
<div id="contentDiv">
<div id="RContent" style="display: block;">
<table width=100% border="0" style="font-family:Monospace;font-size:14px;background:#F2F2F2;" >
<tr><td>
    Dimer structure: 
    <font color=red>Chain 1 in red</font>;
    <font color=blue>Chain 2 in blue</font>.

    <script type="text/javascript"> 
    $(document).ready(function()
    {
        Info = {
            width: 400,
            height: 400,
            j2sPath: "jsmol/j2s",
            script: "load output/$basename; color background black; cartoons; spacefill off; wireframe off; select :A; color red; select :B; color blue; "
        }
        $("#mydiv0").html(Jmol.getAppletHtml("jmolApplet0",Info))
    });
    </script>
    <span id=mydiv0></span>
    <table>
        <tr><td>Color:</td><td>
            [<a href="javascript:Jmol.script(jmolApplet0, 'select :A; color red; select :B; color blue;')">By chain</a>] &nbsp;
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

</td><td>
    Full biological assembly

    <script type="text/javascript"> 
    $(document).ready(function()
    {
        Info = {
            width: 400,
            height: 400,
            j2sPath: "jsmol/j2s",
            script: "load output/$assembly_name; color background black; cartoons; select nucleic; color lightgrey; select :'$chainid1'; color red; select :'$chainid2'; color blue; select protein or solvent or nucleic; spacefill off; wireframe off; "
        }
        $("#mydiv1").html(Jmol.getAppletHtml("jmolApplet1",Info))
    });
    </script>
    <span id=mydiv1></span>
    <table>
        <tr><td>Color:</td><td>
            [<a href="javascript:Jmol.script(jmolApplet1, 'select :$chainid1; color red; select :$chainid2; color blue;')">By chain</a>] &nbsp;
            [<a href="javascript:Jmol.script(jmolApplet1, 'select :$chainid1 or :$chainid2; color group')">By residue index</a>] &nbsp;
        </td></tr>
        <tr><td>Spin:</td><td>
            [<a href="javascript:Jmol.script(jmolApplet1, 'spin off')">Spin off</a>] &nbsp;
            [<a href="javascript:Jmol.script(jmolApplet1, 'spin on')">Spin on</a>] &nbsp;
            [<a href="javascript:Jmol.script(jmolApplet1, 'Reset')">Reset</a>]
        </td></tr>
        <tr><td>Render:</td><td>
            [<a href="javascript:Jmol.script(jmolApplet1, 'set antialiasDisplay false')">Low quality</a>] &nbsp;
            [<a href="javascript:Jmol.script(jmolApplet1, 'set antialiasDisplay true')">High quality</a>] &nbsp;
        </td></tr>
        <tr><td>Background:</td><td>
            [<a href="javascript:Jmol.script(jmolApplet1, 'color background black')">Black quality</a>] &nbsp; 
            [<a href="javascript:Jmol.script(jmolApplet1, 'color background white')">White quality</a>] &nbsp;
        </td></tr>
        <tr><td>Download:</td><td>
            <a href=output/$assembly_name download>$assembly_name</a>
        </td></tr>
    </table>

</td></tr>
</table>
</div>
</td></tr>
'''.replace( "$basename",os.path.basename(filename)
  ).replace( "$entryid",entryid
  ).replace( "$assembly_name",assembly_name
  ).replace( "$chainid1",chainid1).replace( "$chainid2",chainid2
  ))

    #### similar dimer ####
    membership_dict=dict()
    fp=open(rootdir+"/data/cluster/membership.tsv")
    target_seqclust=''
    for line in fp.read().splitlines():
        dimer,seqclust,nonredundant=line.split('\t')
        if dimer==nonredundant:
            continue
        if nonredundant==entryid:
            target_seqclust=seqclust
        if not seqclust in membership_dict:
            membership_dict[seqclust]=dict()
        if not nonredundant in membership_dict[seqclust]:
            membership_dict[seqclust][nonredundant]=[]
        membership_dict[seqclust][nonredundant].append(dimer)
    fp.close()
    seqclust=target_seqclust
    if len(seqclust):
        print('''
<tr><td>
<div id="headerDiv">
    <div id="titleText">Similar dimers</div>
</div>
<div style="clear:both;"></div>
<div id="contentDiv">
    <div id="RContent" style="display: block;">
    <table border="0" style="font-family:Monospace;font-size:14px;background:#F2F2F2;" >
    ''')
        if len(membership_dict[seqclust][entryid])>1:
            print('''
    <tr bgcolor="#DEDEDE" align=center>
        <td><b>Other dimers with similar sequences and structures</b></td>
        <td>$dimer_list</td>
    </tr>
            '''.replace("$dimer_list",' '.join(membership_dict[seqclust][entryid])))
        if len(membership_dict[seqclust])>1:
            dimer_list=[]
            for nonredundant in membership_dict[seqclust]:
                if nonredundant==entryid:
                    continue
                dimer_list.append("<li><a href=pdb.cgi?entryid="+nonredundant+">"+nonredundant+"</a> "+' '.join(membership_dict[seqclust][nonredundant])+'</li>')
            print('''
    <tr align=center>
        <td><b>Other dimers with similar sequences but different poses</b></td>
        <td>$dimer_list</td>
    </tr>
            '''.replace('$dimer_list','\n'.join(dimer_list)))
        print('''
    </table>
</div>
</td></tr>
        ''')
    return 

if __name__=="__main__":
    form   =cgi.FieldStorage()
    entryid=form.getfirst("entryid",'')
    entryid=entryid.strip().split()[0]
    viewer =form.getfirst("viewer",'')
    

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
        display_dimer(entryid,viewer)
    
    print('''</table>
<p></p>
[<a href=.>Back to Home</a>]
</body> </html>''')
