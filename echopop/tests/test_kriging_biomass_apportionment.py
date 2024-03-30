import pandas as pd
import numpy as np
from echopop.computation.biology import sum_strata_weight , compute_index_aged_weight_proportions , compute_summed_aged_proportions
from echopop.computation.biology import compute_index_unaged_number_proportions , distribute_aged_weight_proportions
from echopop.computation.biology import compute_summed_unaged_weight_proportions , compute_unaged_sex_proportions

def test_sum_strata_weight( mock_survey ):

    #### Pull in mock Survey object
    objS = mock_survey

    ### Re-parameterize `specimen_df` with dummy data 
    objS.biology[ 'specimen_df' ] = pd.DataFrame(
        {
            'stratum_num': np.repeat( [ 0 , 1 , 2 , 4 , 5 ] , 4 ) ,
            'haul_num': np.repeat( [ 1 , 2 , 3 , 4 , 5 ] , 4 ) ,
            'species_id': np.repeat( [ 19350 ] , 20 ) ,
            'length': np.linspace( 10 , 100 , 20 ) ,
            'weight': np.linspace( 1 , 5 , 20 ) ,     
        }
    )

    ### Re-parameterize `length_df` with dummy data
    objS.biology[ 'length_df' ] = pd.DataFrame(
        {
            'stratum_num': np.repeat( [ 0 , 1 , 2 , 4 , 5 ] , 4 ) ,
            'haul_num': np.repeat( [ 1 , 2 , 3 , 4 , 5 ] , 4 ) ,
            'species_id': np.repeat( [ 19350 ] , 20 ) ,
            'length': np.linspace( 10 , 100 , 20 ) ,
            'length_count': np.linspace( 10 , 100 , 20 ) ,     
        }
    )

    ### Re-parameterize `catch_df` with dummy data
    objS.biology[ 'catch_df' ] = pd.DataFrame(
        {
            'stratum_num': [ 0 , 1 , 2 , 4 , 5 ] ,
            'haul_num': [ 1 , 2 , 3 , 4 , 5 ] ,
            'haul_weight': [ 51.4 , 0.6 , 81.7 , 16.2 , 12.9 ] ,
        }
    )

    ### Evaluate object for later comparison 
    object_weight_strata_aged_unaged , object_weight_strata = sum_strata_weight( objS.biology[ 'catch_df' ] ,
                                                                                 objS.biology[ 'specimen_df' ] )

    #----------------------------------
    ### Run tests: `sum_strata_weight`
    #----------------------------------
    ### Evaluate shape
    # ---- `object_weight_strata`
    assert object_weight_strata.shape == tuple( [ 5 , 2 ] )
    # ---- `object_weight_strata_aged_unaged`
    assert object_weight_strata_aged_unaged.shape == tuple( [ 10 , 3 ] )

    ### Evaluate value equality
    # ---- `object_weight_strata`
    check_values = np.array( [ 56.663158 , 9.231579 , 93.700000 , 31.568421 , 31.636842 ] )
    assert np.allclose( check_values , object_weight_strata.weight_stratum_all )

    # ---- `object_weight_strata_aged_unaged`
    check_values = np.array( [ 51.400000 , 0.600000 , 81.700000 , 16.200000 , 12.900000 ,
                            5.263158 , 8.631579 , 12.000000 , 15.368421 , 18.736842  ] )
    assert np.allclose( check_values , object_weight_strata_aged_unaged.stratum_weight )

