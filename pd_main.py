
import os
import pandas as pd
import pd_table as pdt
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
import sys
import Back_end as be
import pickle

TESTING = False

#global variables
breed_df = None
breed_df_errors = None
farrow_df = None
farrow_df_errors = None
merged_df = None
merged_df_errors = None


def error_checks():
    isOK = True

    if merged_df is not None:
        return True
    #Error check
    if breed_df is None:
        print('Error: Breed Table is None')
        isOK = False
    if farrow_df is None:
        print('Error: Farrow Table is None')
        isOK = False
    
    if len(breed_df_errors) > 0:
        print('Error: Breeding table contains errors. Please Review.')
        isOK = False
    if len(farrow_df_errors) > 0:
        print('Error: Breeding table contains errors. Please Review.')
        isOK = False

    return isOK

def are_dates_valid(start_end_dates):

    """Performs two checks on inputted start and end dates. One is that they are valid dates and the other is
    that the end date is after the start date"""

    dates = list(start_end_dates.values())
    keys = list(start_end_dates.keys())
    for i in range(0, len(dates)):
        try:
            dates[i] = pd.to_datetime(dates[i])
        except:
            print("The ", keys[i], " date is causing an error.")
            print("The date should be in mm/dd/yy or mm/dd/yyyy format")
            return False

        if i in [1, 3, 5]:
            if not dates[i] > dates[i - 1]:
                print("Error: the ", keys[i - 1], " date is greater than the ", keys[i], " date.")
                print("The date should be in mm/dd/yy or mm/dd/yyyy format")
                return False
    return True
def add_to_master():

    group_num = group_entry.get()

    #If error exists, stop here
    isOK = error_checks()
    if not isOK:
        return

    popup = pdt.popup_yes_no('Proceed to update Master?', root)
    popup.wait_window()

    if not popup.response:
        return
    
    print('Updating Master Spreadsheet...................')
    #JAKE: ADD MASTER FUNCTION
    print('Master Spreadsheet Update Complete.')
    be.output_to_excel(merged_df)
def review_table(df, df_errors, filepath, table_name, pdf_to_df_function, df_error_function, start_end_dates, group_num):
    """
    Generic function to display dataframes in an editable table.
    If necessary, create dataframe from filepath entry.
    """

    isOK = False

    # **********************ERROR CHECKS**********************
    if group_num is None:
        print("Please enter group number")
        return df, df_errors, isOK
    if df is None:
        
        if filepath == '':
            print('Error: file is none')
            return df, df_errors, isOK
        if not os.path.isfile(filepath):
            print('Error: file does not exist')
            return df, df_errors, isOK
        #Date Entry Check
        if not are_dates_valid(start_end_dates):
            return df, df_errors, isOK

        # if start_date is None:
        #     print('Error: Please Enter a Start Date.')
        #     return df, df_errors, isOK
        # if end_date is None:
        #     print('Error: Please Enter an End Date.')
        #     return df, df_errors, isOK

        #IF PICKLE FILE MAYBE SKIP THIS FUNCTION CALL
        if filepath.endswith('.pkl') or filepath.endswith('.pickle'):
            df_raw = pd.read_pickle(filepath)
            df_errors_raw = df_error_function(df_raw, start_end_dates)
        else:
            # FUNCTION CALL:
            df_raw = pdf_to_df_function(filepath, group_num)
            df_errors_raw = df_error_function(df_raw, start_end_dates)
            # filepath would be a path to the pdf
            #The errors would be a list of the sort for each cell in question: [[row1, col1], [row2, col2]]

            #For testing purposes
            # df_raw = pd.read_pickle('testdf.pkl')
            # df_errors_raw = [[1,1], [2,2]]
    else:
        df_raw = df
        df_errors_raw = df_errors

    #Open Table
    df_new, df_errors_new, isOK = pdt.table_editor(root, df_raw, df_errors_raw, name=table_name)

    #if cancelled then do not do further processing and return original df
    if isOK:
        df = df_new
        df.reset_index(drop=True,inplace=True)
        df_errors = df_errors_new

    return df, df_errors, isOK

