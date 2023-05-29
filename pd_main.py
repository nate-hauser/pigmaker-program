
import os
import pandas as pd
import pickle
import pd_table as pdt
import tkinter as tk
from tkinter import filedialog
import sys

TESTING = True

# global breed_df
# global farrow_df 
# global merged_df

breed_df = None
farrow_df = None
merged_df = None

def run_cmd():
    global breed_df, farrow_df, merged_df
    breed_file = breed_entry.get()
    farrow_file = farrow_entry.get()
    group_num = group_entry.get()

    # **********************ERROR CHECKS**********************

    # if breed_file == '':
    #     print('Error: Breed file is none')
    #     return
    # if farrow_file == '':
    #     print('Error: Farrow file is none')
    #     return
    # if not os.path.isfile(breed_file):
    #     print('Error: Breed file does not exist')
    #     return
    # if not os.path.isfile(farrow_file):
    #     print('Error: Farrow File does not exist')
    #     return
    # if group_num == '':
    #     print('Error: Please Enter Group Number')


    #IF PICKLE FILE MAYBE SKIP THIS FUNCTION CALL
    # if breed_file.endswith('.pkl') or breed_file.endswith('.pickle'):
    #     breed_df = pd.read_pickle(breed_file)
    # else:
    
    #FUNCTION CALL: breed_df, farrow_df, breed_errors, farrow_errors = funct(breed_file, farrow_file)
            #The errors would be a list of the sort for each cell in question: [[row1, col1], [row2, col2]]

    #Have user Validate
    breed_df_raw = pd.read_pickle('testdf.pkl') #test df
    errors = [[1,1], [2,2]]
    #errors = None
    breed_df, breed_errors, isOK = pdt.table_editor(root, breed_df_raw, errors, name='Breed Data')
    #print(breed_df)

    #if cancelled then do not do further processing
    if not isOK:
        return

    #FUNCTION CALL: data_good = check_data(df)

    #if data good, proceed

    #ADD POPUP: ADD INFO TO MASTER SPREADSHEET?
        #IF NO, PROMPT TO SAVE WORK

    #FUNCTION CALL: update_spreadsheet(new_breed_df, new_farrow_df)


def review_table(df, filepath, table_name='Table Data', file_function=None):

    # **********************ERROR CHECKS**********************

    # if df is None:
        # if filepath == '':
        #     print('Error: file is none')
        #     return
        # if not os.path.isfile(filepath):
        #     print('Error: file does not exist')
        #     return

    #IF PICKLE FILE MAYBE SKIP THIS FUNCTION CALL
    # if filepath.endswith('.pkl') or filepath.endswith('.pickle'):
    #     df = pd.read_pickle(filepath)
    # else:

    #FUNCTION CALL: df_raw, df_errors = file_function(filepath) 
            # filepath would be a path to the pdf
            #The errors would be a list of the sort for each cell in question: [[row1, col1], [row2, col2]]

    #Have user Validate

    #For testing purposes
    df_raw = pd.read_pickle('testdf.pkl') #test df
    df_errors = [[1,1], [2,2]]
    #errors = None

    df_new, df_errors_new, isOK = pdt.table_editor(root, df_raw, df_errors, name=table_name)

    #if cancelled then do not do further processing
    if not isOK:
        return df
    df = df_new
    return df
    #print(df)

def review_breed():
    
    global breed_df

    #JAKE: REPLACE FILE FUNCTION WITH FUNCTION THAT GENERATES BREED DF
    breed_df = review_table(breed_df, breed_entry.get(), 'Breed Data', file_function=None)

def review_farrow():
    
    global farrow_df

    #JAKE: REPLACE FILE FUNCTION WITH FUNCTION THAT GENERATES FARROW DF
    farrow_df = review_table(farrow_df, farrow_entry.get(), 'Farrow Data', file_function=None)

def review_merged():
    
    global merged_df

    #MAYBE: CREATE MERGED ENTRY
    merged_df = review_table(merged_df, None, 'Merged Data', file_function=None)

def merge_cmd():
    global merged_df
    print('Merging File.................')


    #JAKE ADD FUNCTION TO COMBINE DFs

    # merged_df_raw = merge_file(breed_df, farrow_df)
    # merged_df = review_table(merged_df_raw, None, 'Merged Data', None)

def load_cmd():
    global merged_df
    print('Loading File...................')

    # GET FILEPATH TO MERGED FILE

    # DISPLAY MERGED FILE


def gen_report():
    print('Generating Report....................')

    #ADD ERROR CHECKS
    
    #JAKE ADD FUNCTION TO GENERATE REPORT

