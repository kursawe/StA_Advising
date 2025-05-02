from .infrastructure import *

def find_timetable_clashes(student):
    """Find all modules that the student is planning to take and which are not actually running in the year and semester
    they are claiming.
    
    Parameters:
    -----------
    
    student : instance of Student class
        the student we are investigating
        
    Returns:
    --------
    
    timetable_clashes : string
        comments on all scheduled timetable clashes.
        
    adviser_recommendations : string
        advising recommendations, in this case may include warnings where scheduling is not finalised, or when we couldn't parse all scheduled events.
    """
    # make a list of timetable clashes
    timetable_clashes_list = []
    adviser_recommendations_list = []
    
    # get remaining honours years
    remaining_honours_years = student.honours_module_choices['Honours year'].unique()
    for honours_year in remaining_honours_years:
        for semester in ['S1', 'S2']:
            semester_modules = student.honours_module_choices[(student.honours_module_choices['Semester'] == semester) &  
                                                               (student.honours_module_choices['Honours year'] == honours_year)]['Module code'].to_list()
            timeslot_dictionary = dict()
            for module in semester_modules:
                these_timeslots = get_timeslots_for_module(module, semester)
                timeslot_dictionary[module] = these_timeslots
            
            timetable_clashes_list += find_clashing_timeslots_and_modules(timeslot_dictionary, honours_year, semester)
            reduced_timeslot_dictionary = timeslot_dictionary.copy()
            for _,value in reduced_timeslot_dictionary.items():
                for entry in value:
                    entry.replace(' (even weeks)','')
            timetable_clashes_list += find_clashing_timeslots_and_modules(timeslot_dictionary, honours_year, semester)

            reduced_timeslot_dictionary = timeslot_dictionary.copy()
            for _,value in reduced_timeslot_dictionary.items():
                for entry in value:
                    entry.replace(' (odd weeks)','')
            timetable_clashes_list += find_clashing_timeslots_and_modules(timeslot_dictionary, honours_year, semester)

    # remove duplicate items
    timetable_clashes_list = list(set(timetable_clashes_list))
    # merge all found problems into a string
    timetable_clashes = merge_list_to_long_string(timetable_clashes_list)
    adviser_recommendations = merge_list_to_long_string(adviser_recommendations_list)
    
    return timetable_clashes, adviser_recommendations
 
def find_clashing_timeslots_and_modules(module_dictionary, honours_year, semester):
    """Given timeslot and a dictionary of concurrently running modules return the timeslots that are clashing and the clashing module codes
    
    Parameters:
    -----------
    
    module_dictionary : dictionary
        keys are module codes, values are lists of strings, which represent timeslots
    
    honours_year : string
        the honours year
        
    semester : string
        the semester
    
    Returns:
    --------

    timetable_clashes_list : list of strings
        warning messages about clashing modules
    """
    timetable_clashes_list = []
    all_timeslots = []
    for module, timeslots in module_dictionary.items():
        all_timeslots += timeslots

    my_timeslot_counter = collections.Counter(all_timeslots)
    duplicate_entries = [timeslot for timeslot, count in my_timeslot_counter.items() if count > 1]
    clashing_module_codes = []
    for timeslot in duplicate_entries:
        these_clashing_module_codes = []
        for module, timeslot_list in module_dictionary.items():
            if timeslot in timeslot_list:
                these_clashing_module_codes.append(module)
        these_clashing_module_codes.sort()
        these_clashing_module_codes = tuple(these_clashing_module_codes)
        clashing_module_codes.append(these_clashing_module_codes)
        
    unique_module_clashes = list(set(frozenset(entry) for entry in clashing_module_codes))
    for module_combination in unique_module_clashes:
        all_timeslot_sets = list()
        for module in module_combination:
            module_timeslots = set(module_dictionary[module])
            all_timeslot_sets.append(module_timeslots)
        affected_timeslots = set.intersection(*all_timeslot_sets)
        # sort the list so that we can avoid duplicate warning in the if statement below
        warning_string = 'Clash for ' + honours_year + ' ' + semester + ' between modules '
        for module_index, module in enumerate(module_combination):
            warning_string += module
            if module_index < len(module_combination) - 1:
                warning_string += ' and '
        warning_string += ' at ' 
        for timeslot_index, timeslot in enumerate(affected_timeslots):
            warning_string += timeslot
            if timeslot_index < len(affected_timeslots) - 1:
                warning_string += ' and '
        # if warning_string not in timetable_clashes_list:
        timetable_clashes_list.append(warning_string)
    
    return timetable_clashes_list
   
