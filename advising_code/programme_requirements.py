import collections
from .infrastructure import *

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
    
    # do some sanity check on the module selection first. 
    if len(set(student.full_module_list)) != len(student.full_module_list):
        double_entry_counter = collections.Counter(student.full_module_list)
        duplicate_entries = [module for module, count in double_entry_counter.items() if count > 1]
        warning_string = 'Student selected the following modules twice: '
        for entry in duplicate_entries:
            warning_string += entry
            if entry != duplicate_entries[-1]:
                warning_string += ', '
        list_of_missed_requirements.append(warning_string)
    
    for module in student.planned_honours_modules:
        if module.startswith('MT') and module not in module_catalogue['Module code'].values:
            list_of_missed_requirements.append('Student is planning to take ' + module + ' (which does not exist)')

    ### BSC MATHEMATICS REQUIREMENTS
    if student.programme_name == 'Bachelor of Science (Honours) Mathematics':
        # check the credit load
        missed_requirement, adviser_recommendation = check_for_120_credits_each_year(student)
        list_of_missed_requirements.append(missed_requirement)
        list_of_adviser_recommendations.append(adviser_recommendation)

        # check there are four modules in MT3501 to MT3508
        list_of_MT350X_modules = ['MT3501', 'MT3502', 'MT3503', 'MT3504', 'MT3505', 'MT3506', 'MT3507', 'MT3508']
        number_of_MT350X_modules = student.get_number_of_modules_in_list(list_of_MT350X_modules)
        if number_of_MT350X_modules < 4:
            list_of_missed_requirements.append('Student is only taking ' + str(number_of_MT350X_modules) + 'out of MT3501-MT3508')
            
        # check there is a computing module
        list_of_computing_modules = ['MT3510', 'MT4111', 'MT4112', 'MT4113']
        number_of_computing_modules = student.get_number_of_modules_in_list(list_of_computing_modules)
        if number_of_computing_modules ==0:
            list_of_missed_requirements.append('Student is not taking a computing module')
        
        # check there is a final year project
        list_of_project_codes = ['MT4598', 'MT4599']
        number_final_year_projects= student.get_number_of_modules_in_list(list_of_project_codes)
        if number_final_year_projects !=1:
            list_of_missed_requirements.append('Student is not taking an allowed final year project')
        else:
            # check that the student is actually taking it in year 4
            if 'MT4598' in student.full_module_list:
                this_year = student.honours_module_choices[student.honours_module_choices['Module code'] == 'MT4598']['Honours year'].iloc[0]
            else:
                this_year = student.honours_module_choices[student.honours_module_choices['Module code'] == 'MT4599']['Honours year'].iloc[0]
            if this_year != 'Year 2':
                list_of_missed_requirements.append('Student is not taking their final year project in their final year.')
        
        # check that unallowed modules are not taken
        unallowed_modules = ['MT4794', 'MT4795', 'MT4796', 'MT4797']
        number_of_unallowed_modules = student.get_number_of_modules_in_list(unallowed_modules)
        if number_of_unallowed_modules >0:
            list_of_missed_requirements.append('Student is taking a module in MT4794-MT4797')
            
        # check dip-down and dip-across: no more than two modules should be outside of MT3X to MT5X
        list_of_all_non_honours_modules = [module for module in student.all_honours_modules if 'MT3' not in module 
                                                                                        and 'MT4' not in module 
                                                                                        and 'MT5' not in module
                                                                                        and 'ID4001' not in module
                                                                                        and 'ID5059' not in module]
        if len(list_of_all_non_honours_modules) >2:
            list_of_missed_requirements.append('Student is taking more than 2 modules as dip-down or dip-across, which is not allowed.')

        # check that there are at least 90 credits (6 modules) at 4000 level or above
        list_of_4000_and_5000_modules = [module for module in student.all_honours_modules if 'MT4' in module or 'MT5' in module]
        if len(list_of_4000_and_5000_modules) <6:
            list_of_missed_requirements.append('Student is not planning to take enough credits at 4000 level or above')

        # remind advisers to get permissions
        list_of_planned_5000_level_modules = [module for module in student.planned_honours_modules if 'MT5' in module]
        if len(list_of_planned_5000_level_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take 5000 level modules (which will require permission)')

        list_of_2000_level_modules = [module for module in student.planned_honours_modules if 'MT2' in module]
        if len(list_of_2000_level_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take 2000 level modules, (which will require permission)')

        list_of_planned_non_maths_modules = [module for module in student.planned_honours_modules if 'MT2' not in module 
                                                                                        and 'MT3' not in module 
                                                                                        and 'MT4' not in module 
                                                                                        and 'MT5' not in module]
        if len(list_of_planned_non_maths_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take non-MT modules, which requires permission')

    ### MMATH REQUIREMENTS ###
    elif student.programme_name == 'Master in Mathematics (Honours) Mathematics':
        # check the credit load
        missed_requirement, adviser_recommendation = check_for_120_credits_each_year(student)
        list_of_missed_requirements.append(missed_requirement)
        list_of_adviser_recommendations.append(adviser_recommendation)

        # check there are four modules in MT3501 to MT3508
        list_of_MT350X_modules = ['MT3501', 'MT3502', 'MT3503', 'MT3504']
        number_of_MT350X_modules = student.get_number_of_modules_in_list(list_of_MT350X_modules)
        if number_of_MT350X_modules < 4:
            list_of_missed_requirements.append('Student is only taking ' + str(number_of_MT350X_modules) + ' modules out of MT3501-MT3504')
            
        # check there is a module selected from MT3507 and MT3508
        list_of_statistics_modules = ['MT3507', 'MT3508']
        number_of_statistics_modules = student.get_number_of_modules_in_list(list_of_statistics_modules)
        if number_of_statistics_modules == 0:
            list_of_missed_requirements.append('Student is not taking a module in [MT3507,MT3508]')
 
        # check there is a computing module
        list_of_computing_modules = ['MT3510', 'MT4111', 'MT4112', 'MT4113','MT5611']
        number_of_computing_modules = student.get_number_of_modules_in_list(list_of_computing_modules)
        if number_of_computing_modules ==0:
            list_of_missed_requirements.append('Student is not taking a computing module')
        
        # check there is a final year project
        list_of_project_codes = ['MT5599']
        number_final_year_projects= student.get_number_of_modules_in_list(list_of_project_codes)
        if number_final_year_projects !=1:
            list_of_missed_requirements.append('Student is not taking an allowed final year project')
        else:
            # check that the student is actually taking it in year 5
            this_year = student.honours_module_choices[student.honours_module_choices['Module code'] == 'MT5599']['Honours year'].iloc[0]
            if this_year != 'Year 3':
                list_of_missed_requirements.append('Student is not taking their final year project in their final year.')
        
        # check dip-down and dip-across: no more than two modules should be outside of MT3X to MT5X
        list_of_all_non_honours_modules = [module for module in student.all_honours_modules if 'MT3' not in module 
                                                                                        and 'MT4' not in module 
                                                                                        and 'MT5' not in module
                                                                                        and 'ID5059' not in module]
        if len(list_of_all_non_honours_modules) >2:
            list_of_missed_requirements.append('Student is taking more than 2 modules as dip-down or dip-across, which is not allowed')

        # check that there are at least 120 credits (7 modules) at 5000 level or above
        list_of_5000_modules = [module for module in student.all_honours_modules if 'MT5' in module]
        if len(list_of_5000_modules) <7:
            list_of_missed_requirements.append('Student is not planning to take enough credits at 5000 level')

        list_of_2000_level_modules = [module for module in student.planned_honours_modules if 'MT2' in module]
        if len(list_of_2000_level_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take 2000 level modules, (which will require permission)')

        list_of_planned_non_maths_modules = [module for module in student.planned_honours_modules if 'MT2' not in module 
                                                                                        and 'MT3' not in module 
                                                                                        and 'MT4' not in module 
                                                                                        and 'MT5' not in module]
        if len(list_of_planned_non_maths_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take non-MT modules, which requires permission')
 
    else:
        list_of_missed_requirements.append('No programme requirements available')

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
        if honours_year == 'Year 1' or honours_year == 'Year 2':
            if len(this_data_base)!=8:
                list_of_missed_requirements.append('Not collecting 120 credits in ' + honours_year)
        if honours_year == 'Year 3' and len(this_data_base)!=7:
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
                list_of_adviser_recommendations.append('Student is taking a high course load in second semester of final honours year')
        elif honours_year == 'Year 3':
            this_reduced_data_base = this_data_base[this_data_base['Module code'] != 'MT5599']
            semester_1_modules = this_reduced_data_base[this_reduced_data_base['Semester'] == 'S1']['Module code']
            semester_2_modules = this_reduced_data_base[this_reduced_data_base['Semester'] == 'S1']['Module code']
            if len(semester_1_modules) != 3 or len(semester_2_modules) != 3:
                list_of_adviser_recommendations.append('Student is taking uneven course load in final honours year')
    
    missed_requirement = merge_list_to_long_string(list_of_missed_requirements)
    adviser_recommendation = merge_list_to_long_string(list_of_adviser_recommendations)
    
    return missed_requirement, adviser_recommendation

