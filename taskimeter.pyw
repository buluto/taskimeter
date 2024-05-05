#-------------------------------------------------------------------------------
# Name:        Taskimeter
# Purpose:     Task time tracking
# Version:     1.3
#
# Author:      Bulut Ozturk < firstname dot lastname at gmail dot com >
#
# Created:     24/11/2014
#-------------------------------------------------------------------------------
# Copyright (c) 2014-2024 Bulut Ozturk
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#-------------------------------------------------------------------------------

import os,sys,subprocess,base64
from datetime import date,time,datetime,timedelta
from tkinter import mainloop,Tk,Frame,Label,Menu,Menubutton,Button,Text, \
                    StringVar,BOTH,END,W,E,N,S,X,Y
from tkinter.simpledialog import askstring,messagebox

class App(Frame):

    def __init__(self,parent):

        Frame.__init__(self,parent)
        self.parent = parent
        self.initUI()

    def initUI(self):

        self.parent.title("Taskimeter")
        self.pack(fill=BOTH,expand=1)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Task list
        mbtn = Menubutton(self)
        self.mdrp = Menu(mbtn,tearoff=0,
                         postcommand=lambda: self.menuRefresh())
        mbtn.configure(relief='solid',textvariable=cur.name,
                       background='#ffffff',activebackground='#ffffff',
                       menu=self.mdrp)
        mbtn.grid(row=0,column=0,padx=1,pady=1,sticky=W+E+N+S)

        # Time
        ctim = Label(self,textvariable=cur.duration)
        ctim.configure(relief='groove')
        ctim.grid(row=0,column=1,columnspan=1,rowspan=1,
                     padx=0,pady=0,sticky=W+E+N+S)

        # Log
        dbtn = Button(self,text=ldict['g_log'],
                      command=lambda: self.showLog(),
                      relief='groove')
        dbtn.grid(row=1,column=0,padx=0,pady=0,sticky=W+E+N+S)

        # Start/stop timer
        tbtn = Button(self,text=ldict['g_stop'],
                      command=lambda: self.startStop(),
                      relief='groove')
        tbtn.grid(row=1,column=1,padx=0,pady=0,sticky=W+E+N+S)

        # Recover last task from crash or shutdown
        self.recover()

    def recover(self):

        # Read current task file
        cfile = open(os.path.join(abspath,'res','current.txt'),'r',encoding='utf-8')
        clist = cfile.readlines()
        cfile.close()

        for line in clist:
            cline = line.strip('\ufeff\n')
            if   cline[:1] == '#': # Ignore comment lines
                continue
            try:
                # Update log file
                lfile = open(os.path.join(abspath,'res','log.csv'),'a',encoding='utf-8')
                lline = '\n'+cline
                lfile.writelines(lline)
                lfile.close()
                # Reset current task file
                cfile = open(os.path.join(abspath,'res','current.txt'),'w',encoding='utf-8')
                cfile.close()
            except:
                ebox = messagebox.showerror(ldict['t_error'],ldict['c_logfile'])
                return

    def startStop(self):

        # If timer is off
        if   cur.active == False and cur.name.get() != blank:
            self.start()
        # If timer is on
        elif cur.active == True:
            self.stop()

    def start(self):

        detail = askstring(blank,ldict['c_detail'])
        if detail == None:
            cur.reset()
            return
        cur.detail.set(detail.strip(sep))
        cur.start = datetime.now()
        cur.active = True

    def stop(self):

        if cur.duration.get()[0:4] != '0:00': # Record iff duration > 1 min
            # Review task details
            detail = askstring(blank,ldict['c_detail'],initialvalue=cur.detail.get())
            if detail == None:
                return
            cur.detail.set(detail.strip(sep))
            try:
                # Update log file
                lfile = open(os.path.join(abspath,'res','log.csv'),'a',encoding='utf-8')
                lline = '\n'+str(cur.start)[:10]+sep+str(cur.start)[11:19]+sep+ \
                        cur.duration.get()+sep+cur.name.get()+sep+cur.detail.get()
                lfile.writelines(lline)
                lfile.close()
            except:
                ebox = messagebox.showerror(ldict['t_error'],ldict['c_logfile'])
                return
        # Reset current task file
        cfile = open(os.path.join(abspath,'res','current.txt'),'w',encoding='utf-8')
        cfile.close()
        # Reset current task
        cur.reset()
        cur.active = False

    def menuRefresh(self):

        # Read tasks file...
        tfile = open(os.path.join(abspath,'res','tasks.txt'),'r',
                     encoding='utf-8')
        tlist = tfile.readlines()
        tfile.close()

        # ...and add to menu
        self.mdrp.delete(0,END)
        for line in tlist:
            task = line.strip('\ufeff\n')
            if task[:1] == '#': # Ignore comment lines
                continue
            self.mdrp.add_command(label=line,
                                  command=lambda i=task: self.menuAction(i))
        self.mdrp.add_separator()
        self.mdrp.add_command(label=ldict['g_edit'],
                              command=lambda i='<edit>': self.menuAction(i))

    def menuAction(self,arg):

        # 'Edit' selected
        if   arg == '<edit>':
            filepath = os.path.join(abspath,'res','tasks.txt')
            if sys.platform.startswith('darwin'):
                subprocess.call(('open', filepath))
            elif os.name == 'nt':
                os.startfile(filepath)
            elif os.name == 'posix':
                subprocess.call(('xdg-open', filepath))
        # New task selected
        elif cur.active == False:
            cur.name.set(arg)
            self.startStop()
        elif cur.active == True:
            self.stop()
            if cur.active == True:
                return
            cur.name.set(arg)
            self.start()

    def showLog(self):

        filepath = os.path.join(abspath,'res','log.csv')
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', filepath))
        elif os.name == 'nt':
            os.startfile(filepath)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', filepath))

    def showPrefs(self):

        filepath = os.path.join(abspath,'res','prefs.txt')
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', filepath))
        elif os.name == 'nt':
            os.startfile(filepath)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', filepath))

    def showAbout(self):

        ibox = messagebox.showinfo(ldict['t_about'],
                                   "Taskimeter v1.3\n"+
                                   "\u00a9 2014-2024 Bulut \u00d6zt\u00fcrk\n")

    def openDir(self):

        if sys.platform.startswith('darwin'):
            subprocess.call(('open', abspath))
        elif os.name == 'nt':
            os.startfile(abspath)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', abspath))

