# -*- coding: utf-8 -*-
"""Created on Mon Apr 20 20:25:53 2026 @author: XCG """
# Read Internal Function
import os
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import date


def internal_reader_func(report_folder):
    temp_list = []

    cols = [0, 8, 9, 14, 15, 19, 24]
    col_names = ["transaction_id", "method_gateway_name", "gateway_id",
                 "amount", "currency", "status", "date"]
    data_types = {
        "transaction_id": object,
        "method_gateway_name": "category",
        "currency": "category",
        "status": "category",
        "gateway_id": object
    }

    for file_name in report_folder:
        file_name.seek(0)

        try:
            df = pd.read_excel(
                file_name,
                usecols=cols,
                names=col_names,
                header=0,
                dtype=data_types
            )
        except Exception:
            file_name.seek(0)

            df = pd.read_csv(
                file_name,
                usecols=cols,
                names=col_names,
                header=0,
                dtype=data_types
            )

        df["source_name"] = file_name.name
        df["date_internal_adj"] = pd.to_datetime(df["date"])
        temp_list.append(df)

    if not temp_list:
        return pd.DataFrame()

    merged_df = pd.concat(temp_list, ignore_index=True)
    return merged_df.add_suffix("_int")


# external_path = r"D:\Pagsmile_datasets\April 2026\Channel Reconciliation\6-MOVII CREDIT CARD\2026 external transactions downloaded"

def external_reader_func(report_folder):
    all_dfs = []  # It is better to collect dfs in a list first
    os.chdir(report_folder)

    for file_names in report_folder:
        df = None

        if file_names.endswith(".xlsx"):
            df = pd.read_excel(file_names)
            df["source_name"] = file_names

        elif file_names.endswith(".csv"):
            df = pd.read_csv(file_names)
            # Add the source name column WITHOUT the suffix yet
            df["source_name"] = file_names

        # If a file was successfully read, add it to our list
        if df is not None:
            all_dfs.append(df)

    # 1. Combine everything into one big DataFrame
    if not all_dfs:
        return pd.DataFrame()

    merged_df = pd.concat(all_dfs, ignore_index=True)

    # 2. Apply the suffix ONCE to all columns at the very end
    merged_df = merged_df.add_suffix("_ext")

    return merged_df
# external_reader_func()
        

# Function for checking the datatypes

# def check_datatype(df):
#     return df.info()
# check_datatype(external_reader_func(df))

# Checking the Unique ID for external

def unique_cols(df): # Not Sure if we actually need this or not!
    # 1. Filter for only 'object' (text) columns
    text_columns = df.select_dtypes(include=['object',"str"])

    # 2. Check for unique values while ignoring NaNs
    unique_data = [
        col for col in text_columns.columns
        if df[col].dropna().is_unique]

    print(f"Unique text columns (ignoring NaNs): {unique_data}")

def reconcile(internal_df, external_df, int_unique_col, ext_unique_col, typeof_recon="left",
              need_match_indicator = True):
    return pd.merge(internal_df,external_df, left_on=int_unique_col, right_on=ext_unique_col,
    how = typeof_recon,indicator=need_match_indicator)

# Filter the Date for this Period
def reconcile_filter_status_date(merge_df_reconciled, date_column,date_1, date_2):

    return merge_df_reconciled.loc[(merge_df_reconciled[date_column] >= date_1) & (merge_df_reconciled[date_column] < date_2)]

# Check for Duplicates

def duplicate_checker(merge_df_reconciled, col_name):
    count_duplicates_int = merge_df_reconciled[col_name].duplicated().sum()
    show_int_duplicates = merge_df_reconciled[merge_df_reconciled[col_name].duplicated(keep=False)]
    show_int_duplicates_empty = pd.DataFrame()
    if count_duplicates_int > 0:
        return show_int_duplicates
    else:
        return show_int_duplicates_empty

# Check for Not Found Transactions

def variance_checker(merge_df_reconciled):
    if "left_only" in merge_df_reconciled["_merge"].values:
        int_not_found = merge_df_reconciled[merge_df_reconciled["_merge"] != "both"]
    else:
        int_not_found = pd.DataFrame()
    return int_not_found

def amount_diff_internal(recon_result_internal,recon_result_external,col_internal_amount,col_external_amount):
    recon_result_internal["internal_diff"] = recon_result_internal[col_internal_amount] - recon_result_external[col_external_amount]
    return recon_result_internal["internal_diff"]