def save_cmd():
    print('Saving file(s)..............')

    #ADD POPUPS TO SELECT WHAT DFs TO SAVE

    if breed_df is not None:
        #print(breed_df)
        fileName = filedialog.asksaveasfile(initialfile='breed_df.pickle', filetypes = [('Pickle files', '*.pickle')])
        breed_df.to_pickle(fileName.name)
    
    if farrow_df is not None:
        fileName = filedialog.asksaveasfile(initialfile='farrow_df.pickle', filetypes = [('Pickle files', '*.pickle')])
        farrow_df.to_pickle(fileName.name)

    if merged_df is not None:
        fileName = filedialog.asksaveasfile(initialfile='merged_df.pickle', filetypes = [('Pickle files', '*.pickle')])
        merged_df.to_pickle(fileName.name)

def close_cmd():
    print('closing file.................')
    ##ADD popup: Are you sure? 
    
    root.destroy()

def fileBrowse(entry):
    
    filepath = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = (("PDF files", "*.pdf"),
                                                       ('Pickle files', '*.pickle'),
                                                        ("all files", "*.*")))
    entry.delete(0, tk.END)
    entry.insert(0, filepath)

#Create an instance of Tkinter frame or window
root= tk.Tk()
#Set the geometry of tkinter frame
root.geometry("720x400")

#****************************Dates**********************************
s_date_label = tk.Label(root, text='Start Date', fg='black', font=('Arial', 14))
s_date_label.grid(row=0, column=0)

s_date_entry = tk.Entry(root)
s_date_entry.grid(row =0, column=1)

e_date_label = tk.Label(root, text='End Date', fg='black', font=('Arial', 14))
e_date_label.grid(row=0, column=3)

e_date_entry = tk.Entry(root)
e_date_entry.grid(row =0, column=4)

#****************************File Entry**********************************
breed_label = tk.Label(root, text='Breed file', fg='black', font=('Arial', 14))
breed_label.grid(row=1, column=0, pady=5)

breed_entry = tk.Entry(root)
breed_entry.grid(row =1, column=1, pady=5)

breed_browse = tk.Button(root, text='Browse', width=10, command=lambda: fileBrowse(breed_entry))
breed_browse.grid(row=1, column=2, padx=5)

farrow_label = tk.Label(root, text='Farrow file', fg='black', font=('Arial', 14))
farrow_label.grid(row=1, column=3, pady=5)

farrow_entry = tk.Entry(root)
farrow_entry.grid(row =1, column=4, pady=5)

farrow_browse = tk.Button(root, text='Browse', width=10, command=lambda: fileBrowse(farrow_entry))
farrow_browse.grid(row=1, column=5, padx=5)

group_label = tk.Label(root, text='Group Number', fg='black', font=('Arial', 14))
group_label.grid(row=2, column=0, pady=5, padx=5)

group_entry = tk.Entry(root)
group_entry.grid(row=2, column=1, pady=5)
# breed_file = breed_entry.get()
# farrow_file = None

#****************************Print Output**********************************
class PrintLogger: 
    def __init__(self, textbox): 
        self.textbox = textbox 
 
    def write(self, text): 
        self.textbox.insert(tk.END, text)
output_lbl = tk.Label(root, text='Output', fg='black', font=('Arial', 14))
output_lbl.grid(row=3, column=0)

textbox = tk.Text(root, height=10, width=50) 
textbox.grid(row=3, column=1, columnspan=4, pady=20) 

printlogger = PrintLogger(textbox)

if not TESTING:
    sys.stdout = printlogger 

#****************************Process Control**********************************

#proc_frame = tk.Frame(root).grid(row=4, column=0, columnspan=5)

review_breed_btn = tk.Button(root, text='Review Breed', width=15, command= review_breed)
review_breed_btn.grid(row=4, column=0, pady=10, padx=2)

review_farrow_btn = tk.Button(root, text='Review Farrow', width=15, command= review_farrow)
review_farrow_btn.grid(row=4, column=1, pady=10, padx=2)

merge_btn = tk.Button(root, text='Merge', width=15, command=merge_cmd)
merge_btn.grid(row=4, column=2, pady=10, padx=2)

add_btn = tk.Button(root, text='Add to Master', width=15, command=run_cmd)
add_btn.grid(row=5, column=0, pady=2, padx=2)

load_btn = tk.Button(root, text='Load', width=15, command=load_cmd)
load_btn.grid(row=5, column=1, pady=2, padx=2)

save_btn = tk.Button(root, text='Save', width=15, command=save_cmd)
save_btn.grid(row=5, column=2, pady=2, padx=2)

report_btn = tk.Button(root, text='Generate Report', width=15, command=gen_report)
report_btn.grid(row=5, column=3, pady=2, padx=2)

close_btn = tk.Button(root, text='Close', width=15, command=close_cmd)
close_btn.grid(row=5, column=4, pady=2, padx=2)



#ADD: Separate buttons for each function
#TEST

root.mainloop()