def test_compute_index_aged_weight_proportions( mock_survey ):
    
    #### Pull in mock Survey object
    objS = mock_survey

    ### Re-parameterize `specimen_df` with dummy data 
    objS.biology[ 'specimen_df' ] = pd.DataFrame(
        {
            'stratum_num': np.repeat( [ 0 , 1 ] , 4 ) ,
            'sex': np.tile( [ 'male' , 'female' ] , 4 ) ,
            'haul_num': np.tile( [ 1 , 2 ] , 4 ) ,
            'species_id': np.repeat( [ 19350 ] , 8 ) ,
            'length': [ 12 , 12 , 19 , 19 , 12 , 12 , 19 , 19 ] ,
            'weight': [ 2 , 3 , 8 , 7 , 1 , 4 , 9 , 6 ] ,
            'age': [ 1 , 1 , 2 , 2 , 1 , 1 , 2 , 2 ]    
        }
    )

    ### Length interval
    objS.biology[ 'distributions' ][ 'length' ][ 'length_interval_arr' ] = np.linspace( 9 , 21 , 3 )
    
    ### Age interval
    objS.biology[ 'distributions' ][ 'age' ][ 'age_interval_arr' ] = np.array( [ 0.5 , 1.5 , 2.5 ] )

    ### Evaluate object for later comparison 
    obj_props_wgt_len_age_sex = compute_index_aged_weight_proportions( objS.biology[ 'specimen_df' ] ,
                                                                       objS.biology[ 'distributions' ][ 'length' ][ 'length_interval_arr' ] ,
                                                                       objS.biology[ 'distributions' ][ 'age' ][ 'age_interval_arr' ] )
    ###--------------------------------
    ### Expected outcomes
    ###--------------------------------
    # ---- Expected dimensions of `obj_props_wgt_len_age_sex`   
    expected_dimensions = tuple( [ 16 , 11 ] )
    
    # ---- Expected dataframe output
    expected_output = pd.DataFrame( {
        'stratum_num': np.repeat( [ 0 , 1 ] , 8 ).astype( np.int64 ) ,
        'species_id': np.repeat( 19350 , 16 ).astype( np.int64 ) ,
        'sex': np.tile( [ 'female' , 'female' , 'female' , 'female' ,
                          'male' , 'male' , 'male' , 'male' ] , 2 ).astype( object ) ,
        'length_bin': pd.cut( [ 12 , 12 , 19 , 19 , 12 , 12 , 19 , 19 ,
                                12 , 12 , 19 , 19 , 12 , 12 , 19 , 19 ] ,
                             np.linspace( 9 , 21 , 3 ) ) ,
        'age_bin': pd.cut( [ 1 , 2 , 1 , 2 , 1 , 2 , 1 , 2 ,
                              1 , 2 , 1 , 2 , 1 , 2 , 1 , 2 ] ,
                          np.array( [ 0.5 , 1.5 , 2.5 ] ) ) ,
        'weight_all': [ 3.0 , 0.0 , 0.0 , 7.0 , 2.0 , 0.0 , 0.0 , 8.0 ,
                        4.0 , 0.0 , 0.0 , 6.0 , 1.0 , 0.0 , 0.0 , 9.0 ] ,
        'weight_adult': [ 0.0 , 0.0 , 0.0 , 7.0 , 0.0 , 0.0 , 0.0 , 8.0 ,
                          0.0 , 0.0 , 0.0 , 6.0 , 0.0 , 0.0 , 0.0 , 9.0 ] ,
        'total_weight_sex_all': np.repeat( 10.0 , 16 ) ,
        'total_weight_sex_adult': [ 7.0 , 7.0 , 7.0 , 7.0 , 8.0 , 8.0 , 8.0 , 8.0 ,
                                    6.0 , 6.0 , 6.0 , 6.0 , 9.0 , 9.0 , 9.0 , 9.0 ] ,
        'proportion_weight_sex_all': [ 0.3 , 0.0 , 0.0 , 0.7 , 0.2 , 0.0 , 0.0 , 0.8 ,
                                       0.4 , 0.0 , 0.0 , 0.6 , 0.1 , 0.0 , 0.0 , 0.9 ] ,
        'proportion_weight_sex_adult': [ 0.0 , 0.0 , 0.0 , 1.0 , 0.0 , 0.0 , 0.0 , 1.0 ,
                                         0.0 , 0.0 , 0.0 , 1.0 , 0.0 , 0.0 , 0.0 , 1.0 ] } )
    expected_output[ 'length_bin' ] = pd.IntervalIndex( expected_output[ 'length_bin' ] )
    expected_output[ 'length_bin' ] = pd.Categorical( expected_output[ 'length_bin' ] , 
                                                      categories =  expected_output[ 'length_bin' ].unique( ) , 
                                                      ordered = True )
    expected_output[ 'age_bin' ] = pd.IntervalIndex( expected_output[ 'age_bin' ] )
    expected_output[ 'age_bin' ] = pd.Categorical( expected_output[ 'age_bin' ] , 
                                                 categories = expected_output[ 'age_bin' ].unique( ) , 
                                                 ordered=True)

    #----------------------------------
    ### Run tests: `compute_index_aged_weight_proportions`
    #----------------------------------
    ### Process the specimen data 
    ### Check shape 
    assert obj_props_wgt_len_age_sex.shape == expected_dimensions

    ### Check datatypes
    assert np.all( obj_props_wgt_len_age_sex.dtypes == expected_output.dtypes )
    
    ### Check data value equality
    assert expected_output.equals( obj_props_wgt_len_age_sex )
    

