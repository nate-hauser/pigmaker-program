import PySimpleGUI as sg
import pandas as pd


def get_dataframe_data(dataframe):
    table_headers = dataframe.columns
    table_headers = table_headers.values
    table_values = dataframe.to_numpy()
    data = table_values.tolist()
    headings = list(table_headers)
    return headings, data

def highlight_cell(t_window, key, row, col):
    root = t_window.TKroot
    print(root)
    # Gets the Widget object from the PySimpleGUI table - a PySimpleGUI table is really
    # what's called a TreeView widget in TKinter
    table = t_window[key].Widget
    # Return x and y position of cell as well as width and height (in TreeView widget)
    x, y, width, height = table.bbox(row, col)
    print(x,y)
    x_offset = 5
    y_offset = 35
    x+= x_offset+width-20
    y+= y_offset
    tri_points = [0,0,width,height]
    # i = 0
    # while i < len(tri_points):
    #     if i % 2 == 0:
    #         tri_points[i]+= x
    #     else:
    #         tri_points[i]+= y
    #     i+= 1
    triangle = sg.tk.Canvas(root)
    triangle.create_rectangle(tri_points, fill='red')
    triangle.place(x=x, y=y)
    #triangle.pack()

    

# TKinter function to display and edit value in cell
def edit_cell(dataframe, t_window, key, row, col, justify='left'):

    global textvariable, edit, new_error_loc

    def callback(event, row, col, text, key, dataframe):
        global edit, new_error_loc
        # event.widget gives you the same entry widget we created earlier
        widget = event.widget
        if key == 'Focus_Out':
            # Get new text that has been typed into widget
            text = widget.get()
            # Print to terminal
            print(text)
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
        i = 0
        pos = [row-1, col]
        while i < len(new_error_loc):
            if pos[0] == new_error_loc[i][0] and pos[1] == new_error_loc[i][1]:
                new_error_loc.pop(i)
                #print('Delete')
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
    print(x,y)
    x_offset = 5
    y_offset = 35
    x+= x_offset
    y+= y_offset

    # Create a new container that acts as container for the editable text input widget
    frame = sg.tk.Frame(root)
    # put frame in same location as selected cell
    frame.place(x=x, y=y, anchor='nw', width=width, height=height)

    # textvariable represents a text value
    textvariable = sg.tk.StringVar()
    textvariable.set(text)
    # Used to acceot single line text input from user - editable text input
    # frame is the parent t_window, textvariable is the initial value, justify is the position
    entry = sg.tk.Entry(frame, textvariable=textvariable, justify=justify, font=28)
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

def table_editor(dataframe, error_loc):
    global edit
    global new_error_loc

    edit = False
    new_error_loc = error_loc
    headings, data = get_dataframe_data(dataframe)

    #headings, data = generate_table_data()
    sg.set_options(dpi_awareness=True)
    layout = [[
            sg.Button('Add Row'),
            sg.Button('Delete Row'),
            sg.Button('Undo Delete')
        ],
        [
            sg.Table(values=data, headings=headings, max_col_width=25,
                        font=("Arial", 20),
                        auto_size_columns=True,
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
    while True:
        #print()
        event, values = t_window.read()
        #highlight_cell(t_window, '-TABLE-', new_error_loc[0], new_error_loc[1])
        if event in (sg.WIN_CLOSED, 'Finish', 'Cancel'):
            #t_window.refresh()
            if event == 'Finish':
                if len(new_error_loc) > 0:
                    print('More edits to be made at')
                    for i in new_error_loc:
                        print(f'\t{i}')
                    #ADD PROMPT FOR CONTINUE ANYWAY
                    continue
            
            #ADD LOGIC FOR CANCEL

            break
        # Checks if the event object is of tuple data type, indicating a click on a cell'
        elif isinstance(event, tuple):
            if isinstance(event[2][0], int) and event[2][0] > -1:
                cell = row, col = event[2]
                print(row)

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

    t_window.close()
    return dataframe
