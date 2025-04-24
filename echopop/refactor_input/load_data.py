from typing import Union, Dict
from pathlib import Path
import pandas as pd


# Break up load_data() and read_validated_data() into separate functions to load biological, stratification, and kriging data
# Don't worry about validating input files for now

# TODO: vario_krig_para is currently not used, right? If so, remove any related code


def load_biological_data(root_path: Union[str, Path], file_path_dict: Dict) -> Dict[pd.DataFrame]:
    """
    Load biological data from CSV

    Parameters
    ----------
    root_path : str or Path
        Path to the biological data file
    file_path_dict : dict
        Dictionary of paths to individual biological data files

    Returns
    -------
    A dictionary of dataframes containing biological data
    """
    pass


def load_stratification(root_path: Union[str, Path], file_path_dict: Dict) -> Dict[pd.DataFrame]:
    """
    Load stratification schemes from CSV

    Parameters
    ----------
    root_path : str or Path
        Path to stratification CSV
    file_path_dict : dict
        Dictionary of paths to individual stratification files

    Returns
    -------
    A dictionary of dataframes containing bio_strate and geo_strata info
    """
    # `bio_strata` is the current `strata`
    pass


def load_kriging_paramss(root_path: Union[str, Path], file_path_dict: Dict) -> Dict[pd.DataFrame]:
    """
    Load kriging input

    Parameters
    ----------
    root_path : str or Path
        Path to CSV
    file_path_dict : dict
        Dictionary of paths to individual kriging and isobath files

    Returns
    -------
    A dictionary of dataframes containing kriging and isobath info
    """
    pass