
import pandas as pd
import os
import numpy as np
import datetime
from datetime import datetime
import streamlit as st
import warnings
pd.options.display.float_format = '{:.2f}'.format

warnings.filterwarnings("ignore")
# os.chdir('/Users/anushervonsattorov/Desktop/modules written personally')
import External_File_Reader
import Reconciliation_Scrypt_Payin_adj_streamlit_a

st.title("NEQUI Payin & Settlement Reconciliation")
st.caption("Transaction matching · Fee & VAT validation · Bank settlement reconciliation")


external_file_path = st.file_uploader("""Please upload the external file""",
                                      type = None,
                                      accept_multiple_files=True)

internal_file_path = st.file_uploader("""Please upload the internal file""",
                                      type = None,
                                      accept_multiple_files=True)

bankstatement_path = st.file_uploader("Please upload the bank statement",
                                    type = None,
                                    accept_multiple_files=True)

date_range_for_recon = st.date_input(label = "Please Choose the Reconciliation Period of the Channel:",
                                     value=(datetime.strptime("2026-01-01","%Y-%m-%d"),
                                            datetime.strptime("2026-02-01","%Y-%m-%d")))
start_date, end_date = (date_range_for_recon)

start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)


# Read the files
if external_file_path:
    df_external = External_File_Reader.nequi_payin(external_file_path)
    df_external['Fecha'] = pd.to_datetime(df_external['Fecha'])
    st.write("External Transactions:\n")
    st.write(df_external)
    # st.write("Make sure the columns are filtered and datatypes are handled correctly!")
    
else:
    st.stop()

if internal_file_path:
    df_internal = Reconciliation_Scrypt_Payin_adj_streamlit_a.internal_reader_func(internal_file_path)
    st.write("Internal Transactions:\n")
    df_internal['date_internal_adj_int'] = pd.to_datetime(
        df_internal['date_internal_adj_int']
        )   
    st.write(df_internal)
else:
    st.stop()

# Reconcile
# Stop if either DataFrame has no rows
if df_internal.empty or df_external.empty:
    st.warning("Both internal and external reports must contain data.")
    st.stop()
    
reconciliation_id_internal = df_internal["transaction_id_int"].str.strip()
internal_column_date = pd.to_datetime(df_internal["date_internal_adj_int"])

external_column_date = pd.to_datetime(df_external["Fecha"])
reconciliation_id_external = df_external["Referencia 3"].str.strip()

df_internal_success = df_internal.loc[
    df_internal["status_int"] == "Success"
].copy()

st.write("Original rows:", len(df_internal))
st.write("Success rows:", len(df_internal_success))
st.write(df_internal_success["status_int"].unique())


reconciliation_of_internal_to_external = Reconciliation_Scrypt_Payin_adj_streamlit_a.reconcile(
    internal_df = df_internal,external_df = df_external,
    int_unique_col=reconciliation_id_internal,
    ext_unique_col = reconciliation_id_external)

reconciliation_of_internal_adjusted_period = Reconciliation_Scrypt_Payin_adj_streamlit_a.reconcile_filter_status_date(
        reconciliation_of_internal_to_external, 
        date_column = "date_internal_adj_int", 
        date_1 = start_date,
        date_2 = end_date)

st.write("reconciliation_of_internal:\n")
st.write(reconciliation_of_internal_adjusted_period)

# Reconcile External
reconciliation_of_external_internal = Reconciliation_Scrypt_Payin_adj_streamlit_a.reconcile(
                                                internal_df = df_external,
                                                external_df = df_internal,
                                                int_unique_col=reconciliation_id_external,
                                                ext_unique_col = reconciliation_id_internal)


reconciliation_of_external_adjusted_period = Reconciliation_Scrypt_Payin_adj_streamlit_a.reconcile_filter_status_date(
                                                    reconciliation_of_external_internal, 
                                                        date_column = "Fecha", 
                                                        date_1 = start_date,
                                                        date_2 = end_date)
st.write("reconciliation_of_external_internal:\n")
st.write(reconciliation_of_external_adjusted_period)

# Check for Variance
result_of_internal_reconciliation = Reconciliation_Scrypt_Payin_adj_streamlit_a.variance_checker(
    reconciliation_of_internal_adjusted_period)

st.write("NOT FOUND IN INTERNAL RECON:\n")
st.write(result_of_internal_reconciliation)


result_of_external_reconciliation = Reconciliation_Scrypt_Payin_adj_streamlit_a.variance_checker(
    reconciliation_of_external_adjusted_period,)

st.write("NOT FOUND IN EXTERNAL RECON:\n")
st.write(result_of_external_reconciliation)

# Check for duplicates
duplicates_internal_reconciliation = Reconciliation_Scrypt_Payin_adj_streamlit_a.duplicate_checker(
    reconciliation_of_internal_adjusted_period,"transaction_id_int")

