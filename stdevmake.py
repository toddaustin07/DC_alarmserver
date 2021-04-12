#!/bin/python3
# _*_ coding: utf-8 _*_
###########################################################################
# Copyright 2021 Todd A. Austin  Version 1.20210411
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

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter.filedialog import askopenfile
import tkinter.font as tkFont

import json
import requests
import subprocess
import os
from os import path
from os import listdir
import sys
import glob
import platform

# GLOBAL CONSTANTS

TOKEN_SIZE = 36
VID_SIZE = 36

BASEURL = 'https://api.smartthings.com/v1'
headers = {'Authorization': '',
           'Content-Type' : 'application/json'}
HTTP_OK = 200
ST_STATUSCODE_EXISTS = 422

TESTJSON = \
{
    "name": "00test00",
    "attributes": {},
    "commands": {
        "setSwitch": {
            "name": "setSwitch",
            "arguments": [
                {
                    "name": "value",
                    "schema": {
                        "type": "string"
                    }
                }
            ]
        }
    }
}

# GLOBAL VARIABLES

TOKEN = 'Bearer '

root = Tk()
global cwin
global rwin

ref_caplist = []
ref_capstatlist = []
cre_capstatlist = []
loc_caplist = []
cre_caplist = []
ref_cnames = StringVar(value=ref_caplist)
refstat_cnames = StringVar(value=ref_capstatlist)
cre_cnames = StringVar(value=cre_caplist)
crestat_cnames = StringVar(value=cre_capstatlist)

global savedir
global devconfname
currentdir = "."

token_text = StringVar()
myprefix_text = StringVar()
mnmn_text = StringVar()
devtype_text = StringVar()
defpath_text = StringVar()
vid_text = StringVar()
mnmn2_text = StringVar()
devmnmn_text = StringVar()
clonedmnmn_text = StringVar()

statusmsg = StringVar()
rmsg_text = StringVar()
presentid1 = StringVar()
presentid2 = StringVar()


def custcapname(capid):
    
    if (len(capid.split(".",2)) == 2):
        return capid
    return ""


def updateloclist(prefix):

    global savedir
    global loc_cnames

    checkpath = savedir+os.sep+prefix+os.sep+"capability"+os.sep+"*.json"
    
    flist = glob.glob(checkpath)

    loc_caplist.clear()

    if (flist):

        for jfile in flist:
            fname = os.path.basename(jfile).split('.',2)[0]
            loc_caplist.append(prefix+"."+fname)
            

def resetall():

    getcapbtn.config(state="disabled")
    putcapbtn1.config(state="disabled")
    putcapbtn2.config(state="disabled")
    clonecapbtn.config(state="disabled")
    clonedevbtn.config(state="disabled")
    cloneallbtn.config(state="disabled")
    submitallbtn.config(state="disabled")
    newvidbtn1.config(state="disabled")
    newvidbtn2.config(state="disabled")
    devconf.config(text="")
    mydevconf.config(text="")
    statusmsg.set("")
    ref_caplist.clear()
    ref_cnames.set(ref_caplist)
    cre_caplist.clear()
    cre_cnames.set(cre_caplist)
    loc_caplist.clear()
    
    ref_capstatlist.clear()
    refstat_cnames.set(ref_capstatlist)
    cre_capstatlist.clear()
    crestat_cnames.set(cre_capstatlist)
    presentid1.set('')
    presentid2.set('')
    devmnmn_text.set('')
    clonedmnmn_text.set('')


def showcfg(pydictfull, filepath):
    
    global devconfname
    global ref_caplist
    foreign_flag = 0
    mycap_flag = 0
    
    caplist = []
   
    try:
        dashboard = pydictfull["dashboard"]
        detailview = pydictfull["detailView"]
        automation = pydictfull["automation"]
    
    except:
        statusmsg.set("Invalid device config json")
       
        return
    
    if 'manufacturerName' in pydictfull:
        confmnmn=pydictfull["manufacturerName"]
        devmnmn_text.set('Manufacturer name: '+confmnmn)
        
    elif 'mnmn' in pydictfull:
        confmnmn=pydictfull["mnmn"]
        devmnmn_text.set('Manufacturer name: '+confmnmn)
    else:
        confmnmn=''
        devmnmn_text.set(confmnmn)
    
    devconf.config(text=os.path.basename(filepath))
    devconfname=filepath
     
    pydict = json.loads(json.dumps(dashboard))
    
    states = pydict["states"]
    actions = pydict["actions"]
     
    if states:
        pydict = json.loads(json.dumps(states[0]))
        capability = pydict["capability"]
        name=custcapname(capability)
        if name:
            caplist.append(name)
     
    if actions: 
        pydict = json.loads(json.dumps(actions[0]))
        capability = pydict["capability"]
        name=custcapname(capability)
        if name:
            caplist.append(name)
     
    for item in detailview:
        pydict = json.loads(json.dumps(item))
        capability = pydict["capability"]
        name=custcapname(capability)
        if name:
            caplist.append(name)
    
    ref_caplist = list(set(caplist))
   
    ref_caplistbox.selection_set(0, END)
    getcapbtn.config(state="enable")
    
    mynamespace=myprefix_text.get()
    for cap in caplist:
        if cap.split('.',2)[0] == mynamespace:
            mycap_flag = 1

    if mycap_flag == 1:
        putcapbtn1.config(state="enable")
        
    clonedevbtn.config(state="enable")
    
    # GET LIST OF STORED CAPABILITIES
    
    _capid=ref_caplist[0].split(".",2)
    prefixid=_capid[0]
    capname=_capid[1]
    
    updateloclist(prefixid)
    
    ref_capstatlist.clear()
    for refitem in ref_caplist:
        ref_capstatlist.append(' ')
    
    index=0
    for refitem in ref_caplist:
        
        for locitem in loc_caplist:
            if (locitem == refitem):
                ref_capstatlist[index] = '⇩'
                
        index += 1
        
    ref_cnames.set(ref_caplist)
    refstat_cnames.set(ref_capstatlist)
    
    # Confirm if any of the capabilities are from foreign namespace
    
    for item in loc_caplist:                        
        _item=item.split('.',2)
        if _item[0] != myprefix_text.get():
            foreign_flag = 1
    
    my_mnmn = mnmn_text.get()
    subdirname = os.path.basename(os.path.dirname(filepath))

    if (subdirname == my_mnmn):                     # If file was located in our mnmn directory...
        newvidbtn1.config(state="enable")
        cloneallbtn.config(state="disable")
        clonedevbtn.config(state="disable")
        
    else:                                           # else not from our own mnmn directory...
        if (foreign_flag == 1):        
            clonecapbtn.config(state="enable") 
        else:
            clonecapbtn.config(state="disable") 

        clonedevbtn.config(state="enable")          # default to enabled

        if (confmnmn != ''):                        # But check to see if this is one of ours
            if (confmnmn == my_mnmn):
                newvidbtn1.config(state="enable")   #   If one of ours, enabled vid submission, turn off clone/copy
                clonedevbtn.config(state="disable")
                
    if clonedevbtn.cget('state') == 'enable' and clonecapbtn.cget('state') == 'enable':
        cloneallbtn.config(state="enable")
                
    if ('presentationId' in pydictfull):
        presentid1.set(pydictfull['presentationId'])
    elif ('vid' in pydictfull):
        presentid1.set(pydictfull['vid'])
    else:
        presentid1.set('')
        
    ref_caplistbox.selection_set(0, END)
        
    return
    
