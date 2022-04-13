### MAIN PROGRAM ###

##################
# --- HEADER --- #
##################
__author__ = 'Mike Halbheer'
__version__ = '0.0.1'
__status__ = 'Development'


###################
# --- IMPORTS --- #
###################

import os
import pandas as pd
import numpy as np
from lxml import etree
import json


################
# --- CODE --- #
################

def main():

    # Load the config file
    config_file = open('config.json')
    config = json.load(config_file)
    
    # Load all files that need to be parsed
    parse_files = get_parse_files(config['input_path'])

    # Load all line codes from the Geoterra art code list
    line_codes = get_line_codes(config['line_code_path'])

    # Iterate over all files
    for file in parse_files:
        
        # Load the JXL file as an Element Tree
        sx_job = etree.parse(file)
        JOBFile = sx_job.getroot() # Get the file root
        FieldBook = JOBFile.find('FieldBook') # Get the FieldBook object
        Reductions = JOBFile.find('Reductions') # Get the Reductions object

        # List of point records
        point_records = []

        # Find all point records in the FieldBook
        for index, record in enumerate(FieldBook):
            if record.tag == 'PointRecord':
                code_raw = record.find('Code').text
                # If the point has no code it is ignored
                if code_raw is None:
                    point_records.append([index, None, None])
                    continue
                # Split the code into the actual code and the line start indicator
                # Save the index in the FieldBook element children listfor later access
                code_split = code_raw.split(' ')
                point_records.append([index, code_split[0], 1 if len(code_split) > 1 else None])

        # Cast to numpy array for faster operations
        point_records = np.array(point_records)

        # List of reduction records
        reduction_records = []

        # Split all Reduction records in the actual code and the line start indicator
        # Save the index in the Reductions element children list for later access
        for index, record in enumerate(Reductions):
            code_raw = record.find('Code').text
            # If a point has no code it is ignored
            if code_raw is None:
                reduction_records.append([index, None, None])
                continue
            code_split = code_raw.split(' ')
            reduction_records.append([index, code_split[0], 1 if len(code_split) > 1 else None])

        # Cast to numpy array for faster operations
        reduction_records = np.array(reduction_records)

        # Execute for every line code
        for line_code in line_codes:
            
            # Find all point records that belong to the given code
            point_records_code = point_records[point_records[:, 1] == line_code]
            # Fing all reduction records that belong to the given record
            reduction_records_code = reduction_records[reduction_records[:, 1] == line_code]
            
            # If no points for the code were found continue with next code
            if point_records_code.size == 0:
                continue
                
            # Get the indices of the line starts in the FieldBook element
            line_starts_pr = np.array(point_records_code[point_records_code[:, 2] == 1, 0])
            
            # Get the indices of the line ends in the point record array
            line_end_idx_pr = np.transpose((point_records_code[:, 2] == 1).nonzero()) - 1
            line_end_idx_pr = np.append(line_end_idx_pr, -1)
            
            # Get the indices of the line ends in the FieldBook element
            line_ends_pr = point_records_code[line_end_idx_pr[1:], 0]

            # Get the indices of the line start in the Reductions element 
            line_starts_rr = np.array(reduction_records_code[reduction_records_code[:, 2] == 1, 0])
            
            # Get the indices of the line ends in the reduction record array
            line_end_idx_rr = np.transpose((reduction_records_code[:, 2] == 1).nonzero()) - 1
            line_end_idx_rr = np.append(line_end_idx_rr, -1)
            
            # Get the indices of the line ends in the Reductions element
            line_ends_rr = reduction_records_code[line_end_idx_rr[1:], 0]

            # For all line starts in the point records remove the trailing line start indicator (' S')
            for line_start in line_starts_pr:
                old_code = FieldBook[line_start].find('Code').text
                new_code = old_code[:-2] # Remove the indicator

                FieldBook[line_start].find('Code').text = new_code

            # For all line ends in the point records insert the negative indicator
            for line_end in line_ends_pr:
                old_code = FieldBook[line_end].find('Code').text
                new_code = '-' + old_code

                FieldBook[line_end].find('Code').text = new_code

            # For all line starts in the reductions records remove the trailing line start indicator (' S')
            for line_start in line_starts_rr:
                old_code = Reductions[line_start].find('Code').text
                new_code = old_code[:-2]

                Reductions[line_start].find('Code').text = new_code
            
            # For all line ends in the reduction records insert the negative indicator
            for line_end in line_ends_rr:
                old_code = Reductions[line_end].find('Code').text
                new_code = '-' + old_code

                Reductions[line_end].find('Code').text = new_code

        # Create a new ElementTree object for output
        parsed_jxl = etree.ElementTree(sx_job.getroot())

        # Create the output file name to be identical to the input one
        filename = os.path.basename(file)
        output_path = os.path.join(config['output_path'], filename)
        
        # Write the resulting ElementTree to a new Trimble JobXML file
        parsed_jxl.write(output_path, pretty_print=True)

        # Archive parsed file
        archived = False
        counter = 0
        while not archived:
            # Resolve name collision by appending a running count to the filename
            try:
                archive_file = f'{filename[:-4]} ({counter:03}).jxl' if counter > 0 else f'{filename}'
                os.rename(file, os.path.join(config['archive_path'], archive_file))
                archived = True
            except FileExistsError:
                counter += 1
        

def get_parse_files(dir_input: str) -> list:
    '''
    Gets all files to be parsed from the data folder

    Parameters
    ----------
    dir_input : String
        The path of the input directory

    Returns
    -------
    parse_files : List of strings
        List of files that should be parsed
    '''
    
    # Catchment list of all files to be parsed
    parse_files = []
    
    # Find all files in the direcotry
    for file in os.listdir(dir_input):
        # Ignore any non JobXML file
        if file.endswith('.jxl'):
            # Get full file path
            file_path = os.path.join(dir_input, file)
            parse_files.append(file_path)

    return parse_files

def get_line_codes(dir_line_codes: str) -> list:
    '''
    Gets all line codes from the current code list

    Parameters
    ----------
    dir_line_codes : String
        The directory of the Geoterra code list CSV file

    Returns
    -------
    line_codes : List of ints
        List containing all line codes in the Geoterra Code list
    '''

    # Read the 'Geoterra_Vorlage.csv'
    code_list = pd.read_csv(dir_line_codes, sep=';', header=0, usecols=['Objektart', 'Messcode'], encoding='unicode_escape')

    # Filter for line elements
    line_codes = code_list.Messcode[code_list.Objektart == 'PL'].to_numpy()

    return line_codes


if __name__ == '__main__':
    main()