duplicates_external_reconciliation = Reconciliation_Scrypt_Payin_adj_streamlit_a.duplicate_checker(
    reconciliation_of_external_adjusted_period,"Referencia 3")

# Calculate fees and VAT

reconciliation_of_external_adjusted_period["Amount_Diff"] = reconciliation_of_external_adjusted_period["Valor transaccion"] - reconciliation_of_external_adjusted_period["amount_int"] 
reconciliation_of_external_adjusted_period["Fee_%"] = reconciliation_of_external_adjusted_period["Comision"] / reconciliation_of_external_adjusted_period["Valor transaccion"]
reconciliation_of_external_adjusted_period["VAT_%"] = reconciliation_of_external_adjusted_period["Iva"]/ reconciliation_of_external_adjusted_period["Comision"]
reconciliation_of_external_adjusted_period["Commission_details"] = "1.5% of Order Amount- max amount is 3,334.00 COP"


reconciliation_of_external_adjusted_period = reconciliation_of_external_adjusted_period[[
    "_merge","Referencia 3","transaction_id_int","Producto/Canal",
  "method_gateway_name_int", "Message Id","gateway_id_int",
"Valor transaccion","amount_int","Amount_Diff",
"Comision","Fee_%","Commission_details","Iva","VAT_%",
"currency_int", "status_int", "Fecha","date_internal_adj_int","Tipo Documento"]]

# Summarize 
df_external["Fecha"] = df_external["Fecha"].dt.date
df_external["Fecha"] =pd.to_datetime(df_external["Fecha"])

summary_df_external = df_external.loc[(df_external["Fecha"] >= start_date) & (df_external["Fecha"] < end_date)]

summary_df_external["month_name"] = summary_df_external["Fecha"].dt.month_name()
summary_df_external["year_name"] = summary_df_external["Fecha"].dt.year

commission_rate = 0.015          # 1.5%
max_commission = 3504.00         # COP

base_column = "Valor transaccion"            # ←←← CHANGE THIS to your real column name!

# 3. Calculate the commission with the cap
summary_df_external["Commission_Pagsmile"] = summary_df_external[base_column] * commission_rate
summary_df_external["Commission_Pagsmile"] = round(summary_df_external["Commission_Pagsmile"].clip(upper=max_commission),2)


summary_df_external["Commission_details_Pagsmile"] = summary_df_external.apply(
    lambda row: (
        f"1.5% of {row[base_column]:,.2f} = {row['Commission_Pagsmile']:,.2f} COP "
        f"(MAX CAP APPLIED)" if row['Commission_Pagsmile'] >= max_commission else
        f"1.5% of {row[base_column]:,.2f} = {row['Commission_Pagsmile']:,.2f} COP"),axis=1)

summary_df_external["IVA_Pagsmile"] = summary_df_external["Commission_Pagsmile"] * 0.19
summary_df_external["Net_Amount"] =  summary_df_external["Valor transaccion"] - summary_df_external["Commission_Pagsmile"] - summary_df_external["IVA_Pagsmile"]
summary_df_external["Commission_Pagsmile_%"] = summary_df_external["Commission_Pagsmile"] / summary_df_external["Valor transaccion"] 


df_external_grouped = summary_df_external.groupby(["year_name","month_name"])[["Valor transaccion","Commission_Pagsmile","IVA_Pagsmile","Net_Amount"]].agg(["sum","size","median","mean"])
df_external_grouped["Fee_%"] = summary_df_external["Comision"]/ summary_df_external["Valor transaccion"]
st.write("Summary grouped")
st.write(df_external_grouped)

summarize_external_daily = summary_df_external.groupby("Fecha")[["Valor transaccion","Comision",
                                            "Commission_Pagsmile","IVA_Pagsmile","Iva","Net_Amount"]].sum()
summarize_external_daily = summarize_external_daily.reset_index()
summarize_external_daily["Fecha_adj"] = summarize_external_daily["Fecha"] + pd.Timedelta(days =1)
st.write("Summary daily")
st.write(summarize_external_daily)

# Bank reading and upload
bankstatement_path = st.file_uploader("Please upload the bank statement",
                                    type = None,
                                    accept_multiple_files=True)


if bankstatement_path:
    for reading_bank in bankstatement_path:
        try:
            df_bank_statement = pd.read_csv(reading_bank)
        except Exception:
            df_bank_statement = pd.read_excel(reading_bank, skiprows=13, 
                                              skipfooter = 1,
                                              engine='openpyxl')
        
        except Exception:
        
      
          reading_bank.seek(0)
          df_bank_statement = pd.read_excel(
              reading_bank,
              skiprows=15,
              engine="openpyxl"
          )

else:
    st.stop()


