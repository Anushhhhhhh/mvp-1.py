# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 04:37:46 2026

@author: XCG
"""
import pandas as pd
import os
# Credimax
# print(os.getcwd())
# os.chdir("/Users/anushervonsattorov/Streamlit_Recon_App_Pagsmile")
def payvalida_ecuador_payout_reader(report_dir):

    df_merged_external = pd.DataFrame()
    for files in report_dir:
        df_external = pd.read_csv(files,sep =",",parse_dates = ["Fecha Creacion"])
        df_merged_external = pd.concat([df_external,df_merged_external],ignore_index = True)
    df_merged_external["Debito_adj"] = pd.to_numeric(df_merged_external["Debito"].str.replace(",",""))
    df_merged_external["Valor_adj"] = pd.to_numeric(df_merged_external["Valor"].str.replace(",",""))
    df_merged_external["Credito"] = pd.to_numeric(df_merged_external["Credito"])

    meses_es_en = {'marzo': 'March', 'enero': 'January', 'febrero': 'February', 'abril': 'April', 'mayo': 'May', 'junio': 'June',
        'julio': 'July', 'agosto': 'August', 'septiembre': 'September','octubre': 'October', 'noviembre': 'November', 'diciembre': 'December'}
    clean_dates = df_merged_external['Fecha Creacion'].str.lower()
    clean_dates = clean_dates.str.split(',').str[0:2].str.join(',')
    clean_dates = clean_dates.replace(meses_es_en, regex=True)
    
    # 3. Convert to datetime
    df_merged_external['Fecha Creación-adj'] = pd.to_datetime(clean_dates, format='%B %d, %Y')
    df_merged_external["month_ext-creada"] = df_merged_external["Fecha Creación-adj"].dt.month_name()
    df_merged_external["year_ext-creada"] = df_merged_external["Fecha Creación-adj"].dt.year
    df_merged_external = df_merged_external[['Valor', "year_ext-creada",'Fecha Creacion','Fecha Creación-adj',"month_ext-creada", 'Documento', 'Codigo Operacion', 'Estado', 'Credito', 'Debito',"Debito_adj", 
           'Apellidos', 'Banco',"Valor_adj"]]
    
    return df_merged_external

# Payvalida ECUADOR

def payvalida_ecu_payin(uploaded_files):
    external_payvalida = pd.DataFrame()
    cols_payvalida = ['Sk Orden', 'Autorization ID', 'Referente', 'Monto', 
           'Tarifa_Payvalida', 'Iva_Tarifa_Payvalida',  'Total',
           'Medio Pago',  'Descripción', 'Estado de Orden','Fecha Creación', 'Fecha Actualización', 'Fecha pago']
    
    parse_dates = ["Fecha Creación", "Fecha Creación","Fecha pago"]
    for file in uploaded_files:
        df = pd.read_csv(file, usecols = cols_payvalida, dtype={"Autorization ID": object,
                                                                "Sk Orden":str},
                          parse_dates = parse_dates)
        external_payvalida = pd.concat([df,external_payvalida])

        # 1. Dictionary for translation
    meses_es_en = {'marzo': 'March', 'enero': 'January', 'febrero': 'February', 'abril': 'April', 'mayo': 'May', 'junio': 'June',
        'julio': 'July', 'agosto': 'August', 'septiembre': 'September','octubre': 'October', 'noviembre': 'November', 'diciembre': 'December'}
    # 2. Clean the string:
    clean_dates = external_payvalida['Fecha Creación'].str.lower()
    clean_dates = clean_dates.str.split(',').str[0:2].str.join(',')
    clean_dates = clean_dates.replace(meses_es_en, regex=True)
    
    external_payvalida["Sk Orden"] = external_payvalida["Sk Orden"].str.replace(",","")
    
    # 3. Convert to datetime
    external_payvalida['Fecha Creación-adj'] = pd.to_datetime(clean_dates, format='%B %d, %Y')
    external_payvalida["month_ext-creada"] = external_payvalida["Fecha Creación-adj"].dt.month_name()
    return external_payvalida

def credimax_reader_payin(uploaded_files):
    
    data_frames = pd.DataFrame()
    
    # Define columns and parse dates once (outside the loop for clarity)
    usecols = [
        'Merchant ID', 'Order ID', 'Order Reference', 'Transaction ID',
        'Transaction Date', 'Transaction Type', "Payer Authentication -  Authentication Status",
        'Transaction Amount (amount only)', 'Transaction Amount (currency only)',
        'Transaction Gateway Response Code']
    parse_dates = ["Transaction Date"]
    # Data types to enforce
    dtype = {"Order Reference": object,
        'Transaction ID': object,
        'Merchant ID': object,
        'Transaction Type': object,
        'Order ID': object}
    # Loop through each CSV file
    for file in uploaded_files:

        external = pd.read_csv(
            file,
            dtype=dtype,
            usecols=usecols,
            parse_dates=parse_dates)
        
        # Append to list
        data_frames = pd.concat([external,data_frames],ignore_index=True)
        
    data_frames = data_frames[(data_frames['Transaction Type'] == "Payment") & (data_frames['Transaction Gateway Response Code'] == 'Approved')]
    return data_frames
# Bank131

def bank131_payin_external_reader(report_folder):

    external_transactions_from_email = pd.DataFrame()
    
    for excel_file in report_folder:
        external_bank131 = pd.read_excel(
            excel_file,
            skiprows=1,
            skipfooter=1,
            parse_dates=['Transaction Date and Time'],
            engine='openpyxl'
        )
        external_transactions_from_email = pd.concat(
            [external_transactions_from_email, external_bank131]
        )

    return external_transactions_from_email



def payty_efecty(report_folder):
    
    ext_columns = ['Transaction', 'Order', 'Type', 'Payment date', 'Status',
       'Payment amount', 'Capture date', 'Capture #', 'Terminal ID (TID)',
       'Payment method', 'Expiry date', 'UUID transaction']

    external_original_dashboard = pd.DataFrame()    
    # Correct: list of column names to parse as dates
    parse_date = ["Payment date", "Capture date"]
    for csv_file in report_folder:    
        external = pd.read_excel(csv_file, dtype={"Order": object},usecols = ext_columns, parse_dates=parse_date)
        external_original_dashboard = pd.concat([external, external_original_dashboard], ignore_index=True)
        
    external_original_dashboard['Capture_Date Adjusted'] = external_original_dashboard['Capture date'].astype(str).str.slice(0,11)
    external_original_dashboard['Capture_Date Adjusted'].unique()
    external_original_dashboard['Formatted_Date'] = pd.to_datetime(external_original_dashboard['Capture_Date Adjusted'],dayfirst=True)
    external_original_dashboard["Month_External"] = external_original_dashboard["Formatted_Date"].dt.strftime('%B')    
    
    return external_original_dashboard


def geidea_egp(report_folder):
    for geidea_external in report_folder:
        df_ext = pd.read_csv(geidea_external,parse_dates = ["Date and time"],
                usecols = ['Date and time',  'Order ID', 'Merchant Reference ID',
               'Payment Method', 'Card Type', 'Payment Type', 
               'Status', 'Refund Status',  'Settlement Currency',"Payout ID",
               'Gross Amount', 'Net Amount', 'Total Refund Amount', 
               'Original Amount'],
                            dtype={"Merchant Reference ID":object})
    df_ext['Date and time'] = df_ext['Date and time'].dt.tz_localize(None)
    df_ext["Date and time"] = pd.to_datetime(df_ext["Date and time"], errors="coerce").dt.strftime('%Y-%m-%d')
    df_ext["Date"] = pd.to_datetime(df_ext["Date and time"], format = "%Y-%m-%d")
    df_ext["Month_Ext"] = df_ext["Date"].dt.month_name() 
    df_ext["Fee"] = df_ext["Gross Amount"] - df_ext["Net Amount"]
    df_ext["Fee_%"] = df_ext["Fee"] / df_ext["Gross Amount"]
    return df_ext


def nequi_payin(report_folder):
    ext_file_col_filtered = pd.DataFrame()
    for ext_file_path in report_folder:
        try:
                
            ext_file = pd.read_csv(
                ext_file_path,
                skiprows=9,
                sep=";",
                dtype={"Referencia 3": object},
                encoding="utf-8",
                parse_dates =['Fecha']
            )
        except UnicodeDecodeError:
            print("UTF-8 encoding failed, trying 'latin1'...")
            ext_file = pd.read_csv(
                ext_file_path,
                skiprows=9,
                sep=";",
                parse_dates =['Fecha'],
                dtype={"Referencia 3": object},
                encoding="latin1")
        ext_file_col_filtered = pd.concat([ext_file,ext_file_col_filtered],ignore_index=True)
    ext_file_col_filtered =ext_file[['Valor transaccion', 'Comision', 'Iva','Fecha','Message Id',
'Referencia 3', 'Tipo Documento','Producto/Canal']]
    ext_file_col_filtered['Fecha'] = pd.to_datetime(ext_file_col_filtered['Fecha'])
    return ext_file_col_filtered


import pandas as pd
from pandas.errors import EmptyDataError

import pandas as pd
from pandas.errors import EmptyDataError

import pandas as pd
from pandas.errors import EmptyDataError


def make_datetimes_naive(df):
    """
    Remove timezone information from all timezone-aware datetime columns.
    """
    for col in df.select_dtypes(include=["datetimetz"]).columns:
        df[col] = df[col].dt.tz_localize(None)
    return df


def onvopay_payin(uploaded_files):

    all_dfs = []

    for file in uploaded_files:
        try:
            filename = file.name.lower()

            if filename.endswith(".xlsx"):
                df = pd.read_excel(file)

            elif filename.endswith(".csv"):
                df = pd.read_csv(file, sep=",")

            else:
                continue

            if df.empty:
                print(f"Skipping empty file: {file.name}")
                continue

            df["source_name"] = file.name
            all_dfs.append(df)

        except EmptyDataError:
            print(f"Skipping completely empty file: {file.name}")

        except Exception as e:
            print(f"Error reading {file.name}: {e}")

    if not all_dfs:
        return pd.DataFrame()

    # Merge all uploaded files
    ext_file = pd.concat(all_dfs, ignore_index=True)

    # Add suffix to all columns
    ext_file = ext_file.add_suffix("_ext")

    # Convert datetime columns
    ext_file["Created At_ext"] = pd.to_datetime(
        ext_file["Created At_ext"], errors="coerce"
    )
    ext_file["Updated At_ext"] = pd.to_datetime(
        ext_file["Updated At_ext"], errors="coerce"
    )

    # Remove timezone information (if present)
    ext_file = make_datetimes_naive(ext_file)

    # Additional date columns
    ext_file["Month_CreateT_ext"] = ext_file["Created At_ext"].dt.month_name()

    ext_file["Updated At_no_time_ext"] = (
        ext_file["Updated At_ext"].dt.normalize()
    )

    ext_file["Created At_no time_ext"] = (
        ext_file["Created At_ext"].dt.normalize()
    )

    return ext_file

def interbank_payout(file):
    
    if file:
        df_external = pd.DataFrame()
        for files in file:
            externals = pd.read_excel(files, dtype ={"Documento":str})
            df_external = pd.concat([externals,df_external], ignore_index=True)
    # Data Manipulation
    df_external["adjusted_unique_id"] = df_external["Documento"].str.lstrip("Factura").str.strip()
    df_external["adjusted_monto"] = df_external["Monto"].str.lstrip("S/ ")
    df_external["adjusted_monto"] = pd.to_numeric(df_external["adjusted_monto"].str.replace(",",""))
    # df_external["date_manual"] = pd.to_datetime("2026-05-31")
    return df_external

def interbank_payin(report_dir):
    merged_df = pd.DataFrame()
    for files in report_dir:
        df_external_payin = pd.read_excel(files,skiprows = 11, index_col=0,parse_dates  = ["Fecha de proceso"])
        
        merged_df = pd.concat([df_external_payin,merged_df],ignore_index=True)
    merged_df["Fecha de proceso"] = pd.to_datetime(merged_df["Fecha de proceso"],dayfirst=True)
    merged_df = merged_df.loc[merged_df["Movimiento"] == "RECAUDACION"]
    merged_df["ID_Payin"] = merged_df["Descripción"].str.strip("PAGSMILE PEN-")
    return merged_df

def payvalidacop_reader(report_dir):
    needed_ext_cols = [ 'PO', 'Estado', 'Fecha Creación','Fecha Actualización', 
    'Medio Pago', 'Valor Total', 'Servicio Recaudo','Iva Servicio Recaudo']
    parse_dates = ["Fecha Creación", "Fecha Actualización"]
    df_external = pd.DataFrame()
    for files in report_dir:
        externals = pd.read_excel(files, usecols = needed_ext_cols,dtype={"PO": object, 'Referente Pago': object},
            parse_dates=parse_dates,skipfooter=7)
        externals["source_ext"] = files.name
        df_external = pd.concat([externals,df_external], ignore_index=True)
    df_external['Date_Ext_UPDATETIME'] = df_external['Fecha Actualización'].dt.date
    df_external['Date_Ext_UPDATETIME'] = pd.to_datetime(df_external['Date_Ext_UPDATETIME'], errors ='coerce')
    df_external["month_ext"] = df_external["Fecha Actualización"].dt.month_name()          
    return df_external
    
def rapipagos_reader(report_dir):
    from openpyxl import load_workbook
    df_external = pd.DataFrame()
    for files in report_dir:
        externals = pd.read_excel(files, dtype = {"barTradeNo":object,"gireTransactionNumber":object},
                                  engine = "openpyxl")
        df_external = pd.concat([df_external,externals],ignore_index=True)

    return df_external

def movii_payin_reader(report_dir):
    
    parse_dates = ["transfer_date"]
    excel_files = [file for file in report_dir]
    merged_data_ = pd.DataFrame()
    
    for file in excel_files:    
        external = pd.read_csv(file,
    dtype={"transfer_id": object,'celular_origen':object,
   'celuar_destino':object,'cell_id':object}, parse_dates=parse_dates)   
        merged_data = pd.concat([merged_data_,external])
    return merged_data

def movii_payin_reader(report_dir):
    parse_dates = ["transfer_date"]
    merged_data = pd.DataFrame()
    for file in report_dir:    
        external = pd.read_csv(file, dtype={"transfer_id": object,'celular_origen':object,'celuar_destino':object,'cell_id':object},
        parse_dates=parse_dates)   
        merged_data = pd.concat([merged_data,external])
    return merged_data

def zesta_8b_reader(report_dir):
    import csv
    external_original_dashboard = pd.DataFrame()
    needed_cols = ["order_id", "order_reference", "system_amount", 
    "system_currency", "completed_at", "payment_type", "method_type", "fee"]
    date_cols = ["completed_at"]
    
    for full_path in report_dir:
        # with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
        #     sample = f.read(4096)   # read first 4KB to detect format
        #     sniffer = csv.Sniffer()
        #     dialect = sniffer.sniff(sample, delimiters=',;\t')
        #     detected_sep = dialect.delimiter

        df = pd.read_csv(
            full_path,sep=",",
            usecols=lambda x: str(x).strip() in needed_cols,   # safe column selection
            parse_dates=date_cols,
            dtype={"order_id": "string", "order_reference": "string"},
            encoding='utf-8',on_bad_lines='skip',low_memory=False)        
        df["source_file"] = full_path
        external_original_dashboard = pd.concat([df,external_original_dashboard], ignore_index=True)    
    return external_original_dashboard


def carussell_reader(report_dir):
    external_original_dashboard = pd.DataFrame()
    for file in report_dir:
        df = pd.read_excel(file, skiprows=2, dtype = {"Transaction ID": object,"Client Reference Transaction ID":object})
        df['source_file'] = file
        
        external_original_dashboard = pd.concat([external_original_dashboard,df])
    
    external_original_dashboard = external_original_dashboard.rename(columns = {
    "Transaction ID":                        "order_id",
    "Type":                                  "payment_type", #  payment_type
    "Authorization Amount":                  "system_amount",
    "Authorization Currency":                "system_currency",
    "Last Updated At":                       "completed_at",
    "Client Reference Transaction ID":       "order_reference",
    "Payment Method":                        "method_type",
    "Transaction status":                     "Status",
    "Settlement Account ID":                 None,
    "Settlement Account Name":               "merchant_info"})

    external_original_dashboard["order_reference"] = external_original_dashboard["order_reference"].astype(object)
    external_original_dashboard["order_id"] = external_original_dashboard["order_id"].astype(object)
    external_original_dashboard['completed_at_dt'] = external_original_dashboard['Last Updated'].astype(str).str.slice(0,10)
    external_original_dashboard['date_only'] = pd.to_datetime(external_original_dashboard['completed_at_dt']) # , dayfirst = True
    external_original_dashboard["Month_Ext"] = external_original_dashboard["date_only"].dt.month
    external_original_dashboard["Year_Ext"] = external_original_dashboard["date_only"].dt.year    
    return external_original_dashboard


def bcppayout_reader(report_dir):

    external_df = pd.DataFrame()
    
    for file_path in report_dir:
        print(f"Reading file: {file_path} ...")
        df = pd.read_csv(file_path,skiprows=4, encoding='latin1')
        # Optional: add a column to track the source file
        df['source_file'] = file_path
        external_df = pd.concat(external_df, ignore_index=True)
    return external_df



def alfinbank_reader_payout(report_folder):

    merged_df = pd.DataFrame()
    for external_alfin_files in report_folder:
        try:
            df_ext = pd.read_excel(external_alfin_files, parse_dates = ["createdAt"], dtype = {"payChannelOrder":object})
            df_ext["source"] = external_alfin_files.name
            merged_df = pd.concat([df_ext, merged_df])
        except ValueError as val_e:
            print(f"{external_alfin_files.name}Excel file is empty, please ignore \n{val_e}")
            continue
        
    return merged_df


def bre_b_payout_external_reader(report_dir):

    needed_cols = [
        'transfer_date', 'transfer_id', 'nombre_producto',
        'estado transaccion', 'value', 'cell_id', 'estado',
        'celular_origen', 'celuar_destino', 'entry_type',
        'tipo', 'entidad_destino', 'entidad_origen',
        'estado_transfer', 'transaction_id_redeban',
        'creditor_party_identifier', 'debtor_document_number',
        'creditor_document_number', 'nombre_bicfi_d',
        'status_breb']
    date_cols = ["transfer_date"]
    df_merged = pd.DataFrame()

    for payout_file in report_dir:
        try:
            df = pd.read_csv(
                payout_file,
                sep=",",
                usecols=needed_cols,
                parse_dates=date_cols)
        except:
            print(f"{payout_file.name}: not comma separated, trying ';'")
            try:
                df = pd.read_csv(
                    payout_file,
                    sep=";",
                    usecols=needed_cols,
                    parse_dates=date_cols)

            except:
                print(f"{payout_file.name}: unable to read.")
                continue

        df["source_ext"] = payout_file
        df_merged = pd.concat([df, df_merged], ignore_index=True)
        print(f"{payout_file.name} read successfully!")

    return df_merged


def movii_transfiya_payout(report_dir):
    df_list = pd.DataFrame()
    for file in report_dir:
        try:
            external = pd.read_csv(
                file,usecols=[0,  6, 7, 9, 10, 11, 12, 17],
                dtype={    "Txn ID": object,
                    'celular_origen': object,
                    'celuar_destino': object },
                parse_dates=["transfer_date"])
            df_list = pd.concat([df_list,external],ignore_index= True)
        except Exception as e:
            print(f"Error reading {file}: {e}")
    return df_list
