class Student():
    def __init__(self, 
                 student_id, 
                 full_name,
                 email,
                 programme_name,
                 year_of_study,
                 expected_honours_years,
                 current_honours_year,
                 passed_modules,
                 passed_module_table,
                 passed_honours_modules,
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
        
        passed_moudle_table : pandas data frame
            a pandas data frame that has the same column names as honours_module_choices
            
        passed_honours_modules : list of strings
            A list of all honours modules that the student has already taken and passed
            
        honours_module_choices : Pandas data frame
            The honours module codes that the studen thas selected. The data frame current contains
            the following columns ['Honours year', 'Academic year', 'Semester', 'Module code']
        """
        
        self.student_id = student_id
        self.full_name = full_name
        self.email = email
        self.programme_name = programme_name
        self.year_of_study = year_of_study
        self.expected_honours_years = expected_honours_years
        self.current_honours_year = current_honours_year
        self.passed_modules = passed_modules
        self.passed_module_table = passed_module_table
        self.passed_honours_modules = passed_honours_modules
        self.honours_module_choices = honours_module_choices

        # for convenience also make a list of all selected and taken modules
        self.full_module_list = self.passed_modules.copy()
        self.full_module_list += self.honours_module_choices['Module code'].to_list()
        
        # and a list of all selected and taken honours modules
        self.all_honours_modules = self.passed_honours_modules
        self.all_honours_modules += self.honours_module_choices['Module code'].tolist()
        
        # and a list of planned honours modules
        self.planned_honours_modules = self.honours_module_choices['Module code'].tolist()

    def get_number_of_modules_in_list(self, module_list):
        """Get the number of modules that the student is taking in the module list. Already passed modules and scheduled
        modules are both counted.
        
        Parameters:
        -----------
        
        module_list : list of strings
            list of module codes
            
        Returns: 
        --------
        
        number_of_modules : int
            the number of modules in the given list that the student is taking.
        """
        number_of_modules = len(set.intersection(set(self.full_module_list),set(module_list)))
        
        return number_of_modules
 