from src.advising import *
import argparse
import os

# os.system('color')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='AdvisingScript',
                    description='This script helps with honours advising in the School of Mathematics and Statistics at the University of St Andrews.',
                    epilog='All results are experimental and will need to be double-checked. \n\n')
    
    parser.add_argument('file_or_folder', type = str, nargs='?', help = 'name of the file or folder to be processed, or a student ID')       
    parser.add_argument('-o', '--output', type = str, default = 'summary_file.xlsx', help = 'name of the output excel file')       
    parser.add_argument('--check-final-years', action="store_true", help = 'use this option to check all final year students using the database only')
    parser.add_argument('-p', '--programme_name', type = str, help = 'use this option to provide an alternative programme name. Will be ignored if more than one student is checked.')

    args = parser.parse_args()

    file_or_folder = args.file_or_folder
    saving_name = args.output
    programme_name = args.programme_name
    
    if args.check_final_years:
        summary_data_frame = check_final_year_students()
    elif os.path.isdir(file_or_folder):
        summary_data_frame = process_folder(file_or_folder)
    elif os.path.isfile(file_or_folder):
        summary_data_frame = process_form_file_or_student_id(file_or_folder, programme_name)
    elif file_or_folder.isdigit():
        summary_data_frame = process_form_file_or_student_id(int(file_or_folder), programme_name)
    else:
        raise(ValueError('argument is neither a file or a folder. Does it exist?'))

    save_summary_data_frame(summary_data_frame, saving_name)
