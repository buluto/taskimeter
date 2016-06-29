#-------------------------------------------------------------------------------
# Name:        Taskimeter
# Purpose:     Task time tracking
# Version:     1.0
#
# Author:      Bulut Ozturk < firstname dot lastname at gmail dot com >
#
# Created:     24/11/2014
#-------------------------------------------------------------------------------
# Copyright (c) 2014-2016 Bulut Ozturk
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

import webbrowser

class App(Frame):

    def __init__(self,parent):

        Frame.__init__(self,parent)
        self.parent = parent
        self.initUI()

    def initUI(self):

        self.parent.title("Taskimeter")
        self.pack(fill=BOTH,expand=1)

        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)

        # task list
        mbtn = Menubutton(self)
        self.mdrp = Menu(mbtn,tearoff=0,
                         postcommand=lambda: self.menuRefresh())
        mbtn.configure(relief='solid',textvariable=cur.name,
                       background='#ffffff',activebackground='#ffffff',
                       menu=self.mdrp)
        mbtn.grid(row=0,column=0,padx=2,pady=3,sticky=W+E+N+S)

        # Time
        curtime = Label(self,textvariable=cur.duration)
        curtime.configure(relief='groove',width=6)
        curtime.grid(row=0,column=1,columnspan=1,rowspan=1,
                     padx=2,pady=3,sticky=W+E+N+S)

        # Start/stop timer
        tbtn = Button(self,text=ldict['g_stop'],command=lambda: self.startstop(),
                      relief='groove',width=3)
        tbtn.grid(row=0,column=2,padx=0,pady=3,sticky=W+E+N+S)

        # Timesheet
        cbtn = Button(self,text=ldict['g_timesheet'],command=lambda: self.clicktime(),
                      relief='groove',width=6)
        cbtn.grid(row=1,column=0,padx=2,pady=3,sticky=W+E+N+S)

        # Alarm
        abtn = Button(self,text=ldict['g_alarm'],command=lambda: self.setAlarm(),
                      relief='groove')
        abtn.grid(row=1,column=1,padx=2,pady=3,sticky=W+E+N+S)

        # Log
        dbtn = Button(self,text=ldict['g_log'],command=lambda: self.showLog(),
                      relief='groove')
        dbtn.grid(row=1,column=2,padx=0,pady=3,sticky=W+E+N+S)

    def startstop(self):

        # If timer is off
        if   cur.active == False and cur.name.get() != empty:
            self.start()
        # If timer is on
        elif cur.active == True:
            self.stop()

    def start(self):

        cur.start = datetime.now()
        cur.active = True

    def stop(self):

        cur.active = False
        detail = askstring(empty,
                           ldict['c_detail'])
        if detail == None:
            detail = empty
        sep = pdict['csvsep']
        lfile = open(os.path.join(abspath,'res','log.csv'),'a',encoding='utf-8')
        lline = '\n'+str(cur.start)[:10]+sep+str(cur.start)[11:19]+sep+ \
                cur.duration.get()+sep+cur.name.get()+sep+detail.strip(sep)
        lfile.writelines(lline)
        lfile.close()
        cur.name.set(empty)
        cur.duration.set('0:00:00')

    def menuRefresh(self):

        # Read tasks file...
        tfile = open(os.path.join(abspath,'res','tasks.txt'),'r',
                     encoding='utf-8')
        tlist = tfile.readlines()
        tfile.close()

        # ...and add to menu
        self.mdrp.delete(0,END)
        for line in tlist:
            if line.strip('\ufeff')[:1] == '#': # Ignore comment lines
                continue
            self.mdrp.add_command(label=line,
                                  command=lambda i=line: self.menuAction(i))
        self.mdrp.add_separator()
        self.mdrp.add_command(label=ldict['g_edit'],
                              command=lambda i='<edit>': self.menuAction(i))

    def menuAction(self,arg):

        if   arg == '<edit>':
            filepath = os.path.join(abspath,'res','tasks.txt')
            if sys.platform.startswith('darwin'):
                subprocess.call(('open', filepath))
            elif os.name == 'nt':
                os.startfile(filepath)
            elif os.name == 'posix':
                subprocess.call(('xdg-open', filepath))
        elif cur.active == False:
            cur.name.set(arg.strip('\n'))
            self.startstop()
        elif cur.active == True:
            self.startstop()
            cur.name.set(arg.strip('\n'))
            self.startstop()

    def clicktime(self):

        if pdict['tsurl'] in (None, empty):
            ebox = messagebox.showerror(ldict['t_openurlerr'],ldict['c_openurlerr'])
            return
        webbrowser.open(pdict['tsurl'])

    def setAlarm(self):

        alarm = askstring(ldict['t_alarm'],ldict['c_alarm'].replace('&',pdict['alarm']))
        if   alarm in (None,empty):
            return
        elif len(alarm) != 5 or \
            alarm[2] != ':' or \
            int(alarm[0:2]) > 24 or \
            int(alarm[3:5]) > 59:
            ebox = messagebox.showerror(ldict['t_alarmerr'], ldict['c_alarmerr'])
            return
        setPrefs('alarm',alarm)

    def showLog(self):

        filepath = os.path.join(abspath,'res','log.csv')
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', filepath))
        elif os.name == 'nt':
            os.startfile(filepath)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', filepath))

