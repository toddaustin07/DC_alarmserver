#!/bin/python3
###########################################################################
# Copyright 2021 Todd A. Austin  Version 20210220
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
############################################################################

import json
import requests
import subprocess
import os
from os import path
import sys

################################################################
# Replace 'xxxxx...' with your SmartThings Personal Token Below
################################################################
TOKEN = 'Bearer xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'

BASEURL = 'https://api.smartthings.com/v1'

BASEDIR = "base/"
CREATEDIR = "created/"

HTTP_OK = 200
ST_STATUSCODE_EXISTS = 422

headers = {'Authorization': TOKEN,
           'Content-Type' : 'application/json'}

def do_create():

    # Get list of files in the base subdirectory
    
    dirreq="ls "+BASEDIR+"*.json"
    lsout = subprocess.run([dirreq], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    flist = lsout.stdout.decode('utf-8').split("\n")
    
    # Iterate through each file

    for jfile in flist:
        fname = jfile.split(".")
       
        try:
            if fname[1] == "json":
                
                tname = fname[0].split("_")
                
                # capability json filename should be in form of <capabilityname>_cap.json
                if tname[1] == "cap":
                    print ("\n"+tname[0]+"...")
                    try:
                        with open(jfile) as f:
                            filejson = f.read()    
                    except:
                        print ("Error reading capability json file %s" % jfile)
                        exit(-1)
                    
                    # SmartThings API to create new capability
                    r = requests.post(BASEURL+'/capabilities', headers=headers, data=filejson)
                    
                    if r.status_code == HTTP_OK:
                        
                        pydict = json.loads(r.text)
                
                        # Get assigned capabilityID and version number from post response json 
                
                        capabilityID = pydict['id']
                        capabilityVersion = pydict['version']
                        
                        # Save returned json to file
                        try:
                            with open(CREATEDIR+capabilityID+'_cap.json',"w") as f2:
                                f2.write(json.dumps(json.loads(r.text), indent=4))
                        except:
                            print ("\033[91mError saving returned capability json\033[0m")
                            exit(-1)
                        
                        # Confirm existance of companion presentation json file:  <capabilityname>_pres.json
                        
                        presfile = tname[0]+"_pres.json"
                        
                        if path.exists(presfile):
                            
                            idreplacestr = '    \\\"id\\\": \\\"'+capabilityID+'\\\",'
                            verreplacestr = '    \\\"version\\\": '+str(capabilityVersion)   
                             
                            # Use sed to update capabilityId and Version in the presentation json file
                             
                            sedcmd = 'sed -i "/^    \\\"id\\\":/c\\\\'+idreplacestr+'" "'+presfile+'"'
                            rc = os.system(sedcmd)
                            
                            if rc == 0:
                                
                                sedcmd = 'sed -i "/^    \\\"version\\\":/c\\\\'+verreplacestr+'" "'+presfile+'"'
                                rc = os.system(sedcmd)
                            
                                if rc == 0:
                                
                                    try:
                                        with open(presfile) as f:
                                            filejson = f.read()    
                                    except:
                                        print ("\033[91mError reading presentation json file %s\033[0m" % presfile)
                                        exit(-1)
                                    
                                    buildURL=BASEURL+'/capabilities/'+capabilityID+'/'+str(capabilityVersion)+'/presentation'
                        
                                    # SmartThings API to create new capability presentation
                                    r = requests.post(buildURL, headers=headers, data=filejson)
                            
                                    if r.status_code == HTTP_OK:
                                        # Save returned json to file
                                        try:
                                            with open(CREATEDIR+capabilityID+'_pres.json',"w") as f2:
                                                f2.write(json.dumps(json.loads(r.text), indent=4))
                                        except:
                                            print ("\033[91mError saving returned presentation json\033[0m")
                                            exit(-1)
                                        else:
                                            print ("\033[96mCapability and presentation successfully created: %s\033[0m" % capabilityID)
                                            
                                    elif r.status_code == ST_STATUSCODE_EXISTS:
                                        print ("\033[33mWarning: capability presentation already exists\033[0m")    
                                    else:
                                        print ("\033[91mHTTP error on presentation creation; status code= %s\033[0m" % r.status_code)
                                else:
                                    print ("\033[91msed error updating version in presentation file; returncode = %d\033[0m" % rc)
                                    
                            else:
                                print ("\033[91msed error updating capability id in presentation file; returncode = %d\033[0m" % rc)
                        else:
                            print ("\033[91mpresentation json file missing for %s\033[0m" % presfile)
                    elif r.status_code == ST_STATUSCODE_EXISTS:
                        print ("\033[33mWarning: capability name already exists\033[0m")    
                    else:
                        print ("\033[91mHTTP error on capability creation; status code= %s\033[0m" % r.status_code)                                
                # End if _cap file
            # End if json file
        except IndexError:
            pass


def do_delete():
    
    dirreq="ls "+CREATEDIR+"*.json"
    lsout = subprocess.run([dirreq], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    flist = lsout.stdout.decode('utf-8').split("\n")
    
    # Iterate through each file

    for jfile in flist:
        
        
        fpname = jfile.split("/")
        
        try:
            ftname = fpname[1].split(".")
        
            if ftname[2] == "json":
                tmpname = ftname[0]+"."+ftname[1]
                tname = tmpname.split("_")
                
                # capability json filename should be in form of <capabilityname>_cap.json
                if tname[1] == "cap":
                    
                    print ("\n"+tname[0]+"...")
                                
                    # SmartThings API to delete capability
                    buildURL=BASEURL+'/capabilities/'+tname[0]+'/1'
                    r = requests.delete(buildURL, headers=headers)
                    
                    if r.status_code == HTTP_OK:
                        print ("\033[96m\tCapability Deleted\033[0m")
                    else:
                        print ("\033[91mHTTP error on capability delete; status code= %s\033[0m" % r.status_code)
        except:
            pass
                    
def do_update():

    dirreq="ls "+CREATEDIR+"*.json"
    lsout = subprocess.run([dirreq], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    flist = lsout.stdout.decode('utf-8').split("\n")
    
    # Iterate through each file

    for jfile in flist:
        
        
        fpname = jfile.split("/")
        
        try:
            ftname = fpname[1].split(".")
        
            if ftname[2] == "json":
                tmpname = ftname[0]+"."+ftname[1]
                tname = tmpname.split("_")
                
                # capability json filename should be in form of <capabilityname>_<cap | pres>.json
                if tname[1] == "cap" or tname[1] == "pres":
                    
                    print ("\n"+tname[0]+"...")
                                
                    try:
                        with open(jfile) as f:
                            filejson = f.read()    
                    except:
                        print ("Error reading capability json file %s" % fpname)
                        exit(-1)
                     
                  
                    # SmartThings API to update capability
                    buildURL=BASEURL+'/capabilities/'+tname[0]+'/1'
                    
                    if tname[1] == "pres":
                        buildURL=buildURL+'/presentation'
                        
                    r = requests.put(buildURL, headers=headers, data=filejson)
                    
                    if r.status_code == HTTP_OK:
                        if tname[1] == "cap":
                            print ("\033[96m\tCapability Updated\033[0m")
                        else:
                            print ("\033[96m\tCapability Presentation Updated\033[0m")
                            
                        try:
                            with open(jfile,"w") as f2:
                                f2.write(json.dumps(json.loads(r.text), indent=4))
                        except:
                            print ("\033[91mError saving updated json for %s\033[0m" % jfile)
                        
                    else:
                        print ("\033[91mHTTP error on update; status code= %s\033[0m" % r.status_code)
                    
        except:
            pass

    
####################################################################################################################
#                                 ** MAIN **
####################################################################################################################

if __name__ == '__main__':
    
    if TOKEN == 'Bearer xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx':
        print("\033[93mYou must first edit line 28 in this script to provide your SmartThings personal token\033[0m")
        exit(-1)

    if (len(sys.argv) != 2):
        print("Usage:  STcapabilities <create | update | delete>")
        exit(0)

    mode=sys.argv[1]
    if mode not in ['create', 'update', 'delete']:
        print("Invalid argument")
        print("Usage:  STcapabilities <create | update | delete>")
        exit(0)

    if not path.exists(BASEDIR):
        print("\033[91m'%s' subdirectory containing json files is missing" % BASEDIR)
        exit(-1)
        
    if not path.exists(CREATEDIR):
        os.mkdir(CREATEDIR)

    if mode == 'create':
        do_create()
        
    elif mode == 'delete':
        do_delete()
        
    elif mode == 'update':
        do_update()


    print ("\nDONE")
