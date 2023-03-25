import textractprettyprinter
import textractcaller
import pandas as pd
pd.options.mode.chained_assignment = None
from trp import Document
import numpy as np
from pdf2image import convert_from_path
from openpyxl import load_workbook
from textractcaller.t_call import call_textract, Textract_Features
from textractprettyprinter.t_pretty_print import convert_table_to_list
import pickle
from fpdf import FPDF
from dateutil.parser import ParserError
import table_editor as te
import boto3
from botocore.config import Config


# Scanning pngs using Textract
def extract_data(input_document):
    pages = convert_from_path(input_document,
                              poppler_path=r"C:\Users\jakeh\poppler-0.68.0_x86\poppler-0.68.0\bin")
    dfs = list()
    client = boto3.client("textract", config=Config(connect_timeout=6000))
    for i, page in enumerate(pages):
        # if i != 0:
            page.save("out" + str(i) + ".png", "PNG")
            resp = call_textract(input_document="out" + str(i) + ".png", features=[Textract_Features.TABLES], boto3_textract_client=client)
            tdoc = Document(resp)
            dfs.append(pd.DataFrame(convert_table_to_list(trp_table=tdoc.pages[0].tables[0])))

    return pd.concat(dfs)


# Data Cleaning
def general_clean(df1):
    df1.reset_index(drop=True, inplace=True)
    df1 = df1.applymap(lambda x: x.strip() if type(x) == str else x)
    df1.drop(df1[df1[0] == ''].index, inplace=True)
    df1.reset_index(drop=True, inplace=True)
    df1.rename(columns=df1.iloc[0], inplace=True)
    df1.replace('', np.NaN, inplace=True)
    df1.columns = df1.columns.str.strip()
    df1.drop(df1[df1['Sow ID'] == 'Sow ID'].index, inplace=True)
    df1.reset_index(drop=True, inplace=True)
    return df1


# Convert date columns to datetime data type
def convert_to_date(df1, column_list):
    dates_error_list = []
    for x in column_list:
        for i, value in enumerate(df1[x]):
            try:
                df1.at[i, x] = pd.to_datetime(value, format="%m%d%y")
            except ParserError as pe:
                dates_error_list.append([i,x])
                # print(value, "is causing an error in column", x, "and is in row", i)
                # df1.at[i, x] = input("What would you like to change this value to? ") + "23"
            except ValueError as e:
                dates_error_list.append([i,x])
                # print(value, "is causing an error in column", x, "and is in row", i)
                # df1.at[i, x] = input("What would you like to change this value to? ") + "23"
            # except:
            #     print("Hello")
        # df1[x] = pd.to_datetime(df1[x]).dt.date
    return df1, dates_error_list


def convert_to_numeric(df1, columns_list):
    numeric_error_list=[]
    for x in columns_list:
        for i, value in enumerate(df1[x]):
            try:
                df1.at[i, x] = pd.to_numeric(value)
            except ParserError as pe:
                numeric_error_list.append([i,x])
                # print(value, "is causing an error in column", x, "and is in row", i)
                # df1.at[i, x] = input("What would you like to change this value to? ")
            except ValueError as e:
                numeric_error_list.append([i,x])
                # print(value, "is causing an error in column", x, "and is in row", i)
                # df1.at[i, x] = input("What would you like to change this value to? ")


        # df1[x] = pd.to_numeric(df1[x], downcast='unsigned')

    return df1, numeric_error_list


def fill_table(df1):
    #     for i in range (0,len(df1)):
    #         if pd.isna(df1.at[i,"Last Weaned"]) and pd.notna(df1.at[i,"Date Bred1"]):
    #             df1.at[i,"Last Weaned"]=df1.at[i-1,"Last Weaned"]

    for i in range(0, len(df1)):
        if pd.isna(df1.at[i, "Date Weaned"]) and pd.notna(df1.at[i, "Date Farrowed"]):
            df1.at[i, "Date Weaned"] = df1.at[i - 1, "Date Weaned"]

        for count in range (1,4):
            for i in range (0,len(df1)):
                if pd.isna(df1.at[i,"Breeder"+str(count)]) and pd.notna(df1.at[i,"HC"+str(count)]):
                    df1.at[i,"Breeder"+str(count)]=df1.at[i,"HC"+str(count)]
    # Waiting to get more info

    return df1