class CurrentTask():

    def __init__(self):

        # Variables
        self.name = StringVar()
        self.name.set(empty)
        self.duration = StringVar()
        self.duration.set('0:00:00')
        self.start = datetime.min
        self.active = False

class Timer():

    def __init__(self):

        self.alarmStat = False
        self.update()

    def update(self):

        # Update timer
        if cur.active == True:
            diff = datetime.now() - cur.start
            cur.duration.set(str(diff)[:8].strip('.'))
        # Display reminder if time for alarm
        if pdict['alarm'] == datetime.now().strftime('%H:%M') and \
           self.alarmStat == False:
            wbox = messagebox.showwarning(ldict['t_remind'],ldict['c_remind'])
            self.alarmStat = True
        app.after(1000,self.update) # repeat in ~1 sec

def closeApp():

    # Save ongoing activity
    if cur.active == True:
        app.startstop()
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
    rlist = {'tasks.txt'  :'\ufeff# Add tasks below (one per line)\n',
             'prefs.txt'  :'\ufeff'+
                           'alwaysontop=1\n'+
                           'posx=300\n'+
                           'posy=300\n'+
                           'alarm=09:30\n'+
                           'tsurl=\n'+
                           'csvsep=;\n'+
						   'lang=en',
             'log.csv'    :'\ufeffsep=;\n'+
                           'Date;Start;Duration;Task;Details',
             'lang_en.txt':'\ufeff# GUI elements\n'+
                           'g_edit=Edit\n'+
                           'g_stop=Stop\n'+
                           'g_timesheet=Timesheet\n'+
                           'g_log=Log\n'+
                           'g_alarm=Rmdr\n'+
                           '# Dialog window titles\n'+
                           't_detail=Detail\n'+
                           't_alarm=Set Reminder\n'+
                           't_remind=Reminder\n'+
                           't_alarmerr=Error\n'+
                           't_openurlerr=Error\n'+
                           't_about=About\n'+
                           '# Dialog window content\n'+
                           'c_detail=      Detail of work performed      \n'+
                           'c_alarm=Set reminder to (Current &):\n'+
                           'c_alarmerr=Invalid format. Use HH:MM (24h).\n'+
                           'c_remind=Have you recorded your time worked?\n'+
                           'c_openurlerr=No URL or command defined for timesheet.\n'}

    for fnam in rlist:
        try:
            nfile = open(os.path.join(abspath,'res',fnam),'r')
            nfile.close()
        except:
            nfile = open(os.path.join(abspath,'res',fnam),'w',encoding='utf-8')
            nfile.write(rlist[fnam])
            nfile.close()

    # Default content for binary files
    blist = {'icon.ico'   :base64.b64decode(
                           'AAABAAEAICAAAAEAGACoDAAAFgAAACgAAAAgAAAAQAAAAAEAGAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAOyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oy'+
                           'f8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8O'+
                           'yf8Oyf8Oyf8Oyf8Oyf8AAAAAAAAAAAAAAAAAAAAAAAAOyf8Oyf8'+
                           'Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf'+
                           '8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oy'+
                           'f8AAAAAAAAAAAAOyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8O'+
                           'yf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8'+
                           'Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8AAAAOyf8Oyf8Oyf8Oyf'+
                           '8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oy'+
                           'f8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8O'+
                           'yf8Oyf8AAAAOyf8Oyf8Oyf8Oyf8AAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAOyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oy'+
                           'f8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOyf8'+
                           'Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8AAAAVAIgkHO0kHO0VAIgAAA'+
                           'AVAIgkHO0kHO0VAIgAAAAAAAAAAAAAAAAAAAAAAAAAAAAVAIgAA'+
                           'AAVAIgkHO0kHO0VAIgAAAAOyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8O'+
                           'yf8AAAAkHO0AAAAAAAAkHO0AAAAkHO0AAAAAAAAkHO0AAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAkHO0AAAAkHO0AAAAAAAAkHO0AAAAOyf'+
                           '8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8AAAAkHO0AAAAAAAAkHO0AA'+
                           'AAkHO0AAAAAAAAkHO0AAAAAAAAkHO0AAAAAAAAAAAAAAAAkHO0A'+
                           'AAAkHO0AAAAAAAAkHO0AAAAOyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8'+
                           'Oyf8AAAAkHO0AAAAAAAAkHO0AAAAkHO0AAAAAAAAkHO0AAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAkHO0AAAAkHO0AAAAAAAAkHO0AAAAOy'+
                           'f8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8AAAAkHO0AAAAAAAAkHO0A'+
                           'AAAVAIgkHO0kHO0VAIgAAAAAAAAAAAAAAAAAAAAAAAAAAAAkHO0'+
                           'AAAAkHO0AAAAAAAAkHO0AAAAOyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf'+
                           '8Oyf8AAAAkHO0AAAAAAAAkHO0AAAAkHO0AAAAAAAAkHO0AAAAAA'+
                           'AAkHO0AAAAAAAAAAAAAAAAkHO0AAAAkHO0AAAAAAAAkHO0AAAAO'+
                           'yf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8AAAAkHO0AAAAAAAAkHO0'+
                           'AAAAkHO0AAAAAAAAkHO0AAAAAAAAAAAAAAAAAAAAAAAAAAAAkHO'+
                           '0AAAAkHO0AAAAAAAAkHO0AAAAOyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oy'+
                           'f8Oyf8AAAAkHO0AAAAAAAAkHO0AAAAkHO0AAAAAAAAkHO0AAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAkHO0AAAAkHO0AAAAAAAAkHO0AAAA'+
                           'Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8AAAAVAIgkHO0kHO0VAI'+
                           'gAAAAVAIgkHO0kHO0VAIgAAAAAAAAAAAAAAAAAAAAAAAAAAAAVA'+
                           'IgAAAAVAIgkHO0kHO0VAIgAAAAOyf8Oyf8Oyf8Oyf8Oyf8Oyf8O'+
                           'yf8Oyf8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AOyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8AAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAOyf8Oyf8Oyf8Oyf8Oyf8Oyf8'+
                           'Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf'+
                           '8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oy'+
                           'f8Oyf8Oyf8Oyf8AAAAAAAAOyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8O'+
                           'yf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8'+
                           'Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8AAAAAAAAAAA'+
                           'AOyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oy'+
                           'f8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8O'+
                           'yf8Oyf8Oyf8AAAAAAAAAAAAAAAAAAAAAAAAOyf8Oyf8Oyf8Oyf8'+
                           'Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf'+
                           '8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8Oyf8AAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///'+
                           '////////////////////////AAAA/AAAADgAAAAQAAAAEAAAAAA'+
                           'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+
                           'AAAAAAAAAAAAAAAAAYAAAAHAAAAD8AAAD/wf+D/8H/g////////'+
                           '//////////////w==')}

    for fnam in blist:
        try:
            nfile = open(os.path.join(abspath,'res',fnam),'rb')
            nfile.close()
        except:
            nfile = open(os.path.join(abspath,'res',fnam),'wb')
            nfile.write(blist[fnam])
            nfile.close()

