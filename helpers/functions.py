import pandas as pd

def get_crosstab_simple(df, col1, col2):
    #c = pd.crosstab(df[col1], df[col2], normalize=False,margins=True, margins_name="Total").reset_index()
    c = pd.crosstab(df[col1], df[col2]).reset_index()
    return c


def get_crosstab_percent(df, col1, col2):
    c = (pd.crosstab(df[col1], df[col2], normalize='index')*100).round(1).reset_index()
    return c

def get_filtered_data_by_year(df, year_range_value):
    min_year = int(year_range_value[0])
    max_year = int(year_range_value[1])
    data = df[(df.year.astype(int) >= min_year) & (df.year.astype(int) <= max_year)]
    return data