def review_breed():
    """Display Breed dataframe for editing"""
    global breed_df, breed_df_errors

    #JAKE: REPLACE FILE FUNCTION WITH FUNCTION THAT GENERATES BREED DF
    breed_df, breed_df_errors, isOK = review_table(breed_df, breed_df_errors, breed_entry.get(), 'Breed Data', 
                                                   be.pdf_to_breed, be.breed_produce_errors,
                                                   {"breed start": breed_s_date_entry.get(),
                                                   "breed end": breed_e_date_entry.get()},group_entry.get())

    records_full_path = os.path.join(be.BREEDING_FARROWING_RECORDS_DIRECTORY, "breed" + str(group_entry.get()) + ".pkl")
    breed_df.to_pickle(records_full_path)


def review_farrow():
    """Display farrow dataframe for editing"""
    global farrow_df, farrow_df_errors

    #JAKE: REPLACE FILE FUNCTION WITH FUNCTION THAT GENERATES FARROW DF
    if wean_s_date_entry.get() is None:
        print('Error: Please Enter a Weaning Start Date.')
        return
    if wean_e_date_entry.get() is None:
        print('Error: Please Enter a Weaning End Date.')
        return

    farrow_df, farrow_df_errors, isOK = review_table(farrow_df, farrow_df_errors, farrow_entry.get(), 'Farrow Data', 
                                                     be.pdf_to_farrow,be.farrow_produce_errors,
                                                     {"farrow start": farrow_s_date_entry.get(),
                                                      "farrow end": farrow_e_date_entry.get(),
                                                      "wean start": wean_s_date_entry.get(),
                                                      "wean end": wean_e_date_entry.get()},
                                                     group_entry.get()
                                                     )

    records_full_path = os.path.join(be.BREEDING_FARROWING_RECORDS_DIRECTORY, "farrow" + str(group_entry.get()) + ".pkl")
    farrow_df.to_pickle(records_full_path)

def review_merged():
    """Display merged dataframe for editing"""
    global merged_df, merged_df_errors

    #MAYBE: CREATE MERGED ENTRY
    
    if merged_df is None:
        print('Error: Must Merge tables first!')
        return
    merged_df, merged_df_errors = review_table(merged_df, merged_df_errors, None, 'Merged Data', pdf_to_df_function=None)

def merge_cmd():
    """Command to combine Breed and Farrow tables then display result"""

    global merged_df
    print('Merging File.................')


    #JAKE ADD FUNCTION TO COMBINE DFs

    # merged_df_raw = merge_file(breed_df, farrow_df)
    # merged_df = review_table(merged_df_raw, None, 'Merged Data', None)

def load_cmd():
    """Load in an existing merged table"""
    global merged_df
    print('Loading File...................')

    if merged_df is not None:
        popup = pdt.popup_yes_no('Merged Table already exists')
    # GET FILEPATH TO MERGED FILE
    filepath = filedialog.askopenfilename(initialdir = be.GROUP_RECORDS_DIRECTORY,
                                          title = "Select Merged File",
                                          filetypes = [('Pickle files', '*.pickle *.pkl'),
                                                        ("all files", "*.*")])
    
    merged_df = pd.read_pickle(filepath)

    print("File is loaded")
                                                       

    # DISPLAY MERGED FILE
    # merged_df = review_table(merged_df, None, 'Merged Data', file_function=None)


def gen_report():
    """Generate a report of data"""

    global merged_df
    print('Generating Report....................')
    if merged_df is not None:
        merged_df = be.generate_report(merged_df,group_entry.get(),total_wean_entry.get())
        return

    #ADD ERROR CHECKS
    #If error exists, stop here
    isOK = error_checks()
    if not isOK:
        return

    start_end_dates = {"breed start": breed_s_date_entry.get(),
                              "breed end": breed_e_date_entry.get(),
                              "farrow start": farrow_s_date_entry.get(),
                              "farrow end": farrow_e_date_entry.get(),
                              "wean start": wean_s_date_entry.get(),
                              "wean end": wean_e_date_entry.get()}

    if not are_dates_valid(start_end_dates):
        return
    merged_df = be.pre_report_processing(breed_df,farrow_df,start_end_dates, group_entry.get())

    records_full_path = os.path.join(be.GROUP_RECORDS_DIRECTORY,
                                         "Group" + str(group_entry.get()) + ".pkl")
    merged_df.to_pickle(records_full_path)

    merged_df = be.generate_report(merged_df, group_entry.get(), total_wean_entry.get())

