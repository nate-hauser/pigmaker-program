
import os
import pandas as pd
import pickle
import pd_table as pdt
import tkinter as tk
from tkinter import filedialog
import sys

TESTING = True

def run_cmd():
    
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


    #FUNCTION CALL: breed_df, farrow_df, breed_uncert, farrow_uncert = funct(breed_file, farrow_file)
            #The uncert would be a list of the sort for each cell in question: [[row1, col1], [row2, col2]]

    #Have user Validate
    df = pd.read_pickle('testdf.pkl') #test df
    errors = [[1,1], [2,2]]
    t_df, isOK = pdt.table_editor(root, df, errors)
    print(t_df)

    #if cancelled then do not do further processing
    if not isOK:
        return

    #FUNCTION CALL: data_good = check_data(df)

    #if data good, proceed

    #FUNCTION CALL: update_spreadsheet(new_breed_df, new_farrow_df)

def gen_report():
    print('Generating Report....................')

    #ADD ERROR CHECKS
    
    #ADD FUNCTION CALL

def fileBrowse(entry):
    
    filepath = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = (("PDF files", "*.pdf"),
                                                       ('Pickle files', '*.pkl'),
                                                        ("all files", "*.*")))
    entry.delete(0, tk.END)
    entry.insert(0, filepath)

#Create an instance of Tkinter frame or window
root= tk.Tk()
#Set the geometry of tkinter frame
root.geometry("700x400")

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

run_btn = tk.Button(root, text='Run', width=15, command=run_cmd)
run_btn.grid(row=4, column=0, pady=20, padx=5)

close_btn = tk.Button(root, text='Close', width=15, command=root.destroy)
close_btn.grid(row=4, column=1, pady=20)

report_btn = tk.Button(root, text='Generate Report', width=15, command=gen_report)
report_btn.grid(row=4, column=4, pady=20, padx=5)

#ADD: Group number and Generate report button
#TEST

root.mainloop()





