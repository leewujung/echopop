from typing import List, Union, Generator
from pathlib import Path

import pandas as pd


def read_echoview_export():
    pass


def get_transect_num(ev_nasc_files: dict) -> list:
    pass


# based on the current read_echoview_export
def read_echoview_nasc(filename: str, transect_num: int) -> pd.DataFrame:
    pass
    

# based on the current generate_dataframes
def echoview_nasc_to_df(files: Union[str, Path], transect_num: list) -> Generator[pd.DataFrame]:
    # Iterate through directory
    for filename in files:
        # Read in file and impute, if necessary plus validate columns and dtypes
        yield read_echoview_nasc(filename, transect_num)


# based on the current export_transect_spacing
def update_transect_spacing(intervals_df: pd.DataFrame, default_transect_spacing: float):
    pass


def merge_echoview_nasc(nasc_path: Union[str, Path], nasc_filename_pattern: str, default_transect_spacing: float):
    # ONLY do data ingestion and organization, not writing out anything

    # Get all echoview NASC files: analysis, cells, intervals, layers
    # -- do not need to validate, since non-existing folders/files will error out automatically
    # -- use .glob to get all NASC-related files
    ev_nasc_files: dict = {
        "analysis": nasc_path.glob("PATTERN"),  # PATTERN built from nasc_filename_pattern
        "cells": nasc_path.glob("PATTERN"),
        "intervals": nasc_path.glob("PATTERN"),
        "layers": nasc_path.glob("PATTERN"),
    }

    # Get all transect numbers
    # -- for each transect number, there should be 4 files
    # -- store only transect numbers with a complete set (4) csv files
    # -- raise warning for transect numbers with an incomplete set (<4) csv files
    transect_num: list = get_transect_num(ev_nasc_files)

    # Read and concat intervals, cells, and layers dataframes
    # -- use current code in consolidate_exports
    # -- but do not worry about validator at this time
    df_intervals: pd.DataFrame = pd.concat(echoview_nasc_to_df(ev_nasc_files["intervals"], transect_num), ...)
    df_cells: pd.DataFrame = pd.concat(echoview_nasc_to_df(ev_nasc_files["cells"], transect_num), ...)
    df_layers: pd.DataFrame = pd.concat(echoview_nasc_to_df(ev_nasc_files["layers"], transect_num), ...)

    # Wrangle cells_df columns

    # Update transect spacing
    # TODO: what does update_transect_spacing do?
    df_intervals = update_transect_spacing(df_intervals, default_transect_spacing)

    # Explicitly merge the 3 dataframes
    # -- do not need group_merge as a separate method
    df_merged: pd.DataFrame
    return df_merged


# TODO: do we need this?
def read_transect_region_file() -> pd.DataFrame:
    # add in this the current code in the if statement
    # if read_transect_region_file:
    pass


# same as the current
def construct_transect_region_key(df_merged: pd.DataFrame, region_class_mapping: dict) -> pd.DataFrame:
    """
    Parameters
    ----------
    df_merged : pd.DataFrame
        output of ingest_echoview_nasc()
    region_class_mapping : dict
        content of configuration_dict["transect_region_mapping"]["parts"]

    Returns
    -------
    df_transect_region_key : pd.DataFrame
    """
    pass


# TODO: do we need this?
def write_transect_region_key(df_transect_region_key: pd.DataFrame):
    """
    Write transect region key excel files

    Parameters
    ----------
    df_transect_region_key : pd.DataFrame
        output from construct_transect_region_key()
    """
    pass


# TODO: are the mean depth and layer height here just for cells with the specified regions?
# the current export_transect_layers()
def compute_depth_layer_height() -> pd.DataFrame:
    pass


# Last section of the current ingest_echoview_exports()
# TODO: in the current code you created interval_copy from the updated df_interval, can you not use df_merged to get the same info?
def consolidate_echoview_nasc(df_merged: pd.DataFrame, region_names: List[str]) -> pd.DataFrame:
    """
    df_merged : pd.DataFrame
        output from merge_echoview_nasc
    region_names : list
        e.g. ['Hake', 'Hake Mix'] or ['Age-1 Hake', 'Age-1 Hake Mix', 'Hake', 'Hake Mix']
    """
    pass


# break up load_data
# -- there is no need to have a one-size-fits-all load_data function
# -- you can validate the biological, stratification, and NASC data
# -- but just read them in is fine: these are all files under our control
# TODO: what does prepare_input_data() do?


# Script to organize NASC file
nasc_path = "SOME_PATH"
nasc_filename_pattern = "SOME_PATTERN"
region_class_mapping = {}  # pattern-label mapping under transect_region_mapping/parts

df_merged = merge_echoview_nasc(nasc_path, nasc_filename_pattern)
df_transect_region_key = construct_transect_region_key(df_merged, region_class_mapping)

# Age-1+
df_nasc_all_ages = consolidate_echoview_nasc(
    df_merged,
    region_names=["Age-1 Hake", "Age-1 Hake Mix", "Hake", "Hake Mix"]
)

# Age-2+ (no age 1)
df_nasc_no_age1 = consolidate_echoview_nasc(
    df_merged,
    region_names=["Hake", "Hake Mix"]
)
