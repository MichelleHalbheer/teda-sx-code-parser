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

    config_file = open('config.json')
    config = json.load(config_file)
    
    parse_files = get_parse_files(config['input_path'])

    line_codes = get_line_codes(config['line_code_path'])

    for file in parse_files:
        sx_job = etree.parse(file) # Reads the XML
        JOBFile = sx_job.getroot()
        FieldBook = JOBFile.find('FieldBook')
        Reductions = JOBFile.find('Reductions')

        point_records = []

        for index, record in enumerate(FieldBook):
            if record.tag == 'PointRecord':
                code_raw = record.find('Code').text
                if code_raw is None:
                    point_records.append([index, None, None])
                    continue
                code_split = code_raw.split(' ')
                point_records.append([index, code_split[0], 1 if len(code_split) > 1 else None])

        point_records = np.array(point_records)

        reduction_records = []

        for index, record in enumerate(Reductions):
            code_raw = record.find('Code').text
            if code_raw is None:
                reduction_records.append([index, None, None])
                continue
            code_split = code_raw.split(' ')
            reduction_records.append([index, code_split[0], 1 if len(code_split) > 1 else None])

        reduction_records = np.array(reduction_records)

        for line_code in line_codes:
            point_records_code = point_records[point_records[:, 1] == line_code]
            reduction_records_code = reduction_records[reduction_records[:, 1] == line_code]
            if point_records_code.size == 0:
                continue
            line_starts_pr = np.array(point_records_code[point_records_code[:, 2] == 1, 0])
            
            line_end_idx_pr = np.transpose((point_records_code[:, 2] == 1).nonzero()) - 1
            line_end_idx_pr = np.append(line_end_idx_pr, -1)
            line_ends_pr = point_records_code[line_end_idx_pr[1:], 0]

            line_starts_rr = np.array(reduction_records_code[reduction_records_code[:, 2] == 1, 0])
            line_end_idx_rr = np.transpose((reduction_records_code[:, 2] == 1).nonzero()) - 1
            line_end_idx_rr = np.append(line_end_idx_rr, -1)
            line_ends_rr = reduction_records_code[line_end_idx_rr[1:], 0]

            for line_start in line_starts_pr:
                old_code = FieldBook[line_start].find('Code').text
                new_code = old_code[:-2]

                FieldBook[line_start].find('Code').text = new_code

            for line_end in line_ends_pr:
                old_code = FieldBook[line_end].find('Code').text
                new_code = '-' + old_code

                FieldBook[line_end].find('Code').text = new_code

            for line_start in line_starts_rr:
                old_code = Reductions[line_start].find('Code').text
                new_code = old_code[:-2]

                Reductions[line_start].find('Code').text = new_code

            for line_end in line_ends_rr:
                old_code = Reductions[line_end].find('Code').text
                new_code = '-' + old_code

                Reductions[line_end].find('Code').text = new_code

        parsed_jxl = etree.ElementTree(sx_job.getroot())

        output_path = os.path.join(config['output_path'], os.path.basename(file))
        parsed_jxl.write(output_path, pretty_print=True)

        print('Finished')
            

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

    parse_files = []

    for file in os.listdir(dir_input):
        if file.endswith('.jxl'):
            file_path = os.path.join(dir_input, file)
            parse_files.append(file_path)

    return parse_files

def get_line_codes(dir_line_codes) -> list:
    '''
    Gets all line codes from the current code list

    Parameters
    ----------
    None

    Returns
    -------
    line_codes : List of ints
        List containing all line codes in the Geoterra Code list
    '''

    code_list = pd.read_csv(dir_line_codes, sep=';', header=0, usecols=['Objektart', 'Messcode'], encoding='unicode_escape')

    line_codes = code_list.Messcode[code_list.Objektart == 'PL'].to_numpy()

    return line_codes


if __name__ == '__main__':
    main()