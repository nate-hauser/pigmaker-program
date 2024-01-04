import pandas as pd

pd.options.mode.chained_assignment = None
from trp import Document
import numpy as np
from pdf2image import convert_from_path
from fpdf import FPDF
from textractcaller.t_call import call_textract, Textract_Features
from textractprettyprinter.t_pretty_print import convert_table_to_list
from dateutil.parser import ParserError
import boto3
from botocore.config import Config
from datetime import timedelta
import tempfile
import os
import io
import pickle

CODE_DICT = {22: "Savaged", 21: "Ruptures", 27: "Starvation"}
for key in [1, 13, 20, 26]:
    CODE_DICT[key] = "Low Viability"
for key in [10, 12, 28]:
    CODE_DICT[key] = "Laid On"
for key in [23, 30]:
    CODE_DICT[key] = "Strep"
for key in [2, 3, 7, 9, 15, 25, 31]:
    CODE_DICT[key] = "Other"

DOWNLOADS_DIRECTORY = os.path.expanduser(r"~\\Downloads")
RAW_RECORDS_DIRECTORY = os.path.join(DOWNLOADS_DIRECTORY,"PigmakerProgram","Raw_Records")
BREEDING_FARROWING_RECORDS_DIRECTORY = os.path.join(DOWNLOADS_DIRECTORY, "PigmakerProgram", "Breeding_Farrowing_Records")
GROUP_RECORDS_DIRECTORY = os.path.join(DOWNLOADS_DIRECTORY, "PigmakerProgram", "Group_Records")
REPORTS_DIRECTORY = os.path.join(DOWNLOADS_DIRECTORY,"PigmakerProgram","Reports")
MASTER_DATABASE = os.path.join(DOWNLOADS_DIRECTORY,"PigmakerProgram","PigmakerDB.xlsx")


def extract_data(input_document):
    """Converts the pdf to a png and then to a pandas dataframe using AWS textract"""

    with tempfile.TemporaryDirectory() as temp_dir:
        pages = convert_from_path(input_document, output_folder=temp_dir,
                                  poppler_path=r"poppler-0.68.0_x86\poppler-0.68.0\bin")
        dfs = list()
        client = boto3.client("textract", config=Config(connect_timeout=6000))
        for i, page in enumerate(pages):
            image_io = io.BytesIO()
            page.save(image_io, format="PNG")
            image_io.seek(0)  # Reset the stream position to the beginning
            resp = call_textract(input_document=image_io.read(), features=[Textract_Features.TABLES],
                                 boto3_textract_client=client)
            tdoc = Document(resp)
            dfs.append(pd.DataFrame(convert_table_to_list(trp_table=tdoc.pages[0].tables[0])))
            print("Page"+str(i+1)+"done")

    return pd.concat(dfs)


# def extract_data2(input_document):
#     pages = convert_from_path(input_document,
#                               poppler_path=r"C:\Users\jakeh\poppler-0.68.0_x86\poppler-0.68.0\bin")
#     dfs = pd.DataFrame()
#     for i, page in enumerate(pages):
#         page.save("out" + str(i) + ".png", "PNG")
#         print(pytesseract.image_to_data(Image.open('out' + str(i) + ".png"), output_type='data.frame').to_string())
#
#     return dfs
#
#
# def extract_data3(input_document):
#     pdf = PDF(src=input_document)
#
#     ocr = TesseractOCR(lang="eng")
#
#     pdf_tables = pdf.extract_tables(ocr=ocr)
#     for i in pdf_tables:
#         print(i.to_string())