def test_compute_summed_aged_proportions( ):

    ### Mock data for `proportions_weight_length_age_sex`
    test_proportions_weight_length_age_sex = pd.DataFrame(
        {
            'stratum_num': np.repeat( [ 0.0 , 1.0 ] , 4 ) ,
            'sex': np.tile( [ 'male' , 'female' ] , 4 ) ,
            'weight_all': [ 1.0 , 3.0 , 2.0 , 4.0 , 0.0 , 6.0 , 3.0 , 3.0 ] ,
            'weight_adult': [ 0.0 , 1.5, 2.0 , 4.0 , 0.0 , 4.0 , 3.0 , 3.0 ]
        }
    )

    ### Mock data for `weight_strata`
    test_weight_strata = pd.DataFrame(
        {
            'stratum_num': [ 0.0 , 1.0 ] ,
            'weight_stratum_all': [ 10.0 , 100.0 ]
        }
    )
    
    ### Evaluate for later comparison 
    eval_aged_sex_proportions , eval_aged_proportions = compute_summed_aged_proportions( test_proportions_weight_length_age_sex ,
                                                                                         test_weight_strata )
    ###--------------------------------
    ### Expected outcomes
    ###--------------------------------
    ### `eval_aged_sex_proportions`
    # ---- Expected dimensions
    expected_dimensions_aged_sex_proportions = tuple( [ 4 , 4 ] )
    # ---- Expected dataframe output
    expected_output_aged_sex_proportions = pd.DataFrame( {
        'stratum_num': np.repeat( [ 0.0 , 1.0 ] , 2 ) ,
        'sex': np.tile( [ 'female' , 'male' ] , 2 ) ,
        'proportion_weight_all': [ 0.70 , 0.30 , 0.09 , 0.03 ] ,
        'proportion_weight_adult': [ 0.55 , 0.20 , 0.07 , 0.03 ]
    } )

    ### `eval_aged_proportions`
    # ---- Expected dimensions
    expected_dimensions_aged_proportions = tuple( [ 2 , 3 ] )
    # ---- Expected dataframe output
    expected_output_aged_proportions = pd.DataFrame( {
        'stratum_num': [ 0.0 , 1.0 ] ,
        'proportion_weight_all': [ 1.00 , 0.12 ] ,
        'proportion_weight_adult': [ 0.75 , 0.10 ]
    } )

    #----------------------------------
    ### Run tests: `compute_index_aged_weight_proportions`
    #----------------------------------
    ### `eval_aged_sex_proportions`
    # ---- Shape
    assert eval_aged_sex_proportions.shape == expected_dimensions_aged_sex_proportions
    # ---- Datatypes
    assert np.all( eval_aged_sex_proportions.dtypes == expected_output_aged_sex_proportions.dtypes )
    # ---- Dataframe equality
    assert np.all( eval_aged_sex_proportions == expected_output_aged_sex_proportions )

    ### `eval_aged_proportions`
    # ---- Shape
    assert eval_aged_proportions.shape == expected_dimensions_aged_proportions
    # ---- Datatypes
    assert np.all( eval_aged_proportions.dtypes == expected_output_aged_proportions.dtypes )
    # ---- Dataframe equality
    assert np.all( eval_aged_proportions == expected_output_aged_proportions )