def opencfg():
    
    resetall()
    
    file = askopenfile(parent=root, mode='rb', title="Choose a device config file", filetypes=[("json file", "*.json")])
    
    if file:
        showcfg(json.loads(file.read()), file.name)
    
    
def retrievevid():
    
    resetall()
    
    errors = 0
    vid = vid_text.get()
    my_mnmn = mnmn_text.get()
    my_namespace = myprefix_text.get()
    defpath = defpath_text.get()
    
    if (len(vid) != VID_SIZE):
        if ((vid.startswith('ST_')) and (len(vid) == VID_SIZE+3)):
            pass
                
        else:
            rmsg_text.set("Invalid Presentation ID")
            return
        
    reqmnmn=mnmn2_text.get()
    buildURL=BASEURL+'/presentation/deviceconfig?presentationId='+vid+'&mnmn='+reqmnmn
    
    r = requests.get(buildURL, headers=headers)

    if r.status_code == HTTP_OK:
        # Save returned json to file
        
        pydict = json.loads(r.text)

        if (pydict['manufacturerName'] == my_mnmn):
            savepath = os.path.normpath(defpath+os.sep+reqmnmn+os.sep+vid+'.json')
        else:
            savepath = os.path.normpath(defpath+os.sep+vid+'.json')
        
        if not path.exists(os.path.normpath(defpath+os.sep+reqmnmn)):
            os.mkdir(os.path.normpath(defpath+os.sep+reqmnmn))
        
        proceed = True
        if os.path.isfile(savepath):
            msg = "OK to overwrite existing local device config file?"
            proceed = messagebox.askyesno(message=msg, icon='question', title='Confirm')
                 
        if (proceed):
        
            try:
                with open(savepath,"w") as f2:
                    f2.write(json.dumps(json.loads(r.text), indent=4))
                    
                    statusmsg.set("Device config json saved")
                    
            except:
                statusmsg.set("File Error saving device config json")
                errors += 1
                
        else:
            rwin.grab_release()
            rwin.destroy()
            resetall()
            return

    else:
        statusmsg.set("HTTP Error #"+str(r.status_code))
        errors += 1
        
    rwin.grab_release()
    rwin.destroy()
    
    if (errors == 0):
        showcfg(pydict, savepath)
    
    
def cancelretrieve():
    
    rwin.grab_release()
    rwin.destroy()
    
    
def retrievecfg():
    
    resetall()
    
    global rwin

    # Create window to ask for presentation ID and mnmn
    
    rwin = Toplevel(root)
    rwin.title('Provide device config identifiers')
    rwin.protocol("WM_DELETE_WINDOW", cancelretrieve)
    rwin.resizable(FALSE, FALSE)
    
    retrievebtn = ttk.Button(rwin, text="Retrieve", command=retrievevid)
    cancelbtn = ttk.Button(rwin, text="Cancel", command=cancelretrieve)
    
    vid_label = ttk.Label(rwin, text="Presentation ID", width=16, anchor="e")
    vid_entry = ttk.Entry(rwin, textvariable=vid_text, width=VID_SIZE)
    
    mnmn_label = ttk.Label(rwin, text="Manufacturer ID", width=16, anchor="e")
    mnmn_entry = ttk.Entry(rwin, textvariable=mnmn2_text, width=25)

    rmsg_label = ttk.Label(rwin, textvariable=rmsg_text, width=30, anchor="w", foreground="brown")
    
    vid_label.grid(columnspan=1, column=0, row=3, pady=(10,5), padx=(0,8))
    vid_entry.grid(columnspan=2, column=1, row=3, sticky=(W), padx=(0,30),pady=(10,5))
    mnmn_label.grid(columnspan=1, column=0, row=4, pady=(10,5), padx=(0,8))
    mnmn_entry.grid(columnspan=2, column=1, row=4, sticky=(W), pady=(10,5))
    
    retrievebtn.grid(columnspan=1, column=1, row=6, pady=(10,10))
    cancelbtn.grid(columnspan=1, column=2, row=6, pady=(10,10))
    
    rmsg_label.grid(columnspan=3, column=0, row=7, sticky=W, padx=(15,0), pady=(15,5))
    
    mnmn2_text.set(mnmn_text.get())
    vid_text.set('')
    
    rwin.grid_columnconfigure(4, weight=1)
    rwin.grid_rowconfigure(8, weight=1)
    
    rwin.transient(root)
    rwin.wait_visibility()
    rwin.grab_set()
    rwin.wait_window()
    

