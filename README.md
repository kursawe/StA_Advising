# StA_Advising
This repository provides a tool to help with Honours advising in the School of Mathematics and Statistics at the University of St Andrews.

# Usage
The tool operates from command line. Currently it can process single Honours choice forms from individual students, or a folder containing multiple such forms. To use the script on an Honours choice form, navigate to the folder where `advising_tool.py` is saved and type

```
python advising_tool.py form_file.xlsx
```

If you wish to process a folder of form files, simply replace the `form_file.xlsx` with the folder name.

The tool will save it's findings into an excel file as well as a Microsoft Word file, and also print everything to command line. The output files are `summary_file.xlsx` and `summary_file.xlsx`. You can save into different files by typing

```
python advising_tool.py -o other_file_name.xlsx form_file.xlsx
```

One can get a brief description of the command line arguments by typing

```
python advising_tool.py --help
```

If you would prefer other output formats, let Jochen know.

# Installation and file setup
Installation of this tool requires three steps: (i) Installing python dependencies, (ii) Downloading the code from this repository and (iii) Donwloading student data files from MMS

## Installing python 
If you don't have python installed on your computer, I recommend installing anaconda (https://www.anaconda.com/). Once python is installed, you need to install a small number of python packages by typing

```
pip install openpyxl
pip install pandas
pip install termcolor
pip install python-docx
pip install jinja2
```

## Getting the code
You'll find options for downloading the code by clicking on the green button 'Code' on the top right. For example, if you have ssh access setup in your github user account, you could navigate to the folder you'll want to use and type

```
git clone git@github.com:kursawe/StA_Advising.git
```

Downloading a .zip file and extracting it is also an option. 

## Accessing student data files

To access student module data navigate to the website

https://www.st-andrews.ac.uk/studentrecords/

then click on 'Show extra search options'. This will open up new options to select catagories for students whose files we would like to access. In the section 'taking module' select 'MT2* modules'. Then, under 'and I want the results as' select 'a CSV file of academic data' in 'standard' format.
This should look something like this:
![](./advising_code/repository_image.png)

Click the 'Search' button and save the generated file in the subfolder `student_data`, which is part of the repository file structure. Repeat the process three times by selecting 'MT3* modules', 'MT4* modules' and also 'MT5* modules'.

# Functionality
The tool will check programme requirements, check that modules are running in the selected semesters, it will check for timetable clashes among MT modules, and it will check prerequisites. The script works for students entering Honours as well as returning honours students.

In the module choice forms, the code relies on the fact that a valid student ID is in cell 'D5'. Module choices are identified by their heading. That means, the form can be read even if empty lines or sections are deleted in the module choice form. However, adding or deleting columns may stop the form from being read.

 When accessing student data, the will take as much data from the official data records as possible and minimise the input from the form. That means, the only data read from the module choice forms are the student ID and the selected module codes under each relevant header. If a student is a returning honours student, module choices for previously taken honours years are found in the student data base. Only module choices for planned honours years are read from the module choice form.

# Troubleshooting and known issues
The officially available records do not contain data on the year of study. Hence, the tool infers the year of study and the honours year based on the first year a module was taken, and on the number of subhonours years. This will go wrong if a student is studying part time or has been on leave of absence.

The tool has not been tested extensively, and errors are expected. That means, output from the tool will need to be double-checked.

Specifically, module data for MT modules is read from `module_catalogue/module_catalogue.xlsx`, which as been manually curated with the help of ChatGPT. That file probably contains errors and may not be fully up-to-date.

Finally, the code has only been tested on MacOS. The coloured command line output may look wrong on Windows. Please let Jochen know if that's the case.

# Improving the tool

Please help in improving this tool! To do so, please let Jochen know if you spot any errors in the output.

Additionally, you may notice checks and tests that you would like the tool to do, and which are currently not implemented. Please let Jochen know about these also. The code structure is modular and should allow quick additions of further tests.

Finally, every tool gets better the more collaborators are looking over the code. If you would be open for code-review or contributing to the repository, please let Jochen know and he can give you github access to the repository.

# File structure
For anyone interested, this is a quick explanation of the file struture

- `advising_tool.py`: This file does the command line parsing and calls the actual code in the  `advising_code` folder.
- `advising_code/__init__.py`: This file is part of how python works, and allows us to load the code from all other files in the folder into the main namespace whenever `advising_code` gets imported from within python.
- `advising_code/student.py`: This file defines the main datastructure that we are using inside our checks, the 'Student' class. This is a python class which allows us to curate all information about a student in one object, thus allowing us quick access to which modules have been taken, which modules the student planning to take, which year they are in, etc.
- `advising_code/infrastructure.py`: This file contains the code to read and write files, and multiple helper functions that we use when checking programme requirements and timetable clashes etc.
- `advising_code/programme_requirements.py`: This file contains the code that checks programme requirements.
- `advising_code/prerequisites.py`: This file contains the code that works out whether a student meets the prerequisites for selected modules.
- `advising_code/timetabling.py`: This file contains the code that checks for timetable clashes, and whether modules are running as selected.
