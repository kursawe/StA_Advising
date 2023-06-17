import argparse
import openpyxl
import os
import pandas as pd

def check_form_file(filename):
    """preforms all advising checks on the 
    submitted form.
    
    Parameters:
    -----------
    
    filename : string
        path to the file that is being investigated,
        i.e. a filled-in module choice form
    """ 
    student = parse_excel_form(filename)
    missed_programme_requirements, adviser_recommendations = find_missing_programme_requirements(student)
    
    summary_data = [student.student_id, missed_programme_requirements, adviser_recommendations]
    summary_data_frame = pd.DataFrame([summary_data], columns = ['Student ID', 'Unmet programme requirements', 'Adviser recommendations'])

#     check_programme_requirements(student)
#     check_prerequisites(student)
#     check_timetable_clashes(student)
    return summary_data_frame

def find_missing_programme_requirements(student):
    """check that the student fulfils their honours requirements
    
    Parameters :
    -----------
    
    student : instance of Student class
        can be generated with 'parse_excel_form()'
        
    Returns :
    ---------

    missed_requirements : string
        Unmet programme requirements. Will return 'None' if all programme requirements are met
        
    adviser_recommendations : string
        advising recommendations that don't strictly count as unmet programme requirements
    """
    
    list_of_missed_requirements = []
    list_of_adviser_recommendations = []
    full_module_list = student.full_module_list
    if student.programme_name == 'Bachelor of Science (Honours) Mathematics':
        # check the credit load
        missed_requirement, adviser_recommendation = check_for_120_credits_each_year(student)
        list_of_missed_requirements.append(missed_requirement)
        list_of_adviser_recommendations.append(adviser_recommendation)

        # check there are four modules in MT3501 to MT3508
        list_of_MT350X_modules = ['MT3501', 'MT3502', 'MT3503', 'MT3504', 'MT3505', 'MT3506', 'MT3507', 'MT3508']
        number_of_MT350X_modules = len(set.intersection(set(full_module_list),set(list_of_MT350X_modules)))
        if number_of_MT350X_modules < 4:
            list_of_missed_requirements.append('Student is only taking ' + str(number_of_MT350X_modules) + 'out of MT3501-MT3508')
            
        # check there is a computing module
        list_of_computing_modules = ['MT3510', 'MT4111', 'MT4112', 'MT4113']
        number_of_computing_modules = len(set.intersection(set(full_module_list),set(list_of_computing_modules)))
        if number_of_computing_modules ==0:
            list_of_missed_requirements.append('Student is not taking a computing module')
        
        # check there is a final year project
        list_of_project_codes = ['MT4598', 'MT4599']
        number_final_year_projects = len(set.intersection(set(full_module_list),set(list_of_project_codes)))
        if number_final_year_projects !=1:
            list_of_missed_requirements.append('Student is not taking an allowed final year project')
        
        # check that unallowed modules are not taken
        unallowed_modules = ['MT4794', 'MT4795', 'MT4796', 'MT4797']
        number_of_unallowed_modules = len(set.intersection(set(full_module_list),set(unallowed_modules)))
        if number_of_unallowed_modules >0:
            list_of_missed_requirements.append('Student is taking a module in MT4794-MT4797')
        list_of_5000_level_modules = [module for module in full_module_list if 'MT5' in module]
        if len(list_of_5000_level_modules) >0:
            list_of_missed_requirements.append('Student is taking 5000 level modules')

    # merge all missed requirements into a string
    missed_requirements = merge_list_to_long_string(list_of_missed_requirements)
    adviser_recommendations = merge_list_to_long_string(list_of_adviser_recommendations)

    return missed_requirements, adviser_recommendations
        
