import PySimpleGUI as sg
import os
import pandas as pd
import table_editor as te


headers = ['Sow ID', 'Group', 'Date Breed', 'Breeder Initials', 'Date Farrowed', 'Liter']
sow_ids = [1, 2, 3, 4]
groups = ['A', 'B', 'B', 'C']
date_breed = ['2/17', '2/18', '2/18', '2/19']
breeder_initials = ['MK', 'MK', 'NN', 'NN']
date_farrowed = ['6/19', '6/21', '6/21', '6/25']
liter = [10, 8, 11, 7]

test_data = str([sow_ids, groups, date_breed, breeder_initials, date_farrowed, liter])
#print(test_data)

data = {
    'Sow ID' : sow_ids,
    'Group' : groups,
    'Date Breed' : date_breed,
    'Breeder Initials' : breeder_initials,
    'Date Farrowed' : date_farrowed,
    'Liter Size' : liter
}

# dataframe = pd.DataFrame(data)
# table_headers = dataframe.columns
# table_headers = table_headers.values
# table_values = dataframe.to_numpy()
# table_headers = list(table_headers)


# popup_layout = [[
#             sg.Table(values=table_values, headings=table_headers, justification='center'),
#             sg.Button('Done')
#         ]]

# t_window = sg.Window('Table', popup_layout)
# # gui_table = values['Table']
# # window['Table']
# while True:
#     t_event, t_values = t_window.read()
#     if t_event == "Done" or t_event == sg.WIN_CLOSED:
#         # element = window['End_Date']
#         # print(element.Get())
#         break

# exit()

#*****************layout**********************
title = "Bread/Farrow Data Uploader"

#Start and End date row
date_layout = [
    sg.Text('Start'), 
    sg.In(size=(10,1), enable_events=True, key='Start_Date'),
    sg.CalendarButton('Select Date', format='%Y-%m-%d'),
    sg.Text('\t'),
    sg.Text('End'),
    sg.In(size=(10,1), enable_events=True, key='End_Date'),
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

# #Image Folder Directory
# image_box = sg.Listbox(
#             values=[], enable_events=True, size=(40, 20), key="Image_List"
#         )

# image_list_layout = [
#     [
#         sg.Text('Image directory'),
#         sg.In(size=(20,1),enable_events=True,key='Image_Folder'),
#         sg.FolderBrowse()
#     ],
#     [
#         image_box
#     ]  
# ]

output_box = sg.Multiline(key='-Output-', size=(50, 10), reroute_stdout=False)

output_layout = [
    [
        sg.Text('Output Terminal')
    ],
    [
        output_box
    ]
]


# column_layout = [
#     [
#         sg.Column(image_list_layout),
#         sg.VSeparator(),
#         sg.Column(output_layout)
#     ]
# ]

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

while True:
    event, values = window.read()
    if event == "Close" or event == sg.WIN_CLOSED:
        # element = window['End_Date']
        # print(element.Get())
        break
    # Folder name was filled in, make a list of files in the folder
    # if event == "Image_Folder":
    #     folder = values["Image_Folder"]
    #     try:
    #         # Get list of files in folder
    #         file_list = os.listdir(folder)
    #     except:
    #         file_list = []

    #     fnames = [
    #         f
    #         for f in file_list
    #         if os.path.isfile(os.path.join(folder, f))
    #         and f.lower().endswith((".txt", ".gif"))
    #     ]
    #     window["Image_List"].update(fnames)
    if event == "Run":
        #out_element = window['Output']
        #out_element.print('Testing')
        #out_element.reroute_stdout_to_here()
        #print('Testing')
        
        #pandas_dataframe = data
        dataframe = pd.DataFrame(data)
        

        #gui = show(dataframe)

        # table_layout = [
        #     [
        #         sg.Table(values=table_values, headings=table_headers, justification='center', enable_events = True, enable_click_events=True, key='-Table-')
        #     ],
        #     [
        #         sg.Button('Finish')
        #     ]
        # ]
       

        # t_window = sg.Window('Table', table_layout)
        
        # while True:
        #     t_event, t_values = t_window.read()
        #     if t_event == "Finish" or t_event == sg.WIN_CLOSED:
        #         break
        #     if t_event == '-Table-':
        #         print('Table Clicked')
        #         py_table = t_window['-Table-']
        #         clicked_values = py_table.get_last_clicked_position()
        #         #print(f'X values: {t_values.x} \t Y value: {t_values.y}')
        #         #print(clicked_values)
        #         #print(t_values['-Table-'].get)
        #         print(clicked_values)
        t_data = te.table_editor(dataframe)
        print(dataframe)

    if event == 'Print':
        print('Printing')
    #if event == 'Select Date':
        #print(window.find_element('-End_Date-'))