def amount_diff_external(recon_result_external,recon_result_internal,col_external_amount,col_internal_amount):
    recon_result_external["external_diff"] = recon_result_external[col_external_amount] - recon_result_internal[col_internal_amount]
    return recon_result_external["external_diff"]


    
## Calculation of the Fees
# Each Partner is different


# Summary, depends on settlement type of the external file


# Export the result to excel

# file_path_recon = f"recon_file{current_mm} for {filtered_external["Medio Pago"].to_list()[0]} .xlsx"
# os.chdir(r"D:\Pagsmile_datasets\April 2026\Channel Reconciliation\21-PayValida ECUADOR")


# def result_export(file_path_recon,
#                   internal_recon,
#                   external_recon,
#                   internal_duplicates,
#                   external_duplcates,
#                   internal_not_found,
#                   external_not_found,
#                   summary_df=None,  # Changed
#                   summary_df_transctions=None):  # Changed
#
#     with pd.ExcelWriter(file_path_recon, engine='openpyxl') as writer:
#
#         external_recon.to_excel(writer, sheet_name="External_Recon", index=False)
#         internal_recon.to_excel(writer, sheet_name="Internal_Recon", index=False)
#         external_not_found.to_excel(writer, sheet_name="ext_not_found", index=False)
#         external_duplcates.to_excel(writer, sheet_name="ext_duplicates", index=False)
#         internal_not_found.to_excel(writer, sheet_name="int_not_found", index=False)
#         internal_duplicates.to_excel(writer, sheet_name="int_duplicates", index=False)
#
#         # Handle optional DataFrames safely
#         if summary_df is not None and not summary_df.empty:
#             summary_df.to_excel(writer, sheet_name="Summary_Current_MM", index=False)
#
#         if summary_df_transctions is not None and not summary_df_transctions.empty:
#             summary_df_transctions.to_excel(writer, sheet_name="Summary_Curr_MM_TRANSC", index=False)


def result_export(file_path_recon,
                  internal_recon,
                  external_recon,
                  internal_duplicates,
                  external_duplcates,
                  internal_not_found,
                  external_not_found,
                  original_external,
                  original_internal,
                  summary_df=None,
                  summary_df_transctions=None,
                 recon_refund_internal = None,
                 recon_refund_external = None,
                 refunds_summary_for_current_mm=None):
    # List of all DataFrames to export
    dfs = [external_recon, internal_recon, external_not_found,
           external_duplcates, internal_not_found, internal_duplicates,original_external,
            original_internal,summary_df, summary_df_transctions,recon_refund_internal, recon_result_external,
          refunds_summary_for_current_mm]

    # === Clean all DataFrames before export ===
    for df in dfs:
        if df is None or df.empty:
            continue

        for col in df.columns:
            # Convert to string if column looks like large ID or has many digits
            if pd.api.types.is_numeric_dtype(df[col]):
                # If any value has more than 15 digits → treat as text (Excel limit)
                if df[col].astype(str).str.len().max() > 15:
                    df[col] = df[col].astype(str).str.strip()
            else:
                # Convert all other non-numeric columns to clean string
                df[col] = df[col].astype(str).str.strip()

    # === Export to Excel ===
    with pd.ExcelWriter(file_path_recon, engine='openpyxl') as writer:

        external_recon.to_excel(writer, sheet_name="External_Recon", index=False)
        internal_recon.to_excel(writer, sheet_name="Internal_Recon", index=False)
        external_not_found.to_excel(writer, sheet_name="ext_not_found", index=False)
        external_duplcates.to_excel(writer, sheet_name="ext_duplicates", index=False)
        internal_not_found.to_excel(writer, sheet_name="int_not_found", index=False)
        internal_duplicates.to_excel(writer, sheet_name="int_duplicates", index=False)

        if summary_df is not None and not summary_df.empty:
            summary_df.to_excel(writer, sheet_name="Summary_Current_MM")

        if summary_df_transctions is not None and not summary_df_transctions.empty:
            summary_df_transctions.to_excel(writer, sheet_name="Summary_Curr_MM_TRANSC")
                                            
        if recon_refund_internal is not None and not recon_refund_internal.empty:
            recon_refund_internal.to_excel(writer, sheet_name="Ref_Recon_Internal")

        if recon_refund_external is not None and not recon_refund_external.empty:
            recon_refund_external.to_excel(writer, sheet_name="Ref_Recon_External")
        
        if refunds_summary_for_current_mm is not None and not refunds_summary_for_current_mm.empty:
            refunds_summary_for_current_mm.to_excel(writer, sheet_name="Ref-Summary_Curr_MM_TRANSC")