def getcaps():
    
    errors = 0
    foreign_flag =  0
    
    statusmsg.set("")
    selected_caps = ref_caplistbox.curselection()
  
    if len(selected_caps) >= 1:
        for index in selected_caps:
            
            capid = ref_caplist[index]
        
            _capid=capid.split(".",2)
            prefixid=_capid[0]
            capname=_capid[1]

            def_path = defpath_text.get()
            root_path = os.path.normpath(def_path+os.sep+prefixid)
            cap_path = os.path.normpath(def_path+os.sep+prefixid+os.sep+"capability")
            pre_path = os.path.normpath(def_path+os.sep+prefixid+os.sep+"presentation")
            
            if not os.path.exists(root_path):
                os.mkdir(root_path)
                os.mkdir(cap_path)
                os.mkdir(pre_path)
        
            # GET CAPABILITY JSON
        
            buildURL=BASEURL+'/capabilities/'+capid+'/1'
            
            r = requests.get(buildURL, headers=headers)

            if r.status_code == HTTP_OK:
                # Save returned json to file
                try:
                    with open(cap_path+os.sep+capname+'.json',"w") as f2:
                        f2.write(json.dumps(json.loads(r.text), indent=4))
                except:
                    statusmsg.set("File Error saving capability json")
                    errors += 1
                    break

            else:
                statusmsg.set("HTTP Error #"+str(r.status_code))
                errors += 1
                break
                
             # GET PRESENTATION JSON
                
            buildURL=BASEURL+'/capabilities/'+capid+'/1/presentation'
            r = requests.get(buildURL, headers=headers)

            if r.status_code == HTTP_OK:
                
                # Save returned json to file
                try:
                    with open(pre_path+os.sep+capname+'.json',"w") as f2:
                        f2.write(json.dumps(json.loads(r.text), indent=4))
                        ref_capstatlist[index] = '⬇'    
                        
                except:
                    statusmsg.set("File Error saving presentation json")
                    errors += 1
                    break

            else:
                statusmsg.set("HTTP Error #"+str(r.status_code))
                errors += 1
                break
        
        # End for-loop
        
        if (errors == 0):
            # UPDATE LIST OF STORED CAPABILITIES
            updateloclist(prefixid)
            
            refstat_cnames.set(ref_capstatlist)

            for item in loc_caplist:
                _item=item.split('.',2)
                if _item[0] != myprefix_text.get():
                    foreign_flag = 1
            
            if (foreign_flag == 1):        
                clonecapbtn.config(state="enable")
                if clonedevbtn.cget('state') == "enable":
                    cloneallbtn.config(state="enable")
                
            statusmsg.set("Selected capabilities downloaded")
        
    else:
        statusmsg.set("No capabilities selected")
        
def getstcaplist():
    
    mycaplist = []
    
    mynamespace = myprefix_text.get()
    
    # SmartThings API to get capability list
    
    r = requests.get(BASEURL+'/capabilities/namespaces/'+mynamespace, headers=headers)

    if r.status_code == HTTP_OK:
        # Save returned json to file

        pydict = json.loads(r.text)
        
        for item in pydict['items']:
            mycaplist.append(item['id'])
            
    else:
        msg = "Failed getting your capability list: HTTP error # " + str(r.status_code)
        statusmsg.set(msg)

    return(mycaplist)

def getprefix():
    
    headers['Authorization'] = TOKEN+token_text.get()
    
    # SmartThings API to create temp dummy capability
    r = requests.post(BASEURL+'/capabilities', headers=headers, data=json.dumps(TESTJSON, indent=4))

    if r.status_code == HTTP_OK:
        # Save returned json to file

        pydict = json.loads(r.text)
        
        capid = pydict['id']
        _capid = capid.split('.',2)
        prefix=_capid[0]
        myprefix_text.set(prefix)
        
        r = requests.delete(BASEURL+'/capabilities/'+capid+'/1', headers=headers)   
        
        if r.status_code != HTTP_OK: 
            msg = "Warning: couldn't delete temp capability; HTTP Error # " + str(r.status_code)
            statusmsg.set(msg)
     
    else:
        msg = "Failed: HTTP error # " + str(r.status_code)
        statusmsg.set(msg)

    
