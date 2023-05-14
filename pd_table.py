from tkinter import *
from pandastable import Table, config


class TableApp(Frame):
        """Basic test frame for the table"""
        def __init__(self, df, parent=None):
            self.parent = parent
            f = Frame(self.parent)
            f.pack(fill=BOTH,expand=1)

            self.table = pt = Table(f, dataframe=df,
                                    showtoolbar=True, showstatusbar=True)
            pt.show()
            #set some options
            options = {'colheadercolor':'green'}
            config.apply_options(options, pt)
            pt.show()
            #print('here')
            return

def table_editor(root, df, errors):
    global isOK, top, errors_left
    isOK = False

    errors_left = errors
    def done_table():
        global isOK
        
        isOK = True
        if len(errors_left) == 0:
            #isOK = True
            top.destroy()
            return
        else:
            print('Fix errors at:')
            for e in errors_left:
                print(f'\t{e}')
            top.destroy()
    
    def cancel_table():
        global isOK
        isOK = False
        top.destroy()


    top= Toplevel(root)
    top.geometry("1000x750")
    top.title('Table Window')

    app = TableApp(df, top)

    #highlight errors
    for e in errors:
        app.table.setRowColors(rows=[e[0]],clr='#ed2939',cols=[e[1]])

    done_btn = Button(top, text='Done', width=15, command=done_table)
    done_btn.pack(anchor='center')

    cancel_btn = Button(top, text='Cancel', width=15, command=cancel_table)
    cancel_btn.pack(after=done_btn, pady=5)

    top.wait_window()

    new_df = app.table.model.df
    return new_df, isOK

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