class CurrentTask():

    def __init__(self):

        # Variables
        self.name = StringVar()
        self.name.set(blank)
        self.detail = StringVar()
        self.detail.set(blank)
        self.duration = StringVar()
        self.duration.set('0:00:00')
        self.start = datetime.min
        self.active = False

    def reset(self):

        self.name.set(blank)
        self.duration.set('0:00:00')

class Timer():

    def __init__(self):

        self.update()

    def update(self):

        # Update timer
        if cur.active == True:
            diff = datetime.now() - cur.start
            cur.duration.set(str(diff)[:8].strip('.'))
            # Update current task file every minute
            if cur.duration.get()[0:4] != '0:00' and cur.duration.get()[5:7] == '00':
                lfile = open(os.path.join(abspath,'res','current.txt'),'w',encoding='utf-8')
                lline = '\ufeff'+str(cur.start)[:10]+sep+str(cur.start)[11:19]+sep+ \
                        cur.duration.get()+sep+cur.name.get()+sep+cur.detail.get().strip(sep)
                lfile.writelines(lline)
                lfile.close()
        app.after(1000,self.update) # repeat in ~1 sec

def closeApp():

    # Save ongoing activity
    if cur.active == True:
        app.startStop()
    # Save window position
    setPrefs('posx',str(root.winfo_x()))
    setPrefs('posy',str(root.winfo_y()))
    # Close window
    root.destroy()

def createMissing():

    # res folder
    respath = os.path.join(abspath,'res')
    if os.path.exists(respath) == False:
        os.makedirs(respath)

    # Default content for flat files
    rlist = {'tasks.txt'  :'\ufeff# Add one task per line. Comment lines such as this one ignored.\n',
             'prefs.txt'  :'\ufeff# All changes require restart to take effect.\n'+
                           'lang=en\n'+
                           'alwaysontop=1\n'+
                           'toolwindow=1\n'+
                           'posx=300\n'+
                           'posy=300\n'+
                           'csvsep=;',
             'log.csv'    :'\ufeffsep=;\n'+
                           'Date;Start;Duration;Task;Details',
             'lang_en.txt':'\ufeff# GUI elements\n'+
                           'g_edit=Edit\n'+
                           'g_stop=Stop\n'+
                           'g_log=Log\n'+
                           '# Dialog window titles\n'+
                           't_detail=Detail\n'+
                           't_about=About Taskimeter\n'
                           't_error=Error\n'+
                           '# Dialog window content\n'+
                           'c_detail=Detail of activity\n'+
                           'c_logfile=Please close the log file (log.csv) and try again.',
             'current.txt':'\ufeff'}

    for fnam in rlist:
        try:
            nfile = open(os.path.join(abspath,'res',fnam),'r')
            nfile.close()
        except:
            nfile = open(os.path.join(abspath,'res',fnam),'w',encoding='utf-8')
            nfile.write(rlist[fnam])
            nfile.close()

