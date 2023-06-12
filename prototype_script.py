import argparse

# def check_form_file(filename)
#     """preforms all advising checks on the 
#     submitted form.
#     
#     Parameters:
#     -----------
#     
#     filename : string
#         path to the file that is being investigated,
#         i.e. a filled-in module choice form
#     """
#     student = parse_excel_form(filename)
#     check_programme_requirements(student)
#     check_prerequisites(student)
#     check_timetable_clashes(student)
# 
# def parse_excel_form(filename):
#     """returns an instance of a 'student' class
#     that has all the excel data as named attributes
# 
#     Parameters:
#     -----------
#     
#     filename : string
#         path to the file that is being investigated,
#         i.e. a filled-in module choice form
#         
#     Returns:
#     --------
# 
#     student : instance of Student class
#         an object with student attributes.
#     """
#     this_student = Student()
#     student_id = #
#     year_of_study = ...
#     programme = ...
#     year = ...
#     if year == 3:
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
# class Student():
#     def __init__(self):
#         pass
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
                    epilog='All results are experimental and not to be trusted. Double-check me')
    
    parser.add_argument('filename')       
    args = parser.parse_args()
    form_filename = args['filename']
    print('filename')
   # parse command line
   # get list of form files
   # for each form file check student
   # check_form_file