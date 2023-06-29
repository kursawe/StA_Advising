import collections
from .infrastructure import *
import pandas as pd

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
    
    ### BSC MATHEMATICS REQUIREMENTS
    if student.programme_name in ['Bachelor of Science (Honours) Mathematics',
                                  'Master of Arts (Honours) Mathematics']:
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
            list_of_adviser_recommendations.append('Student is planning to take 2000 level modules (which will require permission)')

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

        # check that there are at least 120 credits (7 modules) at 5000 level
        list_of_5000_modules = [module for module in student.all_honours_modules if 'MT5' in module]
        if len(list_of_5000_modules) <7:
            list_of_missed_requirements.append('Student is not planning to take enough credits at 5000 level')

        list_of_2000_level_modules = [module for module in student.planned_honours_modules if 'MT2' in module]
        if len(list_of_2000_level_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take 2000 level modules (which will require permission)')

        list_of_planned_non_maths_modules = [module for module in student.planned_honours_modules if 'MT2' not in module 
                                                                                        and 'MT3' not in module 
                                                                                        and 'MT4' not in module 
                                                                                        and 'MT5' not in module]
        if len(list_of_planned_non_maths_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take non-MT modules, which requires permission')
            
    ### MMATH APPLIED REQUIREMENTS ###
    elif student.programme_name == 'Master in Mathematics (Honours) Applied Mathematics':
        # check the credit load
        missed_requirement, adviser_recommendation = check_for_120_credits_each_year(student)
        list_of_missed_requirements.append(missed_requirement)
        list_of_adviser_recommendations.append(adviser_recommendation)

        # check there are four modules in MT3501, MT3502, MT3503, MT3504, MT3506
        list_of_MT350X_modules = ['MT3501', 'MT3502', 'MT3503', 'MT3504','MT3506']
        number_of_MT350X_modules = student.get_number_of_modules_in_list(list_of_MT350X_modules)
        if number_of_MT350X_modules < 5:
            list_of_missed_requirements.append('Student is not taking all of [MT3501, MT3502, MT3503, MT3504, MT3506]')
            
        # check there is a computing module
        list_of_computing_modules = ['MT3510', 'MT4111', 'MT4112']
        number_of_computing_modules = student.get_number_of_modules_in_list(list_of_computing_modules)
        if number_of_computing_modules ==0:
            list_of_missed_requirements.append('Student is not taking a computing module')
        
        # check there are enough applied modules
        list_of_applied_modules_1 = ['MT4005', 'MT4507', 'MT4508', 'MT4509', 'MT4510', 'MT4511', 'MT4551', 'MT4552', 'MT4553']
        number_of_applied_modules_1 = student.get_number_of_modules_in_list(list_of_applied_modules_1)
        if number_of_applied_modules_1 < 3:
            list_of_missed_requirements.append('Student is not taking sufficiently many 4000 level applied modules')
      
        list_of_applied_modules_2 = ['MT5802', 'MT5806', 'MT5809', 'MT5810', 'MT5840', 'MT5842',
                                     'MT5846','MT5849','MT5850','MT5853','MT5854','MT5855','MT5856','MT5590', 'MT5990']
        number_of_applied_modules_2 = student.get_number_of_modules_in_list(list_of_applied_modules_2)
        if number_of_applied_modules_2 < 3:
            list_of_missed_requirements.append('Student is not taking sufficiently many 5000 level applied modules')

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
            list_of_adviser_recommendations.append('Student is planning to take 2000 level modules (which will require permission)')

        list_of_planned_non_maths_modules = [module for module in student.planned_honours_modules if 'MT2' not in module 
                                                                                        and 'MT3' not in module 
                                                                                        and 'MT4' not in module 
                                                                                        and 'MT5' not in module]
        if len(list_of_planned_non_maths_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take non-MT modules, which requires permission')

    ### MMATH PURE REQUIREMENTS ###
    elif student.programme_name == 'Master in Mathematics (Honours) Pure Mathematics':
        # check the credit load
        missed_requirement, adviser_recommendation = check_for_120_credits_each_year(student)
        list_of_missed_requirements.append(missed_requirement)
        list_of_adviser_recommendations.append(adviser_recommendation)

        # check there are four modules in MT3501, MT3502, MT3503, MT3504, MT3505, MT4003, MT4004
        list_of_MT350X_modules = ['MT3501', 'MT3502', 'MT3503', 'MT3504', 'MT3505', 'MT4003', 'MT4004']
        number_of_MT350X_modules = student.get_number_of_modules_in_list(list_of_MT350X_modules)
        if number_of_MT350X_modules < 4:
            list_of_missed_requirements.append('Student is only taking ' + str(number_of_MT350X_modules) + ' modules out of MT3501, MT3502, MT3503, MT3504, MT3505, MT4003, MT4004')
            
        # check there is a computing module
        list_of_computing_modules = ['MT3510', 'MT4111', 'MT4112']
        number_of_computing_modules = student.get_number_of_modules_in_list(list_of_computing_modules)
        if number_of_computing_modules ==0:
            list_of_missed_requirements.append('Student is not taking a computing module')
        
        # check there are enough pure modules
        list_of_pure_modules = ['MT5821', 'MT5823', 'MT5824', 'MT5825', 'MT5826', 'MT5827', 'MT5828', 'MT5829','MT5830', 'MT5836','MT5837', 'MT5861', 'MT5862','MT5863', 'MT5864',
                                'MT5865','MT5866', 'MT5687', 'MT5868', 'MT5869', 'MT5870', 'MT5876','MT5877', 'MT5590', 'MT5990']
        number_of_pure_modules = student.get_number_of_modules_in_list(list_of_pure_modules)
        if number_of_pure_modules < 4:
            list_of_missed_requirements.append('Student is not taking sufficiently many pure modules')
      
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
            list_of_adviser_recommendations.append('Student is planning to take 2000 level modules (which will require permission)')

        list_of_planned_non_maths_modules = [module for module in student.planned_honours_modules if 'MT2' not in module 
                                                                                        and 'MT3' not in module 
                                                                                        and 'MT4' not in module 
                                                                                        and 'MT5' not in module]
        if len(list_of_planned_non_maths_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take non-MT modules, which requires permission')

    ### MA STATISTICS REQUIREMENTS ###
    elif student.programme_name in ['Bachelor of Science (Honours) Statistics','Master of Arts (Honours) Statistics']:
        # check the credit load
        missed_requirement, adviser_recommendation = check_for_120_credits_each_year(student)
        list_of_missed_requirements.append(missed_requirement)
        list_of_adviser_recommendations.append(adviser_recommendation)

        # check there are four modules in MT3501, MT3502, MT3503, MT3504, MT3505, MT4003, MT4004
        list_of_MT350X_modules = ['MT3501', 'MT3507', 'MT3508', 'MT4606', 'MT4531']
        number_of_MT350X_modules = student.get_number_of_modules_in_list(list_of_MT350X_modules)
        if number_of_MT350X_modules < 5:
            list_of_missed_requirements.append('Student is not taking all of MT3501, MT3507, MT3508, MT4606, MT4531')
            
        # check there is a computing module
        list_of_computing_modules = ['MT4113']
        number_of_computing_modules = student.get_number_of_modules_in_list(list_of_computing_modules)
        if number_of_computing_modules ==0:
            list_of_missed_requirements.append('Student is not taking a computing module')
        
        # check there are enough statistics modules
        list_of_statistics_modules = ['MT4527', 'MT4528', 'MT4530', 'MT4537', 'MT4539', 'MT4607', 'MT4608', 'MT4609', 'MT4614']
        number_of_statistics_modules = student.get_number_of_modules_in_list(list_of_statistics_modules)
        if number_of_statistics_modules < 2:
            list_of_missed_requirements.append('Student is not taking sufficiently many statistics modules')
      
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
                                                                                        and 'ID5059' not in module]
        if len(list_of_all_non_honours_modules) >2:
            list_of_missed_requirements.append('Student is taking more than 2 modules as dip-down or dip-across, which is not allowed')

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
            list_of_adviser_recommendations.append('Student is planning to take 2000 level modules (which will require permission)')

        list_of_planned_non_maths_modules = [module for module in student.planned_honours_modules if 'MT2' not in module 
                                                                                        and 'MT3' not in module 
                                                                                        and 'MT4' not in module 
                                                                                        and 'MT5' not in module]
        if len(list_of_planned_non_maths_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take non-MT modules, which requires permission')
 

    ### MASTER IN CHEMISTRY WITH MATHEMATICS REQUIREMENTS ###
    elif student.programme_name == 'Master in Chemistry (Honours) Chemistry with Mathematics':
        # This next code is different from other requirements because the conditions on year 4 and 5 are different for this particular
        # programme
        full_module_table = pd.concat([student.passed_module_table, student.honours_module_choices], ignore_index=True)
        reduced_module_table = full_module_table[(full_module_table['Honours year'] == 'Year 1') | (full_module_table['Honours year']=='Year 2')]
        year_three_and_four_modules = reduced_module_table['Module code'].to_list()
        
        second_reduced_module_table = full_module_table[full_module_table['Honours year'] == 'Year 3']
        year_five_modules = second_reduced_module_table['Module code'].to_list()

        # check there are three modules in MT3501 to MT3508
        list_of_MT350X_modules = ['MT3501', 'MT3502', 'MT3503', 'MT3504', 'MT3505', 'MT3506', 'MT3507', 'MT3508']
        number_of_MT350X_modules = len(set.intersection(set(year_three_and_four_modules),set(list_of_MT350X_modules)))
        if number_of_MT350X_modules < 3:
            list_of_missed_requirements.append('Student is only taking ' + str(number_of_MT350X_modules) + ' modules out of MT3501-MT3508 in years 3 and 4 (instead of 3)')
            
        # check there are 90 credits (6 modules) in MT modules for year 3 and 4
        list_of_all_MT_modules = [module for module in year_three_and_four_modules if 'MT3' in module 
                                                                                   or 'MT4' in module]

        if len(list_of_all_MT_modules) < 6:
            list_of_missed_requirements.append('Student is not taking 90 credits in MT modules in year 3 and 4')

        # check year 5 modules have maximally 30 credits in MT5600-MT5899:
        number_of_counting_year_5_modules = 0
        number_of_unallowed_modules = 0
        for module in year_five_modules:
            if module.startswith('MT'):
                module_number = int(module[2:])
                if module_number > 5600 and module_number< 5899:
                    number_of_counting_year_5_modules += 1
                else:
                    number_of_unallowed_modules += 1
        
        if number_of_counting_year_5_modules>2:
            list_of_missed_requirements.append('Student is taking taking more than 2 MT modules in year 5 (which is not allowed)')
        
        if number_of_unallowed_modules > 0:
            list_of_missed_requirements.append('Student is taking a MT module in year 5 which they are not allowed to take (i.e. outside of MT5600-MT5899)')
            
        # Students are not allowed to take MT4599
        if 'MT4599' in student.all_honours_modules:
            list_of_missed_requirements.append('Student is taking taking MT4599 (which is not allowed)')
                
        list_of_adviser_recommendations.append('This is a joint honours programme and the adviser needs to manually check that the student \
takes a total of 120 credits per year')

    ### BSC MATH AND PHYSICS REQUIREMENTS
    elif student.programme_name == 'Bachelor of Science (Honours) Mathematics and Physics':
        # This next code is different from other requirements because the conditions on year 3 are different for this particular
        # programme
        full_module_table = pd.concat([student.passed_module_table, student.honours_module_choices], ignore_index=True)
        reduced_module_table = full_module_table[(full_module_table['Honours year'] == 'Year 1')]
        year_three_modules = reduced_module_table['Module code'].to_list()
        
        second_reduced_module_table = full_module_table[full_module_table['Honours year'] == 'Year 0']
        relevant_subhonours_modules = second_reduced_module_table['Module code'].to_list()
        
        if 'MT2507' in relevant_subhonours_modules and 'MT2506' in relevant_subhonours_modules:
            if 'MT3504' not in year_three_modules:
                list_of_missed_requirements.append('Student is not taking MT3504 in year 3 (which is required for them)')
        elif 'MT2502' in relevant_subhonours_modules and 'MT2505' in relevant_subhonours_modules:
            if 'MT3502' not in year_three_modules or 'MT3505' not in year_three_modules:
                list_of_missed_requirements.append('Student is not taking MT3505 and MT3502 in year 3 (which is a requirement for them)')
        else:
            list_of_missed_requirements.append('Student does not seem to have an allowed selection of subhonours MT modules')
                
        # check that there are at least 90 credits of MT modules across both honours years
        list_of_all_MT_modules = [module for module in student.all_honours_modules if 'MT3' in module 
                                                                                   or 'MT4' in module]
        if len(list_of_all_MT_modules) < 6:
            list_of_missed_requirements.append('Student planning less then 90 credits (6 modules) in MT modules')

        # check there is a final year project
        list_of_project_codes = ['MT4596', 'MT4599', 'PH4111']
        number_final_year_projects= student.get_number_of_modules_in_list(list_of_project_codes)
        if number_final_year_projects !=1:
            list_of_missed_requirements.append('Student is not taking an allowed final year project')
        else:
            # check that the student is actually taking it in year 4
            if 'MT4596' in student.full_module_list:
                this_year = student.honours_module_choices[student.honours_module_choices['Module code'] == 'MT4596']['Honours year'].iloc[0]
            elif 'MT4599' in student.full_module_list:
                this_year = student.honours_module_choices[student.honours_module_choices['Module code'] == 'MT4599']['Honours year'].iloc[0]
            else:
                this_year = student.honours_module_choices[student.honours_module_choices['Module code'] == 'PH4111']['Honours year'].iloc[0]
            if this_year != 'Year 2':
                list_of_missed_requirements.append('Student is not taking their final year project in their final year.')
 
        list_of_adviser_recommendations.append('This is a joint honours programme and the adviser needs to manually check that the student \
takes a total of 120 credits per year and that the student takes at least 90 credits at 4000 level')

    ### MASTER MATHEMATICS AND THEORETICAL PHYSICS REQUIREMENTS
    elif student.programme_name == 'Master in Physics (Honours) Mathematics and Theoretical Physics':
        # This next code is different from other requirements because the conditions on year 3 are different for this particular
        # programme
        full_module_table = pd.concat([student.passed_module_table, student.honours_module_choices], ignore_index=True)
        reduced_module_table = full_module_table[(full_module_table['Honours year'] == 'Year 1')]
        year_three_modules = reduced_module_table['Module code'].to_list()
        
        second_reduced_module_table = full_module_table[full_module_table['Honours year'] == 'Year 0']
        relevant_subhonours_modules = second_reduced_module_table['Module code'].to_list()
        
        third_reduced_module_table = full_module_table[full_module_table['Honours year'] == 'Year 2']
        year_four_modules = third_reduced_module_table['Module code'].to_list()

        # Check the analysis part of the requirements
        if 'MT2507' in relevant_subhonours_modules and 'MT2506' in relevant_subhonours_modules:
            if 'MT3504' not in year_three_modules:
                list_of_missed_requirements.append('Student is not taking MT3504 in year 3 (which is required for them)')
        elif 'MT2502' in relevant_subhonours_modules and 'MT2505' in relevant_subhonours_modules:
            if 'MT3502' not in year_three_modules or 'MT3505' not in year_three_modules:
                list_of_missed_requirements.append('Student is not taking MT3505 and MT3502 in year 3 (which is a requirement for them)')
        else:
            list_of_missed_requirements.append('Student does not seem to have an allowed selection of subhonours MT modules')
                
        # Check the linear mathematics part of the requirements:
        if 'MT3501' not in year_three_modules:
            list_of_missed_requirements.append('Student is not taking MT3501 in year 3, which is a requirement')
        
        # check fourth year requirement
        list_of_required_fourth_year_modules = ['MT3503', 'PH4028']
        number_of_required_fourth_year_modules = len(set.intersection(set(year_four_modules),set(list_of_required_fourth_year_modules)))
        if number_of_required_fourth_year_modules == 0:
            list_of_missed_requirements.append('Student is not taking one of [MT3505, PH4028] in year 4')
            
        # check that there are at least 135 credits of MT modules (9 modules) across all honours years
        list_of_all_MT_modules = [module for module in student.all_honours_modules if 'MT2' in module 
                                                                                   or 'MT3' in module 
                                                                                   or 'MT4' in module
                                                                                   or 'MT5' in module]
        if len(list_of_all_MT_modules) < 9 and 'MT5599' not in student.all_honours_modules:
            list_of_missed_requirements.append('Student planning less then 135 credits (9 modules) in MT modules')
        elif len(list_of_all_MT_modules) < 8 and 'MT5599' in student.all_honours_modules:
            list_of_missed_requirements.append('Student planning less then 135 credits (8 modules + MT5599) in MT modules')

        # check dip-down 
        list_of_all_dip_down_modules = [module for module in student.all_honours_modules if 'MT2' in module]
        if len(list_of_all_dip_down_modules) >2:
            list_of_missed_requirements.append('Student is taking more than 2 modules as dip-down, which is not allowed')

        # check there is a final year project
        list_of_project_codes = ['MT5599', 'PH5103']
        number_final_year_projects= student.get_number_of_modules_in_list(list_of_project_codes)
        if number_final_year_projects !=1:
            list_of_missed_requirements.append('Student is not taking an allowed final year project')
        else:
            # check that the student is actually taking it in year 4
            if 'MT5599' in student.full_module_list:
                this_year = student.honours_module_choices[student.honours_module_choices['Module code'] == 'MT5599']['Honours year'].iloc[0]
            elif 'PH5103' in student.full_module_list:
                this_year = student.honours_module_choices[student.honours_module_choices['Module code'] == 'PH5103']['Honours year'].iloc[0]
            if this_year != 'Year 3':
                list_of_missed_requirements.append('Student is not taking their final year project in their final year.')
 
        list_of_2000_level_modules = [module for module in student.planned_honours_modules if 'MT2' in module]
        if len(list_of_2000_level_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take 2000 level modules (which will require permission)')

        list_of_adviser_recommendations.append('This is a joint honours programme and the adviser needs to manually check that the student \
takes a total of 120 credits per year and that the student takes at least 120 credits at 5000 level')

    elif student.programme_name == 'Bachelor of Science (Honours) Computer Science and Statistics':

        list_of_MT350X_modules = ['MT3501', 'MT3502', 'MT3503', 'MT3504', 'MT3505', 'MT3506', 'MT3507', 'MT3508']
        number_of_MT350X_modules = student.get_number_of_modules_in_list(list_of_MT350X_modules)
        if number_of_MT350X_modules < 3:
            list_of_missed_requirements.append('Student is only taking ' + str(number_of_MT350X_modules) + ' modules out of MT3501-MT3508 (instead of 3)')
            
        list_of_stats_modules_1 = ['MT4531','MT4606']
        number_of_stats_modules_1 = student.get_number_of_modules_in_list(list_of_stats_modules_1)
        if number_of_stats_modules_1 == 0:
            list_of_missed_requirements.append('Student not taking a module in [MT4531,MT4606]')

        list_of_stats_modules_2 = ['MT4113', 'MT4527', 'MT4528', 'MT4530', 'MT4537', 'MT4539', 'MT4607', 'MT4608', 'MT4609', 'MT4614']
        number_of_stats_modules_2 = student.get_number_of_modules_in_list(list_of_stats_modules_2)
        if number_of_stats_modules_2 == 0:
            list_of_missed_requirements.append('Student not taking a module in [MT4113, MT4527, MT4528, MT4530, MT4537, MT4539, MT4607, MT4608, MT4609, MT4614]')

        # check there is a final year project
        list_of_project_codes = ['MT4599']
        number_final_year_projects= student.get_number_of_modules_in_list(list_of_project_codes)
        if number_final_year_projects !=1:
            list_of_missed_requirements.append('Student is not taking an allowed final year project')
        else:
            # check that the student is actually taking it in year 4
            this_year = student.honours_module_choices[student.honours_module_choices['Module code'] == 'MT4599']['Honours year'].iloc[0]
            if this_year != 'Year 2':
                list_of_missed_requirements.append('Student is not taking their final year project in their final year.')
        
        # check that the student is taking at least 120 credits (8 modules) in MT modules (60 modules any code + 15 modules final year project + 45 credits of MT3501-MT3508)
        # while also checking that there are not too many dip-down ID/VP modules
        list_of_all_MT_modules = [module for module in student.all_honours_modules if 'MT3' in module 
                                                                                      or 'MT4' in module]
    
        list_of_all_allowed_modules = [module for module in student.all_honours_modules if 'MT2' in module 
                                                                                        or 'MT3' in module 
                                                                                        or 'MT4' in module
                                                                                        or 'ID4001' in module
                                                                                        or 'VP' in module]

        if len(list_of_all_allowed_modules) <8 or len(list_of_all_MT_modules) < 7:
            if len(list_of_all_MT_modules) < 7 and len(list_of_all_allowed_modules) > 7:
                list_of_missed_requirements.append('Student is taking too many modules as dip-down or in ID/VP moduels (which is not allowed)')
            else:
                list_of_missed_requirements.append('Student is not taking enough credits (less than 8 modules) among MT modules')
    
        # check planned dip-down
        list_of_planned_2000_level_modules = [module for module in student.planned_honours_modules if 'MT2' in module
                                                                                                    or 'ID4001' in module
                                                                                                    or 'VP' in module]
        if len(list_of_planned_2000_level_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take 2000 level modules or ID4001 or VP modules (which all require permission)')
    
        list_of_adviser_recommendations.append('This is a joint honours programme and the adviser needs to manually check that the student \
takes a total of 120 credits per year and that they take at least 90 credits at 4000 level')

 
    ### JOINT HONOURS REQUIREMENTS ###
    elif student.programme_name in ['Master of Arts (Honours) Mathematics and Philosophy',
                                    'Bachelor of Science (Honours) Chemistry and Mathematics',
                                    'Bachelor of Science (Honours) Mathematics and Psychology (BPS Recognition Route)',
                                    'Master of Arts (Honours) English and Mathematics',
                                    'Bachelor of Science (Honours) Mathematics and Philosophy',
                                    'Bachelor of Science (Honours) Economics and Mathematics',
                                    'Bachelor of Science (Honours) Computer Science and Mathematics',
                                    'Bachelor of Science (Honours) Financial Economics and Mathematics',
                                    'Master of Arts (Honours) Art History and Mathematics',
                                    'Master of Arts (Honours) Mathematics and Medieval History',
                                    'Bachelor of Science (Honours) Biology and Mathematics',
                                    'Master of Arts (Honours) International Relations and Mathematics',
                                    'Master of Arts (Honours) Economics and Mathematics',
                                    'Master of Arts (Honours) Arabic and Mathematics']:
        
        missed_requirement, adviser_recommendation = check_joint_honours_requirements(student)
        list_of_missed_requirements.append(missed_requirement)
        list_of_adviser_recommendations.append(adviser_recommendation)
        
    else:
        list_of_missed_requirements.append('No programme requirements available')

    # merge all missed requirements into a string
    missed_requirements = merge_list_to_long_string(list_of_missed_requirements)
    adviser_recommendations = merge_list_to_long_string(list_of_adviser_recommendations)

    return missed_requirements, adviser_recommendations
    
def check_joint_honours_requirements(student):
    """Check whether a student meets the requirements for a joint honours programme, 
    such as the Bachelor of Science (Honours) Chemistry and Mathematics or the
    Master of Arts (Honours) Mathematics and Philosophy. These requirements can be used as a
    reference for these conditions.

    Parameters :
    ------------

    student : instance of Student() class
        the student for which we are checking the requirements.

    Returns :
    ---------

    missed_requirements : string
        Unmet programme requirements. Will return 'None' if all programme requirements are met
        
    adviser_recommendations : string
        advising recommendations that don't strictly count as unmet programme requirements. Here,
        this includes conditions that the adviser needs to check manually
    """
    list_of_missed_requirements = []
    list_of_adviser_recommendations = []

    # check there are three modules in MT3501 to MT3508
    list_of_MT350X_modules = ['MT3501', 'MT3502', 'MT3503', 'MT3504', 'MT3505', 'MT3506', 'MT3507', 'MT3508']
    number_of_MT350X_modules = student.get_number_of_modules_in_list(list_of_MT350X_modules)
    if number_of_MT350X_modules < 3:
        list_of_missed_requirements.append('Student is only taking ' + str(number_of_MT350X_modules) + ' modules out of MT3501-MT3504 (instead of 3)')
        
    # check there is a final year project
    list_of_project_codes = ['MT4599']
    number_final_year_projects= student.get_number_of_modules_in_list(list_of_project_codes)
    if number_final_year_projects !=1:
        list_of_missed_requirements.append('Student is not taking an allowed final year project')
    else:
        # check that the student is actually taking it in year 4
        this_year = student.honours_module_choices[student.honours_module_choices['Module code'] == 'MT4599']['Honours year'].iloc[0]
        if this_year != 'Year 2':
            list_of_missed_requirements.append('Student is not taking their final year project in their final year.')
    
    # check that the student is taking at least 120 credits (8 modules) in MT modules (60 modules any code + 15 modules final year project + 45 credits of MT3501-MT3508)
    # while also checking that there are not too many dip-down ID/VP modules
    list_of_all_MT_modules = [module for module in student.all_honours_modules if 'MT3' in module 
                                                                                  or 'MT4' in module]

    list_of_all_allowed_modules = [module for module in student.all_honours_modules if 'MT2' in module 
                                                                                    or 'MT3' in module 
                                                                                    or 'MT4' in module
                                                                                    or 'ID4001' in module
                                                                                    or 'VP' in module]

    if len(list_of_all_allowed_modules) <8 or len(list_of_all_MT_modules) < 7:
        if len(list_of_all_MT_modules) < 7 and len(list_of_all_allowed_modules) > 7:
            list_of_missed_requirements.append('Student is taking too many modules as dip-down or in ID/VP moduels (which is not allowed)')
        else:
            list_of_missed_requirements.append('Student is not taking enough credits (less than 8 modules) among MT modules')

    # check planned dip-down
    list_of_planned_2000_level_modules = [module for module in student.planned_honours_modules if 'MT2' in module
                                                                                                or 'ID4001' in module
                                                                                                or 'VP' in module]
    if len(list_of_planned_2000_level_modules) >0:
        list_of_adviser_recommendations.append('Student is planning to take 2000 level modules or ID4001 or VP modules (which all require permission)')

    list_of_adviser_recommendations.append('This is a joint honours programme and the adviser needs to manually check that the student \
takes a total of 120 credits per year and that they take at least 90 credits at 4000 level')


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

