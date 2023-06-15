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

#     check_programme_requirements(student)
#     check_prerequisites(student)
#     check_timetable_clashes(student)

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
    this_workbook = openpyxl.load_workbook(filename=filename)
    sheet = this_workbook.active
    this_student = Student()
    this_student.student_id = sheet["D5"].value
    
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
        if this_student.student_id in this_data_base['Student ID'].to_numpy():
            student_not_yet_found = False
            student_data_base = this_data_base[this_data_base['Student ID'] == this_student.student_id]
        data_base_index += 1

    # infer the year of study from the earliest module taken
    data_of_module_years = student_data_base['Year'].str.slice(0,4).astype('int')
    earliest_year = data_of_module_years.min()
    
    #students who took their first module in 2021 will now be in year 3, i.e. 2023-2021+1
    year_of_study = 2023 - earliest_year + 1
    this_student.year_of_study = year_of_study
    
    # identify all modules that the student has passed
    data_base_of_passed_modules = student_data_base[student_data_base['Assessment result']=='P']
    passed_modules = data_base_of_passed_modules['Module code'].to_list()
    this_student.passed_modules = passed_modules
    
    #identify the programme of the student
    programme_entries = student_data_base['Programme name'].unique()    
    assert(len(programme_entries == 1))
    this_student.programme_name = programme_entries[0]
    print(this_student.programme_name)
    
    this_student.honours_module_choices = {}
    
    if 'Bachelor of Science' in this_student.programme_name:
        no_of_programme_years = 4
        expected_honours_years = 2
    if 'Master in Mathematics' in this_student.programme_name:
        no_of_programme_years = 5
        expected_honours_years = 3
    
    if 'EXA120' in student_data_base['Module code']:
        no_of_programme_years -=1
        
    no_subhonours_years = no_of_programme_years - expected_honours_years
    current_honours_year = year_of_study - no_subhonours_years
    
    for remaining_honours_year in range(current_honours_year,expected_honours_years + 1):
        print('processing honours year')
        print(remaining_honours_year)
        modules_key = 'Year ' + str(remaining_honours_year)
        this_student.honours_module_choices[modules_key]={}
        semester_one_modules = get_modules_under_header(sheet, modules_key + ' of Honours: Semester 1') 
        this_student.honours_module_choices[modules_key]['S1'] = semester_one_modules
        semester_two_modules = get_modules_under_header(sheet, modules_key + ' of Honours: Semester 2') 
        this_student.honours_module_choices[modules_key]['S2'] = semester_two_modules

    # if year_of_study == 3:
    #     modules_year_1_s1 = get_modules_under_header(sheet,'Year 1 of Honours: Semester 1') 
    #     if len(modules_year_1_s1) >0:
    #         this_student.honours_module_choices['Year 1']= {}
    #         this_student.honours_module_choices['Year 1']['S1'] = modules_year_1_s1

        print('found the following module codes')
        print(this_student.honours_module_choices)

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

#         module_choices_3rd_year_s1 = ...
#         module_choices_3rd_year_s2 = ...
#         module_choices_4th_year_s1 = ...
#         module_choices_4th_year_s2 = ...
#         if programme in list_of_long_programmes:
#             module_choices_5th_year = ...
#     if year == 4:
#         #get module choices from student records for 3rd year
#         module_choices_4th_year = ...
#         if programme in list_of_long_programmes:
#             module_choices_5th_year = ...
#     if year == 5:
#         # get module choices from student records 3rd and 4th year
#         module_choices_5th_year = ...
#     # check programme requirements are fulfilled
#     # check course pre-requisites
#     # check for timetable clashes

class Student():
    def __init__(self):
        pass
#     
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='AdvisingScript',
                    description='This script helps with advising',
                    epilog='All results are experimental and not to be trusted. Double-check me. \n\n')
    
    parser.add_argument('filename')       
    args = parser.parse_args()
    form_filename = args.filename
    check_form_file(form_filename)
   # parse command line
   # get list of form files
   # for each form file check student
   # check_form_file