def test_distribute_aged_weight_proportions( ):

    ### Mock data for `proportions_weight_length_age_sex`
    test_proportions_weight_length_age_sex = pd.DataFrame( 
        {
            'stratum_num': np.repeat( [ 0.0 , 1.0 ] , 2 ) ,
            'sex': np.tile( [ 'female' , 'male' ] , 2 ) ,
            'proportion_weight_sex_all': [ 0.50 , 0.50 , 0.25 , 0.50 ] ,
            'proportion_weight_sex_adult': [ 0.50 , 0.25 , 0.00 , 0.25 ]
        } 
    )

    ### Mock data for `aged_sex_proportions`
    test_aged_sex_proportions = pd.DataFrame( {
        'stratum_num': np.repeat( [ 0.0 , 1.0 ] , 2 ) ,
        'sex': np.tile( [ 'female' , 'male' ] , 2 ) ,
        'proportion_weight_all': [ 0.25 , 0.50 , 0.20 , 0.10 ] ,
        'proportion_weight_adult': [ 0.20 , 0.30 , 0.10 , 0.10 ]
    } )

    ### Evaluate for later comparison 
    eval_distributed_aged_weight_proportions = distribute_aged_weight_proportions( test_proportions_weight_length_age_sex ,
                                                                                   test_aged_sex_proportions )
    
    ###--------------------------------
    ### Expected outcomes
    ###--------------------------------
    ### `eval_aged_sex_proportions`
    # ---- Expected dimensions
    expected_dimensions_distributed_aged_weight_proportions = tuple( [ 4 , 4 ] )
    # ---- Expected dataframe output
    expected_output_distributed_aged_weight_proportions = pd.DataFrame( {
        'stratum_num': np.repeat( [ 0.0 , 1.0 ] , 2 ) ,
        'sex': np.tile( [ 'female' , 'male' ] , 2 ) ,
        'normalized_proportion_weight_all': [ 0.125 , 0.250 , 0.050 , 0.050 ] ,
        'normalized_proportion_weight_adult': [ 0.100 , 0.150 , 0.025 , 0.050 ]
    } )

    #----------------------------------
    ### Run tests: `distribute_aged_weight_proportions`
    #----------------------------------
    ### `eval_aged_sex_proportions`
    # ---- Shape
    assert eval_distributed_aged_weight_proportions.shape == expected_dimensions_distributed_aged_weight_proportions
    # ---- Datatypes
    assert np.all( eval_distributed_aged_weight_proportions.dtypes == expected_output_distributed_aged_weight_proportions.dtypes )
    # ---- Dataframe equality
    eval_distributed_aged_weight_proportions.equals( expected_output_distributed_aged_weight_proportions )