def general_clean(df1):
    """Performs data cleaning that is common to both breeding and farrowing"""

    df1.reset_index(drop=True, inplace=True)
    df1.drop(df1[(df1[0] == '')].index, inplace=True)
    # df1 = df1.applymap(lambda x: x.strip() if type(x) == str else x)
    df1.iloc[0] = df1.iloc[0].str.strip()
    # df1.replace("NOT_SELECTED,",np.NaN,inplace=True)
    df1.rename(columns=df1.iloc[0], inplace=True)
    df1.rename(columns={'': "Crate#"}, inplace=True)
    # df1.drop(df1[(df1['Sow ID'] == '')].index, inplace=True)
    # df1 = df1.dropna(subset=['Sow ID'])
    df1.reset_index(drop=True, inplace=True)
    # df1.columns = df1.columns.str.strip()
    df1.drop(df1[df1['Sow ID'] == 'Sow ID'].index, inplace=True)
    df1.replace('', np.NaN, inplace=True)
    # df1.reset_index(drop=True, inplace=True)
    df1 = df1.applymap(lambda x: x.replace(" ","") if type(x) == str else x)
    df1.drop(df1[df1['Sow ID'] == 'SowID'].index, inplace=True)
    df1.reset_index(drop=True, inplace=True)
    df1 = df1.dropna(subset=["Sow ID"])
    df1.reset_index(drop=True, inplace=True)
    return df1


def convert_to_date(df1, column_list, start_end_dates):
    """Converts values from string to pandas date format"""

    for x in column_list:
        possible_dates, possible_days, four_digit_dates = generate_possible_dates(x, start_end_dates)
        for i, value in enumerate(df1[x]):
            if pd.notna(value):
                value = str(value)
                if len(value) <= 2:
                    converted_value_location = possible_days.index(int(value))
                    df1.at[i, x] = possible_dates[converted_value_location]
                elif len(value) == 4:
                    converted_value_location = four_digit_dates.index(value)
                    df1.at[i, x] = possible_dates[converted_value_location]

        # else:
        #     for i, value in enumerate(df1[x]):
        #         df1.at[i, x] = pd.to_datetime(value).date()

    return df1


def convert_to_numeric(df1, columns_list):
    """Converts value from string to pandas numeric"""

    for x in columns_list:
        for i, value in enumerate(df1[x]):
            df1.at[i, x] = pd.to_numeric(value)

    return df1


def produce_numeric_errors(df, cols_list):
    """Produces errors on values that cannot be converted to numeric"""

    numeric_error_list = []
    for x in cols_list:
        for i, value in enumerate(df[x]):
            try:
                pd.to_numeric(value)
                if x in ["P", "#L", "#S", "#M", "#W"] and value == value and int(value) >= 30:
                    numeric_error_list.append([i, df.columns.get_loc(x)])

            except ParserError as pe:
                numeric_error_list.append([i, df.columns.get_loc(x)])

            except ValueError as e:
                numeric_error_list.append([i, df.columns.get_loc(x)])

    return numeric_error_list


def generate_possible_dates(col, start_end_dates):
    """Given the start and end dates for specified columns, function will generate all valid dates and days that are
     within the date ranges"""

    if "Bred" in col:
        start = pd.to_datetime(start_end_dates["breed start"]).date()
        end = pd.to_datetime(start_end_dates["breed end"]).date()
    elif "Date F" in col:
        start = pd.to_datetime(start_end_dates["farrow start"]).date()
        end = pd.to_datetime(start_end_dates["farrow end"]).date()

    elif col == "LW":
        start = pd.to_datetime(start_end_dates["breed end"]).date() - timedelta(days=365)
        end = pd.to_datetime(start_end_dates["breed end"]).date() - timedelta(days=1)
    else:
        start = pd.to_datetime(start_end_dates["wean start"]).date()
        end = pd.to_datetime(start_end_dates["wean end"]).date()

    possible_dates = []
    num_days = (end - start).days

    for i in range(num_days + 1):
        possible_dates.append(start + timedelta(days=i))

    possible_days = [y.day for y in possible_dates]

    four_digit_dates = [str(y.month) + str(y.day) if len(str(y.day)) == 2 else str(y.month) + "0" + str(y.day) for y in
                        possible_dates]
    four_digit_dates = [y if len(y) == 4 else "0" + y for y in four_digit_dates]

    return possible_dates, possible_days, four_digit_dates


