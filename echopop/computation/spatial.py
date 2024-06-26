import pandas as pd
import numpy as np
import geopandas as gpd
import geopy.distance
from typing import Union
from typing import Optional , Tuple
from scipy import interpolate , special
                        
def correct_transect_intervals( dataframe: pd.DataFrame ,
                                threshold: np.float64 = 0.05 ):
    """
    Calculate along-transect intervals and impute erroneous values

    Parameters
    ----------
    dataframe: pd.DataFrame
        DataFrame

    Notes
    -----
    This function calculates the along-track transect interval length and areas.
    It then 'searches' for possible erroneous values at the end of each line 
    and replaces/imputes with alternative lengths/areas.
    """
    return (
            dataframe
                        # Calculate along-transect interval distances
                .pipe( lambda df: df.assign( interval = df[ 'vessel_log_start' ].diff( periods = -1 ).abs( ) ) 
                                    .replace( np.nan , df[ 'vessel_log_end' ].iloc[ -1 ] - df[ 'vessel_log_start' ].iloc[ -1 ] ) )
                # Replace likely erroneous interval lengths associated with the edges of each transect
                .pipe
                ( lambda df: df.assign( median_interval = np.median( df[ 'interval' ] ) )
                                    .assign( interval = lambda x: np.where( np.abs( x[ 'interval' ] - x[ 'median_interval' ] > threshold ) ,
                                                                            x.vessel_log_end - x.vessel_log_start ,
                                                                            x.interval ) ) )
                # Calculate interval area
                .pipe( lambda df: df.assign( interval_area = df[ 'interval' ] * df[ 'transect_spacing' ] ) )                            
                # Keep dataframe tidy by only retaining the necessary columns/variables
                .loc[ : , [ 'latitude' , 'longitude' , 'transect_num' , 'stratum_num' , 'haul_num' , 
                            'interval' , 'interval_area' , 'NASC_all_ages' , 'NASC_no_age1' ] ]
            )


def calculate_start_end_coordinates( group ,
                                     contrast ):
    """
    Calculates start and end latitude/longitude   

    Parameters
    ----------
    group: pd.DataFrameGroupBy
        Grouped DataFrame
    contrast: List
        Target contrast for grouping

    Notes
    -----
    This function calculates the bounding rectangle surrounding the latitude/longitude values
    for each grouped value (e.g. transect)
    """ 

    return (
        group
        .groupby( contrast )
        .apply( lambda x: pd.Series( { 'minimum_longitude': x['longitude'].min() , 
                                       'maximum_longitude': x['longitude'].max() ,
                                       'center_latitude': x[ 'latitude' ].mean() } ) )
        .reset_index( )
    )

def calculate_transect_distance( dataframe ,
                                 contrast = 'transect_num' ):
    """
    Calculates spatial features of each transect    

    Parameters
    ----------
    dataframe: pd.DataFrame
        DataFrame
    contrast: List
        Target contrast for grouping

    Notes
    -----
    This function calculates the bounding rectangle surrounding the latitude/longitude values
    for each transect and stratum, the average spacing between transects, approximate areas 
    relative to each transect, and the distance for each transect
    """ 
    
    ### Calculate mean transect spacinge
    transect_spacing = dataframe.groupby( contrast )[ 'transect_spacing' ].mean().reset_index()
    
    ### Calculate minimum/maximum longitude, mean latitude, spacing, and area
    return (
            dataframe
            .pipe( lambda df: calculate_start_end_coordinates( df , [ contrast ] ) )
            .assign(transect_distance=lambda x: x.apply( lambda row: geopy.distance.distance( 
                    ( row[ 'center_latitude' ] , row[ 'minimum_longitude' ] ) , 
                    ( row[ 'center_latitude' ] , row[ 'maximum_longitude' ] ) ).nm , 
                    axis=1 ) )
            .merge( transect_spacing , on = [ contrast ] )
            .assign( transect_area = lambda x: x.transect_distance * x.transect_spacing )
    )
    
