import pandas as pd
import numpy as np
import re

def clean_data(df):
    # TODO: later: Create a way to pick only the columns that need to stay, default keep all but then add an option to pick    
    _required_columns = df.columns

    df = df[_required_columns]

    df = normalize_columns(df)

    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    return df


def normalize_columns(df):
    """Normalize column names by lowercasing, stripping whitespace, replacing spaces with underscores, and removing special characters."""
    new_columns = []
    for col in df.columns:
        col = str(col).lower()
        
        # Strip leading/trailing whitespaces
        col = col.strip()

        # Replace spaces and special characters with underscores
        col = re.sub(r'[^\w\s-]', '', col)  # Remove special characters except spaces and hyphens
        col = re.sub(r'[\s-]+', "_", col) # Replace spaces and hyphens with underscores

        # Remove leading/trailing underscores
        col = col.strip("_")

        # Handle empty column names
        if not col:
            col = "unamed_column"
        
        new_columns.append(col)
    
    df.columns = new_columns
    return df