def reset_cmd():
    """Reset all Entry boxes and Tables"""
    global merged_df, merged_df_errors
    global breed_df, breed_df_errors
    global farrow_df, farrow_df_errors

    popup = pdt.popup_yes_no('Clear all stored Process data?', root)
    popup.wait_window()

    if not popup.response:
        return

    print('Reseting................')

    #clear all entries and global variables
    merged_df = None
    merged_df_errors = None
    breed_df = None
    breed_df_errors = None
    farrow_df = None
    farrow_df_errors = None

    def reset_entry(entry):
        entry.delete(0, tk.END)
        entry.insert(0, '')
    #Clear entries
    reset_entry(breed_s_date_entry)
    reset_entry(breed_e_date_entry)
    reset_entry(farrow_s_date_entry)
    reset_entry(farrow_e_date_entry)
    reset_entry(wean_s_date_entry)
    reset_entry(wean_e_date_entry)
    reset_entry(breed_entry)
    reset_entry(farrow_entry)
    reset_entry(group_entry)

def close_cmd():
    """Exit program and shutdown all screens"""

    print('closing file.................')
    ##ADD popup: Are you sure? 
    close_popup = pdt.popup_yes_no('Are you sure you want to close?', root)
    close_popup.wait_window()

    if close_popup.response:
        root.destroy()

def fileBrowse(entry):
    
    filepath = filedialog.askopenfilename(initialdir = be.DOWNLOADS_DIRECTORY,
                                          title = "Select a File",
                                          filetypes = (("PDF files", "*.pdf"),
                                                       ('Pickle files', '*.pickle *.pkl'),
                                                        ("all files", "*.*")))
    entry.delete(0, tk.END)
    entry.insert(0, filepath)

def modify_breeder_list():
    root = tk.Tk()
    root.title("Breeder List")

    listbox = tk.Listbox(root)
    listbox.pack()

    with open("breeders.pkl", 'rb') as file:
        breeders = (pickle.load(file))

    for i in breeders:
        listbox.insert(tk.END, i)

    def remove_item():
        selected_index = listbox.curselection()
        if selected_index:
            selected_index = selected_index[0]
            listbox.delete(selected_index)

    def add_item():
        new_item = simpledialog.askstring("Add Item", "Enter a new item:")
        if new_item:
            listbox.insert(tk.END, new_item)

    def edit_item():
        selected_index = listbox.curselection()
        if selected_index:
            selected_index = selected_index[0]
            updated_item = simpledialog.askstring("Edit Item", "Edit selected item:",
                                                  initialvalue=listbox.get(selected_index))
            if updated_item:
                listbox.delete(selected_index)
                listbox.insert(selected_index, updated_item)

    def save_list():
        updated_breeders = set()
        for i in listbox.get(0, tk.END):
            updated_breeders.add(i)

        with open("breeders.pkl", "wb") as file:
            pickle.dump(updated_breeders, file)

        root.destroy()



    add_button = tk.Button(root, text="Add Item", command=add_item)
    remove_button = tk.Button(root, text="Remove Item", command=remove_item)
    edit_button = tk.Button(root,text="Edit Item",command=edit_item)
    save_button = tk.Button(root, text="Save", command=save_list)

    add_button.pack()
    edit_button.pack()
    remove_button.pack()
    save_button.pack()

    root.mainloop()


#Create an instance of Tkinter frame or window
root= tk.Tk()
#Set the geometry of tkinter frame
root.geometry("740x500")

#****************************Dates**********************************

s_date_label = tk.Label(root, text='Start Date', fg='black', font=('Arial', 14))
s_date_label.grid(row=0, column=1)

e_date_label = tk.Label(root, text='End Date', fg='black', font=('Arial', 14))
e_date_label.grid(row=0, column=3)

breed_date_label = tk.Label(root, text='Breeding', fg='black', font=('Arial', 14))
breed_date_label.grid(row=1, column=0)

breed_s_date_entry = tk.Entry(root)
breed_s_date_entry.grid(row=1, column=1)

breed_e_date_entry = tk.Entry(root)
breed_e_date_entry.grid(row=1, column=3)

farrow_date_label = tk.Label(root, text='Farrowing', fg='black', font=('Arial', 14))
farrow_date_label.grid(row=2, column=0)

farrow_s_date_entry = tk.Entry(root)
farrow_s_date_entry.grid(row=2, column=1)

farrow_e_date_entry = tk.Entry(root)
farrow_e_date_entry.grid(row=2, column=3)

