import json

import pprint

 

import pandas as pd

from pathlib import Path

import great_expectations as ge

from time import perf_counter

 

# source the data we want to validate

excel_file = Path("poc_expectations.xlsx")

df = pd.read_excel(io=excel_file, sheet_name="data", header=0)

df['F3.to_datetime'] = pd.to_datetime(df["F3"], format="%m%d%Y", errors="coerce")

df["X"] = df.F3.astype('str')

# Scala data frame to realistic sizes

scale_factor = 1_000_000

 

ts = perf_counter()

df = pd.concat([df]*scale_factor, ignore_index=True)

lenDf = len(df)

es = perf_counter()

print(f"After scaling by {scale_factor=}, it took {es-ts=:5.2f} sec. Records = {len(df)}")

 

 

# create ge rules to match our specification

edf = ge.from_pandas(df)

es2 = perf_counter()

print(f"Converted to ge dataframe, it took {es2-es=:5.2f}")

 

r1 = edf.expect_column_to_exist("AccountNumber", result_format="COMPLETE", meta=dict(errno="E1", errmsg="AccountNumber columns does not exist."))

r2 = edf.expect_column_values_to_not_be_null("AccountNumber", result_format="COMPLETE", meta=dict(errno="E2", errmsg="AccountNumber is MANDATORY"))

r3 = edf.expect_column_values_to_not_be_null("F2", result_format="COMPLETE", meta=dict(errno="E3", errmsg="F2 is MANDATORY."))

r4 = edf.expect_column_values_to_not_be_null("F3.to_datetime", result_format="COMPLETE", meta=dict(errno="E4", errmsg="F3 is MANDATORY. Format must be MMDDYYYY"))

# r4alt = edf.expect_column_values_to_match_strftime_format("F3", "%m%d%Y")

# understand role of kwargs (meta=)

# understand how to use conditional expectations (look at pandas doc)

r5 = edf.expect_column_values_to_not_be_null("F1", result_format="COMPLETE", condition_parser="pandas", row_condition='F2 == 5', meta=dict(errno="E5", errmsg="F1 is required when F2 == 5"))

r6 = edf.expect_column_values_to_not_be_null("F4", result_format="COMPLETE", condition_parser="pandas", row_condition='~F1.isna()', meta=dict(errno="E6", errmsg="F4 is required when ~F1.isna()"))

r7 = edf.expect_column_values_to_not_be_null("F5", result_format="COMPLETE", condition_parser="pandas", row_condition='F1 == "US" | F1 == "CANADA"', meta=dict(errno="E7", errmsg='F5 is required when F1 == "US" | F1 == "CANADA"'))

r7alt = edf.expect_column_values_to_not_be_null("F5", result_format="COMPLETE", condition_parser="pandas", row_condition='F1.isin(["US","CANADA","OTHER"])', meta=dict(errno="E8", errmsg='F5 is required when F1.isin(["US","CANADA","OTHER"])'))

r8 = edf.expect_column_values_to_be_in_set("Capital", value_set=['New York'], result_format="COMPLETE", condition_parser="pandas", row_condition='CountryCode == "US"', include_config=True, meta=dict(errno="E9", errmsg='Capital should be New York when CountryCode == "US"'))

r9 = edf.expect_column_values_to_be_in_set("Capital", value_set=['New York','Chicago'], result_format="COMPLETE", condition_parser="pandas", row_condition='CountryCode == "US"', include_config=True, meta=dict(errno="E9", errmsg='Capital should be New York or Chicago when CountryCode == "US"'))

r10 = edf.expect_column_values_to_be_unique("AccountNumber", result_format="COMPLETE", meta=dict(errno="E10", errmsg="AccountNumber should have unique values."))

r11 = edf.expect_column_values_to_be_unique("CountryCode", result_format="COMPLETE", meta=dict(errno="E11", errmsg="CountryCode should have unique values."))

 

es3 = perf_counter()

print(f"Generated expectations in {es3-es2=:5.2f}")

# save expectations above, lets see what they look like

with open("poc_expectations.json", "w") as f:

    f.write(json.dumps(edf.get_expectation_suite(discard_failed_expectations=False).to_json_dict()))

 

allr = [r1, r2, r3, r4, r5, r6, r7, r7alt, r8, r9, r10, r11]

 

summary_results = []

for r in allr:

    # print(r.meta)

    summary_item = dict(errors=not r.success, error_indexes=len(r.result.get("unexpected_index_list", [])))

    summary_item = {**summary_item, **r.meta}

    summary_results.append(summary_item)

 

for summary_result in summary_results:

    pprint.pprint(summary_result)

 

# walk through results to generate output df E+W

 

# AccountNumber columns does not exist, []

# AccountNumber is MANDATORY, [3]

# F2 is MANDATORY, [5]

# F3 is MANDATORY. Format must be MMDDYYYY, [4]

# F1 is required when F2 == 5, [2]

# F4 is required when ~F1.isna(), [3,5]

# F5 is required when F1 == "US" | F1 == "CANADA", [7,8]

# F5 is required when F1.isin(["US","CANADA","OTHER"]), [7,8,9,10]

# Capital should be New York when CountryCode == "US", [10]

# Capital should be New York or Chicago when CountryCode == "US", []

# AccountNumber should have unique values, []

# CountryCode should have unique values, [0, 9, 10]

# test conditions

conditions = ['F2 == 5',

              '~CountryCode.isna()',

              'CountryCode == "US" | CountryCode == "CANADA"',

              'CountryCode.isin(["US","CANADA","OTHER"])',

              'F2 > 4',

              'F2.abs() == 5',

              'F1 <="4" & F3 < 99999999',

              'CountryCode.str.lower().isin(["us","canada","other", "in"])',

              'CountryCode.str.lower() == "sp"',

              'CountryCode.str.contains("jp")',

              'F3.astype("str") == "6012022.0"']

 

for condition in conditions:

    print(f"Trying {condition=}")

    cr = edf.expect_column_values_to_not_be_null("F1", result_format="COMPLETE", condition_parser="pandas", row_condition=condition, meta=dict(errno="E5", errmsg=f"F1 is required when {condition}"))

    print(cr.success, len(cr.result.get("unexpected_index_list", [])))