def produce_date_errors(df, cols_list, start_end_dates):
    """Produces errors on invalid dates or on dates that are outside the specified start and end dates"""

    dates_error_list = []
    for x in cols_list:

        possible_dates, possible_days, four_digit_dates = generate_possible_dates(x, start_end_dates)

        for i, value in enumerate(df[x]):
            try:
                if pd.notna(value):
                    if "/" in str(value):
                        value = str(value).partition("/")[2]
                        df.at[i,x] = value
                    if len(value) <= 2:
                        if not int(value) in possible_days:
                            dates_error_list.append([i, df.columns.get_loc(x)])

                    elif len(value) == 4:
                        if not value in four_digit_dates:
                            dates_error_list.append([i, df.columns.get_loc(x)])

                    else:
                        dates_error_list.append([i, df.columns.get_loc(x)])

            except ParserError as pe:
                dates_error_list.append([i, df.columns.get_loc(x)])
            except ValueError as e:
                dates_error_list.append([i, df.columns.get_loc(x)])
        # else:
        #     for i, value in enumerate(df[x]):
        #         try:
        #             if pd.notna(value):
        #
        #                 pd.to_datetime(value)
        #
        #         except ValueError as e:
        #             dates_error_list.append([i, df.columns.get_loc(x)])

    return dates_error_list


def fill_table(df1):
    """Autofills the Date Weaned and Breeder columns"""

    for i in range(0, len(df1)):
        if pd.isna(df1.at[i, "Date W"]) and pd.notna(df1.at[i, "Date F"]):
            df1.at[i, "Date W"] = df1.at[i - 1, "Date W"]

        if pd.isna(df1.at[i,"Crate#"]) and pd.notna(df1.at[i,"Date F"]):
            df1.at[i,"Crate#"] = df1.at[i-1,"Crate#"] + 1

        for count in range(1, 4):
            for x in range(0, len(df1)):
                if pd.isna(df1.at[x, "Breeder" + str(count)]) and pd.notna(df1.at[x, "HC" + str(count)]):
                    df1.at[x, "Breeder" + str(count)] = df1.at[x, "HC" + str(count)]

        if i != 0 and pd.isna(df1.at[i,"LW"]):
            df1.at[i,"LW"] = df1.at[i-1,"LW"]


    # Waiting to get more info

    return df1


def breed_produce_errors(df1, start_end_dates):
    """Produces date, and Sow ID errors on the breeding dataframe"""

    df1.replace({"NOT_SELECTED,": np.NaN}, inplace=True)

    dates_cols_list = ["Date Bred1", "Date Bred2", "Date Bred3","LW"]
    breeder_hc_cols = ["HC1", "Breeder1", "HC2", "Breeder2", "HC3", "Breeder3"]
    breeder_list = ["BV", "AC", "CJ", "HR", "JS", "J", "NS","GH","TW"]
    df1[breeder_hc_cols] = df1[breeder_hc_cols].applymap(lambda x: x.upper() if isinstance(x, str) else x)

    with open("breeders.pkl", 'rb') as file:
        breeders = (pickle.load(file))

    breeders_replace_dict = {}
    for breeder in breeders:
        first_initial = breeder[0]
        breeders_replace_dict[first_initial] = breeder

    breeders_replace_dict.update({"AL":"AC","BL":"BV","PV":"BV","P":"BV","8":"BV","LT":"HR","3":"BV","IT":"HR","F":"BV",
                                  "3V":"BV","BU":"BV","BR":"BV","4C":"AC","4":"AC","IS":"BV","13":"BV","R":"BV","5":"BV"})
    df1[breeder_hc_cols] = df1[breeder_hc_cols].replace(breeders_replace_dict)
    df1[dates_cols_list] = df1[dates_cols_list].replace(
        {"1b": "16", "1>": "17", "lb": "16", "1)": "17", "lt": "16", "It": "16",'\\': "1","/":"1","l":"1","I":"1"})

    error_list = []

    for x in breeder_hc_cols:
        for i, value in enumerate(df1[x]):
            if value not in breeder_list and pd.notna(value):
                error_list.append([i, df1.columns.get_loc(x)])

    error_list.extend(produce_date_errors(df1, dates_cols_list, start_end_dates))
    error_list.extend(produce_sow_id_errors(df1))


    return error_list