def readPrefs():

    # Read prefs file
    pfile = open(os.path.join(abspath,'res','prefs.txt'),'r',encoding='utf-8')
    plist = pfile.readlines()
    pfile.close()

    # Read and populate prefs dict
    global pdict
    pdict = {'alwaysontop':blank,'toolwindow':blank,'posx':blank,'posy':blank,
             'csvsep':blank,'lang':blank}
    # = separates parameter (left) and value (right)
    for line in plist:
        pline = line.strip('\ufeff\n')
        if pline[:1] == '#': # Ignore comment lines
            continue
        pitem = pline.split('=')
        try:
            pdict[pitem[0]] = pitem[1]
        except:
            pass

    global sep
    sep = pdict['csvsep']

def readLang():

    # Read language file
    lfile = open(os.path.join(abspath,'res','lang_'+pdict['lang']+'.txt'),'r',encoding='utf-8')
    llist = lfile.readlines()
    lfile.close()

    global ldict
    ldict = {}

    for line in llist:
        lline = line.strip('\ufeff\n')
        if lline[:1] == '#': # Ignore comment lines
            continue
        litem = lline.split('=')
        ldict[litem[0]] = litem[1]

def setPrefs(pnam,pval):

    # Read prefs file
    pfile = open(os.path.join(abspath,'res','prefs.txt'),'r',encoding='utf-8')
    plist = pfile.readlines()
    pfile.close()

    # Update prefs dict value
    pdict[pnam] = pval

    # Update prefs file
    prefi = blank # Pref item
    prefl = blank # Pref line
    # = separates parameter (left) and value (right)
    for line in plist:
        pline = line.strip('\ufeff\n')
        if pline[:1] == '#': # Ignore comment lines
            continue
        pitem = pline.split('=')
        if pitem[0] == pnam:
            prefi = pnam+'='+pval+'\n'
        else:
            prefi = line
        prefl+=prefi
    # Regenerate prefs file
    pfile = open(os.path.join(abspath,'res','prefs.txt'),'w',encoding='utf-8')
    pfile.writelines(prefl)
    pfile.close()

def handleKeys(arg, event=None):

    # About
    if   arg == 'abt':
        app.showAbout()
    # Prefs
    elif arg == 'prf':
        app.showPrefs()
    # Log
    elif arg == 'log':
        app.showLog()
    # Directory
    elif arg == 'dir':
        app.openDir()

if __name__ == '__main__':

    # Create root object
    root = Tk()

    # Path to .py or .exe file
    global abspath
    #abspath = os.path.abspath(os.path.dirname(sys.executable))
    abspath = os.path.abspath(os.path.dirname(__file__))

    # Blank string
    global blank
    blank = ""

    # Create missing files
    createMissing()

    # Preferences
    readPrefs()

    # Language
    readLang()

    # Non-resizable
    root.resizable(0,0)
  
    # Window dimensions (x,y) and position (x,y)
    root.geometry('200x65+300+300')
    try:
        if int(pdict['posx']) < root.winfo_screenwidth() and int(pdict['posy']) < root.winfo_screenheight():
            root.geometry('200x65+'+pdict['posx']+'+'+pdict['posy'])
    except:
        pass

    # Window on top
    root.wm_attributes('-topmost',1)
    try:
        root.wm_attributes('-topmost',pdict['alwaysontop'])
    except:
        pass

    # Tool window
    root.wm_attributes('-toolwindow', 1)
    try:
        root.wm_attributes('-toolwindow',pdict['toolwindow'])
    except:
        pass
  
    # When closing
    root.protocol('WM_DELETE_WINDOW',lambda: closeApp())

    # Keyboard shortcuts
    root.bind('<Control_L>a',lambda event=None, i='abt': handleKeys(i))
    root.bind('<Control_R>a',lambda event=None, i='abt': handleKeys(i))
    root.bind('<Control_L>A',lambda event=None, i='abt': handleKeys(i))
    root.bind('<Control_R>A',lambda event=None, i='abt': handleKeys(i))
    root.bind('<Control_L>p',lambda event=None, i='prf': handleKeys(i))
    root.bind('<Control_R>p',lambda event=None, i='prf': handleKeys(i))
    root.bind('<Control_L>P',lambda event=None, i='prf': handleKeys(i))
    root.bind('<Control_R>P',lambda event=None, i='prf': handleKeys(i))
    root.bind('<Control_L>l',lambda event=None, i='log': handleKeys(i))
    root.bind('<Control_R>l',lambda event=None, i='log': handleKeys(i))
    root.bind('<Control_L>L',lambda event=None, i='log': handleKeys(i))
    root.bind('<Control_R>L',lambda event=None, i='log': handleKeys(i))
    root.bind('<Control_L>f',lambda event=None, i='dir': handleKeys(i))
    root.bind('<Control_R>f',lambda event=None, i='dir': handleKeys(i))
    root.bind('<Control_L>F',lambda event=None, i='dir': handleKeys(i))
    root.bind('<Control_R>F',lambda event=None, i='dir': handleKeys(i))

    # Create other objects
    cur = CurrentTask()
    app = App(root)
    tmr = Timer()

    # Main loop
    root.mainloop()