def check_for_120_credits_each_year(student):
    """check whether the student is actually taking 120 credits each acacemic year, and whether they 
       have an even split of modules.

    Parameters:
    -----------

    student : instance of Student()
        the student we are investigating

    Returns:
    --------

    missed_requirement : string
        a note if credits are not satisfied

    adviser_recommendation : string
        a note if module split is uneven 
    """
    honours_years = student.honours_module_choices['Honours year'].unique()
    list_of_missed_requirements = []
    list_of_adviser_recommendations = []
    
    #checking total number of modules
    for honours_year in honours_years:
        this_data_base = student.honours_module_choices[student.honours_module_choices['Honours year'] == honours_year]
        if honours_year == 'Year 1' or (honours_year == 'Year 2' and student.expected_honours_years == 3):
            if len(this_data_base)!=8:
                list_of_missed_requirements.append('Not collecting 120 credits in ' + honours_year)
        if honours_year== 3 and len(these_modules)!=7:
            list_of_missed_requirements.append('Not collecting 120 credits in ' + honours_year)
    
    #checking moduel splits
    for honours_year in honours_years:
        if honours_year == 'Year 1' or (honours_year == 'Year 2' and student.expected_honours_years == 3):
            for semester in ['S1', 'S2']:
                this_smaller_data_base = this_data_base[this_data_base['Semester'] == semester]
                if len(this_smaller_data_base) !=4:
                    list_of_adviser_recommendations.append('Not taking even credit split in ' + honours_year)
        elif honours_year == 'Year 2':
            this_reduced_data_base = this_data_base[this_data_base['Module code'] != 'MT4599']
            semester_1_modules = this_reduced_data_base[this_reduced_data_base['Semester'] == 'S1']['Module code']
            semester_2_modules = this_reduced_data_base[this_reduced_data_base['Semester'] == 'S1']['Module code']
            if len(semester_1_modules) != 4 or len(semester_2_modules) != 3:
                list_of_adviser_recommendations.append('taking high course load in second semester of final honours year')
        elif honours_year == 'Year 3':
            this_reduced_data_base = this_data_base[this_data_base['Module code'] != 'MT5599']
            semester_1_modules = this_reduced_data_base[this_reduced_data_base['Semester'] == 'S1']['Module code']
            semester_2_modules = this_reduced_data_base[this_reduced_data_base['Semester'] == 'S1']['Module code']
            if len(semester_1_modules) != 3 or len(semester_2_modules) != 3:
                list_of_adviser_recommendations.append('taking uneven course load in final honours year')
    
    missed_requirement = merge_list_to_long_string(list_of_missed_requirements)
    adviser_recommendation = merge_list_to_long_string(list_of_adviser_recommendations)
    
    return missed_requirement, adviser_recommendation
 

def merge_list_to_long_string(a_list):
    """takes a list of strings and returns a string that separates the entries with a comma and a space.
        Returns the string 'None' if the list is empty. 
    
    Parameters:
    -----------
    a_list : list
        the list we want to parse, for example a list of unmet programme requirements
    
    Returns:
    --------
    a_string : string
        contains all entries in a_list separated by a comma and a space
        is 'None' if a_list is empty
    """
    if len(a_list) == 0:
        a_string = 'None'
    else:
        a_string = a_list[0]
        if len(a_list) > 1:
            for list_entry in a_list[1:]:
                a_string += ', ' + list_entry
    
    return a_string
    