def clonecaps():
    
    global cre_capstatlist
    
    namespace = myprefix_text.get()
    defpath = defpath_text.get()
    cre_caplist.clear()
    cre_capstatlist.clear()
    cre_capstatlist = [' '] * len(loc_caplist)
    errors = 0
    index = 0
    overwriteflag = False
    
    for cap in loc_caplist:
        
        _cap = cap.split('.',3)
        subdir = _cap[0]
        fname = _cap[1]+'.json'
       
        # Copy the capability json
        
        path = defpath+os.sep+subdir+os.sep+'capability'+os.sep+fname
        path = os.path.normpath(path)
                
        try:
            with open(path,"r") as f:
                pydict = json.loads(f.read())
        except:
            statusmsg.set("Error opening capability json file")  
            errors += 1
            break
                
        del pydict['id']
        del pydict['version']
        del pydict['status']

        newnamespdir = os.path.normpath(defpath+os.sep+namespace)
        
        if not os.path.exists(newnamespdir):
            os.mkdir(newnamespdir)
            os.mkdir(newnamespdir+os.sep+'capability')
            os.mkdir(newnamespdir+os.sep+'presentation')
            
        newpath = newnamespdir+os.sep+'capability'+os.sep+fname
        newpath = os.path.normpath(newpath)
        
        proceed = True
        if (os.path.isfile(newpath)):
            
            if overwriteflag == False:
                msg = "OK to overwrite existing local capability files?"
                proceed = messagebox.askyesno(message=msg, icon='question', title='Confirm')
                if proceed:
                    overwriteflag = True
                else:
                    return False
         
        if (proceed):
            
            try:
                with open(newpath,"w") as f2:
                    
                    f2.write(json.dumps(pydict, indent=4))
                
            except:
                statusmsg.set("Error saving capability json file") 
                errors += 1
        
            
        # Copy the presentation json
        
        path = defpath+os.sep+subdir+os.sep+'presentation'+os.sep+fname
        path = os.path.normpath(path)
                
        try:
            with open(path,"r") as f:
                pydict = json.loads(f.read())
        except:
            statusmsg.set("Error opening presentation json file")
            errors += 1        
            break
                
        # Change the namespace to ours
        
        pydict['id'] = namespace+'.'+_cap[1]
        del pydict['version']
      
        newpath = newnamespdir+os.sep+'presentation'+os.sep+fname
        newpath = os.path.normpath(newpath)
        
        proceed = True
        if (os.path.isfile(newpath)):
            
            if overwriteflag == False:
                msg = "OK to overwrite existing capability presentation files?"
                proceed = messagebox.askyesno(message=msg, icon='question', title='Confirm')
                if proceed:
                    overwriteflag = True
                else:
                    return False
         
        if (proceed):
        
            try:
                with open(newpath,"w") as f2:
                    
                    f2.write(json.dumps(pydict, indent=4))
                    
                    cre_caplist.append(namespace+'.'+_cap[1])
                    cre_capstatlist[index] = '⬇' 
                        
            except:
                statusmsg.set("Error saving presentation json file") 
                errors += 1
                
        index += 1
        
    # End for-loop        
            
    if errors == 0:
        cre_cnames.set(cre_caplist)
        crestat_cnames.set(cre_capstatlist)
        putcapbtn2.config(state="enable")
        cre_caplistbox.selection_set(0, END)
        statusmsg.set("Capability conversion complete")
        return True
    else:
        return False
        

def savecfg():

    global savedir

    try: 
        with open(CONFIGFILE,"w") as f:
            f.write(token_text.get()+'\n')
            f.write(myprefix_text.get()+'\n')
            f.write(mnmn_text.get()+'\n')
            f.write(devtype_text.get()+'\n')
            
            savedir = os.path.normpath(defpath_text.get())
            f.write(savedir+'\n')
            
    except:
        statusmsg.set("File error saving preferences")

    else:
        if not os.path.exists(savedir):
             os.mkdir(savedir)
                        
        
        if len(token_text.get()) == TOKEN_SIZE:
            statusmsg.set("Preferences saved")
            menubar.entryconfig('File', state="active")
        else:
            statusmsg.set("Warning: Personal Token not valid")
            menubar.entryconfig('File', state="disabled")
    
    cwin.grab_release()
    cwin.destroy()

    
def readcfg():
    
    global token_text
    global mnmn_text
    global defpath_text
    global TOKEN
    global savedir
    
    try: 
        with open(CONFIGFILE,"r") as f:
            
            token_text.set(f.readline().rstrip())
            myprefix_text.set(f.readline().rstrip())
            mnmn_text.set(f.readline().rstrip())
            devtype_text.set(f.readline().rstrip())
            defpath_text.set(f.readline().rstrip())

            if len(token_text.get())== TOKEN_SIZE:
                menubar.entryconfig('File', state="active")
            else:
                menubar.entryconfig('File', state="disabled")
            
    except:
        token_text.set("")
        myprefix_text.set("")
        mnmn_text.set("SmartThingsCommunity")
        devtype_text.set("profile")
        defpath_text.set(HOMEPATH+os.sep+"SmartThings_json")
        menubar.entryconfig('File', state="disabled")
        
    headers['Authorization'] = TOKEN+token_text.get()
    savedir = defpath_text.get()
    
def cancelcfg():
    
    cwin.grab_release()
    cwin.destroy()
    
def tokenedit(something):
    
    if (len(token_text.get()) == TOKEN_SIZE):
        getprefixbtn.config(state="active")
    else:
        getprefixbtn.config(state="disabled")

    
def getconfig():
    
    global cwin
    global getprefixbtn
    
    # Create window to display/get configuration parameters
    
    cwin = Toplevel(root)
    cwin.title('Preferences')
    cwin.protocol("WM_DELETE_WINDOW", cancelcfg)
    cwin.resizable(FALSE, FALSE)
    
    readcfg()
    
    s = ttk.Style()
    s.configure('small.TButton', font=('helvetica 8'), foreground='blue')
       
    savebtn = ttk.Button(cwin, text="Save", command=savecfg)
    cancelbtn = ttk.Button(cwin, text="Cancel", command=cancelcfg)
    getprefixbtn = ttk.Button(cwin, text="Get it", style='small.TButton', command=getprefix, width=7)
    
    token_label = ttk.Label(cwin, text="Personal Token", width=20, anchor="e")
    token_entry = ttk.Entry(cwin, textvariable=token_text, width=TOKEN_SIZE)
    token_entry.bind('<FocusOut>', tokenedit)
    
    myprefix_label = ttk.Label(cwin, text="My namespace", width=20, anchor="e")
    myprefix_entry = ttk.Entry(cwin, textvariable=myprefix_text, width=TOKEN_SIZE)

    mnmn_label = ttk.Label(cwin, text="Manufacturer Name", width=20, anchor="e")
    mnmn_entry = ttk.Entry(cwin, textvariable=mnmn_text, width=25)
    
    devtype_label = ttk.Label(cwin, text="Device type", width=20, anchor="e")
    devtype_entry = ttk.Entry(cwin, textvariable=devtype_text, width=8)
    
    defpath_label = ttk.Label(cwin, text="Saved-json folder", width=20, anchor="e")
    defpath_entry = ttk.Entry(cwin, textvariable=defpath_text, width=40)
    
    token_label.grid(columnspan=1, column=0, row=3, pady=(10,5), padx=(0,8))
    token_entry.grid(columnspan=2, column=1, row=3, sticky=(W), pady=(10,5))
    myprefix_label.grid(columnspan=1, column=0, row=4, pady=(10,5), padx=(0,8))
    myprefix_entry.grid(columnspan=2, column=1, row=4, sticky=(W), pady=(10,5))
    getprefixbtn.grid(columnspan=1, column=3, row=4, sticky=(W), pady=(10,5), padx=(5,15))
    mnmn_label.grid(columnspan=1, column=0, row=5, pady=(5,5), padx=(0,8))
    mnmn_entry.grid(columnspan=2, column=1, row=5, sticky=(W), pady=(5,5))
    devtype_label.grid(columnspan=1, column=0, row=6, pady=(5,5), padx=(0,8))
    devtype_entry.grid(columnspan=2, column=1, row=6, sticky=(W), pady=(5,5))
    defpath_label.grid(columnspan=1, column=0, row=7, pady=(5,5), padx=(0,8))
    defpath_entry.grid(columnspan=3, column=1, row=7, sticky=(W),padx=(0,15), pady=(5,5))
    
    savebtn.grid(columnspan=1, column=1, row=8, pady=(10,10))
    cancelbtn.grid(columnspan=1, column=2, row=8, pady=(10,10))
    
    cwin.grid_columnconfigure(4, weight=1)
    cwin.grid_rowconfigure(9, weight=1)
    
    if (token_text.get() != ""):
        getprefixbtn.config(state="enable")
    else:
        getprefixbtn.config(state="disable")
    
    cwin.transient(root)
    cwin.wait_visibility()
    cwin.grab_set()
    cwin.wait_window()
    
