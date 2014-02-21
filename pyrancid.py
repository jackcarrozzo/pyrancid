#! /usr/bin/python
# pyrancid - Jack Carrozzo <jack@crepinc.com>
#
#   minirant: do you know how enraging it is
#       that vim can't figure out gg=G 
#       with python?

from ConfigParser import SafeConfigParser
import sys,os
import smtplib

# DISCLAIMER! I wrote this when I was just starting to use Python, please
# don't judge my abilities from it. I'd really like to rewrite it when 
# I have time.

p = SafeConfigParser()
p.read('/home/jackc/Projects/pyrancid/mythings.cfg')

mailfromname="pyrancid"
mailfromaddr="pyrancid@crepinc.com"
receivers=['jack@crepinc.com']
mailto="Jack C <jack@crepinc.com>"

if not p.has_section('global'):
    print "Config has no 'global' section!"
    sys.exit(1)

if not p.has_option('global','textpath'):
    print "Global config missing 'textpath'!"
    sys.exit(1)
textpath=p.get('global','textpath')

if not textpath[0]=='/':
    print "textpath is not an absolute path!"
    sys.exit(1)

if not textpath[-1]=='/': #add trailing /
    textpath+='/'

if p.has_option('global','debug'):
    debug=True
else:
    debug=False

if debug:
    print "Text path  : '"+textpath+'"'

firstmail=True
p.remove_section('global')
for machine in p.sections():
    newmachine=False

    if debug:
        print "---"
        print 'Interviewing:', machine

    if not p.has_option(machine,'addr'):
        print "Config for %s is missing required option 'addr'!"%machine
        sys.exit(1)
    addr=p.get(machine,'addr');
    if debug:
        print "addr: '"+addr+"'"

    if not p.has_option(machine,'mode'):
        print "Config for %s is missing required option 'mode'!"%machine
        sys.exit(1)
    mode=p.get(machine,'mode');
    if debug:
        print "mode: '"+mode+"'"

    if not p.has_option(machine,'cmd'):
        print "Config for %s is mising required option 'cmd'!"%machine
        sys.exit(1)
    cmd=p.get(machine,'cmd');
    if debug:
        print "cmd : '"+cmd+"'"

    if mode=="ssh":
        syscmd="ssh "
        if p.has_option(machine,'port'):
            syscmd+="-p "+p.get(machine,'port')+" "
        syscmd+=addr+" \""+cmd+"\""
    elif (mode=="telnet") or (mode=="raw"):
        syscmd="echo \""+cmd+"\"|nc "+addr+" "
        if p.has_option(machine,'port'):
            syscmd+=p.get(machine,'port')
        else:
            syscmd+="23"
    
    syscmd+=" >"+textpath+machine+'-incoming'
    if debug:
        print "sys : "+syscmd
    ret=os.system(syscmd)
    if ret>0:
        print "Got return code %d!"%ret
    else:
        if not os.path.isfile(textpath+machine+"-current"):
            newmachine=True
            ret=os.system("touch "+textpath+machine+"-current")
            if ret>0:
                print "Could not touch -current workfile. Check perms?"

        syscmd="mv "+textpath+machine+"-current "+textpath+machine+"-previous"
        if debug:
            print "sys : "+syscmd
        ret=os.system(syscmd)
        if ret>0:
            print "There was an issue moving the current conf to previous!"
        else:
            syscmd="mv "+textpath+machine+"-incoming "+textpath+machine+"-current"
            if debug:
                print "sys : "+syscmd
            ret=os.system(syscmd)
            if ret>0:
                print "There was an issue moving incoming conf to current!"
            
    syscmd="diff -b "+textpath+machine+"-previous "+textpath+machine+"-current >"+textpath+machine+"-diff"
    os.system(syscmd) # diff returns >0 if it finds a difference. TODO: handle returns

    diff=''
    for line in open(textpath+machine+"-diff",'r'):
        diff+=line

    if not diff=='' and not newmachine:
        if debug:
            print "We have a change! "

        if firstmail:
            firstmail=False
            smtp=smtplib.SMTP('localhost')

        message="From: "+mailfromname+"<"+mailfromaddr+">\n"
        message+="To: "+mailto+"\n"
        message+="Subject: pyrancid change notice: "+machine+"\n\n"
        message+=diff
        smtp.sendmail(mailfromaddr,receivers,message)
    else:
        if debug:
            print "No change detected."

        

#print '  Options:', parser.options(section_name)
#    for name, value in parser.items(section_name):
#        print '  %s = %s' % (name, value)
#    print