for col in ["SALDO", "VALOR"]:
    if col in df_bank_statement.columns:
        df_bank_statement[col] = (
            df_bank_statement[col]
            .astype(str)
            .str.replace(r'[,\s]', '', regex=True))
        df_bank_statement[col] = pd.to_numeric(df_bank_statement[col], errors='coerce')
    else:
        print(f"These are the actual columns {df_bank_statement.columns}")

df_bank_statement["FECHA"] = df_bank_statement["FECHA"].astype(str) + "/2026"
df_bank_statement["FECHA"] = (
    pd.to_datetime(df_bank_statement["FECHA"], dayfirst=True)
      .dt.strftime("%Y-%m-%d")
)

df_bank_statement["FECHA"] = df_bank_statement["FECHA"].astype(str).replace("/","-")
# bank_statement["FECHA"] = pd.to_datetime(bank_statement["FECHA"]).dt.strftime("%Y-%m-%d")

df_bank_statement["FECHA"] = pd.to_datetime(df_bank_statement["FECHA"], format = "mixed")

# Clean description column first (removes extra spaces, handles possible NaNs)
df_bank_statement["DESCRIPCIÓN"] = df_bank_statement["DESCRIPCIÓN"].astype(str).str.strip()

st.write("Bankstatement original")
st.write(df_bank_statement.iloc[[0,-1]])


# Filter + groupby
summary_daily_bank = df_bank_statement[
    df_bank_statement["DESCRIPCIÓN"] == "PAGO DE PROV BANCOLOMBIA SA"
].groupby("FECHA").agg({
    "VALOR": "sum",           # total amount paid per day
    "SALDO": "last"           # ← better than .sum() for balance (last balance of the day)
}).reset_index()
 

recon_to_bank = pd.merge(summarize_external_daily,summary_daily_bank,left_on = "Fecha_adj",right_on ="FECHA", how = "left",
        indicator=True)

recon_to_bank_adj = recon_to_bank[["Fecha_adj","FECHA","Net_Amount","VALOR"]]
recon_to_bank_adj["Difference"] = recon_to_bank_adj["VALOR"] - recon_to_bank_adj["Net_Amount"]
   
st.write("Reconciliation Bankstatement")
st.write(recon_to_bank_adj.iloc[[0,5,8,-1]])    

from io import BytesIO
output = BytesIO()


try:
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        reconciliation_of_internal_adjusted_period.to_excel(writer, sheet_name="Internal_Recon", index=False)
        reconciliation_of_external_adjusted_period.to_excel(writer, sheet_name="External_Recon", index=False)
        result_of_external_reconciliation.to_excel(writer, sheet_name="Ext_Not_Found", index=False)
        duplicates_external_reconciliation.to_excel(writer, sheet_name="Ext_Duplicates", index=False)
        result_of_internal_reconciliation.to_excel(writer, sheet_name="Int_Not_Found", index=False)
        duplicates_internal_reconciliation.to_excel(writer, sheet_name="Int_Duplicates", index=False)
        df_external.to_excel(writer, sheet_name = "External_Fee &IVA Review",index = False)
        df_external_grouped.to_excel(writer, sheet_name="Ext_Summarized")
        summarize_external_daily.to_excel(writer, sheet_name="Ext_Daily-for Recon", index=False)
        summary_daily_bank.to_excel(writer, sheet_name="Bank_Ext_Daily-for Recon", index=False)
        recon_to_bank_adj.to_excel(writer, sheet_name ="Recon_Bank_Settlement", index = False)
        df_bank_statement.to_excel(writer, sheet_name ="Original_Bank_Statement", index = False)
    # print(f"Saved External and Internal Recon files to: {file_path}")
except Exception as e:
    print(f"An error occurred: {e}")

name = df_internal['method_gateway_name_int'].iloc[0]
period_start, period_end = str(date_range_for_recon[0]), str(date_range_for_recon[-1])
st.download_button(label="Download the Reconciliation Result in Excel Format", data =output.getvalue(),
file_name = f"Reconciliation for {name} for the period of {period_start} and {period_end}.xlsx")

    

# # Notification:
# st.write("Would you like to send the result for reconciliation to Slack group chat?")
# st.write("Choose Yes if you need")
# st.write("Choose No if you need to investigate by yourself!")
    
# if st.button("Yes, send it to Slack and inform the team!"):
#     from slack_notification_test_1 import send_slack_message
#     from slack_notification_test_2 import generate_recon_message
#     type_of_message = generate_recon_message(
#         start_date,
#         end_date,
#         result_of_external_reconciliation,
#         result_of_internal_reconciliation)

#     send_slack_message(type_of_message)
# if st.button("No need, let me investigate it on my own first!"):
#     pass
# st.write(external_reconciliation_adj_date.columns.tolist())
# import Full_Recon_for_Streamlit
# from Full_Recon_for_Streamlit import recon_summary_credimax

# elif selected_type_of_recon == "Bank Reconciliation":
#     st.write("We have no bank reconciliation system yet, it's under development!")
