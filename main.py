import PySimpleGUI as sg
import os
import pandas as pd
import table_editor as te

test = True
#test = None

headers = ['Sow ID', 'Group', 'Date Breed', 'Breeder Initials', 'Date Farrowed', 'Liter']
sow_ids = [1, 2, 3, 4]
groups = ['A', 'B', 'B', 'C']
date_breed = ['2/17', '2/18', '2/18', '2/19']
breeder_initials = ['MK', 'MK', 'NN', 'NN']
date_farrowed = ['6/19', '6/21', '6/21', '6/25']
liter = [10, 8, 11, 7]

data = {
    'Sow ID' : sow_ids,
    'Group' : groups,
    'Date Breed' : date_breed,
    'Breeder Initials' : breeder_initials,
    'Date Farrowed' : date_farrowed,
    'Liter Size' : liter
}

#*****************layout**********************
title = "Bread/Farrow Data Uploader"

#Start and End date row
date_layout = [
    sg.Text('Start'), 
    sg.In(size=(10,1), enable_events=True, key='-Start Date-'),
    sg.CalendarButton('Select Date', format='%Y-%m-%d'),
    sg.Text('\t'),
    sg.Text('End'),
    sg.In(size=(10,1), enable_events=True, key='-End Date-'),
    sg.CalendarButton('Select Date', format='%Y-%m-%d')
]

#Input Breeding and Farrowing file
input_layout = [
    sg.Text('Breeding File'),
    sg.In(size=(20,1), enable_events=True, key='-Breeding File-'),
    sg.FileBrowse(),
    sg.Text('\t'),
    sg.Text('Farrow File'),
    sg.In(size=(20,1), enable_events=True, key='-Farrow File-'),
    sg.FileBrowse()
]

output_box = sg.Multiline(key='-Output-', size=(50, 10), reroute_stdout=False)

output_layout = [
    [
        sg.Text('Output Terminal')
    ],
    [
        output_box
    ]
]

close_layout = [
    sg.Button('Run'),
    sg.Button('Close'),
    sg.Button('Print')
]

layout = [
            date_layout,
            input_layout,
            output_layout,
            close_layout      
]

window = sg.Window(title, layout)
breed_file = None
farrow_file = None
start_date = None
end_date = None

while True:
    event, values = window.read()
    if event == "Close" or event == sg.WIN_CLOSED:
        break
    elif event == "Run":
        if breed_file == None or farrow_file == None:
            if not test:
                print('Missing Files')
                continue
        #FUNCTION CALL: breed_df, farrow_df, breed_uncert, farrow_uncert = funct(breed_file, farrow_file)
            #The uncert would be a list of the sort for each cell in question: [[row1, col1], [row2, col2]]

        #Have user Validate
        dataframe = pd.DataFrame(data)
        t_data, isOK = te.table_editor(dataframe, [[1,1], [2,2]])
        print(t_data)
        
        #if cancelled then do not do further processing
        if not isOK:
            continue

        #FUNCTION CALL: data_good = check_data(df)

        #if data good, proceed

        #FUNCTION CALL: update_spreadsheet(new_breed_df, new_farrow_df)

    elif event == 'Print':
        print('Printing')
    elif event == '-Breeding File-':
        breed_file = window['-Breeding File-'].get()
        #print(breed_file)
    elif event == '-Farrow File-':
        farrow_file = window['-Farrow File-'].get()
    elif event == '-Start Date-':
        start_date = window['-Start Date-'].get()
    elif event == '-End Date-':
        end_date = window['-End Date-'].get()


