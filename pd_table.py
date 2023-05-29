from tkinter import *
from pandastable import Table, config


class TableApp(Frame):
        """Basic test frame for the table"""

        def __init__(self, df, errors=None, parent=None):
            self.parent = parent
            self.errors = errors
            self.orig_df = df.copy()
            self.row_edit = 0
            self.col_edit = 0

            f = Frame(self.parent)
            f.pack(fill=BOTH,expand=1)

            self.table = pt = Table(f, dataframe=df,
                                    showtoolbar=True, showstatusbar=True)
            
            self.highlight_errors()
            pt.show()
            #set some options
            options = {'colheadercolor':'green'}
            config.apply_options(options, pt)
            pt.show()
            
            #To clear error highlighting
            self.table.bind('<FocusOut>', self.focus_out)
            self.table.bind('<FocusIn>', self.focus_in)

            return
        
        def highlight_errors(self):
            #highlight errors

            if self.errors == None:
                return
            for e in self.errors:
                self.table.setRowColors(rows=[e[0]],clr='#ed2939',cols=[e[1]])
        
        def focus_out(self, *args):
            #print(args)
            # print('Focus Out')
            # print('row', self.table.currentrow)
            # print('col', self.table.currentcol)

            self.row_edit = self.table.currentrow
            self.col_edit = self.table.currentcol

        def focus_in(self, *args):
            #print(args)
            # print('Focus IN')
            # print('row', self.table.currentrow)
            # print('col', self.table.currentcol)

            last_val = self.orig_df.iloc[self.row_edit, self.col_edit]
            cur_val = self.table.model.df.iloc[self.row_edit, self.col_edit]

            if str(cur_val) != str(last_val):
                self.table.setRowColors(rows=[self.row_edit], clr=self.table.cellbackgr, cols=[self.col_edit])

                try:
                    idx = self.errors.index([self.row_edit, self.col_edit])
                    self.errors.pop(idx)
                    #print(self.errors)
                except:
                    return

class popup_yes_no(Toplevel):

    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, *kwargs)
        # self.popup=Toplevel(root)
        self.title('Yes/No popup')
        self.response = False

        Label(self, text=text, font=('Arial', 14)).grid(row=0, columnspan=2, column=0, pady=20)

        Button(self, text='Yes', width=10, command=self.yes_clicked).grid(row=1, column=0, pady=20)
        Button(self, text='No', width=10, command=self.no_clicked).grid(row=1, column=1, pady=20)

    def yes_clicked(self, *args):
        #print('Yes Clicked')
        self.response = True
        self.destroy() 
        
    def no_clicked(self, *args):
       
        #print('No clicked')
        self.destroy()

def table_editor(root, df, errors, name='Table Window'):

    #ADD SAVE as PICKLE feature
    
    global isOK, top, errors_left
    isOK = False

    errors_left = errors
    def done_table():
        global isOK
        isOK = True

        if app.errors is None:
            top.destroy()
            return
        
        if len(app.errors) == 0:
            #isOK = True
            top.destroy()
            return
        else:
            print('Fix errors at:')
            for e in app.errors:
                print(f'\t{e}')

            popup = popup_yes_no('Errors Present! Continue anyway?', top)
            popup.wait_window()
            #print(popup.response)
            if popup.response:
                top.destroy()
    
    def cancel_table():
        global isOK
        isOK = False
        top.destroy()


    top= Toplevel(root)
    top.geometry("1000x750")
    top.title(name)

    app = TableApp(df, errors, top)

    done_btn = Button(top, text='Done', width=15, command=done_table)
    done_btn.pack(anchor='center')

    cancel_btn = Button(top, text='Cancel', width=15, command=cancel_table)
    cancel_btn.pack(after=done_btn, pady=5)

    top.wait_window()

    new_df = app.table.model.df
    return new_df, app.errors, isOK

if __name__ == '__main__':

    pass
    # win = Tk()
    # win.geometry("1500x750")
    # df = pd.read_pickle('testdf.pkl')

    # btn = Button(win, text='Run', command=lambda: run_table(df, win))
    # btn.pack(side='left')

    # win.mainloop()
    # app = TestApp()
    # app.mainloop()
    # print(app.table.model.df)