# taskimeter

A no-nonsense task time tracking tool written in Python that
* stays out of your way but still reminds itself with its tiny always-on-top widget
* uses your default programs to edit configurations and view logs
* avoids heavy dependencies by using TkInter for the GUI
* in fact has no dependencies other than the Python standard distribution (at least for Windows, see previous item)
* runs on Windows, Linux and Mac

Requirements

* Python 3
* TkInter (included in Python for Windows)

How to Use

Simply run ```taskimeter.py```. This will create all the necessary configuration and log files inside a ```res``` directory in the path where ```taskimeter.py``` is located. These are
* ```prefs.txt``` - Preferences file with default values
* ```tasks.txt``` - Task list
* ```lang_en.txt``` - English language file with default values (other language files in the repository)

Once Taskimeter is running, click on the task field (top left) to open the tasks menu. This is empty at this point, so you will only see the ```Edit``` option.

Choosing ```Edit``` will open the ```tasks.txt``` file in your default program. Add any number of tasks, one per line, and save the file. Next time you click on the task field, your newly added tasks will be listed.

Choosing a task from this list will start the counter, which will continue counting until you either click ```Stop```, choose another task, or close the program. When you do any one of these, you will be asked to provide a little detail of what you did during this time. You can leave this prompt blank as well.

Your time worked has now been recorded in the  ```log.csv``` file.

The bottom row buttons are rather straightforward, so I'll just go over them briefly.

```Log``` - Opens ```log.csv``` in your default program.

```Stop``` - Ends and saves the task as explained above.

Finally, the following keyboard shortcuts are available.

```ctrl-f``` - Opens the Taskimeter folder.

```ctrl-t``` - Displays the ```About``` window.

```ctrl-o``` - Opens the ```prefs.txt``` file in your default program.

```ctrl-l``` - Shortcut for the ```Log``` button.
