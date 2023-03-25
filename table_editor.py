import PySimpleGUI as sg
import pandas as pd
from datetime import datetime


def get_dataframe_data(dataframe):
    table_headers = dataframe.columns
    table_headers = table_headers.values
    table_values = dataframe.to_numpy()
    data = table_values.tolist()
    headings = list(table_headers)
    return headings, data

def highlight_cells(t_window, key):
    global error_widgets, error_cells

    root = t_window.TKroot
    #print(root)
     # Gets the Widget object from the PySimpleGUI table - a PySimpleGUI table is really
    # what's called a TreeView widget in TKinter
    table = t_window[key].Widget

    #remove any current squares
    for wid in error_widgets:
        if wid is not None:
            wid.destroy()
    #clear error widget list
    error_widgets = []

    #for each error cell create a red square to be displayed
    for cell in error_cells:
        row = cell[0]+1
        col = cell[1]
        x, y, width, height = table.bbox(row, col)
        #offsets to adjust for new window
        x_offset = 5
        y_offset = 35
        x+= x_offset+width-10
        y+= y_offset

        #Create red square
        rect_points = [0,0,10,10]
        rect = sg.tk.Canvas(root, height=10, width=10, bg='red', bd=.1)
        rect.create_rectangle(rect_points, fill='red', outline='red')
        rect.pack()
        rect.place(x=x, y=y)

        #add to widgets list
        error_widgets.append(rect)

# TKinter function to display and edit value in cell
def edit_cell(dataframe, t_window, key, row, col, justify='left'):

    global textvariable, edit, error_cells
    global cell_font

    def callback(event, row, col, text, key, dataframe):
        global edit, error_cells
        orig_text = text
        # event.widget gives you the same entry widget we created earlier
        widget = event.widget
        if key == 'Focus_Out':
            # Get new text that has been typed into widget
            text = widget.get()
            # Print to terminal
            #print(text)
        # Destroy the entry widget
        widget.destroy()
        # Destroy all widgets
        widget.master.destroy()
        # Get the row from the table that was edited
        # table variable exists here because it was called before the callback
        values = list(table.item(row, 'values'))
        # Store new value in the appropriate row and column
        values[col] = text
        dataframe.iloc[row-1, col] = text
        #print(dataframe)
        table.item(row, values=values)

        #if text changed then remove canvas object
        if orig_text != text:
            i = 0
            pos = [row-1, col]
            while i < len(error_cells):
                if pos[0] == error_cells[i][0] and pos[1] == error_cells[i][1]:
                    error_cells.pop(i)
                    error_widgets[i].destroy()
                    error_widgets.pop(i)
                    continue
                i+= 1
        edit = False

    if edit or row <= 0:
        return

    edit = True
    # Get the Tkinter functionality for our t_window
    root = t_window.TKroot
    # Gets the Widget object from the PySimpleGUI table - a PySimpleGUI table is really
    # what's called a TreeView widget in TKinter
    table = t_window[key].Widget
    # Get the row as a dict using .item function and get individual value using [col]
    # Get currently selected value
    text = table.item(row, "values")[col]
    # Return x and y position of cell as well as width and height (in TreeView widget)
    x, y, width, height = table.bbox(row, col)
    #print(x,y)
    x_offset = 5
    y_offset = 35
    x+= x_offset
    y+= y_offset

    i = 0
    pos = [row-1, col]
    # print(pos)
    # print(error_cells)
    while i < len(error_cells):
        if pos[0] == error_cells[i][0] and pos[1] == error_cells[i][1]:
            #error_cells.pop(i)
            error_widgets[i].pack_forget()
            #error_widgets.pop(i)
            print('Hide')
            # print(error_cells)
        i+= 1

    # Create a new container that acts as container for the editable text input widget
    frame = sg.tk.Frame(root)
    #print(frame)
    # put frame in same location as selected cell
    frame.place(x=x, y=y, anchor='nw', width=width, height=height)

    # textvariable represents a text value
    textvariable = sg.tk.StringVar()
    textvariable.set(text)
    # Used to acceot single line text input from user - editable text input
    # frame is the parent t_window, textvariable is the initial value, justify is the position
    entry = sg.tk.Entry(frame, textvariable=textvariable, justify=justify, font=(f'Arial {cell_font}'))
    #print(entry)
    # Organizes widgets into blocks before putting them into the parent
    entry.pack()
    # selects all text in the entry input widget
    entry.select_range(0, sg.tk.END)
    # Puts cursor at end of input text
    entry.icursor(sg.tk.END)
    # Forces focus on the entry widget (actually when the user clicks because this initiates all this Tkinter stuff, e
    # ending with a focus on what has been created)
    entry.focus_force()
    # When you click outside of the selected widget, everything is returned back to normal
    # lambda e generates an empty function, which is turned into an event function 
    # which corresponds to the "FocusOut" (clicking outside of the cell) event
    entry.bind("<FocusOut>", lambda e, r=row, c=col, t=text, k='Focus_Out', d = dataframe:callback(e, r, c, t, k, d))
    # allow the Return to also trigger the event function
    entry.bind("<Return>", lambda e, r=row, c=col, t=text, k='Focus_Out', d = dataframe:callback(e, r, c, t, k, d))

