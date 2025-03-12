import collections
from .infrastructure import *
import pandas as pd

# a dictionary of possible joint projects
joint_project_dictionary = {}
joint_project_dictionary['Bachelor of Science (Honours) Computer Science and Mathematics'] = ['CS4796']
joint_project_dictionary['Bachelor of Science (Honours) Computer Science and Statistics'] = ['CS4796']
joint_project_dictionary['Master of Arts (Honours) Mathematics and Philosophy'] = ['SA4796', 'SA4797']
joint_project_dictionary['Bachelor of Science (Honours) Mathematics and Psychology (BPS Recognition Route)'] = ['PS4796', 'PS4797']
joint_project_dictionary['Bachelor of Science (Honours) Psychology and Statistics'] = ['PS4796', 'PS4797']
joint_project_dictionary['Bachelor of Science (Honours) Mathematics and Philosophy'] = ['SA4796', 'SA4797']
joint_project_dictionary['Master of Arts (Honours) Art History and Mathematics'] = ['AH4795']
joint_project_dictionary['Master of Arts (Honours) Mathematics and Medieval History'] = ['HI4797']
joint_project_dictionary['Bachelor of Science (Honours) Biology and Mathematics'] = ['BL4797','BL4796']
joint_project_dictionary['Master of Arts (Honours) International Relations and Mathematics'] = ['IR4795']
joint_project_dictionary['Master of Arts (Honours) Arabic and Mathematics'] = ['ML4794']

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
    
    # unaccounted years of absence
    if student.current_honours_year > student.expected_honours_years:
        list_of_missed_requirements.append('Year could not be inferred, student will require manual checking - flagged issues can be wrong')

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
        
    # flag up z-coded and deferred modules
    if len(student.z_coded_modules) > 0:
        advise_string = 'Modules '
        for entry in student.z_coded_modules:
            advise_string += entry
            if entry != student.z_coded_modules[-1]:
                advise_string += ' and '
        advise_string += ' have been treated as passed even though they are z-coded - action may be required if these are failed'
        list_of_adviser_recommendations.append(advise_string)

    if len(student.deferred_modules) > 0:
        advise_string = 'Modules '
        for entry in student.deferred_modules:
            advise_string += entry
            if entry != student.deferred_modules[-1]:
                advise_string += ' and '
        advise_string += ' have been treated as passed even though they are deferred - action may be required if these are failed'
        list_of_adviser_recommendations.append(advise_string)
        
    if len(student.s_coded_modules) > 0:
        advise_string = 'Modules '
        for entry in student.s_coded_modules:
            advise_string += entry
            if entry != student.s_coded_modules[-1]:
                advise_string += ' and '
        advise_string += ' have been treated as passed even though they are failed and s-coded - action may be required if these are failed'
        list_of_adviser_recommendations.append(advise_string)
 
    if len(student.modules_awaiting_reassessment) > 0:
        advise_string = 'Modules '
        for entry in student.modules_awaiting_reassessment:
            advise_string += entry
            if entry != student.modules_awaiting_reassessment[-1]:
                advise_string += ' and '
        advise_string += ' have been treated as passed even though they are failed and are awaiting reassessment - action may be required if these are failed'
        list_of_adviser_recommendations.append(advise_string)
    
    # Check for study abroad
    student_studied_abroad = (any('J' in item for item in student.full_module_list) or 
                              any('MTSAU' in item for item in student.full_module_list) or
                              any('MT30' in item for item in student.full_module_list))

    if student_studied_abroad:
        list_of_missed_requirements.append('Student studied abroad and will require manual checking - flagged issues can be wrong')
    
    ### BSC MATHEMATICS REQUIREMENTS
    if ( student.programme_name  == 'Bachelor of Science (Honours) Mathematics' or
         student.programme_name  == 'Master of Arts (Honours) Mathematics'):
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
        if number_final_year_projects <1:
            list_of_missed_requirements.append('Student is not taking an allowed final year project')
        elif number_final_year_projects >1:
            list_of_missed_requirements.append('Student selected multiple final year projects')
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
            
        # # check dip-down and dip-across: no more than two modules should be outside of MT3X to MT5X
        # list_of_all_non_honours_modules = [module for module in student.all_honours_modules if 'MT3' not in module 
        #                                                                                 and 'MT4' not in module 
        #                                                                                 and 'MT5' not in module
        #                                                                                 and 'ID4001' not in module
        #                                                                                 and 'ID5059' not in module]
        # if len(list_of_all_non_honours_modules) >2:
        #     list_of_missed_requirements.append('Student is taking more than 2 modules as dip-down or dip-across, which is not allowed.')
            
        list_of_all_MT_modules = [module for module in student.all_honours_modules if 'MT3' in module 
                                                                                        or 'MT4' in module 
                                                                                        or 'MT5' in module
                                                                                        or 'ID4001' in module
                                                                                        or 'ID5059' in module]

        if len(list_of_all_MT_modules) <14:
            list_of_missed_requirements.append('Student is taking more than 2 modules as dip-down or dip-across, which is not allowed')
 
        # check that there are at least 90 credits (6 modules) at 4000 level or above
        list_of_4000_and_5000_modules = [module for module in student.all_honours_modules if 'MT4' in module or 'MT5' in module]
        if len(list_of_4000_and_5000_modules) <6:
            list_of_missed_requirements.append('Student is not planning to take enough credits at 4000 level or above')

        # remind advisers to get permissions
        list_of_planned_5000_level_modules = [module for module in student.planned_honours_modules if 'MT5' in module or 'ID5059' in module]
        if len(list_of_planned_5000_level_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take 5000 level modules (which will require permission)')

        list_of_2000_level_modules = [module for module in student.planned_honours_modules if 'MT2' in module]
        if len(list_of_2000_level_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take 2000 level modules (which will require permission)')

        list_of_planned_non_maths_modules = [module for module in student.planned_honours_modules if 'MT2' not in module 
                                                                                        and 'MT3' not in module 
                                                                                        and 'MT4' not in module 
                                                                                        and 'MT5' not in module
                                                                                        and 'ID5059' not in module]

        if len(list_of_planned_non_maths_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take non-MT modules, which requires permission and may affect credit balance')

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
        list_of_all_MT_modules = [module for module in student.all_honours_modules if 'MT3' in module 
                                                                                        or 'MT4' in module 
                                                                                        or 'MT5' in module
                                                                                        or 'ID4001' in module
                                                                                        or 'ID5059' in module]

        if len(list_of_all_MT_modules) <21:
            list_of_missed_requirements.append('Student is taking more than 2 modules as dip-down or dip-across, which is not allowed')

        # check that there are at least 120 credits (7 modules) at 5000 level
        list_of_5000_modules = [module for module in student.all_honours_modules if 'MT5' in module or 'ID5059' in module]
        if len(list_of_5000_modules) <7:
            list_of_missed_requirements.append('Student is not planning to take enough credits at 5000 level')

        list_of_2000_level_modules = [module for module in student.planned_honours_modules if 'MT2' in module]
        if len(list_of_2000_level_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take 2000 level modules (which will require permission)')

        list_of_planned_non_maths_modules = [module for module in student.planned_honours_modules if 'MT2' not in module 
                                                                                        and 'MT3' not in module 
                                                                                        and 'MT4' not in module 
                                                                                        and 'MT5' not in module
                                                                                        and 'ID5059' not in module]
        if len(list_of_planned_non_maths_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take non-MT modules, which requires permission and may affect credit balance')
            
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
                                                                                        and 'MT5' not in module
                                                                                        and 'ID5059' not in module]
        if len(list_of_planned_non_maths_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take non-MT modules, which requires permission and may affect credit balance')

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
                                'MT5865','MT5866', 'MT5867', 'MT5868', 'MT5869', 'MT5870', 'MT5876','MT5877', 'MT5590', 'MT5990']
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
        # list_of_all_non_honours_modules = [module for module in student.all_honours_modules if 'MT3' not in module 
        #                                                                                 and 'MT4' not in module 
        #                                                                                 and 'MT5' not in module
        #                                                                                 and 'ID5059' not in module]

        list_of_all_MT_modules = [module for module in student.all_honours_modules if 'MT3' in module 
                                                                                        or 'MT4' in module 
                                                                                        or 'MT5' in module
                                                                                        or 'ID5059' in module]

        if len(list_of_all_MT_modules) <21:
            list_of_missed_requirements.append('Student is taking more than 2 modules as dip-down or dip-across, which is not allowed')
            
        list_of_2000_level_modules = [module for module in student.planned_honours_modules if 'MT2' in module]
        if len(list_of_2000_level_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take 2000 level modules (which will require permission)')

        list_of_planned_non_maths_modules = [module for module in student.planned_honours_modules if 'MT2' not in module 
                                                                                        and 'MT3' not in module 
                                                                                        and 'MT4' not in module 
                                                                                        and 'MT5' not in module
                                                                                        and 'ID5059' not in module]
        if len(list_of_planned_non_maths_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take non-MT modules, which requires permission and may affect credit balance')
 
            
    ### MMATH STATISTICS REQUIREMENTS ###
    elif student.programme_name == 'Master in Mathematics (Honours) Statistics':
        # check the credit load
        missed_requirement, adviser_recommendation = check_for_120_credits_each_year(student)
        list_of_missed_requirements.append(missed_requirement)
        list_of_adviser_recommendations.append(adviser_recommendation)

        # Students need to take all fo these:
        list_of_essential_modules = ['MT3501', 'MT3507', 'MT3508', 'MT4113', 'MT4606', 'MT5761', 'MT5764'] 
        
        number_of_essential_modules = student.get_number_of_modules_in_list(list_of_essential_modules)
        if number_of_essential_modules < 7:
            list_of_missed_requirements.append('Student is only taking ' + str(number_of_essential_modules) + ' out of [MT3501, MT3507, MT3508, MT4113, MT4606, MT5761, MT5764]')
        
        list_one_of_selective_modules = ['MT4531', 'MT5731']
        number_of_selective_modules_one = student.get_number_of_modules_in_list(list_one_of_selective_modules)
        if number_of_selective_modules_one < 1:
            list_of_missed_requirements.append('Student is not taking a module out of [MT4531, MT5731]')
            
        list_of_stats_modules = ['MT4527', 'MT4528', 'MT4530', 'MT4537', 'MT4539', 'MT4607', 'MT4608', 'MT4609', 'MT4614']
        number_of_stats_modules = student.get_number_of_modules_in_list(list_of_stats_modules)
        if number_of_stats_modules < 2:
            list_of_missed_requirements.append('Student is only taking ' + str(number_of_stats_modules) + ' instead of 2 out of [MT4527, MT4528, MT4530, MT4537, MT4539, MT4607, MT4608, MT4609, MT4614]')

        list_of_5000_level_stats_modules = ['MT5751', 'MT5758', 'MT5761', 'MT5762', 'MT5763', 'MT5764', 'MT5765', 'MT5766', 'MT5767', 'ID5059']
        number_of_5000_level_stats_modules = student.get_number_of_modules_in_list(list_of_5000_level_stats_modules)
        if number_of_5000_level_stats_modules < 2:
            list_of_missed_requirements.append('Student is only taking ' + str(number_of_stats_modules) + ' instead of 2 out MT5751-MT5799, ID5059')
      
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
        list_of_5000_modules = [module for module in student.all_honours_modules if 'MT5' in module or 'ID5059' in module]
        if len(list_of_5000_modules) <7:
            list_of_missed_requirements.append('Student is not planning to take enough credits at 5000 level')

        list_of_2000_level_modules = [module for module in student.planned_honours_modules if 'MT2' in module]
        if len(list_of_2000_level_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take 2000 level modules (which will require permission)')

        list_of_planned_non_maths_modules = [module for module in student.planned_honours_modules if 'MT2' not in module 
                                                                                        and 'MT3' not in module 
                                                                                        and 'MT4' not in module 
                                                                                        and 'MT5' not in module
                                                                                        and 'ID5059' not in module]
        if len(list_of_planned_non_maths_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take non-MT modules, which requires permission and may affect credit balance')

    ### MA STATISTICS REQUIREMENTS ###
    elif ( student.programme_name  == 'Bachelor of Science (Honours) Statistics' or 
           student.programme_name == 'Master of Arts (Honours) Statistics') :
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
                                                                                        and 'MT5' not in module
                                                                                        and 'ID5059' not in module]
        if len(list_of_planned_non_maths_modules) >0:
            list_of_adviser_recommendations.append('Student is planning to take non-MT modules, which requires permission and may affect credit balance')
 

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
                

        if 'Credits' in student.passed_module_table and not student.honours_module_choices['Credits'].isnull().any():
            if get_total_honours_credits(student)<360:
                list_of_missed_requirements.append('Student is not taking a total of 360 credits across honours.')
            if get_total_credits_at_level(student,5)<120:
                list_of_missed_requirements.append('Student is not taking a total of 120 credits at 5000 level.')
        else:
            list_of_adviser_recommendations.append('This is a joint honours programme and the adviser needs to manually check that the student \
takes a total of 120 credits per year')

    ### BSC MATH AND PHYSICS REQUIREMENTS
    elif student.programme_name == 'Bachelor of Science (Honours) Mathematics and Physics':
        # This next code is different from other requirements because the conditions on year 3 are different for this particular
        # programme
        full_module_table = pd.concat([student.passed_module_table, student.honours_module_choices], ignore_index=True)
        reduced_module_table = full_module_table[(full_module_table['Honours year'] == 'Year 1')]
        year_three_modules = reduced_module_table['Module code'].to_list()
        
        relevant_subhonours_modules = student.passed_module_table['Module code'].to_list()
        # Check the analysis part of the requirements
        student_took_MT2507_and_MT2506 = 'MT2507' in relevant_subhonours_modules and 'MT2506' in relevant_subhonours_modules
        student_took_MT2502_and_MT2505 = 'MT2502' in relevant_subhonours_modules and 'MT2505' in relevant_subhonours_modules
        if student.current_honours_year==1:
            student_takes_3504 = 'MT3504' in year_three_modules or 'MT3504' in student.passed_modules
            student_takes_3502_and_3505 = ('MT3502' in year_three_modules or 'MT3502' in student.passed_modules) and ('MT3505' in year_three_modules or 'MT3505' in student.passed_modules)
        else:
            student_takes_3504 = 'MT3504' in student.planned_honours_modules or 'MT3504' in student.passed_modules
            student_takes_3502_and_3505 = (('MT3502' in student.planned_honours_modules or 'MT3502' in student.passed_modules) and 
                                          ('MT3505' in student.planned_honours_modules or 'MT3505' in student.passed_modules))

        if student_took_MT2507_and_MT2506 and student_took_MT2502_and_MT2505:
            if not student_takes_3504 and not student_takes_3502_and_3505:
                list_of_missed_requirements.append('Student is not taking MT3504 or (MT3502 and MT3505) (which is required for them)')
        elif student_took_MT2507_and_MT2506:
            if not student_takes_3504:
                list_of_missed_requirements.append('Student is not taking MT3504 in year 3 (which is required for them)')
        elif student_took_MT2502_and_MT2505:
            if not student_takes_3502_and_3505:
                list_of_missed_requirements.append('Student is not taking MT3505 and MT3502 in year 3 (which is a requirement for them)')
        else:
            list_of_missed_requirements.append('Student does not seem to have an allowed selection of subhonours MT modules')
 
        # check that there are at least 90 credits of MT modules across both honours years
        list_of_all_MT_modules = [module for module in student.all_honours_modules if 'MT3' in module 
                                                                                   or 'MT4' in module
                                                                                   or 'ID4001' in module]
        if len(list_of_all_MT_modules) < 6:
            list_of_missed_requirements.append('Student planning less than 90 credits (6 modules) in MT modules')

        # check there is a final year project
        list_of_project_codes = ['MT4796', 'MT4599', 'PH4111']
        number_final_year_projects= student.get_number_of_modules_in_list(list_of_project_codes)
        if number_final_year_projects !=1:
            list_of_missed_requirements.append('Student is not taking an allowed final year project')
        else:
            # check that the student is actually taking it in year 4
            if 'MT4796' in student.full_module_list:
                this_year = student.honours_module_choices[student.honours_module_choices['Module code'] == 'MT4796']['Honours year'].iloc[0]
            elif 'MT4599' in student.full_module_list:
                this_year = student.honours_module_choices[student.honours_module_choices['Module code'] == 'MT4599']['Honours year'].iloc[0]
            else:
                this_year = student.honours_module_choices[student.honours_module_choices['Module code'] == 'PH4111']['Honours year'].iloc[0]
            if this_year != 'Year 2':
                list_of_missed_requirements.append('Student is not taking their final year project in their final year.')
 

        if 'Credits' in student.passed_module_table and not student.honours_module_choices['Credits'].isnull().any():
            if get_total_honours_credits(student)<240:
                list_of_missed_requirements.append('Student is not taking a total of 240 credits across honours.')
            if (get_total_credits_at_level(student,4) + get_total_credits_at_level(student,5) ) <90:
                list_of_missed_requirements.append('Student is not taking a total of 90 credits at 4000 level.')
        else:
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
        relevant_subhonours_modules = student.passed_module_table['Module code'].to_list()
        
        third_reduced_module_table = full_module_table[full_module_table['Honours year'] == 'Year 2']
        year_four_modules = third_reduced_module_table['Module code'].to_list()

        # Check the analysis part of the requirements
        student_took_MT2507_and_MT2506 = 'MT2507' in relevant_subhonours_modules and 'MT2506' in relevant_subhonours_modules
        student_took_MT2502_and_MT2505 = 'MT2502' in relevant_subhonours_modules and 'MT2505' in relevant_subhonours_modules
        if student.current_honours_year==1:
            student_takes_3504 = 'MT3504' in year_three_modules or 'MT3504' in student.passed_modules
            student_takes_3502_and_3505 = ('MT3502' in year_three_modules or 'MT3502' in student.passed_modules) and ('MT3505' in year_three_modules or 'MT3505' in student.passed_modules)
        else:
            student_takes_3504 = 'MT3504' in student.planned_honours_modules or 'MT3504' in student.passed_modules
            student_takes_3502_and_3505 = (('MT3502' in student.planned_honours_modules or 'MT3502' in student.passed_modules) and 
                                          ('MT3505' in student.planned_honours_modules or 'MT3505' in student.passed_modules))

        if student_took_MT2507_and_MT2506 and student_took_MT2502_and_MT2505:
            if not student_takes_3504 and not student_takes_3502_and_3505:
                list_of_missed_requirements.append('Student is not taking MT3504 or (MT3502 and MT3505) (which is required for them)')
        elif student_took_MT2507_and_MT2506:
            if not student_takes_3504:
                list_of_missed_requirements.append('Student is not taking MT3504 in year 3 (which is required for them)')
        elif student_took_MT2502_and_MT2505:
            if not student_takes_3502_and_3505:
                list_of_missed_requirements.append('Student is not taking MT3505 and MT3502 in year 3 (which is a requirement for them)')
        else:
            list_of_missed_requirements.append('Student does not seem to have an allowed selection of subhonours MT modules')
                
        # Check the linear mathematics part of the requirements:
        if 'MT3501' not in year_three_modules and 'MT3501' not in student.passed_modules:
            list_of_missed_requirements.append('Student is not taking MT3501 in year 3, which is a requirement')
        
        # check fourth year requirement
        list_of_required_fourth_year_modules = ['MT3503', 'PH4028']
        number_of_required_fourth_year_modules = len(set.intersection(set(year_four_modules),set(list_of_required_fourth_year_modules)))
        if number_of_required_fourth_year_modules == 0:
            list_of_missed_requirements.append('Student is not taking one of [MT3503, PH4028] in year 4')
            
        # check that there are at least 135 credits of MT modules (9 modules) across all honours years
        list_of_all_MT_modules = [module for module in student.all_honours_modules if 'MT2' in module 
                                                                                   or 'MT3' in module 
                                                                                   or 'MT4' in module
                                                                                   or 'MT5' in module
                                                                                   or 'ID5059' in module]

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

        if 'Credits' in student.passed_module_table and not student.honours_module_choices['Credits'].isnull().any():
            if get_total_honours_credits(student)<360:
                list_of_missed_requirements.append('Student is not taking a total of 360 credits across honours.')
            if get_total_credits_at_level(student,5)<120:
                list_of_missed_requirements.append('Student is not taking a total of 120 credits at 5000 level.')
        else:
            list_of_adviser_recommendations.append('This is a joint honours programme and the adviser needs to manually check that the student \
takes a total of 120 credits per year and that the student takes at least 120 credits at 5000 level')

    ## Joint honours programms with statistics
    elif ( student.programme_name == 'Bachelor of Science (Honours) Computer Science and Statistics' or
           student.programme_name == 'Bachelor of Science (Honours) Psychology and Statistics' or 
           student.programme_name == 'Bachelor of Science (Honours) Economics and Statistics' or 
           student.programme_name == 'Master of Arts (Honours) Economics and Statistics' or 
           student.programme_name == 'Bachelor of Science (Honours) Management Science and Statistics'):

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
        if student.programme_name in joint_project_dictionary.keys():
            list_of_project_codes = joint_project_dictionary[student.programme_name]
        else:
            list_of_project_codes = []
        list_of_project_codes += ['MT4794', 'MT4796','MT4599']

        number_final_year_projects= student.get_number_of_modules_in_list(list_of_project_codes)
        if number_final_year_projects !=1:
            list_of_missed_requirements.append('Student is not taking an allowed final year project')
        else:
            (final_year_module_code,) = set.intersection(set(student.full_module_list),set(list_of_project_codes))
            # check that the student is actually taking it in year 4
            this_year = student.honours_module_choices[student.honours_module_choices['Module code'] == final_year_module_code]['Honours year'].iloc[0]
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
                                                                                        or 'VP' in module
                                                                                        or 'CS4796' in module]

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
    
        if 'Credits' in student.passed_module_table and not student.honours_module_choices['Credits'].isnull().any():
            if get_total_honours_credits(student)<240:
                list_of_missed_requirements.append('Student is not taking a total of 240 credits across honours.')
            if ( get_total_credits_at_level(student,4) + get_total_credits_at_level(student,5) )<90:
                list_of_missed_requirements.append('Student is not taking a total of 90 credits at 4000 level.')
        else:
            list_of_adviser_recommendations.append('This is a joint honours programme and the adviser needs to manually check that the student \
takes a total of 120 credits per year and that they take at least 90 credits at 4000 level')

    ### JOINT HONOURS REQUIREMENTS ###
    elif student.programme_name in ['Bachelor of Science (Honours) Computer Science and Mathematics',
                                    'Master of Arts (Honours) Mathematics and Philosophy',
                                    'Bachelor of Science (Honours) Chemistry and Mathematics',
                                    'Bachelor of Science (Honours) Mathematics and Psychology (BPS Recognition Route)',
                                    'Bachelor of Science (Honours) Mathematics and Psychology',
                                    'Master of Arts (Honours) Mathematics and Psychology',
                                    'Master of Arts (Honours) English and Mathematics',
                                    'Bachelor of Science (Honours) Mathematics and Philosophy',
                                    'Master of Arts (Honours) Mathematics and Russian',
                                    'Bachelor of Science (Honours) Economics and Mathematics',
                                    'Bachelor of Science (Honours) Geography and Mathematics',
                                    'Bachelor of Science (Honours) Financial Economics and Mathematics',
                                    'Master of Arts (Honours) Financial Economics and Mathematics',
                                    'Master of Arts (Honours) Art History and Mathematics',
                                    'Master of Arts (Honours) Mathematics and Medieval History',
                                    'Bachelor of Science (Honours) Biology and Mathematics',
                                    'Master of Arts (Honours) International Relations and Mathematics',
                                    'Master of Arts (Honours) Economics and Mathematics',
                                    'Master of Arts (Honours) Arabic and Mathematics',
                                    'Master of Arts (Honours) Mathematics and Modern History',
                                    'Bachelor of Science (Honours) Management Science and Mathematics']:
        
        missed_requirement, adviser_recommendation = check_joint_honours_requirements(student)
        list_of_missed_requirements.append(missed_requirement)
        list_of_adviser_recommendations.append(adviser_recommendation)
        
    else:
        list_of_missed_requirements.append('No programme requirements available')

    # merge all missed requirements into a string
    missed_requirements = merge_list_to_long_string(list_of_missed_requirements)
    adviser_recommendations = merge_list_to_long_string(list_of_adviser_recommendations)

    return missed_requirements, adviser_recommendations
    
def get_total_honours_credits(student):
    """Calculate and return the total credits the student took at honours
    
    Parameters :
    ------------
    
    student : Student object
        the student we want to investigate
    
    Returns :
    ---------
    
    total_credits : int
        total number of credtis the student took at honours
    """
    passed_honours_module_table = student.passed_module_table[student.passed_module_table['Honours year'].isin(['Year 1',
                                                                                                                'Year 2',
                                                                                                                'Year 3',
                                                                                                                'Year 4',
                                                                                                                'Year 5',
                                                                                                                'Year 6'])]
    passed_honours_credits = passed_honours_module_table['Credits'].sum()
    planned_honours_credits = student.honours_module_choices['Credits'].sum()
    total_credits = passed_honours_credits + planned_honours_credits

    return total_credits

def get_total_credits_at_level(student, level):
    """Calculate and return the total credits the student took at honours
    
    Parameters :
    ------------
    
    student : Student object
        the student we want to investigate
    
    level : int
        the level we want to sum up. Needs to be 1, 2, 3, 4, or 5.
    
    Returns :
    ---------
    
    total_credits : int
        total number of credits the student took at this level
    """
    passed_modules_at_level = student.passed_module_table[student.passed_module_table['Module code'].str[2] == str(level)]
    passed_credits_at_level = passed_modules_at_level['Credits'].sum()

    planned_modules_at_level = student.honours_module_choices[student.honours_module_choices['Module code'].str[2] == str(level)]
    planned_credits_at_level = planned_modules_at_level['Credits'].sum()
    total_credits = passed_credits_at_level + planned_credits_at_level
    
    return total_credits

def check_joint_honours_requirements(student):
    """Check whether a student meets the requirements for a joint honours programme, 
    such as the Bachelor of Science (Honours) Chemistry and Mathematics or the
    Master of Arts (Honours) Mathematics and Philosophy. These requirements can be used as a
    reference for these conditions.

    Parameters :
    ------------

    student : instance of Student() class
        the student for which we are checking the requirements.
    
    approved_honours_projects : list of strings
        list of project codes for approved honours projects

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
    if student.programme_name in joint_project_dictionary.keys():
        list_of_project_codes = joint_project_dictionary[student.programme_name]
    else:
        list_of_project_codes = []
    list_of_project_codes += ['MT4794', 'MT4796','MT4599']
    number_final_year_projects= student.get_number_of_modules_in_list(list_of_project_codes)
    if number_final_year_projects ==0:
        list_of_missed_requirements.append('Student is not taking an allowed final year project')
        final_year_module_code = '000000'
    elif number_final_year_projects >1:
        list_of_missed_requirements.append('Student is taking too many final year projects')
    else:
        (final_year_module_code,) = set.intersection(set(student.full_module_list),set(list_of_project_codes))
        # check that the student is actually taking it in year 4
        this_year = student.honours_module_choices[student.honours_module_choices['Module code'] == final_year_module_code]['Honours year'].iloc[0]
        if this_year != 'Year 2':
            list_of_missed_requirements.append('Student is not taking their final year project in their final year')
        if final_year_module_code != 'MT4599':
            list_of_adviser_recommendations.append('Student has chosen the joint honours project ' + final_year_module_code + ' which requires a letter of agreement')
    
    # check that the student is taking at least 120 credits (8 modules) in MT modules (60 modules any code + 15 modules final year project + 45 credits of MT3501-MT3508)
    # while also checking that there are not too many dip-down ID/VP modules
    list_of_all_MT_modules = [module for module in student.all_honours_modules if 'MT3' in module 
                                                                                  or 'MT4' in module]

    list_of_all_allowed_modules = [module for module in student.all_honours_modules if 'MT2' in module 
                                                                                    or 'MT3' in module 
                                                                                    or 'MT4' in module
                                                                                    or 'ID4001' in module
                                                                                    or 'VP' in module
                                                                                    or final_year_module_code in module]

    if len(list_of_all_allowed_modules) <8 or len(list_of_all_MT_modules) < 7:
        if len(list_of_all_MT_modules) < 7 and len(list_of_all_allowed_modules) > 7:
            list_of_missed_requirements.append('Student is taking too many modules as dip-down or in ID/VP moduels (which is not allowed)')
        else:
            list_of_missed_requirements.append('Student is not taking enough credits (less than 8 modules) among MT modules')
            
    # check 5000 level modules
    list_of_5000_level_modules =  [module for module in student.all_honours_modules if 'MT5' in module or 'ID5059' in module]

    if len(list_of_5000_level_modules) > 0:
        list_of_missed_requirements.append('Student is planning to take 5000 level modules (which is not allowed for joint honours students)')

    # check planned dip-down
    list_of_planned_2000_level_modules = [module for module in student.planned_honours_modules if 'MT2' in module
                                                                                                or 'ID4001' in module
                                                                                                or 'VP' in module]
    if len(list_of_planned_2000_level_modules) >0:
        list_of_adviser_recommendations.append('Student is planning to take 2000 level modules or ID4001 or VP modules (which all require permission)')

    if 'Credits' in student.passed_module_table and not student.honours_module_choices['Credits'].isnull().any():
            if get_total_honours_credits(student)<240:
                list_of_missed_requirements.append('Student is not taking a total of 240 credits across honours.')
            if ( get_total_credits_at_level(student,4) + get_total_credits_at_level(student,5) )<90:
                list_of_missed_requirements.append('Student is not taking a total of 90 credits at 4000 level.')
    else:
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
    
    current_honours_year_string = 'Year ' + str(student.current_honours_year)
    
    #checking total number of modules
    for honours_year in honours_years:
        this_planned_data_base = student.honours_module_choices[student.honours_module_choices['Honours year'] == honours_year]
        this_passed_data_base = student.passed_module_table[student.passed_module_table['Honours year'] == honours_year]
        this_data_base = pd.concat([this_planned_data_base, this_passed_data_base], ignore_index=True) 

        if honours_year == 'Year 1' or honours_year == 'Year 2':
            if len(this_data_base)<8:
                if 'Credits' in this_data_base.columns:
                    if this_data_base['Credits'].sum()<120:
                        definitely_undercrediting = True
                    else:
                        definitely_undercrediting = False
                else:
                    definitely_undercrediting = True
                if definitely_undercrediting:
                    list_of_missed_requirements.append('Not collecting 120 credits in ' + honours_year)
            elif len(this_data_base) > 8 and honours_year ==current_honours_year_string :
                list_of_adviser_recommendations.append('Student is planning to overcredit, which requires permission')
        if honours_year == 'Year 3':
            if len(this_data_base)<7:
                if 'Credits' in this_data_base.columns:
                    if this_data_base['Credits'].sum()<120:
                        definitely_undercrediting = True
                    else:
                        definitely_undercrediting = False
                else:
                    definitely_undercrediting = True
                if definitely_undercrediting:
                    list_of_missed_requirements.append('Not collecting 120 credits in ' + honours_year)
            if ( len(this_data_base)>7 and honours_year == current_honours_year_string ):
                list_of_adviser_recommendations.append('Student is planning to overcredit, which requires permission')
    
    #checking moduel splits
    for honours_year in honours_years:
        this_planned_data_base = student.honours_module_choices[student.honours_module_choices['Honours year'] == honours_year]
        this_passed_data_base = student.passed_module_table[student.passed_module_table['Honours year'] == honours_year]
        this_data_base = pd.concat([this_planned_data_base, this_passed_data_base], ignore_index=True) 
        if honours_year == 'Year 1' or (honours_year == 'Year 2' and student.expected_honours_years == 3):
            for semester in ['S1', 'S2']:
                this_smaller_data_base = this_data_base[this_data_base['Semester'] == semester]
                if len(this_smaller_data_base) !=4:
                    list_of_adviser_recommendations.append('Not taking even credit split in ' + honours_year)
        elif honours_year == 'Year 2':
            this_reduced_data_base = this_data_base[this_data_base['Module code'] != 'MT4599']
            semester_1_modules = this_reduced_data_base[this_reduced_data_base['Semester'] == 'S1']['Module code']
            semester_2_modules = this_reduced_data_base[this_reduced_data_base['Semester'] == 'S2']['Module code']
            if len(semester_1_modules) != 4 or len(semester_2_modules) != 3:
                list_of_adviser_recommendations.append('Student is taking a high course load in second semester of final honours year so should ensure the majority of their project is completed before the start of S2')
        elif honours_year == 'Year 3':
            this_reduced_data_base = this_data_base[this_data_base['Module code'] != 'MT5599']
            semester_1_modules = this_reduced_data_base[this_reduced_data_base['Semester'] == 'S1']['Module code']
            semester_2_modules = this_reduced_data_base[this_reduced_data_base['Semester'] == 'S2']['Module code']
            if not ((len(semester_1_modules) == 3 and len(semester_2_modules) == 3) or (len(semester_1_modules) == 4 and len(semester_2_modules) == 2)):
                list_of_adviser_recommendations.append('Student is taking a high course load second semester of final honours year (which may make project completion difficult)')
    
    missed_requirement = merge_list_to_long_string(list_of_missed_requirements)
    adviser_recommendation = merge_list_to_long_string(list_of_adviser_recommendations)
    
    return missed_requirement, adviser_recommendation