def get_timeslots_for_module(module, semester):
    """Returns all timeslots for a module
    
    Parameters:
    -----------
    
    module : string
        the module code we are interested in.
        
    semester : string
        needs to be one of 'S1' or 'S2'
        
    Returns:
    --------
    
    timeslots : list of strings
        all timeslots that the module is running in
    """
    if len(module_catalogue[module_catalogue['Module code'] == module]) == 0:
        # The module does not exist, we have already flagged this
        timeslot_entry = float('nan')
    else:
        timeslot_entries = module_catalogue[module_catalogue['Module code'] == module]['Timetable'].values
        if len(timeslot_entries) == 1:
            timeslot_entry = timeslot_entries[0]
        else:
            timeslot_entry = module_catalogue[(module_catalogue['Module code'] == module) & 
                                                              (module_catalogue['Semester'] == semester)]['Timetable'].values[0]

    timeslots = []
    
    # special treatment for MT4112 bewcause I can't be bothered to update the parsing below, it'd be a pain
    if timeslot_entry == '10am Wed (odd weeks), 10am Fri (odd weeks)':
        timeslots = ['10am Wed (odd weeks)', '10am Fri (odd weeks)']
        return timeslots

    if isinstance(timeslot_entry,str):
        timeslot_splits = timeslot_entry.split()
        first_timeslot = timeslot_splits[0]
        if len(timeslot_splits) > 2 and timeslot_splits[2].startswith('('):
            second_timeslot = first_timeslot + ' ' + timeslot_splits[4][:-1]
            third_timeslot = first_timeslot + ' ' + timeslot_splits[5]
            if third_timeslot.endswith(','):
                third_timeslot = third_timeslot[:-1]
            first_timeslot += ' ' + timeslot_splits[1] + ' ' + timeslot_splits[2] + ' ' + timeslot_splits[3][:-1]
            timeslots += [first_timeslot, second_timeslot, third_timeslot]
            if len(timeslot_splits) > 7:
                remaining_splits = timeslot_splits[6:]
            else:
                remaining_splits = []
        else:
            first_timeslot += ' ' + timeslot_splits[1]
            if first_timeslot.endswith(','):
                first_timeslot = first_timeslot[:-1]
            if len(timeslot_splits) > 2:
                remaining_splits = timeslot_splits[2:]
            else:
                remaining_splits = []
            timeslots.append(first_timeslot)
        
        current_index = 0
        while current_index < len(remaining_splits):
            this_timeslot = remaining_splits[current_index] + ' ' +  remaining_splits[current_index + 1]
            if this_timeslot.endswith(','):
                this_timeslot = this_timeslot[:-1]
            timeslots.append(this_timeslot)
            current_index +=2
        
    return timeslots

def find_not_running_modules(student):
    """Find all modules that the student is planning to take and which are not actually running in the year and semester
    they are claiming.
    
    Parameters:
    -----------
    
    student : instance of Student class
        the student we are investigating
        
    Returns:
    --------
    
    not_running_modules : string
        comments on all modules that won't be running as intended.
        
    adviser_recommendations : string
        advising recommendations, in this case may include warnings where scheduling is not finalised.
    """
    # make a list of not running modules
    not_running_modules_list = []
    adviser_recommendations_list = []
    
    for module in student.planned_honours_modules:
        if module.startswith('MT') and module not in module_catalogue['Module code'].values:
            not_running_modules_list.append('Student is planning to take ' + module + ' (which does not exist)')

    for _, row in student.honours_module_choices.iterrows():
        # get the module data
        planned_module_code = row['Module code']
        planned_academic_year = row['Academic year']
        planned_semester = row['Semester']
        if len(module_catalogue[module_catalogue['Module code'] == planned_module_code]) == 0:
            # the module does not exist, we have already flagged this so we are just going to
            # skip this here
            continue
        module_catalogue_entry = module_catalogue[module_catalogue['Module code'] == planned_module_code]
        # module_semester = module_catalogue_entry['Semester'].values[0]
        module_semesters = module_catalogue_entry['Semester']
        # tell if the student picked the wrong semester
        # if planned_semester != module_semester and module_semester != 'Full Year':
        if (planned_semester not in module_semesters.values) and ('Full Year' not in module_semesters.values):
            not_running_modules_list.append('Selected module ' + planned_module_code + ' for Semester ' +
                                            planned_semester + ' but it is actually running in ' + module_semesters.values[0])
        # figure out when the module is running
        module_academic_year = module_catalogue_entry['Year'].values[0]
        module_is_alternating_entry = module_catalogue_entry['Alternate years'].values[0]
        if module_is_alternating_entry == 'Yes':
            module_is_alternating = True
        elif module_is_alternating_entry == 'No':
            module_is_alternating = False
        else:
            raise(ValueError('cannot tell if module ' + planned_module_code + ' is alternating or not. Check the table entry.'))
        # figure out which years the module is running in
        list_of_running_academic_years = [module_academic_year]
        start_year = int(module_academic_year[:4])
        for repeat_index in range(20):
            if module_is_alternating:
                new_academic_year = str(start_year + 2*repeat_index) + '/' + str(start_year + 2*repeat_index + 1)
            else:
                new_academic_year = str(start_year + repeat_index) + '/' + str(start_year + repeat_index + 1)
            list_of_running_academic_years.append(new_academic_year)
        if planned_module_code == 'MT4614':
            list_of_running_academic_years = ['2024/2025']
        if planned_academic_year not in list_of_running_academic_years:
            not_running_modules_list.append('Selected module ' + planned_module_code + ' is not running in academic year ' +
                                            str(planned_academic_year))

    if 'MT45AB' in student.planned_honours_modules or 'MT45ML' in student.planned_honours_modules:
        adviser_recommendations_list.append('Student is planning to take MT45AB or MT45ML - these will be new modules and their timetabling and prerequisites may change')

    # merge all found problems into a string
    not_running_modules = merge_list_to_long_string(not_running_modules_list)
    adviser_recommendations = merge_list_to_long_string(adviser_recommendations_list)
    
    return not_running_modules, adviser_recommendations