def farrow_produce_errors(df1, start_end_dates):
    """Produces code, numeric, date, and Sow ID errors on the farrowing dataframe"""

    dates_cols_list = ["Date F", "Date W"]
    numeric_cols_list = ["Crate#", "P", "#L", "#S", "#M", "#W"]
    error_dict = {"\\": "1", "I": "1", "o": "0", "O": "0", "&": "9", "a": "9", "/": "1","L":"1","l":"1","i":"1","(":"1",")":"1"}
    df1[numeric_cols_list] = df1[numeric_cols_list].replace(error_dict)
    error_list = []
    for i in range(1, 5):
        for count, x in enumerate(df1["C" + str(i)]):
            is_num_deaths = True
            num_deaths = []
            death_code = []
            if pd.notna(x):
                for j in x:
                    if j == '-' or j == '/':
                        is_num_deaths = False

                    elif is_num_deaths:
                        num_deaths.append(j)

                    else:
                        death_code.append(j)

                deaths = ''.join(num_deaths)
                code = ''.join(death_code)
                try:
                    if int(code) not in CODE_DICT.keys() or not deaths.isdigit():
                        error_list.append([count, df1.columns.get_loc("C" + str(i))])
                except ValueError:
                    error_list.append([count, df1.columns.get_loc("C" + str(i))])

    error_list.extend(produce_date_errors(df1, dates_cols_list, start_end_dates))
    error_list.extend(produce_numeric_errors(df1, numeric_cols_list))
    error_list.extend(produce_sow_id_errors(df1))


    return error_list


def produce_sow_id_errors(df):
    """Produces errors for the Sow ID column. Will produce error if value has non-Alphanumeric characters or lower-case
    letters"""

    error_list = []
    for i, value in enumerate(df["Sow ID"]):
        if not value.isalnum() or not value.isupper() and not value.isdigit():
            error_list.append([i, df.columns.get_loc("Sow ID")])

    return error_list


def pdf_to_breed(filepath, group_num):
    """Takes a pdf of breeding information and converts to a dataframe"""

    df = extract_data(filepath)
    raw_record_path = os.path.join(RAW_RECORDS_DIRECTORY,"raw_breeding"+str(group_num)+".pkl")
    df.to_pickle(raw_record_path)
    df = general_clean(df)

    return df


def pdf_to_farrow(filepath, group_num):
    """Takes a pdf of farrowing information and converts to a dataframe"""

    df = extract_data(filepath)
    raw_record_path = os.path.join(RAW_RECORDS_DIRECTORY,"raw_farrowing"+str(group_num)+".pkl")
    df.to_pickle(raw_record_path)
    df = general_clean(df)

    return df


def pre_report_processing(df1, df2, start_end_dates, group_num):
    """ Converts columns to their correct data type and merges the farrow and breed dataframes on Sow ID"""

    df1 = convert_to_date(df1, ["Date Bred1", "Date Bred2", "Date Bred3", "LW"], start_end_dates)
    df2 = convert_to_date(df2, ["Date F", "Date W"], start_end_dates)
    df2 = convert_to_numeric(df2, ["Crate#", "P", "#L", "#S", "#M", "#W"])

    df2["Low Viability"] = 0
    df2["Laid On"] = 0
    df2["Strep"] = 0
    df2["Scours"] = 0
    df2["Other"] = 0
    df2["Savaged"] = 0
    df2["Ruptures"] = 0
    df2["Starvation"] = 0
    df2["Unknown"] = 0
    for i in range(1, 5):
        for count, x in enumerate(df2["C" + str(i)]):
            is_num_deaths = True
            num_deaths = []
            death_code = []
            if pd.notna(x):
                for j in x:
                    if j == '-' or j == '/':
                        is_num_deaths = False

                    elif is_num_deaths:
                        num_deaths.append(j)

                    else:
                        death_code.append(j)

                deaths = ''.join(num_deaths)
                code = ''.join(death_code)
                df2.at[count, CODE_DICT[int(code)]] += int(deaths)
        df2.drop("C" + str(i), axis=1, inplace=True)

    df2[["#L", "#S", "#M", "#W","P"]] = df2[["#L", "#S", "#M", "#W","P"]].replace(np.NaN, 0)


    df3 = df2.merge(df1, how='outer', on="Sow ID")
    df3 = fill_table(df3)
    df3["Group Number"] = int(group_num)

    return df3


