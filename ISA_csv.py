#!/usr/bin/env python3
# coding: utf-8






import csv
from pathlib import Path
import datetime
import sys







# just for testing in jupyter
# sys.argv = [sys.argv[0]]

# sys.argv.append('/Users/aaronciuffo/Downloads/ISA testing - Data processing - 1. Source.csv')






def main():
    
    # tags we want to have in the tags column -- this is terribly messy 
    tags = {
        'course': ['MA', 'ENG'],
        'eal': ['Academic', 'Foundations'],
        'ls': ['Learning Support']
    }

    # these are the colunmns that will appear in the final CSV
    desired_columns = ['Last Name', 
                       'First Name', 
                       'Emailstudent', 
                       'Dob', 
                       'Gender', 
                       'Student Number',
                       'Grade Level', 
                       'Primarylanguage',
                       'Tags',
                       'Password',
                       'School year',
                       'ESOL',
                      ]

    # lookup table to convert the "expression" field from PowerSchool into a block letter
    # note the leading `0` to make the indexing the same as the expression indexing: 1==A, 2==B
    expression_lookup = '0ABCDEFGH'
    
    # lookup table to convert 'm' to male, etc.
    gender_lookup = {'m': 'male',
                     'f': 'female',
                    }
    
    
    # get the time in YYYY-MM-DD_HHMM format to use for naming the output file
    date_time = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
    try:
        csv_file = Path(sys.argv[1]).expanduser().resolve()
    except Exception as e:
        print('No input file name supplied! Exiting')
        # bail out if no input file is specified
        return
    output_file = csv_file.parent/f'ISA_READY_{csv_file.stem}{date_time}.csv'

    # read the CSV into a list
    csv_list = []
    # make one big list with every row from the CSV
    with open(csv_file) as csvin:
        csvreader = csv.DictReader(csvin)
        for row in csvreader:
            csv_list.append(row)

    student_dict = {}
    # make a dictionary of unique student numbers and consolodate each course row into one entry in the dict
    for row in csv_list:
        # if the student number doesn't exist, add it to the dictionary
        if not row['Student Number'] in student_dict:
            student_dict[row['Student Number']] = []

        # add all the rows that match the student number to a long list under the dictionary
        student_dict[row['Student Number']].append(row)



    # empty dictionary to hold everything
    output_dict = {}

    # work through each student entry in the large dictionary
    for s_number, data in student_dict.items():
        # if the student doesn't yet exist, create an entry and add the tags column
        if not s_number in output_dict:
            output_dict[s_number] = {'Tags': []}

        # process each row contined in each student
        for row in data:
            for column in row:
                # add desired columns
                if column in desired_columns:
                    output_dict[s_number][column] = row[column]

            # kludge to get gender into 'male' or 'female' format; ignore everything else
            if row['Gender'].lower() in gender_lookup:
                output_dict[s_number]['Gender'] = gender_lookup[row['Gender'].lower()]

            # try to convert dob into dd/mm/yyyy format; on failure just use whatever powerschool supplied
            try:
                dob = datetime.datetime.strptime(row['Dob'], '%d-%b-%y').strftime('%d/%m/%Y')
            except Exception as e:
                dob = row['Dob']

            output_dict[s_number]['Dob'] = dob



            # add courses to the tags list; append the block number
            for c in tags['course']:
                if c in row['Course name']:
                    # try to convert the block number into a letter
                    try:
                        block = expression_lookup[int(row['Expression'][0])]
                    # on thrown exception, just revert to the expression
                    except Exception:
                        block = row['Expression']

                    output_dict[s_number]['Tags'].append(f"{row['Course name']} {block}")

            # add 'EAL' tag
            for e in tags['eal']:
                if e in row['Course name']:
                    output_dict[s_number]['Tags'].append("EAL")
                    output_dict[s_number]['ESOL'] = 'Yes'

            # add 'LS' tag
            for l in tags['ls']:
                if l in row['Course name']:
                    output_dict[s_number]['Tags'].append('LSC')

            # make sure all the desired columns are represented
            for each in desired_columns:
                if each not in output_dict[s_number]:
                    output_dict[s_number][each] = ''

        # kludge to add "No" to ESOL field
        if not output_dict[s_number]['ESOL'] == 'Yes':
            output_dict[s_number]['ESOL'] = 'No'

        # consolodate tags into a string
        output_dict[s_number]['Tags'] = ', '.join(output_dict[s_number]['Tags'])
        
        # kludge to remove @ from username
        try:
            username = output_dict[s_number]['Emailstudent'].split('@')[0]
        except Exception:
            username = output_dict[s_number]['Emailstudent']
        
        output_dict[s_number]['Emailstudent'] = username


    with open(output_file, 'w') as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=desired_columns,
            delimiter=',',
            quotechar='"',
            quoting=csv.QUOTE_ALL
        )
        writer.writeheader()
        for row in output_dict.values():
            writer.writerow(row)






if __name__ == '__main__':
    main()