def clonedev():
    
    my_mnmn = mnmn_text.get()
    defpath = defpath_text.get()
    myprefix = myprefix_text.get()
    retcode = False
    
    savedir = os.path.normpath(defpath+os.sep+my_mnmn)
    savetopath=savedir+os.sep+os.path.basename(devconfname)
    
    if not path.exists(savedir):
        os.mkdir(savedir)
    
    try:
        with open(devconfname, "r") as file:
            fullpydict = json.loads(file.read())
    
    except:
        statusmsg.set("File error reading device config json")
        return False
                
    # Update type element
    
    try:
        fullpydict["type"] = devtype_text.get()
        
    except:
        statusmsg.set("Can't update 'type' element in json")
        return False
    
    # Get rid of any account-specific elements
    
    try:
        del fullpydict["mnmn"]
        del fullpydict["manufacturerName"]
        del fullpydict["vid"]
        del fullpydict["presentationId"]
        del fullpydict["version"]
        del fullpydict["migration"]
    except:
        pass
        
    # Make sure it looks like a valid device config file
    
    try:
        dashboard = fullpydict["dashboard"]
        detailview = fullpydict["detailView"]
        automation = fullpydict["automation"]
        
    except:
        statusmsg.set("Invalid device config json")
        return False
    
    # Change custom capability prefix ids to our own prefix
                
    for dashitem in fullpydict["dashboard"]:

        for capitem in fullpydict["dashboard"][dashitem]:
            capability = capitem["capability"]
            _capability = capability.split('.',2)

            if len(_capability) == 2:
                capitem["capability"] = myprefix+'.'+_capability[1]

    for capitem in fullpydict["detailView"]:

        capability = capitem["capability"]
        _capability = capability.split('.',2)

        if len(_capability) == 2:
            capitem["capability"] = myprefix+'.'+_capability[1]
        
    for autoitem in fullpydict["automation"]:

        for capitem in fullpydict["automation"][autoitem]:
            capability = capitem["capability"]
            _capability = capability.split('.',2)

            if len(_capability) == 2:
                capitem["capability"] = myprefix+'.'+_capability[1]
    
    proceed = True
    if os.path.isfile(savetopath):
        msg = "OK to overwrite existing local device config file?"
        proceed = messagebox.askyesno(message=msg, icon='question', title='Confirm')
         
    if (proceed):
        
        # Write the updated json out to new file
        
        try:
            with open(savetopath, "w") as file:
                file.write(json.dumps(fullpydict, indent=4))
                
        except:
            statusmsg.set("File error writing new device config json file")    
            return False
            
        msg="New device config file saved: "+savetopath
        statusmsg.set(msg)   
        
        mydevconf.config(text=os.path.basename(devconfname))
        
        clonedmnmn_text.set('Manufacturer name: '+my_mnmn)
        
        newvidbtn2.config(state="enable")

        return True
            
    