def transform_geometry( dataframe: pd.DataFrame ,
                        dataframe_reference: pd.DataFrame ,
                        longitude_reference: np.float64 ,
                        longitude_offset: np.float64 ,
                        latitude_offset: np.float64 ,
                        projection: str = 'epsg:4326' ,
                        range_output: bool = True ,
                        d_longitude: Optional[ np.float64 ] = None ,
                        d_latitude: Optional[ np.float64 ] = None , ) -> Union[ Tuple[ pd.DataFrame , 
                                                                                       np.float64 ,
                                                                                       np.float64 ] ,
                                                                                pd.DataFrame ]:
    """
    Transforms the geometry of a GeoDataFrame to reference coordinates

    Parameters
    ----------
    dataframe: pd.DataFrame
        DataFrame
    geodataframe_reference: gpd.GeoDataFrame
        Reference GeoDataFrame
    longitude_reference: np.float64
        Reference longitude used to 'center' all coordinates
    longitude_offset: np.float64
        Longitude value used to shift longitude coordinates
    latitude_offset: np.float64
        Latitude value used to shift latitude coordinates
    projection: str
        Projection (EPSG) string
    d_longitude: np.float64
        Total longitudinal distance (degrees) used for standardizing coordinates
    d_latitude: np.float64
        Total longitudinal distance (degrees) used for standardizing coordinates   
    """

    ### Parse longitude and latitude column names
    ref_lat_col = [ col for col in dataframe_reference.columns if 'latitude' in col.lower( ) ][ 0 ]
    ref_lon_col = [ col for col in dataframe_reference.columns if 'longitude' in col.lower( ) ][ 0 ]
    
    ### Interpolate coordinates
    # This transformation will be applied the appropriate datasets
    coordinate_interp = interpolate.interp1d(
        dataframe_reference[ ref_lat_col ] ,
        dataframe_reference[ ref_lon_col ] ,
        kind = 'linear' ,
        bounds_error = False
    )
    
    ### Parse longitude and latitude column names
    lat_col = [ col for col in dataframe.columns if 'latitude' in col.lower( ) ][ 0 ]
    lon_col = [ col for col in dataframe.columns if 'longitude' in col.lower( ) ][ 0 ]
    
    ### Reduce coordinates to prevent issues with unwieldly dataframes
    dataframe_geometry = (
        # dataframe.loc[ : , [ lon_col , lat_col ] ]
        dataframe[ [ lon_col , lat_col ] ]
        .drop_duplicates( )
        .assign( geometry = lambda x: gpd.points_from_xy( x[ lon_col ] , x[ lat_col ] ) )
    )
    
    ### Convert to GeoDataFrame
    geodataframe_geometry = gpd.GeoDataFrame( dataframe_geometry ,
                                              geometry = 'geometry' ,
                                              crs = projection )

    ### Apply transformation to pre-existing coordinates
    geodataframe_transformed = (
        geodataframe_geometry
        .assign( longitude_transformed = lambda df: ( 
                    df.geometry.x - coordinate_interp( df.geometry.y ) + longitude_reference ) 
                )
        .pipe( lambda df: df.assign( geometry = gpd.points_from_xy( df.longitude_transformed , df.geometry.y ) ) )
    )

    ### Calculate geospatial distances in longitudinal and latitudinal axes
    # Based on 'd_longitude' and 'd_latitude' inputs
    # If 'd_longitude' and 'd_latitude' is not defined
    if ( d_longitude is None ) & ( d_latitude is None ):
        d_longitude = geodataframe_transformed.geometry.x.max( ) - geodataframe_transformed.geometry.x.min( )
        d_latitude = geodataframe_transformed.geometry.y.max( ) - geodataframe_transformed.geometry.y.min( )

    ### Apply transformation to coordinates and assign to reduced geodataframe
    geodataframe_result = (
        geodataframe_transformed
        .assign( x_transformed = lambda dfs: ( np.cos( np.pi / 180.0 * dfs.geometry.y ) *
                                               ( dfs.geometry.x - longitude_offset ) /
                                               d_longitude ) ,
                 y_transformed = lambda dfs: ( dfs.geometry.y - latitude_offset ) /
                                               d_latitude ) )  

    ### Merge back with original input data in case of reduction
    if range_output:
        return geodataframe_result.merge( dataframe , on = [ lon_col , lat_col ] ) , d_longitude , d_latitude
    else:
        return geodataframe_result.merge( dataframe , on = [ lon_col , lat_col ] )
    
