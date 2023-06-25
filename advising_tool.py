from advising_code import *
import argparse
import os

# os.system('color')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='AdvisingScript',
                    description='This script helps with advising',
                    epilog='All results are experimental and not to be trusted. Double-check me. \n\n')
    
    parser.add_argument('file_or_folder', type = str, help = 'name of the file or folder to be processed')       
    args = parser.parse_args()

    file_or_folder = args.file_or_folder
    
    if os.path.isdir(file_or_folder):
        summary_data_frame = process_folder(file_or_folder)
    elif os.path.isfile(file_or_folder):
        summary_data_frame = process_form_file(file_or_folder)
    else:
        raise(ValueError('argument is neither a file or a folder. Does it exist?'))

    saving_name = 'summary_file.xlsx'
    save_summary_data_frame(summary_data_frame, saving_name)
