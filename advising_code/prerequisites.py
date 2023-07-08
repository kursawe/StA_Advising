import re
from .infrastructure import *

def find_missing_prerequisites(student):
    """find any missing prerequisites or violated anti-requisites.
    
    Parameters :
    -----------
    
    student : instance of Student class
        can be generated with 'parse_excel_form()'
        
    Returns :
    ---------

    missed_prerequisites : string
        Unmet programme requirements and violated anti-requisites. Will return 'None' if all prerequisites are met and
        no anti-requisite is violated.
        
    adviser_recommendations : string
        advising recommendations, in this case may include reminders to get letters of approval.
    """
    list_of_missed_prerequisites = []
    list_of_recommendations = []
    
    for module in student.planned_honours_modules:
        these_missing_prerequisites, these_adviser_recommendations = get_missing_prerequisites_for_module(module, student)
        list_of_missed_prerequisites += [these_missing_prerequisites]
        list_of_recommendations += [these_adviser_recommendations]
        
    # merge all missed prerequisites into a string
    missed_prerequisites = merge_list_to_long_string(list_of_missed_prerequisites)
    adviser_recommendations = merge_list_to_long_string(list_of_recommendations)

    return missed_prerequisites, adviser_recommendations
    
def get_missing_prerequisites_for_module(module, student):
    """Find which prerequisites the student is missing for the given module.
    Will also check anti-requisites.
    
    Parameters :
    ------------
    
    module : string
        module code for the module that we are investigating
        
    student : instance of Student class
        The student we are checking
        
    Returns :
    ---------

    missed_prerequisites : string
        missing prerequisites and violated anti-requisites
        
    adviser_recommendation : string
        any relevant adviser recommndations for this module
    """
    # make a list of missing prerequisites
    missed_prerequisites_list = []
    adviser_recommendations_list = []

    # find which year and semester the module is selected for
    year_of_this_module = student.honours_module_choices[student.honours_module_choices['Module code'] == module]['Honours year'].values[0]
    year_number_of_this_module = int(year_of_this_module[-1])
    semester_of_this_module = student.honours_module_choices[student.honours_module_choices['Module code'] == module]['Semester'].values[0]

    # construct a list of all courses the student has taken by then
    # and construct a list of all modules the student is taking concurrently
    previously_taken_modules = student.passed_modules.copy()
    simultaneously_taken_modules = []
    # we need this one for anti-requisites below
    modules_taken_in_same_year=[]

    for _, row in student.honours_module_choices.iterrows():
        year_number = int(row['Honours year'][-1])
        if year_number < year_number_of_this_module:
            previously_taken_modules.append(row['Module code'])
        if semester_of_this_module == 'S2':
            if row['Honours year'] == year_of_this_module and row['Semester'] == 'S1' :
                previously_taken_modules.append(row['Module code'])
        if (row['Honours year'] == year_of_this_module 
            and row['Semester'] == semester_of_this_module
            and row['Module code'] != module):
            simultaneously_taken_modules.append(row['Module code'])
        if (row['Honours year'] == year_of_this_module 
            and row['Module code'] != module):
            modules_taken_in_same_year.append(row['Module code'])

    # get pre-requisite string for that module
    if len(module_catalogue[module_catalogue['Module code'] == module])> 0:
        prerequisites = module_catalogue[module_catalogue['Module code'] == module]['Prerequisites'].values[0]
    else:
        # The student has chosen a module that doesn't exist. We have flagged this already in the programme requirements,
        # so don't need to do that again here.
        # choosing this because that's what pandas would return if the entry was just empty
        prerequisites = float('nan')

    # if the prerequsites are not empty
    if  isinstance(prerequisites,str) and module!='MT5867':
        prerequisite_list = prerequisites.split()
        # if there is only one prerequisite we can easily parse that
        if len(prerequisite_list) == 1:
            # this must be a module code now
            required_module = prerequisite_list[0]
            if required_module not in previously_taken_modules:
                missed_prerequisites_list.append('Student is missing prerequisite ' + required_module + ' for module ' + module)
        # sometiems it's just a letter of agreement that we need to know about
        elif prerequisites == 'Letter of Agreement':
                adviser_recommendations_list.append('Module ' + module + ' requires a letter of agreement')
        elif prerequisites == 'Students must have gained admission onto an MSc programme':
            missed_prerequisites_list.append('Student cannot take module ' + module + ' as this module is only available to Msc students')
        else:
            #now there is a boolean statement coming, so we turn the module codes into boolean strings and evaluate the outcome
            # (thanks, ChatGPT)
            module_codes = re.findall(r'[A-Z]{2}\d{4}', prerequisites)
            parsed_prerequisites = prerequisites
            for module_code in module_codes:
                # co-requisites are preceded by the word co-requisite and don't have brackets after
                if module_code in prerequisite_list:
                    location_index = prerequisite_list.index(module_code)
                    if location_index > 0:
                        if prerequisite_list[location_index - 1] == 'co-requisite':
                            if module_code in previously_taken_modules or module_code in simultaneously_taken_modules:
                                parsed_prerequisites = parsed_prerequisites.replace(module_code, 'True')
                            else:
                                parsed_prerequisites = parsed_prerequisites.replace(module_code, 'False')
                            parsed_prerequisites = parsed_prerequisites.replace('co-requisite ', '')
                        else: 
                            # the location index is larger than one but we are not at a co-requisite
                            if module_code in previously_taken_modules:
                                parsed_prerequisites = parsed_prerequisites.replace(module_code, 'True')
                            else:
                                parsed_prerequisites = parsed_prerequisites.replace(module_code, 'False')
                    # the location index is zero and we just check the module code
                    if module_code in previously_taken_modules:
                        parsed_prerequisites = parsed_prerequisites.replace(module_code, 'True')
                    else:
                        parsed_prerequisites = parsed_prerequisites.replace(module_code, 'False')
                else:
                    if module_code in previously_taken_modules:
                        parsed_prerequisites = parsed_prerequisites.replace(module_code, 'True')
                    else:
                        parsed_prerequisites = parsed_prerequisites.replace(module_code, 'False')
            prerequisites_are_met = eval(parsed_prerequisites)
            if not prerequisites_are_met:
                missed_prerequisites_list.append('Student is missing prerequisite [' + prerequisites+ '] for module ' + module + 
                                                 ' ([' + parsed_prerequisites + '])')
            
    # MT5867 is a special case that I don't know how to parse automatically:
    if module == 'MT5867':
        prerequisites = 'two of (MT3505, MT4003, MT4004, MT4512, MT4514, MT4515, MT4526)'
        list_of_modules = ['MT3505', 'MT4003', 'MT4004', 'MT4512', 'MT4514', 'MT4515', 'MT4526']
        number_of_matching_modules = len(set.intersection(set(list_of_modules), set(previously_taken_modules)))
        if number_of_matching_modules <2:
            missed_prerequisites_list.append('Student is missing prerequisite [' + prerequisites + '] for module MT5867')
            
    # now check anti-requisites:
    # to do so, get the anti-requisites
    if len(module_catalogue[module_catalogue['Module code'] == module])> 0:
        antirequisites = module_catalogue[module_catalogue['Module code'] == module]['Antirequisites'].values[0]
    else:
        # The student has chosen a module that doesn't exist. We have flagged this already in the programme requirements,
        # so don't need to do that again here.
        # choosing this because that's what pandas would return if the entry was just empty
        antirequisites = float('nan')

    if isinstance(antirequisites, str):
        # check any listed module code individually
        anti_module_codes = re.findall(r'[A-Z]{2}\d{4}', antirequisites)
        for module_code in anti_module_codes:
            if module_code in previously_taken_modules or module_code in simultaneously_taken_modules:
                missed_prerequisites_list.append('Student selected antirequisite ' + module_code + ' for module ' + module)

    
    # merge all missed prerequisites into a string
    missed_prerequisites = merge_list_to_long_string(missed_prerequisites_list)
    adviser_recommendations = merge_list_to_long_string(adviser_recommendations_list)
    
    return missed_prerequisites, adviser_recommendations