def generate_report(df3, group_num, total_weaned):
    """Takes the merged dataframe and generates a report"""

    length = len(df3)
    total_weaned = int(total_weaned)

    # Calculate difference between total born live and total dead. This should equal the total weaned
    diff = df3["#L"].sum() - (
            df3["Low Viability"].sum() + df3["Laid On"].sum() + df3["Strep"].sum() + df3["Scours"].sum()
            + df3["Other"].sum() + df3["Savaged"].sum() + df3["Ruptures"].sum() + df3["Starvation"].sum())

    print(diff)
    print(df3["#L"].sum())


    diff2 = total_weaned - df3["#W"].sum()
    diff3 = diff - total_weaned
    df3 = pd.concat(
        [df3, pd.DataFrame([{"Sow ID": "Y", "Unknown": diff3, "#W":diff2, "Group Number": group_num}])],
        ignore_index=True)

    # print(df3["#L"].sum()-df3["#W"].sum())
    # print(df3["Low Viability"].sum() + df3["Laid On"].sum() + df3["Strep"].sum() + df3["Scours"].sum()
    #                    + df3["Other"].sum() + df3["Savaged"].sum() + df3["Ruptures"].sum() + df3["Starvation"].sum() +df3["Unknown"].sum())
    pdf = FPDF()
    pdf.add_page()

    # Prints report heading
    pdf.set_font("Times", "B", 25)
    pdf.cell(0, 0, "Group " + group_num + " Pigmaker Report", 0, 2, "C")

    mode = df3["Date W"].mode()[0].strftime("%m-%d-%Y")
    pdf.set_y(27)
    pdf.cell(0, 0, str(mode), 0, 2, 'C')

    CELL_WIDTH = 49
    CELL_HEIGHT = 8

    # Calculate separate statistics for rooms 1-6 and 8-12

    Half1 = df3[df3["Crate#"] < 700]
    Half2 = df3[df3["Crate#"] >= 800]

    def make_farrowing_statistics_table(dfs: list):

        """Produces farrowing statistics table given list of dataframes"""

        pdf.set_font("Times", 'B', 15)

        pdf.set_y(40)

        pdf.cell(CELL_WIDTH, CELL_HEIGHT, "Statistic", 1, 0, 'C')
        pdf.cell(CELL_WIDTH, CELL_HEIGHT, "Rooms 1-6", 1, 0, 'C')
        pdf.cell(CELL_WIDTH, CELL_HEIGHT, "Rooms 8-12", 1, 0, 'C')
        pdf.cell(CELL_WIDTH, CELL_HEIGHT, "Overall", 1, 1, 'C')

        pdf.set_font("Times", '', 12)

        pdf.cell(CELL_WIDTH, CELL_HEIGHT, "Total born per litter", 1, 1, 'C')
        pdf.cell(CELL_WIDTH, CELL_HEIGHT, "Still birth rate", 1, 1, 'C')
        pdf.cell(CELL_WIDTH, CELL_HEIGHT, "Mum birth rate", 1, 1, 'C')
        pdf.cell(CELL_WIDTH, CELL_HEIGHT, "Born live per litter", 1, 1, 'C')
        pdf.cell(CELL_WIDTH, CELL_HEIGHT, "Weaned per litter", 1, 1, 'C')
        pdf.cell(CELL_WIDTH, CELL_HEIGHT, "Pre-weaning mortality rate", 1, 1, 'C')

        pdf.set_xy(59, 48)

        for df in dfs:
            num_farrowed = df["Date F"].count()

            total_born = round(((df["#S"].sum() + df["#M"].sum() + df["#L"].sum()) / num_farrowed), 2)
            pdf.cell(CELL_WIDTH, CELL_HEIGHT, str(total_born), 1, 2, 'C')

            still_rate = df["#S"].sum() / (total_born * num_farrowed)
            pdf.cell(CELL_WIDTH, CELL_HEIGHT, "{:.2%}".format(still_rate), 1, 2, 'C')

            mum_rate = df["#M"].sum() / (total_born * num_farrowed)
            pdf.cell(CELL_WIDTH, CELL_HEIGHT, "{:.2%}".format(mum_rate), 1, 2, 'C')

            live_per_litter = round(df["#L"].sum() / num_farrowed, 2)
            pdf.cell(CELL_WIDTH, CELL_HEIGHT, str(live_per_litter), 1, 2, 'C')

            weaned_per_litter = round(df["#W"].sum() / num_farrowed, 2)
            pdf.cell(CELL_WIDTH, CELL_HEIGHT, str(weaned_per_litter), 1, 2, 'C')

            preweaning_mortality = (df["Low Viability"].sum() + df["Laid On"].sum() + df["Strep"].sum() + df[
                "Scours"].sum() + df["Other"].sum() + df["Savaged"].sum() + df["Ruptures"].sum() + df[
                                        "Starvation"].sum() + df["Unknown"].sum()) / df["#L"].sum()
            pdf.cell(CELL_WIDTH, CELL_HEIGHT, "{:.2%}".format(preweaning_mortality), 1, 0, 'C')

            pdf.set_xy(pdf.get_x(), 48)

    make_farrowing_statistics_table([Half1, Half2, df3])

    pdf.set_xy(10, 105)

    combo = df3.copy()

    def generate_combos(cols):

        """Generate unique combinations given three columns"""

        combo["combo"] = combo.apply(lambda row: list({row[cols[0]], row[cols[1]], row[cols[2]]}), axis=1)
        combo["combo"] = combo["combo"].apply(lambda x: [i for i in x if not (pd.isna(i) or i is None)]).astype(
            'object')
        combo["combo"] = combo["combo"].apply(tuple)
        combo_groupby = combo.groupby(by="combo").agg({'#S': 'sum',
                                                       '#M': 'sum',
                                                       '#L': 'sum',
                                                       'Group Number': 'count',
                                                       'Date F': 'count'})

        return combo_groupby

    def make_combo_table(df, name):

        """Output table of statistics per combination to pdf report"""

        df["Farrowing rate"] = df["Date F"] / df["Group Number"]
        df["Total born"] = df["#S"] + df["#M"] + df["#L"]
        df = df.sort_values(by="Farrowing rate", ascending=False)

        pdf.set_font('Times', 'B', 12)

        pdf.cell(CELL_WIDTH, CELL_HEIGHT, name + " combination", 1, 0, 'C')
        pdf.cell(CELL_WIDTH, CELL_HEIGHT, "Total born per litter", 1, 0, 'C')
        pdf.cell(CELL_WIDTH, CELL_HEIGHT, "Farrowing rate", 1, 0, 'C')
        pdf.cell(CELL_WIDTH, CELL_HEIGHT, "Count", 1, 1, 'C')

        pdf.set_font('Times', '', 12)

        for i in df.index:
            if i == ():
                pdf.cell(CELL_WIDTH, CELL_HEIGHT, "Unknown", 1, 0, 'C')
            else:
                pdf.cell(CELL_WIDTH, CELL_HEIGHT, str(', '.join(sorted(i))), 1, 0, 'C')

            if df.at[i, "Date F"] == 0:
                pdf.cell(CELL_WIDTH, CELL_HEIGHT, "NA", 1, 0, 'C')
            else:
                pdf.cell(CELL_WIDTH, CELL_HEIGHT, str(round(df.at[i, "Total born"] / df.at[i, "Date F"], 2)), 1,
                         0, 'C')
            pdf.cell(CELL_WIDTH, CELL_HEIGHT, "{:.2%}".format(df.at[i, "Farrowing rate"]), 1, 0, 'C')
            pdf.cell(CELL_WIDTH, CELL_HEIGHT, str(df.at[i, "Group Number"]), 1, 1, 'C')

    heat_checker_combos = generate_combos(["HC1", "HC2", "HC3"])

    # nonbred_pigs = int(heat_checker_combos.at[(),"Group Number"])

    num_farrowed = df3["Date F"].count()
    farrowing_rate = num_farrowed / (length)

    # Making comments underneath farrowing statistics table
    pdf.cell(0, 10, "*The overall farrowing rate is: " + "{:.2%}".format(farrowing_rate) + " (" + str(
        num_farrowed) + " out of " + str(length) + ")", 0, 1, 'L')

    weaned_pigs = df3["#W"].sum()
    pdf.cell(0, 10, "*The total number of weaned pigs is " + str(weaned_pigs), 0, 1, 'L')

    pdf.multi_cell(0,10, "*" + str(diff2) + " weaned pigs were added to sow 'Y'",0, 'L')

    pdf.multi_cell(0, 10, "*" + str(diff3) +
                       " unknown deaths were added to imaginary sow 'Y' to make the total born live minus the total dead equal the total weaned",
                       0, 'L')

    pdf.set_y(pdf.get_y()+5)

    heat_checker_combos = generate_combos(["HC1", "HC2", "HC3"])

    make_combo_table(heat_checker_combos, "Heat checker")

    pdf.set_y(pdf.get_y() + 10)

    def make_table_by_individual(df, name):

        """Outputs table of statistics for each individual heat checker or breeder to pdf report"""

        pdf.set_font('Times', 'B', 12)
        pdf.cell(CELL_WIDTH, CELL_HEIGHT, "Individual " + name, 1, 0, 'C')
        pdf.cell(CELL_WIDTH, CELL_HEIGHT, "Total born per litter", 1, 0, 'C')
        pdf.cell(CELL_WIDTH, CELL_HEIGHT, "Farrowing rate", 1, 0, 'C')
        pdf.cell(CELL_WIDTH, CELL_HEIGHT, "Count", 1, 1, 'C')

        pdf.set_font('Times', '', 12)

        v = []
        for i in df.index:
            v.extend(i)

        v = list(set(v))
        dfl = {}
        for i in v:
            i_df = df[df.index.map(lambda tpl: any(str(i) in elem for elem in tpl))]
            dfl[str(i)] = (i_df["Date F"].sum() / i_df["Group Number"].sum())

        sorted_dfl = sorted(dfl.items(), key=lambda kv: kv[1], reverse=True)
        workers = []
        for worker, farrowing_rate in sorted_dfl:
            workers.append(worker)
        for i in workers:
            i_df = df[df.index.map(lambda tpl: any(str(i) in elem for elem in tpl))]
            pdf.cell(CELL_WIDTH, CELL_HEIGHT, str(i), 1, 0, 'C')
            if i_df["Date F"].sum() == 0:
                pdf.cell(CELL_WIDTH, CELL_HEIGHT, "NA", 1, 0, 'C')
            else:
                tbpl = round(i_df["Total born"].sum() / i_df["Date F"].sum(), 2)
                pdf.cell(CELL_WIDTH, CELL_HEIGHT, str(tbpl), 1, 0, 'C')

            pdf.cell(CELL_WIDTH, CELL_HEIGHT, "{:.2%}".format(i_df["Date F"].sum() / i_df["Group Number"].sum()),
                     1, 0, 'C')
            pdf.cell(CELL_WIDTH, CELL_HEIGHT, str(i_df["Group Number"].sum()), 1, 1, 'C')

    make_table_by_individual(heat_checker_combos, "heat checker")

    pdf.set_y(pdf.get_y() + 10)

    breeder_combos = generate_combos(["Breeder1", "Breeder2", "Breeder3"])

    make_combo_table(breeder_combos, "Breeder")

    pdf.set_y(pdf.get_y() + 10)

    make_table_by_individual(breeder_combos, "breeder")
    full_report_path = os.path.join(REPORTS_DIRECTORY,"Group"+group_num+" Report.pdf")
    pdf.output(full_report_path)
    print("Report has been created")

    return df3


def output_to_excel(df):
    """ Outputs merged dataframe to output.xlsx excel file"""

    reader = pd.read_excel(MASTER_DATABASE)
    writer = pd.ExcelWriter(MASTER_DATABASE, engine='openpyxl', mode='a', if_sheet_exists="overlay")
    df.to_excel(writer, header=False, index=False, startrow=len(reader) + 1)
    writer.close()