def parse_excel_form(filename):
    """returns an instance of a 'student' class
    that has all the excel data as named attributes

    Parameters:
    -----------
    
    filename : string
        path to the file that is being investigated,
        i.e. a filled-in module choice form
        
    Returns:
    --------

    student : instance of Student class
        an object with student attributes.
    """
    # open the form file and read in the student ID
    this_workbook = openpyxl.load_workbook(filename=filename)
    sheet = this_workbook.active
    student_id = sheet["D5"].value
    
    # Now that we have the student ID we can look up the student in the database:
    current_directory = os.path.dirname(os.path.abspath(__file__))
    potential_data_files = os.listdir(os.path.join(current_directory, 'student_data'))
    data_files = []
    for candidate_filename in potential_data_files:
       this_filename, file_extension = os.path.splitext(candidate_filename)
       if file_extension == '.csv':
           data_files.append(candidate_filename)
    
    # turn them all into data base files
    data_bases = []
    for data_file_name in data_files:
        data_path = os.path.join(current_directory, 'student_data', data_file_name)
        this_data_frame = pd.read_csv(data_path)
        data_bases.append(this_data_frame)
    
    # get a table with only the entries for this student
    student_not_yet_found = True

    data_base_index = 0
    while student_not_yet_found:
        this_data_base = data_bases[data_base_index]
        if student_id in this_data_base['Student ID'].to_numpy():
            student_not_yet_found = False
            student_data_base = this_data_base[this_data_base['Student ID'] == student_id]
        data_base_index += 1

    # infer the year of study from the earliest module taken
    data_of_module_years = student_data_base['Year'].str.slice(0,4).astype('int')
    earliest_year = data_of_module_years.min()
    
    #students who took their first module in 2021 will now be in year 3, i.e. 2023-2021+1
    year_of_study = 2023 - earliest_year + 1
    year_of_study = year_of_study
    
    # identify all modules that the student has passed
    data_base_of_passed_modules = student_data_base[student_data_base['Assessment result']=='P']
    passed_modules = data_base_of_passed_modules['Module code'].to_list()
    passed_modules = passed_modules
    
    #identify the programme of the student
    programme_entries = student_data_base['Programme name'].unique()    
    assert(len(programme_entries == 1))
    programme_name = programme_entries[0]
    
    # Figure out what year they are in and how many they have left
    if 'Bachelor of Science' in programme_name:
        no_of_programme_years = 4
        expected_honours_years = 2
    elif 'Master in Mathematics' in programme_name:
        no_of_programme_years = 5
        expected_honours_years = 3
    else: 
        print('what the heck kind of programme is that?? ' + programme_name)
    
    if 'EXA120' in student_data_base['Module code']:
        no_of_programme_years -=1
        
    no_subhonours_years = no_of_programme_years - expected_honours_years
    current_honours_year = year_of_study - no_subhonours_years
    
    # read in modules for all honours years that have not happened yet
    module_table = []
    
    for remaining_honours_year in range(current_honours_year,expected_honours_years + 1):
        year_key = 'Year ' + str(remaining_honours_year)
        calendar_year = 22 + remaining_honours_year
        calendar_year_string = '20' + str(calendar_year) + '/' + str(calendar_year + 1)
        for semester_number in [1,2]:
            semester_modules = get_modules_under_header(sheet, year_key + ' of Honours: Semester ' + str(semester_number)) 
            for module in semester_modules:
                module_table.append([year_key, calendar_year_string, 'S' + str(semester_number), module,])

    # Turn this all into a nice pandas data frame
    honours_module_choices = pd.DataFrame(module_table, columns = ['Honours year', 'Calendar year', 'Semester', 'Module code'])
    
    this_student = Student(student_id, 
                           programme_name, 
                           year_of_study,
                           expected_honours_years,
                           current_honours_year,
                           passed_modules,
                           honours_module_choices)
    
    # return the student
    return this_student

class Student():
    def __init__(self, 
                 student_id, 
                 programme_name,
                 year_of_study,
                 expected_honours_years,
                 current_honours_year,
                 passed_modules,
                 honours_module_choices):
        """Constructor for the Student class.
        
        Parameters:
        -----------
        
        student_id : int
            The student ID
            
        programme_name : string
            the full name of the programme, as it appears in the MMS databases
            
        year_of_study : int
            the current year of study
            
        expected_honours_years : int
            the number of expected honours years. This is slightly superfluous as it can be
            inferred from the programme, i.e. it will be 3 for masters programmes and 2 for
            bachelors programmes
            
        current_honours_year : int
            Which year of honours the student is in - this is not superfluous, as it cannot always
            be inferred from the year of study, since Advance Standing Credits (direct entry) need
            to be taken into account
            
        passed_modules : list of strings
            A list containing the module codes of all passed modules
            
        honours_module_choices : Pandas data frame
            The honours module codes that the studen thas selected. The data frame current contains
            the following columns ['Honours year', 'Calendar year', 'Semester', 'Module code']
        """
        
        self.student_id = student_id
        self.programme_name = programme_name
        self.year_of_study = year_of_study
        self.expected_honours_years = expected_honours_years
        self.current_honours_year = current_honours_year
        self.passed_modules = passed_modules
        self.honours_module_choices = honours_module_choices

        # for convenience also make a list of all selected and taken modules
        self.full_module_list = self.passed_modules.copy()
        self.full_module_list += self.honours_module_choices['Module code'].to_list()


