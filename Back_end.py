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
import pd_table as pdt
import boto3
from botocore.config import Config
from PIL import Image
import pytesseract
from img2table.document import PDF
from img2table.ocr import TesseractOCR


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

def extract_data2(input_document):
    pages = convert_from_path(input_document,
                              poppler_path=r"C:\Users\jakeh\poppler-0.68.0_x86\poppler-0.68.0\bin")
    dfs = pd.DataFrame()
    for i, page in enumerate(pages):
        page.save("out" + str(i) + ".png", "PNG")
        print(pytesseract.image_to_data(Image.open('out'+str(i)+".png"),output_type='data.frame').to_string())

    return dfs

def extract_data3(input_document):
    pdf=PDF(src=input_document)

    ocr = TesseractOCR(lang="eng")

    pdf_tables = pdf.extract_tables(ocr=ocr)
    for i in pdf_tables:
        print(i.to_string())


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
                if not pd.notna(value):
                    continue
                else:
                    value=str(value)
                    if len(value)<=2:
                        df1.at[i,x]=pd.to_datetime("09"+value+"23", format="%m%d%y").date()
                    elif len(value)>2:
                        df1.at[i,x]=pd.to_datetime(value + "23", format="%m%d%y").date()
            except ParserError as pe:
                dates_error_list.append([i,df1.columns.get_loc(x)])
            except ValueError as e:
                dates_error_list.append([i,df1.columns.get_loc(x)])
        # df1[x] = pd.to_datetime(df1[x]).dt.date
    return df1, dates_error_list


def convert_to_numeric(df1, columns_list):
    numeric_error_list=[]
    for x in columns_list:
        for i, value in enumerate(df1[x]):
            try:
                df1.at[i, x] = pd.to_numeric(value)
            except ParserError as pe:
                numeric_error_list.append([i,df1.columns.get_loc(x)])
                # print(value, "is causing an error in column", x, "and is in row", i)
                # df1.at[i, x] = input("What would you like to change this value to? ")
            except ValueError as e:
                numeric_error_list.append([i,df1.columns.get_loc(x)])
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

def farrowing_clean(df1):
    df1 = general_clean(df1)
    numeric_list = ["Crate#", "P", "#L", "#S", "#M", "#W"]
    error_dict = {r"\\": "1", "I": "1", "o": "0", "O": "0", "&": "9", "a": "9","/":"1"}
    df1[numeric_list]=df1[numeric_list].replace(error_dict, regex=True)
    error_list=[]
    dates_list = ["Date Farrowed", "Date Weaned"]
    # df1[dates_list] += "23"
    df1, error_list = convert_to_date(df1, dates_list)

    df1, error_list1 = convert_to_numeric(df1, numeric_list)
    error_list.extend(error_list1)
    error_list2=[]
    t_data,isOKAY = pdt.table_editor(df1,error_list2)

    code_dict = {22: "Savaged", 21: "Ruptures", 27: "Starvation"}
    for key in [1, 13, 20, 26]:
        code_dict[key] = "Low Viability"
    for key in [10, 12, 28]:
        code_dict[key] = "Laid On"
    for key in [23, 30]:
        code_dict[key] = "Strep"
    for key in [2, 3, 7, 9, 15, 25, 31]:
        code_dict[key] = "Other"
    # Convert codes to columns
    df1["Low Viability"] = 0
    df1["Laid On"] = 0
    df1["Strep"] = 0
    df1["Scours"] = 0
    df1["Other"] = 0
    df1["Savaged"] = 0
    df1["Ruptures"] = 0
    df1["Starvation"] = 0
    df1["Unknown"] = 0
    for i in range(1, 5):
        for count, x in enumerate(df1["C" + str(i)]):
            is_num_deaths = True
            num_deaths = []
            death_code = []
            if pd.notna(x):
                for j in x:
                    if j == '-':
                        is_num_deaths = False

                    elif is_num_deaths:
                        num_deaths.append(j)

                    else:
                        death_code.append(j)

                deaths = ''.join(num_deaths)
                code = ''.join(death_code)
                df1.at[count, code_dict[int(code)]] = int(deaths)
        df1.drop("C" + str(i), axis=1, inplace=True)
    return t_data


