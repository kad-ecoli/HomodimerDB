#!/bin/bash

# This folder is the temporary folder for writing pdb files by cgi script.
# Permission and context of the folder and cgi scripts must be correctly set:

# First, set the permission:

    chmod a+x index.cgi
    chmod a+x pdb.cgi
    chmod a+x qsearch.cgi
    chmod a+x ssearch.cgi
    chmod a+x csearch.cgi
    chmod 777 output/
    chmod a+r+x -R data

# Second, set the context, which may not be necessary on some system:

    chcon -t httpd_sys_script_exec_t index.cgi
    chcon -t httpd_sys_script_exec_t pdb.cgi
    chcon -t httpd_sys_script_exec_t qsearch.cgi
    chcon -t httpd_sys_script_exec_t ssearch.cgi
    chcon -t httpd_sys_script_exec_t csearch.cgi
    chcon -t httpd_sys_script_exec_t script/blastp
    chcon -t httpd_sys_rw_content_t  output/

# third make blastdb:
    
    script/formatdb.sh