wean_date_label = tk.Label(root, text='Weaning', fg='black', font=('Arial', 14))
wean_date_label.grid(row=3, column=0)

wean_s_date_entry = tk.Entry(root)
wean_s_date_entry.grid(row=3, column=1)

wean_e_date_entry = tk.Entry(root)
wean_e_date_entry.grid(row=3, column=3)

end_date_row = 3 # Used for placing widgets in the correct row
#****************************File Entry**********************************
file_row = end_date_row + 1

breed_label = tk.Label(root, text='Breed file', fg='black', font=('Arial', 14))
breed_label.grid(row=file_row, column=0, pady=5)

breed_entry = tk.Entry(root)
breed_entry.grid(row=file_row, column=1, pady=5)

breed_browse = tk.Button(root, text='Browse', width=10, command=lambda: fileBrowse(breed_entry))
breed_browse.grid(row=file_row, column=2, padx=5)

farrow_label = tk.Label(root, text='Farrow file', fg='black', font=('Arial', 14))
farrow_label.grid(row=file_row, column=3, pady=5)

farrow_entry = tk.Entry(root)
farrow_entry.grid(row=file_row, column=4, pady=5)

farrow_browse = tk.Button(root, text='Browse', width=10, command=lambda: fileBrowse(farrow_entry))
farrow_browse.grid(row=file_row, column=5, padx=5)

group_row = file_row + 1

group_label = tk.Label(root, text='Group Number', fg='black', font=('Arial', 14))
group_label.grid(row=group_row, column=0, pady=5, padx=5)

group_entry = tk.Entry(root)
group_entry.grid(row=group_row, column=1, pady=5)

total_wean_label = tk.Label(root, text='Total Weaned', fg='black', font=('Arial', 14))
total_wean_label.grid(row=group_row, column=2, pady=5)

total_wean_entry = tk.Entry(root)
total_wean_entry.grid(row=group_row, column=3, pady=5)


#****************************Print Output**********************************
class PrintLogger: 
    def __init__(self, textbox): 
        self.textbox = textbox 
 
    def write(self, text): 
        self.textbox.insert(tk.END, text)

output_row = group_row + 1

output_lbl = tk.Label(root, text='Output', fg='black', font=('Arial', 14))
output_lbl.grid(row=output_row, column=0)

textbox = tk.Text(root, height=10, width=50) 
textbox.grid(row=output_row, column=1, columnspan=4, pady=20) 

printlogger = PrintLogger(textbox)

if not TESTING:
    sys.stdout = printlogger 

#****************************Process Control**********************************

review_row = output_row +1

review_breed_btn = tk.Button(root, text='Review Breed', width=15, command= review_breed)
review_breed_btn.grid(row=review_row, column=0, pady=10, padx=2)

review_farrow_btn = tk.Button(root, text='Review Farrow', width=15, command= review_farrow)
review_farrow_btn.grid(row=review_row, column=1, pady=10, padx=2)

# review_merge_btn = tk.Button(root, text='Review Merged', width=15, command= review_merged)
# review_merge_btn.grid(row=4, column=2, pady=10, padx=2)

# merge_btn = tk.Button(root, text='Merge', width=15, command=merge_cmd)
# merge_btn.grid(row=4, column=3, pady=10, padx=2)

report_btn = tk.Button(root, text='Generate Report', width=15, command=gen_report)
report_btn.grid(row=review_row, column=2, pady=10, padx=2)

command_row = review_row + 1

add_btn = tk.Button(root, text='Add to Master', width=15, command=add_to_master)
add_btn.grid(row=command_row, column=0, pady=2, padx=2)

load_btn = tk.Button(root, text="Load Group Record", width=15, command=load_cmd)
load_btn.grid(row=command_row, column=2, pady=2, padx=2)

breeders_btn = tk.Button(root, text='Breeders', width=15, command=modify_breeder_list)
breeders_btn.grid(row=command_row, column=1, pady=2, padx=2)

reset_btn = tk.Button(root, text='Reset', width=15, command=reset_cmd)
reset_btn.grid(row=command_row, column=3, pady=2, padx=2)

close_btn = tk.Button(root, text='Close', width=15, command=close_cmd)
close_btn.grid(row=command_row, column=4, pady=2, padx=2)





#ADD: Separate buttons for each function
#TEST

root.mainloop()