def putcaps(incaplist, statlist, instat_cnames, selected_caps):
    
    errors = 0
    overwriteflag = False
    
    statusmsg.set("")
    defpath = defpath_text.get()
    prefixid = myprefix_text.get()

    if len(selected_caps) >= 1:
        
        stcaplist = getstcaplist()
        
        for index in selected_caps:
            
            capid = incaplist[index]
            _capid=capid.split(".",2)
            prefixid=_capid[0]
            capname=_capid[1]
            
            # Process custom capability
            
            filepath = os.path.normpath(defpath+os.sep+prefixid+os.sep+'capability'+os.sep+capname+'.json')
            
            try:
                with open(filepath, 'r') as f:
                    filejson=f.read()
            except:
                statusmsg.set("Error opening capability json file: "+capname)
                return False
                        
            if capid in stcaplist:
                
                # Capability exists; confirm to update
                
                proceed = True
                
                if overwriteflag == False:
                    msg = "OK to update existing capability?"
                    proceed = messagebox.askyesno(message=msg, icon='question', title='Confirm')
                    if proceed == True:
                        overwriteflag = True
                    else:
                        return False
                
                if (proceed):
                    buildURL=BASEURL+'/capabilities/'+capid+'/1'
                    r = requests.put(buildURL, headers=headers, data=json.dumps(json.loads(filejson), indent=4))
                    
                else:
                    break
            
            else:
                # Capability doesn't yet exist; create new capability
                
                buildURL=BASEURL+'/capabilities'
                r = requests.put(buildURL, headers=headers, data=json.dumps(json.loads(filejson), indent=4))

            # Capability created or updated; check return code

            if r.status_code == HTTP_OK:
                
                # Update the local capability file
                
                #   Get id from json in case it's changed
                
                pydict = json.loads(r.text)
                newcapid = pydict['id']
                _newcapid=newcapid.split(".",2)
                newcapname=_newcapid[1]
                
                newfilepath = os.path.normpath(defpath+os.sep+prefixid+os.sep+'capability'+os.sep+newcapname+'.json')
                
                try:
                    with open(newfilepath, 'w') as f2:
                        
                        f2.write(json.dumps(json.loads(r.text), indent=4))
                    
                except:
                    
                    statusmsg.set("Error writing capability json file: "+newcapname)
                    return False
                
            else:
                statusmsg.set("HTTP Error # "+str(r.status_code))
                errors += 1
                break        
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # Process presentation
            
            filepath = os.path.normpath(defpath+os.sep+prefixid+os.sep+'presentation'+os.sep+capname+'.json')
            
            try:
                with open(filepath, 'r') as f:
                    filejson=f.read()
            except:
                statusmsg.set("Error opening presentation json file: "+capname)
                return False
            
            buildURL=BASEURL+'/capabilities/'+capid+'/1/presentation'
                        
            if capid in stcaplist:
                
                # Presentation exists; confirm to update
                
                proceed = True
                msg = "OK to update existing presentation?"
                proceed = messagebox.askyesno(message=msg, icon='question', title='Confirm')
                
                if (proceed):
                    r = requests.put(buildURL, headers=headers, data=json.dumps(json.loads(filejson), indent=4))
                    
                else:
                    break
            
            else:
                # Presentation doesn't yet exist; create new capability
                
                r = requests.post(buildURL, headers=headers, data=json.dumps(json.loads(filejson), indent=4))

            # Presentation created or updated; check return code

            if r.status_code == HTTP_OK:
                
                # Update the local presentation file
                
                #   Get id from json in case it's changed
                
                pydict = json.loads(r.text)
                newcapid = pydict['id']
                _newcapid=newcapid.split(".",2)
                newcapname=_newcapid[1]
                
                newfilepath = os.path.normpath(defpath+os.sep+prefixid+os.sep+'presentation'+os.sep+newcapname+'.json')
                
                try:
                    with open(newfilepath, 'w') as f2:
                        
                        f2.write(json.dumps(json.loads(r.text), indent=4))
                        
                        statlist[index] = '⬆'
                    
                except:
                    
                    statusmsg.set("Error writing presentation json file: "+newcapname)
                    return False
                
            else:
                statusmsg.set("HTTP Error # "+str(r.status_code))
                errors += 1
                break
        
        # end for-loop
                
        if errors == 0:
            statusmsg.set("Selected capabilities (and presentations) updated in SmartThings")
            instat_cnames.set(statlist)
            return True
    else:
        statusmsg.set("No capabilities selected")
                
    return False
    
        
def putcaps1():
    
    putcaps(ref_caplist, ref_capstatlist, refstat_cnames, ref_caplistbox.curselection())
    
    
    
def putcaps2():
    
    putcaps(cre_caplist, cre_capstatlist, crestat_cnames, cre_caplistbox.curselection())


def cloneall():
    
    if clonedev():
    
        clonecaps()
    
        if (statusmsg.get() == "Capability conversion complete"):
            statusmsg.set("Conversion complete")
            submitallbtn.config(state="enable")
            
    
def newvid(deviceconfig):
    
    mnmn = mnmn_text.get()      # can only submit device configs for our own manufacturerName
    
    filepath = os.path.normpath(defpath_text.get()+os.sep+mnmn+os.sep+deviceconfig)
    
    try:
        with open(filepath, 'r') as f:
            pydict = json.loads(f.read())
            
    except:
        statusmsg.set("Error opening device config file")
        return False
            
    buildURL=BASEURL+'/presentation/deviceconfig'
    r = requests.post(buildURL, headers=headers, data=json.dumps(pydict, indent=4))
    
    if r.status_code == HTTP_OK:
        
        pydict = json.loads(r.text)
        
        if (mnmn != ""):
            if (mnmn != "SmartThingsCommunity"):
                pydict['manufacturerName'] = mnmn
                pydict['mnmn'] = mnmn
    
        try:
            with open(filepath, 'w') as f2:
                f2.write(json.dumps(pydict, indent=4))
                
        except:
            statusmsg.set("Error saving device config file")
            return False
                
        clonedmnmn_text.set('Manufacturer Name: '+pydict['manufacturerName'])
        presentid2.set(pydict['presentationId'])
        
        statusmsg.set("New presentation ID created; upload >"+filepath+"< to Developer Workspace")
        
        return True
        
    else:
        statusmsg.set("HTTP error # "+str(r.status_code))
        return False
    
        
def newvid1():

    newvid(devconf.cget("text"))

def newvid2():

    newvid(mydevconf.cget("text"))
    
    
def submitall():
    
    if putcaps(cre_caplist, cre_capstatlist, crestat_cnames, cre_caplistbox.curselection()):
    
        newvid(mydevconf.cget("text"))
    

def closefile():
    
    statusmsg.set("")
    resetall()
    
def cancelhelp():
    
    hwin.grab_release()
    hwin.destroy()
    
