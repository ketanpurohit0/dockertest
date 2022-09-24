import pprint

from pathlib import Path

from time import perf_counter

 

import great_expectations as ge

import pandas as pd

from pydantic import BaseModel

 

# import the rules database

excel_file = Path("poc_expectations.xlsx")

rulesDf = pd.read_excel(io=excel_file, sheet_name="expectations_nmaddr", header=0)

activeRuleDf = rulesDf.loc[(rulesDf["Active"] == "Yes") & (rulesDf["Namespace"] == "nmaddr")]

 

# source the data we want to validate

excel_file = Path("poc_expectations.xlsx")

df = pd.read_excel(io=excel_file, sheet_name="data", header=0, dtype=object)

scale_factor = 1

df = pd.concat([df] * scale_factor, ignore_index=True)

geDf = ge.from_pandas(df)

 

# map to underlying method names

func_map = {"column_exists": geDf.expect_column_to_exist,

            "column_values_to_not_be_null": geDf.expect_column_values_to_not_be_null,

            "column_to_be_in_set": geDf.expect_column_values_to_be_in_set,

            "column_values_to_be_unique": geDf.expect_column_values_to_be_unique,

            "column_values_to_match_date_format": geDf.expect_column_values_to_match_strftime_format

            }

 

# convert human-readable format to machine

date_formats_map = {

    "MMDDYYYY": "%m%d%Y",

    "YYYY-MM-DD": "%Y-%m-%d",

    "YYYYMMDD": "%Y%m%d",

    "DD-MM-YYYY": "%d-%m-%Y",

    "MM-DD-YYYY": "%m-%d-%Y"

}

 

 

# Model for the rules

class RulesModel(BaseModel):

    Active: str

    Level: str

    FieldName: str

    ExpectationType: str

    ExpectedDateFormat: str

    ValueSet: str

    RowCondition: str

    FieldNameForErrorReport: str

    ErrorCode: str

    ErrorMessage: str

    UserComment: str

 

 

# getter from model instance

def has_value(v):

    return False if (v is None or v == "nan") else True

 

 

def get_value(v):

    return v if has_value(v) else None

 

 

def get_column_param(rule: RulesModel):

    col = get_value(rule.FieldName)

    if col:

        return dict(column=col)

    return dict()

 

 

def get_strftime_format_param(rule: RulesModel):

    dfmt = get_value(rule.ExpectedDateFormat)

    if dfmt and dfmt in date_formats_map:

        return dict(strftime_format=date_formats_map[dfmt])

    return dict()

 

 

def get_value_set_param(rule: RulesModel):

    vs = get_value(rule.ValueSet)

    if vs:

        return dict(value_set=[s.strip() for s in vs.split(",")])

    return dict()

 

 

def get_row_condition_param(rule: RulesModel):

    rc = get_value(rule.RowCondition)

    if rc:

        return dict(condition_parser="pandas", row_condition=rc)

    return dict()

 

 

def get_result_format_param():

    return dict(result_format="COMPLETE")

 

 

def get_meta_param(rule: RulesModel):

    return dict(meta=dict(errno=rule.ErrorCode, errmsg=rule.ErrorMessage, field=rule.FieldNameForErrorReport))

 

 

ts = perf_counter()

# Build active rules as models

active_rule_models = [RulesModel(**record) for record in activeRuleDf.to_dict("records")]

 

# for activeRule in active_rule_models:

#     print("===", activeRule.Active, activeRule.ErrorCode)

#     print(f"Column={get_column_param(activeRule)}")

#     print(f"ExpectedDateFormat={get_strftime_format_param(activeRule)}")

#     print(f"ValueSet={get_value_set_param(activeRule)}")

#     print(f"RowCondition={get_row_condition_param(activeRule)}")

#     print(f"Meta={get_meta_param(activeRule)}")

 

#  for every active rule

errors_found=[]

for activeRule in active_rule_models:

    # get method to serve that expectation

    print("***", activeRule.ExpectationType)

    expectation_fn = func_map.get(activeRule.ExpectationType, None)

    if expectation_fn:

        # build parameters as kwargs

        keyword_args = {**get_column_param(activeRule),

                        **get_strftime_format_param(activeRule),

                        **get_value_set_param(activeRule),

                        **get_row_condition_param(activeRule),

                        **get_meta_param(activeRule),

                        **get_result_format_param()

                        }

        # pprint.pprint(keyword_args)

        # run the expectation

        try:

            r = expectation_fn(**keyword_args)

            summary_item = dict(errors=not r.success, error_indexes=(r.result.get("unexpected_index_list", [])))

            summary_item = {**summary_item, **r.meta}

            # pprint.pprint(summary_item)

            errors_found.append(len(summary_item["error_indexes"]))

 

        except TypeError as te:

            print(f"== Exception: {te}")

 

te = perf_counter()

 

print(f"Time to process {len(df)} records is {te-ts} sec. Errors found {sum(errors_found)}")