def test_compute_index_unaged_number_proportions( mock_survey ):

    #### Pull in mock Survey object
    objS = mock_survey

    ### Re-parameterize `length_df` with dummy data 
    objS.biology[ 'length_df' ] = pd.DataFrame(
        {
            'stratum_num': np.repeat( [ 0 , 1 ] , 4 ) ,
            'sex': np.tile( [ 'male' , 'female' ] , 4 ) ,
            'species_id': np.repeat( [ 19350 ] , 8 ) ,
            'length': [ 12 , 12 , 19 , 19 , 12 , 12 , 19 , 19 ] ,
            'length_count': [ 5 , 10 , 15 , 20 , 20 , 15 , 10 , 5 ]
        }
    )

    ### Length interval
    objS.biology[ 'distributions' ][ 'length' ][ 'length_interval_arr' ] = np.linspace( 9 , 21 , 3 )

    ### Evaluate object for later comparison 
    obj_proportions_unaged_length = compute_index_unaged_number_proportions( objS.biology[ 'length_df' ] ,
                                                                             objS.biology[ 'distributions' ][ 'length' ][ 'length_interval_arr' ] )
    
    ###--------------------------------
    ### Expected outcomes
    ###--------------------------------
    ### `eval_aged_sex_proportions`
    # ---- Expected dimensions
    expected_dimensions_proportions_unaged_length = tuple( [ 4 , 4 ] )
    # ---- Expected dataframe output
    expected_output = pd.DataFrame( {
        'stratum_num': np.repeat( [ 0 , 1 ] , 2 ).astype( np.int64 ) ,
        'species_id': np.repeat( [ 19350 ] , 4 ).astype( np.int64 ) ,
        'length_bin': pd.IntervalIndex.from_arrays( np.tile( [9.0 , 15.0 ] , 2 ) , 
                                                    np.tile( [ 15.0 , 21.0 ] , 2 ) , 
                                                    closed = 'right' ) ,
        'proportion_number_all': [ 0.3 , 0.7 , 0.7 , 0.3 ]
    } )
    expected_output[ 'length_bin' ] = pd.IntervalIndex( expected_output[ 'length_bin' ] )
    expected_output[ 'length_bin' ] = pd.Categorical( expected_output[ 'length_bin' ] , 
                                                      categories =  expected_output[ 'length_bin' ].unique( ) , 
                                                      ordered = True )
    #----------------------------------
    ### Run tests: `compute_index_unaged_number_proportions`
    #----------------------------------
    ### `eval_aged_sex_proportions`
    # ---- Shape
    assert obj_proportions_unaged_length.shape == expected_dimensions_proportions_unaged_length
    # ---- Datatypes
    assert np.all( obj_proportions_unaged_length.dtypes == expected_output.dtypes )
    # ---- Dataframe equality
    assert obj_proportions_unaged_length.equals( expected_output )

def test_compute_summed_unaged_weight_proportions( ):

    ### Create mock `proportions_unaged_length`
    test_proportions_unaged_length = pd.DataFrame( {
        'stratum_num': np.repeat( [ 0 , 1 ] , 3 ) ,
        'species_id': np.repeat( 19880 , 6 ) , 
        'length_bin': [ 'small' , 'medium' , 'big' , 
                        'small' , 'medium' , 'big' ] ,
        'proportion_number_all': [ 0.1 , 0.85 , 0.05 ,
                                   0.0 , 0.75 , 0.25 ]
    } ) 

    ### Create mock `length_weight_df`
    test_length_weight_df = pd.DataFrame( {
        'length_bin': [ 'small' , 'small' , 'small' ,
                        'medium' , 'medium' , 'medium' ,
                        'big' , 'big' , 'big' ] ,
        'sex': [ 'all' , 'male' , 'female' ,
                 'all' , 'male' , 'female' ,
                 'all' , 'male' , 'female' ] ,
        'weight_modeled': [ 0.5 , 0.242424 , 0.32562252 ,
                            1.0 , 1.141414 , 0.99999999 ,
                            2.0 , 1.942424 , 2.12313131 ]
    } )

    ### Evaluate for later comparison 
    eval_proportions_unaged_weight_length = compute_summed_unaged_weight_proportions( test_proportions_unaged_length , 
                                                                                      test_length_weight_df )
    
    ###--------------------------------
    ### Expected outcomes
    ###--------------------------------
    ### `eval_proportions_unaged_weight_length`
    # ---- Expected dimensions
    expected_dimensions_proportions_unaged_length_sex = tuple( [ 6 , 4 ] )
    # ---- Expected dataframe output
    expected_output = pd.DataFrame( {
        'stratum_num': np.repeat( [ 0 , 1 ] , 3 ) ,
        'species_id': np.repeat( [ 19880 ] , 6 ) ,
        'length_bin': [ 'small' , 'medium' , 'big' , 
                        'small' , 'medium' , 'big' ] ,
        'proportion_weight_length': [ 0.05 , 0.85 , 0.10 ,
                                      0.0 , 0.60 , 0.40 ]
    } )
    #----------------------------------
    ### Run tests: `compute_index_unaged_number_proportions`
    #----------------------------------
    ### `eval_aged_sex_proportions`
    # ---- Shape
    assert eval_proportions_unaged_weight_length.shape == expected_dimensions_proportions_unaged_length_sex
    # ---- Datatypes
    assert np.all( eval_proportions_unaged_weight_length.dtypes == expected_output.dtypes )
    # ---- Dataframe equality
    assert eval_proportions_unaged_weight_length.equals( expected_output )