def showhelp():
    
    global hwin
    
    text = "\
    SmartThings Custom Capability Cloner\n\
    \n\
    Copyright 2021 Todd A. Austin  Version 1.20210411\n\
    \n\
    Problem:\n\
    - Sharing custom capabilities across accounts is not currently enabled for profile-based devices\n\
       (not applicable to legacy Groovy-based DTHs)\n\
    \n\
    Interim Solution:\n\
    - Custom capabilities (and their presentations) authored by others have to be manually replicated inside your own namespace.\n\
      This tool automates that process for you.\n\
    \n\n\
    MANDATORY FIRST STEP:\n\
    \n\
    Choose Preferences->Configure from the menu bar and fill out the fields - all are mandatory\n\
    \n\
      SmartThings Personal Token: required to perform restful API calls to SmartThings to get and update device definitions.\n\
      Namespace: Press the 'Get it' button if you don't know it.\n\
      Manufacturer Name: Can be gotten from your Developer Workspace profile if you don't know it.  Default is 'SmartThingsCommunity'\n\
      Device Type:  normally 'profile' but could also be 'DTH'\n\
      Saved-JSON folder:  this is the local directory where all JSON files will be stored.  Device configs will be saved in a subfolder\n\
            with name == device config Manufacturing Name.  Capabilities will be stored in a subfolder with name == namespace,\n\
            with further separate subfolders for capability files and presentation files.\n\
    \n\
    HOW TO USE:\n\
    \n\
    Everthing starts with an existing device configuration definition JSON file, which can be obtained in either of two ways:\n\
         a) The original developer provides the json file to you\n\
              Note: the original developer can strip the file of his/her own Presentation ID and Manufacturer Name, but if they didn't,\n\
              the tool will do that for you.\n\
         b) The original developer provides you the Presentation ID and Manufacturer Name and you retrieve the device config using this tool\n\
    \n\
    1. Use the menu bar 'File->Open local device config json file' for scenario (a) above, or 'File->Retrieve device config from SmartThings'\n\
       for scenario (b) above\n\
        - Once the device config is loaded, the custom capabilities it contains will be displayed.\n\
    \n\
    2. Be sure all capabilities are selected and click the 'RETRIEVE' buttton to download the custom capability definition JSON files\n\
       (including presentation JSON).\n\
    \n\
    3. Click the 'COPY ALL' button to clone the device config and custom capabilities to files onto your local disk.\n\
    \n\
    4. Be sure all capabilities in the righthand listbox are selected and click the 'SUBMIT ALL' button\n\
        - Capabilities will be submitted to SmartThings to be created under your own namespace\n\
        - A new device config Presentation ID (vid) will be generated by SmartThings.\n\
        - All JSON returned by SmartThings will be saved locally.\n\
    \n\
    The returned & saved device config JSON file can now be uploaded to the Developer Workspace to complete your device profile UI Display\n\
    definition.  (There you will be using the 'Customize through device configuration file' option)\n\
    \n\
    Additional Info\n\
    \n\
    To the right of the capability list boxes is a column which shows the progress of capability processing:\n\
         ⇩ - indicates local files were found for the capability, but they may not be up-to-date (press the 'Retrieve' button)\n\
         ⬇ - indicates the capability (and its associated presentation) was just downloaded via the 'Retrieve' button, or just copied\n\
         ⬆ - indicates the capability was successfully submitted to SmartThings via the 'Submit' button (it was created or updated)\n\
    \n\
    TIP: It's always a good idea to do a new 'Retrieve' from SmartThings to be sure you are working with the latest definition files\n\
    \n\
    Additional Features\n\
    \n\
    The tool also allows for more granular control of working with device configs and custom capabilities:\n\
        - Select individual capabilities in the listboxes to download, clone, or submit to SmartThings\n\
        - Instead of using the blue highlighted 'COPY ALL' and 'SUBMIT ALL' buttons, individual buttons are provided for more\n\
          stepwise control of copy and update submissions to SmartThings.\n\
    \n\
    Any SmartThings device configuration - yours or other author's - can be retrieved for examination and download of referenced capability\n\
    JSON files.\n\
    \n\
    Any locally saved device configuration file can be opened with the tool and, for your own device configs and capabilities, submitted to\n\
    Smartthings for updates. Your device configs will be saved in a subdirectory with name equal to your configured Manufacturer Name.  Your\n\
    cloned custom capabilities are saved in a subdirectory with name equal to your SmartThings namespace.\n\
    \n\
        - Retrieve the latest files from SmartThings, use an editor of your choice to modify the local JSON files, then Submit to SmartThings\n\
          to update\n\
    "
    
    hwin = Toplevel(root)
    hwin.title('Help')
    hwin.protocol("WM_DELETE_WINDOW", cancelhelp)
    hwin.resizable(FALSE, FALSE)
    
    helptext = scrolledtext.ScrolledText(hwin, width=150, height=30)
    helptext.grid(column=0, row=0, sticky=N+S+E+W)
    helptext.insert(END, text)
    helptext.configure(state="disabled")
    
    hwin.grid_columnconfigure(3, weight=1)
    hwin.grid_rowconfigure(5, weight=1)
    hwin.transient(root)
    hwin.wait_visibility()
    hwin.grab_set()
    hwin.wait_window()
    
    
def exitfunc():

    exit(0)
    

##########################################################################
#                             * MAIN *
##########################################################################

