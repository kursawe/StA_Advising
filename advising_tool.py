from advising_code import *
import argparse
import os

# os.system('color')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='AdvisingScript',
                    description='This script helps with honours advising in the School of Mathematics and Statistics at the University of St Andrews.',
                    epilog='All results are experimental and will need to be double-checked. \n\n')
    
    parser.add_argument('file_or_folder', type = str, help = 'name of the file or folder to be processed')       
    parser.add_argument('-o', '--output', type = str, default = 'summary_file.xlsx', help = 'name of the output excel file')       
    args = parser.parse_args()

    file_or_folder = args.file_or_folder
    saving_name = args.output
    
    if os.path.isdir(file_or_folder):
        summary_data_frame = process_folder(file_or_folder)
    elif os.path.isfile(file_or_folder):
        summary_data_frame = process_form_file(file_or_folder)
    else:
        raise(ValueError('argument is neither a file or a folder. Does it exist?'))

    save_summary_data_frame(summary_data_frame, saving_name)