def breeding_clean(df1):
    df1 = general_clean(df1)
    df1.replace({'AL': 'AC', 'BL': 'BV', 'PV': 'BV', 'B': 'BV', 'A': 'AC', 'H': 'HR',"C":"CJ"}, inplace=True)
    dates_list = ["Date Bred" + str(i) for i in range(1, 4)]
    # df1[dates_list] += "23"
    error_list=[]
    df1, error_list = convert_to_date(df1, dates_list)
    error_list1=[]
    t_data, isOKAY = pdt.table_editor(df1,error_list1)
    print(t_data)

    return t_data

# def produce_errors(df1,date_list,numeric_list):
# to do


def generate_report(df1, df2):
    df3 = df1.merge(df2, how='outer', on="Sow ID")
    df3 = fill_table(df3)
    length=len(df3)
    df3=df3.replace("Ll",11)
    df3=df3.replace("J","JS")
    df3=df3.replace("BY","BV")
    df3.insert(loc=17,column="Unknown",value=np.NaN)
    for i, value in enumerate (df3["Date Farrowed"]):
        if pd.notna(value):
            df3.at[i,"Unknown"]=0

    num_list=["#L","#S","#M","#W"]
    df3[num_list]=df3[num_list].replace(np.NaN,0)
    group_num = input("What group are you inputting? ")
    df3["Group Number"] = int(group_num)
    df3,error=convert_to_numeric(df3,["P","#L","#S","#M","#W","Crate#","Group Number"])
    df3,error=convert_to_date(df3,["Date Farrowed","Date Weaned","LW","Date Bred1","Date Bred2","Date Bred3"])
    diff = df3["#L"].sum() - (df3["Low Viability"].sum() + df3["Laid On"].sum() + df3["Strep"].sum() + df3["Scours"].sum()
                       + df3["Other"].sum() + df3["Savaged"].sum() + df3["Ruptures"].sum() + df3["Starvation"].sum())
    balance = 0
    if diff > df3["#W"].sum():
        df3 = pd.concat([df3,pd.DataFrame([{"Sow ID":"Y","Unknown":diff-df3["#W"].sum(),"Group Number":group_num}])],ignore_index=True)
        balance = 1
    elif diff < df3["#W"].sum():
        df3 = pd.concat([df3,pd.DataFrame([{"Sow ID": "Y", "#W": diff-df3["#W"].sum(),"Group Number":group_num}])], ignore_index=True)
        balance = 2

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Times","B",25)
    pdf.cell(0,0,"Group "+group_num+ " Pigmaker Report",0,2,"C")

    mode=df3["Date Weaned"].mode()[0].strftime("%m-%d-%Y")
    pdf.set_y(27)
    pdf.cell(0,0,str(mode),0,2,'C')
    pdf.set_font("Times",'B',15)

    pdf.set_y(40)

    pdf.cell(48,8,"Statistic",1,0,'C')
    pdf.cell(48,8,"Rooms 1-6",1,0,'C')
    pdf.cell(48,8,"Rooms 8-12",1,0,'C')
    pdf.cell(48,8,"Overall",1,1,'C')

    pdf.set_font("Times", '', 12)

    pdf.cell(48,8,"Total born per litter",1,1,'C')
    pdf.cell(48, 8,"Still birth rate", 1, 1,'C')
    pdf.cell(48, 8, "Mum birth rate", 1, 1, 'C')
    pdf.cell(48, 8, "Born live per litter", 1, 1, 'C')
    pdf.cell(48, 8, "Weaned per litter", 1, 1, 'C')
    pdf.cell(48, 8, "Pre-weaning mortality rate", 1, 1, 'C')

    pdf.set_xy(58,48)

    num_farrowed = df3["Date Farrowed"].count()
    farrowing_rate = num_farrowed / length

    Half1 = df3[df3["Crate#"] < 700]
    Half2 = df3[df3["Crate#"] >= 800]
    for half in [Half1,Half2]:
        half_num_farrowed = half["Date Farrowed"].count()

        total_born = round(((half["#S"].sum() + half["#M"].sum() + half["#L"].sum())/half_num_farrowed),2)
        pdf.cell(48,8,str(total_born),1,2,'C')

        still_rate=half["#S"].sum()/(total_born * half_num_farrowed)
        pdf.cell(48,8,"{:.2%}".format(still_rate),1,2,'C')

        mum_rate=half["#M"].sum()/(total_born * half_num_farrowed)
        pdf.cell(48,8,"{:.2%}".format(mum_rate),1,2,'C')

        live_per_litter=round(half["#L"].sum()/half_num_farrowed,2)
        pdf.cell(48, 8, str(live_per_litter), 1, 2,'C')

        weaned_per_litter=round(half["#W"].sum()/half_num_farrowed,2)
        pdf.cell(48, 8, str(weaned_per_litter), 1, 2,'C')

        preweaning_mortality = (half["Low Viability"].sum() + half["Laid On"].sum() + half["Strep"].sum() + half["Scours"].sum()
        + half["Other"].sum() + half["Savaged"].sum() + half["Ruptures"].sum() + half["Starvation"].sum())/half["#L"].sum()
        pdf.cell(48, 8, "{:.2%}".format(preweaning_mortality), 1, 2,'C')

        pdf.set_xy(106,48)

    pdf.set_x(154)

    total_num_farrowed = df3["Date Farrowed"].count()

    total_born = round(((df3["#S"].sum() + df3["#M"].sum() + df3["#L"].sum()) / total_num_farrowed), 2)
    pdf.cell(48, 8, str(total_born), 1, 2, 'C')

    still_rate = df3["#S"].sum() / (total_born * total_num_farrowed)
    pdf.cell(48, 8, "{:.2%}".format(still_rate), 1, 2, 'C')

    mum_rate = df3["#M"].sum() / (total_born * total_num_farrowed)
    pdf.cell(48, 8, "{:.2%}".format(mum_rate), 1, 2, 'C')

    live_per_litter = round(df3["#L"].sum() / total_num_farrowed, 2)
    pdf.cell(48, 8, str(live_per_litter), 1, 2, 'C')

    weaned_per_litter = round(df3["#W"].sum() / total_num_farrowed, 2)
    pdf.cell(48, 8, str(weaned_per_litter), 1, 2, 'C')

    preweaning_mortality = (df3["Low Viability"].sum() + df3["Laid On"].sum() + df3["Strep"].sum() + df3[
        "Scours"].sum() + df3["Other"].sum() + df3["Savaged"].sum() + df3["Ruptures"].sum() + df3[
                                "Starvation"].sum()) / df3["#L"].sum()
    pdf.cell(48, 8, "{:.2%}".format(preweaning_mortality), 1, 2, 'C')


    pdf.set_xy(10,105)

    pdf.cell(0,10,"*The overall farrowing rate is: "+"{:.2%}".format(farrowing_rate)+" ("+str(num_farrowed)+" out of "+str(length)+")",0,1,'L')
    weaned_pigs=df3["#W"].sum()
    pdf.cell(0,10,"*The total number of weaned pigs is "+str(weaned_pigs),0,1,'L')
    if balance == 1:
        pdf.multi_cell(0,10,"*"+str(int(diff-df3["#W"].sum()))+
        " unknown deaths were added to imaginary sow 'Y' to make the total born live minus the total dead equal the total weaned",0,'L')
    elif balance ==2:
        pdf.multi_cell(0,10, "*" + str(int(df3["#W"].sum() - diff)) +
        " weaned pigs were added to imaginary sow 'Y' to make the total born live minus the total dead equal the total weaned", 0, 'L')
    else:
        pdf.multi_cell(0,10, "* The total born live minus the total dead equal the total weaned", 0, 'L')



    combo=df3
    combo["HC_combo"] = combo.apply(lambda row: list({row['HC1'], row['HC2'], row['HC3']}), axis=1)
    combo['HC_combo'] = combo['HC_combo'].apply(lambda x: [i for i in x if not (pd.isna(i) or i is None)]).astype('object')
    combo["Breeder_combo"]= combo.apply(lambda row: list({row['Breeder1'], row['Breeder2'], row['Breeder3']}), axis=1)
    combo['Breeder_combo'] = combo['Breeder_combo'].apply(lambda x: [i for i in x if not (pd.isna(i) or i is None)]).astype('object')

    combo['HC_combo2'] = combo['HC_combo'].apply(tuple)
    combo['Breeder_combo2'] = combo['Breeder_combo'].apply(tuple)

    hc = combo.groupby(by="HC_combo2").agg({'#S':'sum',
                                           '#M':'sum',
                                           '#L':'sum',
                                           'Group Number':'count',
                                           'Date Farrowed':'count'})

    hc["Farrowing rate"] = hc["Date Farrowed"]/hc["Group Number"]
    hc["Total born"] = hc["#S"] + hc["#M"] + hc["#L"]
    hc = hc.sort_values(by="Farrowing rate",ascending=False)


    pdf.set_font('Times','B',12)

    pdf.set_y(150)
    pdf.cell(49,8,"Heat checker combination",1,0,'C')
    pdf.cell(49, 8, "Total born per litter", 1, 0, 'C')
    pdf.cell(49, 8, "Farrowing rate", 1, 0, 'C')
    pdf.cell(49, 8, "Count", 1, 1, 'C')

    pdf.set_font('Times','',12)

    for i in hc.index:
        if i == ():
            pdf.cell(49,8,"Unknown",1,0,'C')
        else:
            pdf.cell(49,8,str(', '.join(sorted(i))),1,0,'C')

        if hc.at[i,"Date Farrowed"] == 0:
            pdf.cell(49,8,"NA",1,0,'C')
        else:
            pdf.cell(49, 8, str(round(hc.at[i,"Total born"]/hc.at[i,"Date Farrowed"],2)), 1, 0, 'C')
        pdf.cell(49, 8, "{:.2%}".format(hc.at[i,"Farrowing rate"]), 1, 0, 'C')
        pdf.cell(49,8,str(hc.at[i,"Group Number"]),1,1,'C')

    print(hc)
    print(hc.index)

    pdf.set_y(pdf.get_y()+10)

    pdf.set_font('Times','B',12)
    pdf.cell(49,8,"Individual heat checker",1,0,'C')
    pdf.cell(49, 8, "Total born per litter", 1, 0, 'C')
    pdf.cell(49, 8, "Farrowing rate", 1, 0, 'C')
    pdf.cell(49, 8, "Count", 1, 1, 'C')

    pdf.set_font('Times', '', 12)

    v = []
    for i in hc.index:
        v.extend(i)

    v = list(set(v))
    dfl = {}
    for i in v:
        i_df = hc[hc.index.map(lambda tpl: any(str(i) in elem for elem in tpl))]
        dfl[str(i)]=(i_df["Date Farrowed"].sum() / i_df["Group Number"].sum())

    sorted_dfl = sorted(dfl.items(), key = lambda kv: kv[1],reverse = True)
    heat_checkers = []
    for heat_checker, farrowing_rate in sorted_dfl:
        heat_checkers.append(heat_checker)
    print(heat_checkers)
    for i in heat_checkers:

        i_df = hc[hc.index.map(lambda tpl: any(str(i) in elem for elem in tpl))]
        print (i_df)
        pdf.cell(49,8,str(i),1,0,'C')
        if i_df["Date Farrowed"].sum() == 0:
            pdf.cell(49,8,"NA",1,0,'C')
        else:
            tbpl = round(i_df["Total born"].sum()/i_df["Date Farrowed"].sum(),2)
            pdf.cell(49,8,str(tbpl),1,0,'C')

        pdf.cell(49, 8, "{:.2%}".format(i_df["Date Farrowed"].sum()/i_df["Group Number"].sum()), 1, 0, 'C')
        pdf.cell(49,8,str(i_df["Group Number"].sum()),1,1,'C')

    br = combo.groupby(by="Breeder_combo2").agg({'#S': 'sum',
                                                 '#M': 'sum',
                                                 '#L': 'sum',
                                                 'Group Number': 'count',
                                                 'Date Farrowed': 'count'})

    br["Farrowing rate"] = br["Date Farrowed"] / br["Group Number"]
    br["Total born"] = br["#S"] + br["#M"] + br["#L"]

    br = br.sort_values(by="Farrowing rate", ascending=False)

    pdf.set_y(pdf.get_y()+10)

    pdf.set_font('Times','B',12)
    pdf.cell(49,8,"Breeder combination",1,0,'C')
    pdf.cell(49, 8, "Total born per litter", 1, 0, 'C')
    pdf.cell(49, 8, "Farrowing rate", 1, 0, 'C')
    pdf.cell(49, 8, "Count", 1, 1, 'C')

    pdf.set_font('Times','',12)

    for i in br.index:
        if i == ():
            pdf.cell(49, 8, "Unknown", 1, 0, 'C')
        else:
            pdf.cell(49, 8, str(', '.join(sorted(i))), 1, 0, 'C')

        if br.at[i, "Date Farrowed"] == 0:
            pdf.cell(49, 8, "NA", 1, 0, 'C')
        else:
            pdf.cell(49, 8, str(round(br.at[i, "Total born"] / br.at[i, "Date Farrowed"], 2)), 1, 0, 'C')
        pdf.cell(49, 8, "{:.2%}".format(br.at[i, "Farrowing rate"]), 1, 0, 'C')
        pdf.cell(49, 8, str(br.at[i, "Group Number"]), 1, 1, 'C')

    pdf.set_y(pdf.get_y() + 10)

    pdf.set_font('Times', 'B', 12)
    pdf.cell(49, 8, "Individual breeder", 1, 0, 'C')
    pdf.cell(49, 8, "Total born per litter", 1, 0, 'C')
    pdf.cell(49, 8, "Farrowing rate", 1, 0, 'C')
    pdf.cell(49, 8, "Count", 1, 1, 'C')

    pdf.set_font('Times', '', 12)

    v = []
    for i in br.index:
        v.extend(i)

    v = list(set(v))
    dfl = {}
    for i in v:
        i_df = br[br.index.map(lambda tpl: any(str(i) in elem for elem in tpl))]
        dfl[str(i)] = (i_df["Date Farrowed"].sum() / i_df["Group Number"].sum())

    sorted_dfl = sorted(dfl.items(), key=lambda kv: kv[1], reverse=True)
    breeders = []
    for breeder, farrowing_rate in sorted_dfl:
        breeders.append(breeder)
    print (breeders)
    for i in breeders:

        i_df = br[br.index.map(lambda tpl: any(str(i) in elem for elem in tpl))]
        print(i_df)
        pdf.cell(49, 8, str(i), 1, 0, 'C')
        if i_df["Date Farrowed"].sum() == 0:
            pdf.cell(49, 8, "NA", 1, 0, 'C')
        else:
            tbpl = round(i_df["Total born"].sum() / i_df["Date Farrowed"].sum(), 2)
            pdf.cell(49, 8, str(tbpl), 1, 0, 'C')

        pdf.cell(49, 8, "{:.2%}".format(i_df["Date Farrowed"].sum() / i_df["Group Number"].sum()), 1, 0, 'C')
        pdf.cell(49, 8, str(i_df["Group Number"].sum()), 1, 1, 'C')






    pdf.output("Group" + group_num + " Report.pdf")
    print("Report has been created")

    return df3

def output_to_excel(df):
    df.to_excel(r"C:\Users\jakeh\output.xlsx",index=False)