def check_all_values(df1, dates_list):
    not_done = True
    while not_done:
        print(df1.to_string())
        r = input("What is the row? ")
        if r == 'd':
            not_done = False
        else:
            c = input("What is the column? ")
            if c in dates_list:
                df1.at[int(r), c] = input("What would you like this value to be? ") + "23"
                df1[c] = pd.to_datetime(df1[c]).dt.date
            else:
                df1.at[int(r), c] = input("What would you like this value to be? ")

    return df1


def farrowing_clean(df1):
    df1 = general_clean(df1)
    dict = {"\\": "1", "I": "1", "o": "0", "O": "0", "&": "9", "a": "9"}
    df1.replace({"P": dict, "#S": dict, "#M": dict, "#L": dict, "#W": dict}, inplace=True)

    dates_list = ["Date Farrowed", "Date Weaned"]
    df1[dates_list] += "23"
    # df1, error_list = convert_to_date(df1, dates_list)

    numeric_list = ["Crate#", "Parity", "#Live", "#Still", "#Mum", "#Weaned"]
    # df1, error_list1 = convert_to_numeric(df1, numeric_list)

    t_data = te.table_editor(df1)
    print(t_data)

    # Final check
    # df1 = check_all_values(df1, dates_list)

    # code_dict = {22: "Savaged", 21: "Ruptures", 27: "Starvation"}
    # for key in [1, 13, 20, 26]:
    #     code_dict[key] = "Low Viability"
    # for key in [10, 12, 28]:
    #     code_dict[key] = "Laid On"
    # for key in [23, 30]:
    #     code_dict[key] = "Strep"
    # for key in [2, 3, 7, 9, 15, 25, 31]:
    #     code_dict[key] = "Other"
    # Convert codes to columns
    # df1["Low Viability"] = 0
    # df1["Laid On"] = 0
    # df1["Strep"] = 0
    # df1["Scours"] = 0
    # df1["Other"] = 0
    # df1["Savaged"] = 0
    # df1["Ruptures"] = 0
    # df1["Starvation"] = 0
    # for i in range(1, 5):
    #     for count, x in enumerate(df1["Cause" + str(i)]):
    #         is_num_deaths = True
    #         num_deaths = []
    #         death_code = []
    #         if pd.notna(x):
    #             for j in x:
    #                 if j == '-':
    #                     is_num_deaths = False
    #
    #                 elif is_num_deaths:
    #                     num_deaths.append(j)
    #
    #                 else:
    #                     death_code.append(j)
    #
    #             deaths = ''.join(num_deaths)
    #             code = ''.join(death_code)
    #             df1.at[count, code_dict[int(code)]] = int(deaths)
    #     df1.drop("Cause" + str(i), axis=1, inplace=True)
    return t_data


def breeding_clean(df1):
    df1 = general_clean(df1)
    df1.replace({'AL': 'AC', 'BL': 'BV', 'PV': 'BV', 'B': 'BV', 'A': 'AC', 'H': 'HR',"C":"CJ"}, inplace=True)
    dates_list = ["Date Bred" + str(i) for i in range(1, 4)]
    df1[dates_list] += "23"

    # df1, error_list = convert_to_date(df1, dates_list)
    t_data = te.table_editor(df1)
    print(t_data)

    # Final check
    # df1 = check_all_values(df1, dates_list)

    return t_data


def generate_report(df1, df2):
    df3 = df1.merge(df2, how='outer', on="Sow ID")
    df3 = fill_table(df3)
    group_num = input("What group are you inputting? ")
    df3["Group Number"] = int(group_num)
    pdf = FPDF()

    pdf.output("Group" + group_num + " Report.pdf")