def readPrefs():

    # Read prefs file
    pfile = open(os.path.join(abspath,'res','prefs.txt'),'r',encoding='utf-8')
    plist = pfile.readlines()
    pfile.close()

    # Read and populate prefs dict
    global pdict
    pdict = {'alwaysontop':empty,'posx':empty,'posy':empty,'alarm':empty,
             'tsurl':empty,'csvsep':empty,'lang':empty}
    # = separates parameter (left) and value (right)
    for line in plist:
        if line.strip('\ufeff')[:1] == '#': # Ignore comment lines
            continue
        pitem = line.strip('\ufeff\n').split('=')
        try:
            pdict[pitem[0]] = pitem[1]
        except:
            pass

def readLang():

    # Read language file
    lfile = open(os.path.join(abspath,'res','lang_'+pdict['lang']+'.txt'),'r',encoding='utf-8')
    llist = lfile.readlines()
    lfile.close()

    global ldict
    ldict = {}

    for line in llist:
        if line.strip('\ufeff')[:1] == '#': # Ignore comment lines
            continue
        litem = line.strip('\ufeff\n').split('=')
        ldict[litem[0]] = litem[1]

def setPrefs(pnam,pval):

    # Read prefs file
    pfile = open(os.path.join(abspath,'res','prefs.txt'),'r',encoding='utf-8')
    plist = pfile.readlines()
    pfile.close()

    # Update prefs dict value
    pdict[pnam] = pval

    # Update prefs file
    prefi = empty # Pref item
    prefl = empty # Pref line
    # = separates parameter (left) and value (right)
    for line in plist:
        if line.strip('\ufeff')[:1] == '#': # Ignore comment lines
            continue
        pitem = line.strip('\n').split('=')
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

    if   arg == 'about':
        ibox = messagebox.showinfo(ldict['t_about'],"Taskimeter v1.0\n\n"+
                                   "\u00a9 2014-2016 Bulut \u00d6zt\u00fcrk")
    elif arg == 'prefs':
        filepath = os.path.join(abspath,'res','prefs.txt')
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', filepath))
        elif os.name == 'nt':
            os.startfile(filepath)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', filepath))