def get_modules_under_header(sheet, header):
    """get all the modules in the student module choice form under a given heading
    
    Parameters:
    -----------
    
    sheet : openpyxl sheet object
        generated from the workbook excel file
        
    header : string
        the header that we are investigating

    Returns:
    --------

    modules : list of strings
        module codes under the given header
    """
    modules = []
    for row in sheet.iter_rows():
        if isinstance(row[1].value, str):
            if header in row[1].value:
                row_number = row[1].row

    # the row number where modules are entered is 2 down
    row_number += 2
    next_cell_name_with_module = 'B' + str(row_number)
    module_code_is_not_empty = sheet[next_cell_name_with_module].value is not None

    while module_code_is_not_empty:
        modules.append(sheet[next_cell_name_with_module].value)
        row_number+=1 
        next_cell_name_with_module = 'B' + str(row_number)
        module_code_is_not_empty = sheet[next_cell_name_with_module].value is not None

    return modules

# def check_programme_requirements(Student)
#     """This checks if a student passes their programme requirements.
#     
#     Parameters:
#     -----------
#     
#     student : instance of Student class
#         The student we are investigating
#     """
#     # Look up math requirements as a list of conditions
#     # loop through the list of conditions
#     # check if conditions are fulfilled
#     
# def check_prerequisites(student):
#     """This checks if a student meets the prerequisits for their courses
#     
#     Parameters:
#     -----------
#     
#     student : instance of Student class
#         The student we are investigating
#     """
#     for module in get_all_student_modules(student):
#         check_specific_module_requirements(student, module)
# 
# def check_specific_module_requirements(module, student):
#     """This checks if a student meets the prerequisits for their courses
#     
#     Parameters:
#     -----------
#     
#     module : string
#         module code we are investigating
# 
#     student : instance of Student class
#         The student we are investigating
#     """
#     these_module_requirements = get_requirements_for_module(module_code)
#     previous_modules = get_previous_modules(student, module)
#     concurrent_modules = get_concurrent_modules(student, module)
#     for requirement in these_module_requirements:
#         if not requirement.is_fulfilled(student, previous_modules, concurrent_modules)
#             print('missing requirement ' + requirement.blurb())
#             
# def check_for_timetable_clashes(student):
#     """This checks if a student will have any timetable clashes within maths
#     
#     Parameters:
#     -----------
#     
#     student : instance of Student class
#         The student we are investigating
#     """
#     for year in student.get_honours_years():
#         for semester in [1,2]:
#             these_modules = student.get_modules(year, semester)
#             check_for_timetable_clashes(these_modules)

def colour_code_passes(column):
    passed_colour = 'background-color: palegreen;'
    failed_colour = 'background-color: lightcoral;'
    return [passed_colour if value=='None' else failed_colour for value in column]

def colour_recommendations(column):
    recommendation_colour = 'background-color: orange;'
    default_colour = ''
    return [default_colour if value=='None' else recommendation_colour for value in column]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='AdvisingScript',
                    description='This script helps with advising',
                    epilog='All results are experimental and not to be trusted. Double-check me. \n\n')
    
    parser.add_argument('filename')       
    args = parser.parse_args()
    form_filename = args.filename
    summary_data_frame = check_form_file(form_filename)
    summary_data_frame = (summary_data_frame.style.apply(colour_code_passes, subset = ['Unmet programme requirements'], axis = 0).
                          apply(colour_recommendations, subset = ['Adviser recommendations'], axis = 0))
    writer = pd.ExcelWriter('summary_file.xlsx') 
    # Manually adjust the width of the last column
    summary_data_frame.to_excel(writer)
    writer.sheets['Sheet1'].set_column(0,0,width=5)
    writer.sheets['Sheet1'].set_column(1,1,width=10)
    writer.sheets['Sheet1'].set_column(2,2,width=30)
    writer.sheets['Sheet1'].set_column(3,3,width=30)
    writer.save()
   # parse command line
   # get list of form files
   # for each form file check student
   # check_form_file