if __name__ == '__main__':

    global CONFIGFILE
    global HOMEPATH
    global menubar

    ostype = platform.system()
    if ostype == "Linux":
        HOMEPATH = os.environ['HOME']
    elif ostype == "Windows":
        HOMEPATH = os.environ['HOMEPATH']
    else:
        print ("Unrecognized OS platform\n")
        exit -1
        
    CONFIGFILE = HOMEPATH+os.sep+".stcapcfg"
    
    currentdir  = os.getcwd()

    # TKINTER INITIALIZATION STUFF

    root.title("SmartThings Device Config Replicator")

    c = ttk.Frame(root, padding="3 3 12 12")
    c.grid(column=0, row=0, sticky=(N, W, E, S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.option_add('*tearOff', FALSE)

    # STYLE STUFF

    fname_fontStyle = tkFont.Font(family="Raleway", size=10)
    label_fontStyle = tkFont.Font(family="Raleway", size=10)
    smlabel_fontStyle = tkFont.Font(family="Raleway", size=8)

    hilite = ttk.Style()
    hilite.configure('hilite.TButton', foreground="blue")

    # MENU STUFF

    menubar = Menu(root)
    root['menu'] = menubar

    menu_file = Menu(menubar)
    menubar.add_cascade(menu=menu_file, label='File')
    menu_file.add_command(label='Open local Device Config json file...', command=opencfg)
    menu_file.add_command(label='Retrieve Device Config from SmartThings...', command=retrievecfg)
    menu_file.add_command(label='Close file', command=closefile)
    menu_file.add_command(label='Exit', command=exitfunc)

    menu_config = Menu(menubar)
    menubar.add_cascade(menu=menu_config, label='Preferences')
    menu_config.add_command(label='Configure', command=getconfig)

    menu_help = Menu(menubar)
    menubar.add_cascade(menu=menu_help, label='Help')
    menu_help.add_command(label='About', command=showhelp)


    # WIDGET DEFINITIONS

    devmnmn_label = ttk.Label(c, textvariable=devmnmn_text, anchor="center", width=40)
    clonedmnmn_label = ttk.Label(c, textvariable=clonedmnmn_text, anchor="center", width=40)

    devconf = ttk.Label(c, text="", width=40, anchor="center", background="ivory", foreground="blue")
    mydevconf = ttk.Label(c, text="", width=40, anchor="center", background="ivory", foreground="blue")
    presentid_label1 = ttk.Label(c, textvariable=presentid1, anchor="center", width=40, font=smlabel_fontStyle)
    presentid_label2 = ttk.Label(c, textvariable=presentid2, anchor="center", width=40, font=smlabel_fontStyle)

    ref_caplistbox = Listbox(c, listvariable=ref_cnames, height=8, width=40, selectmode="extended")
    ref_capstatbox = Listbox(c, listvariable=refstat_cnames, height=8, width=2, selectmode="extended", foreground="dark green")

    cre_caplistbox = Listbox(c, listvariable=cre_cnames, height=8, width=40, selectmode="extended")
    cre_capstatbox = Listbox(c, listvariable=crestat_cnames, height=8, width=2, selectmode="extended", foreground="dark green")

    ref_capslabel = ttk.Label(c, text="Custom Capabilities in device config", font=label_fontStyle)
    cre_capslabel = ttk.Label(c, text="Cloned Custom Capabilities", font=label_fontStyle)
    getcapbtn = ttk.Button(c, text="RETRIEVE", command=getcaps, state="disabled", style='hilite.TButton')
    putcapbtn1 = ttk.Button(c, text="Submit", command=putcaps1, state="disabled")
    putcapbtn2 = ttk.Button(c, text="Submit", command=putcaps2, state="disabled")
    clonecapbtn = ttk.Button(c, text=">> Copy CCs Only >>", command=clonecaps, state="disabled")
    statuslabel = ttk.Label(c, textvariable=statusmsg, width=90, anchor="w", font=fname_fontStyle, foreground="brown")
    clonedevbtn = ttk.Button(c, text=">> Copy Device Config File >>", command=clonedev, state="disabled")
    cloneallbtn = ttk.Button(c, text=">> COPY ALL >>", command=cloneall, state="disabled", style='hilite.TButton')
    newvidbtn1 = ttk.Button(c, text="Submit for new vid", command=newvid1, state="disabled")
    newvidbtn2 = ttk.Button(c, text="Submit for new vid", command=newvid2, state="disabled")
    submitallbtn = ttk.Button(c, text="SUBMIT ALL", command=submitall, state="disabled", style='hilite.TButton')

    # WIDGET GRID PLACEMENT

    devmnmn_label.grid(columnspan=2, column=0, row=1, sticky=S, pady=(5,0), padx=(15,0))
    clonedmnmn_label.grid(columnspan=2, column=4, row=1, sticky=SW, pady=(5,0))

    devconf.grid(columnspan=2, column=0, row=2, padx=(20,0), pady=(5,0))
    mydevconf.grid(columnspan=3, column=4, row=2, pady=(5,0))
    presentid_label1.grid(columnspan=2, column=0, row=3, pady=(3,2), padx=(20,0))
    presentid_label2.grid(columnspan=2, column=4, row=3, pady=(3,2))

    cloneallbtn.grid(column=3, row=0, sticky=N, pady=(15,0), padx=(0,0))
    submitallbtn.grid(columnspan=2, column=4, row=0, sticky=N, pady=(15,15), padx=(0,0))
    clonedevbtn.grid(column=3, row=2, pady=(10,0), padx=(5,15))
    clonecapbtn.grid(column=3, row=7, padx=(0,0))

    ref_capslabel.grid(columnspan=2, column=0, row=6, padx=(15,0), pady=(10,0))
    ref_caplistbox.grid(columnspan=2, rowspan=2, column=0, row=7, sticky=E, padx=(15,0))
    ref_capstatbox.grid(columnspan=1, rowspan=2, column=2, row=7, sticky=W, padx=(0,0))

    newvidbtn1.grid(columnspan=2, column=0, row=4, pady=(0,30))
    newvidbtn2.grid(columnspan=2, column=4, row=4, pady=(0,30))

    cre_capslabel.grid(columnspan=2, column=4, row=6, pady=(10,0))
    cre_caplistbox.grid(columnspan=2, rowspan=2, column=4, row=7)
    cre_capstatbox.grid(columnspan=1, rowspan=2, column=8, row=7, sticky=W)

    getcapbtn.grid(columnspan=1, column=0, row=9, padx=(0,0), pady=(10,10))
    putcapbtn1.grid(columnspan=1, column=1, row=9, padx=(0,0), pady=(10,10))
    putcapbtn2.grid(columnspan=2, column=4, row=9, padx=(0,0), pady=(10,10))

    statuslabel.grid(columnspan=6, column=0, row=10, sticky=W, pady=(15,0), padx=(20,0))
      
    c.grid_columnconfigure(8, weight=1)
    c.grid_rowconfigure(11, weight=1)

    readcfg()

    print ("\nSmartThings Device Config Replicator starting in GUI\n")

    root.mainloop()