def lag_distance_griddify( dataset1 ,
                           dataset2 ):
    """
    Calculate point-to-point distances between two gridded dataframes

    Parameters
    ----------
    dataframe1: pd.DataFrame
        Background dataframe mesh that represents the "complete" field 
        of values
    dataframe2: pd.DataFrame
        Georeferenced dataframe
        
    Notes
    ----------
    This is used to effectively create a matrix comprising gridded 
    distance values (i.e. 'griddify').
    """
    ###
    if all( isinstance( dataset , pd.DataFrame ) for dataset in ( dataset1 , dataset2 ) ):
        ### 
        x_distance = np.subtract.outer( dataset1.x_transformed.values ,
                                        dataset2.x_transformed.values )
        y_distance = np.subtract.outer( dataset1.y_transformed.values ,
                                        dataset2.y_transformed.values )
    elif all( isinstance( dataset , np.ndarray ) for dataset in ( dataset1 , dataset2 ) ):
        ###
        x_distance = np.subtract.outer( dataset1 , dataset1 )
        y_distance = np.subtract.outer( dataset2 , dataset2 )    
    
    return np.sqrt( x_distance * x_distance + y_distance * y_distance )

def local_search_index( dataframe_mesh ,
                        dataframe ,
                        k_max ):
    """
    Search for the closest georeferenced values

    Parameters
    ----------
    dataframe_mesh: pd.DataFrame
        Background dataframe mesh that represents the "complete" field 
        of values
    dataframe: pd.DataFrame
        Georeferenced dataframe
    k_max: int
        Maximum number of nearest neighbors allowed
        
    Notes
    ----------
    This finds the 'k' number of nearest neighboring geoferenced values.
    """
    
    ###
    distance_matrix = lag_distance_griddify( dataframe_mesh , dataframe )
    
    ###
    sorted_distance_matrix = np.argpartition( distance_matrix , k_max , axis = 1 )

    return distance_matrix , sorted_distance_matrix[ : , : k_max ]

def grid_cv( biomass_density_df: pd.DataFrame ,
             kriged_results: pd.DataFrame ,
             kriging_config: dict ):
     ### Calculate grid CV  
    biomass_density_adult = ( 
        biomass_density_df
        .loc[ lambda df: df.sex == 'all' ] 
        .drop_duplicates( subset = [ 'transect_num' , 'latitude' , 'longitude' , 'stratum_num' ] ) 
    ) 
    
    ### --------------------------------------------------------------- 
    ### !!! TODO:  
    ### While `C0` produces a similar standard deviation as the original 
    ### code, `Bn` does not. This discrepancy results in an order of  
    ### magnitude change in the resulting `biomass_adult_cell_CV` estimate. 
    ### The source of this error stems from `kriged_results.B_a_adult_mean` 
    ### whereby the right-tail of the `B_a_adult_mean` distribution is  
    ### substantially shorter than from values (`biomass_density_adult_mean`) 
    ### produced in the original code. This therefore relates to Issue #202. 
    ### --------------------------------------------------------------- 
    C0 = np.std( biomass_density_adult.B_a , ddof = 1 ) ** 2 
    Bn = np.nansum( kriged_results.B_a_adult_mean * kriged_results.cell_area_nmi2 ) * 1e-9 
    kriged_results = ( 
        kriged_results 
        .assign( biomass_adult_cell_CV = lambda df: ( 
            kriging_config[ 'A0' ] * 
            np.sqrt( kriged_results.B_a_adult_prediction_variance * C0 ) * 
            1e-9 / 
            Bn * 
            np.sqrt( len( kriged_results.B_a_adult_prediction_variance ) ) 
        ) ) 
    ) 

    ### Carriage return
    return kriged_results