def table_editor(dataframe, error_loc):
    global edit
    global error_cells, error_widgets
    global cell_font

    datetime_str = '09/19/22 13:55:26'

    datetime_object = datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S')

    #print(type(datetime_object))

    col_datatypes = []
    cell_font = 20
    edit = False
    error_cells = error_loc
    headings, data = get_dataframe_data(dataframe)

    column_widths = []
    max_col = 10
    for header in headings:
        width = len(header)
        if width > max_col:
            width = max_col
        column_widths.append((width))
    
    #print(column_widths)

    #headings, data = generate_table_data()
    sg.set_options(dpi_awareness=True)
    layout = [[
            sg.Button('Add Row'),
            sg.Button('Delete Row'),
            sg.Button('Undo Delete')
        ],
        [
            sg.Table(values=data, headings=headings, 
                        #max_col_width=8,
                        font=("Arial", cell_font),
                        auto_size_columns=False,
                        col_widths=column_widths,
                        # display_row_numbers=True,
                        justification='center',
                        num_rows=20,
                        #alternating_row_color=sg.theme_button_color()[1],
                        key='-TABLE-',
                        # selected_row_colors='red on yellow',
                        # enable_events=True,
                        # select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                        expand_x=True,
                        expand_y=True,
                        enable_click_events=True,  # Comment out to not enable header and other clicks
                        )
        ],

        [
            sg.Button('Finish'),
            sg.Button('Cancel'),
            sg.Text('Cell clicked:'), 
            sg.T(key='-CLICKED_CELL-'),
        ]]


    t_window = sg.Window('Clickable Table Element', layout, resizable=True, finalize=True)
    row = None
    last_del_row = None
    last_del_data = None
    isOK = True
    error_widgets = []
    first_scan = True
    while True:
        #print()
        #highlight_cells(t_window, '-TABLE-', error_cells)
        if first_scan:
            false_event, false_values = t_window.read(timeout=100)
            highlight_cells(t_window, '-TABLE-')
            first_scan = False
        event, values = t_window.read()
        highlight_cells(t_window, '-TABLE-')

        if event in (sg.WIN_CLOSED, 'Finish', 'Cancel'):
            if event == 'Finish':
                if len(error_cells) > 0:
                    print('More edits to be made at')
                    for i in error_cells:
                        print(f'\t{i}')
                    popup = sg.popup_yes_no('More edits required.\nContinue anyway?', title='Close Table')
                    if popup == 'Yes':
                        break
                    continue
            if event == 'Cancel' or event==sg.WIN_CLOSED:
                isOK = False

            break
        # Checks if the event object is of tuple data type, indicating a click on a cell'
        elif isinstance(event, tuple):
            if isinstance(event[2][0], int) and event[2][0] > -1:
                cell = row, col = event[2]
                #print(row, col)
                # Displays that coordinates of the cell that was clicked on
                t_window['-CLICKED_CELL-'].update(cell)
                edit_cell(dataframe, t_window, '-TABLE-', row+1, col, justify='right')
        elif event == 'Add Row':
            new_row = {}
            for header in headings:
                new_row[header] = 'NULL'

            new_data_frame = pd.DataFrame(new_row, index=[0])
            dataframe = pd.concat([dataframe, new_data_frame], ignore_index=True)
            headings, data = get_dataframe_data(dataframe)
            t_window['-TABLE-'].update(values=data)
        elif event == 'Delete Row':
            if row is not None:
                last_del_data = dataframe.iloc[row]
                last_del_row = row
                dataframe = dataframe.drop(row)
                dataframe = dataframe.sort_index().reset_index(drop=True)
                headings, data = get_dataframe_data(dataframe)
                t_window['-TABLE-'].update(values=data)
            else:
                print('No row selected')
                sg.popup_auto_close('No row selected')
        elif event == 'Undo Delete':
            if last_del_row is not None:
                dataframe.loc[last_del_row-0.5] = last_del_data
                dataframe = dataframe.sort_index().reset_index(drop=True)
                last_del_row = None
                last_del_data = None
                headings, data = get_dataframe_data(dataframe)
                t_window['-TABLE-'].update(values=data)
            else:
                print('No row deleted')
                sg.popup_auto_close('No row deleted')

        #ADD A RESIZE EVENT TO AUTOMATICALLY MOVE CANVAS
        elif event == '-Resize-':
            print('Table Resized')

    t_window.close()
    return dataframe, isOK