def test_compute_unaged_sex_proportions( ):

    ### Mock data for `length_data`
    test_length_data = pd.DataFrame(
        {
            'stratum_num': np.repeat( [ 0 , 1 ] , 4 ) ,
            'sex': np.tile( [ 'male' , 'female' ] , 4 ) ,
            'species_id': np.repeat( [ 19350 ] , 8 ) ,
            'length': [ 12 , 12 , 19 , 19 , 12 , 12 , 19 , 19 ] ,
            'length_count': [ 5 , 10 , 15 , 20 , 20 , 15 , 10 , 5 ]
        }
    )

    ### Mock data for `length_intervals`
    test_length_intervals = np.linspace( 9 , 21 , 3 )

    ### Mock data for `length_weight_df`
    test_length_weight_df = pd.DataFrame(
        {
            'length_bin': pd.cut( [ 12 , 12 , 12 , 19 , 19 , 19 ,
                                    12 , 12 , 12 , 19 , 19 , 19 ] ,
                             np.linspace( 9 , 21 , 3 ) ) ,
            'sex': [ 'male' , 'female' , 'all' , 'male' , 'female' , 'all' ,
                     'male' , 'female' , 'all' , 'male' , 'female' , 'all' ] ,
            'weight_modeled': [ 1 , 3 , 2 , 6 , 8 , 7 ,
                                4 , 2 , 3 , 9 , 11 , 10 ]
        }
    )
    test_length_weight_df[ 'length_bin' ] = pd.IntervalIndex( test_length_weight_df[ 'length_bin' ] )
    test_length_weight_df[ 'length_bin' ] = pd.Categorical( test_length_weight_df[ 'length_bin' ] , 
                                                            categories =  test_length_weight_df[ 'length_bin' ].unique( ) , 
                                                            ordered = True )

    ### Mock data for `weight_strata`
    test_weight_strata = pd.DataFrame(
        {
            'stratum_num': [ 0 , 1 ] ,
            'weight_stratum_all': [ 50 , 100 ] ,
        }
    )

    ### Mock data for `weight_strata_aged_unaged`
    test_weight_strata_aged_unaged = pd.DataFrame(
        {
            'stratum_num': [ 0 , 1 , 0 , 1 ] ,
            'stratum_weight': [ 500 , 400 , 50 , 100 ] ,
            'group': [ 'unaged' , 'unaged' , 'aged' , 'aged' ] ,
        }
    )

    ### Evaluate for later comparison 
    eval_proportions_unaged_weight_sex = compute_unaged_sex_proportions( test_length_data , 
                                                                         test_length_intervals ,
                                                                         test_length_weight_df ,
                                                                         test_weight_strata ,
                                                                         test_weight_strata_aged_unaged )  
    
    ###--------------------------------
    ### Expected outcomes
    ###--------------------------------
    # ---- Expected dimensions of `obj_props_wgt_len_age_sex`   
    expected_dimensions = tuple( [ 4 , 3 ] )
    
    # ---- Expected dataframe output
    expected_output = pd.DataFrame( {
        'stratum_num': [ 0 , 0 , 1 , 1 ] ,
        'sex': [ 'female' , 'male' , 'female' , 'male' ] ,
        'proportion_weight_sex': [ 0.607595 , 0.392405 , 0.333333 , 0.666667 ]
    } )

    #----------------------------------
    ### Run tests: `compute_index_aged_weight_proportions`
    #----------------------------------
    ### Process the specimen data 
    ### Check shape 
    assert eval_proportions_unaged_weight_sex.shape == expected_dimensions

    ### Check datatypes
    assert np.all( eval_proportions_unaged_weight_sex.dtypes == expected_output.dtypes )
    
    ### Check data value equality
    # ---- `stratum_num`
    assert np.all( eval_proportions_unaged_weight_sex.stratum_num == expected_output.stratum_num )
    assert np.allclose( eval_proportions_unaged_weight_sex.proportion_weight_sex , expected_output.proportion_weight_sex )