if __name__ == '__main__':

    # Create root object
    root = Tk()

    # Path to .py or .exe file
    global abspath
    #abspath = os.path.abspath(os.path.dirname(sys.executable))
    abspath = os.path.abspath(os.path.dirname(__file__))

    # Empty string
    global empty
    empty = ""

    # Create missing files
    createMissing()

    # Preferences
    readPrefs()

    # Language
    readLang()

    # Window dimensions (x,y) and position (x,y)
    try:
        root.geometry('200x65+'+pdict['posx']+'+'+pdict['posy'])
    except:
        root.geometry('200x65+300+300')

    # Non-resizable
    root.resizable(0,0)

    # Window icon
    try:
        root.iconbitmap(os.path.join(abspath,'res','icon.ico'))
    except:
        pass

    # When closing
    root.protocol('WM_DELETE_WINDOW',lambda: closeApp())

    # Window on top
    try:
        root.wm_attributes('-topmost',pdict['alwaysontop'])
    except:
        root.wm_attributes('-topmost',1)

    # Keyboard shortcuts
    root.bind('<Control_L>t',lambda event=None, i='about': handleKeys(i))
    root.bind('<Control_R>t',lambda event=None, i='about': handleKeys(i))
    root.bind('<Control_L>o',lambda event=None, i='prefs': handleKeys(i))
    root.bind('<Control_R>o',lambda event=None, i='prefs': handleKeys(i))

    # Create other objects
    cur = CurrentTask()
    app = App(root)
    tmr = Timer()

    # Main loop
    root.mainloop()