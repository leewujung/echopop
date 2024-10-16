import numpy as np
import pandas as pd

from ..utils.input_checks_read import check_and_read


class LoadBioData:  # TODO: Does it make sense for this to be a class?
    """
    This class loads and checks those files
    associated with the biological data.

    Parameters
    ----------
    survey : Survey
        An initialized Survey object. Note that any change to
        self.survey will also change this object.
    """

    def __init__(self, survey=None):

        self.survey = survey

        # expected columns for length Dataframe
        self.len_cols_types = {
            "haul_num": int,
            "species_id": int,
            "sex": np.int8,
            "length": np.float64,
            "length_count": np.float64,
        }

        # expected columns for specimen Dataframe
        self.spec_cols_types = {
            "haul_num": int,
            "species_id": int,
            "sex": np.int8,
            "length": np.float64,
            "weight": np.float64,
            "age": np.float64,
        }

        # expected columns for catch Dataframe
        self.catch_cols_types = {
            "haul_num": int,
            "species_id": int,
            "haul_weight": np.float64,
        }

        # Species mapping from short species name to species_id
        self._species_id_mapping = {
            "pacific_hake": 22500,
            # "krill": 1234  # placeholder
        }

        # expected columns for haul_to_transect_mapping Dataframe
        self.haul_to_transect_mapping_cols_types = {"haul_num": int, "transect_num": int}

        self._load_length_data()
        self._load_specimen_data()
        self._load_catch_data()
        self._load_haul_to_transect_mapping_data()

    def _extract_target_species(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract target species data by using the species to species_id mapping,
        then remove species_id column from the target Dataframe

        Parameters
        ----------
        df : pd.Dataframe
            Target Dataframe

        Returns
        -------
        Processed Dataframe
        """

        species_id = self._species_id_mapping[self.survey.params["species"]]
        df = df.loc[df["species_id"] == species_id].copy()

        return df.drop(columns=["species_id"])

    def _process_length_data_df(
        self, df: pd.DataFrame, haul_num_offset: int
    ) -> pd.DataFrame:
        """
        Processes the length dataframe by:
        * Extracting only the target species
        * Applying a haul offset, if necessary
        * Setting the index required for downstream processes

        Parameters
        ----------
        df : pd.Dataframe
            Dataframe holding the length data
        haul_num_offset : int
            The offset that should be applied to the ``haul_num`` column

        Returns
        -------
        Processed Dataframe
        """

        df = self._extract_target_species(df)

        # Apply haul offset
        df.loc[:, "haul_num"] = df["haul_num"] + haul_num_offset

        # TODO: Implement processing of all-age data (including age 1)
        if self.survey.params["exclude_age1"] is False:
            raise NotImplementedError("Including age 1 data has not been implemented!")

        df.set_index("haul_num", inplace=True)

        return df

    def _process_specimen_data(
        self, df: pd.DataFrame, haul_num_offset: int
    ) -> pd.DataFrame:
        """
        Processes the specimen dataframe by:
        * Extracting only the target species
        * Applying a haul offset, if necessary
        * Setting the index required for downstream processes

        Parameters
        ----------
        df : pd.Dataframe
            Dataframe holding the specimen data
        haul_num_offset : int
            The offset that should be applied to the ``haul_num`` column

        Returns
        -------
        Processed Dataframe
        """

        df = self._extract_target_species(df)

        # Apply haul_num_offset
        df.loc[:, "haul_num"] = df["haul_num"] + haul_num_offset

        # TODO: Implement processing of all-age data (including age 1)
        if self.survey.params["exclude_age1"] is False:
            raise NotImplementedError("Including age 1 data has not been implemented!")

        # set and organize index
        df.set_index("haul_num", inplace=True)
        df.sort_index(inplace=True)

        # perform check on data
        if len(df["age"]) - df["age"].isna().sum() < 0.1 * len(df["age"]):
            raise RuntimeWarning("Aged data are less than 10%!\n")

        return df

    def _process_catch_data(
        self, df: pd.DataFrame, haul_num_offset: int
    ) -> pd.DataFrame:
        """
        Processes the catch dataframe by:
        * Extracting only the target species
        * Applying a haul offset, if necessary
        * Setting the index required for downstream processes

        Parameters
        ----------
        df : pd.Dataframe
            Dataframe holding the catch data
        haul_num_offset : int
            The offset that should be applied to the ``haul_num`` column

        Returns
        -------
        Processed Dataframe
        """

        df = self._extract_target_species(df)

        # Apply haul offset
        df.loc[:, "haul_num"] = df["haul_num"] + haul_num_offset

        df.set_index("haul_num", inplace=True)
        df.sort_index(inplace=True)

        return df

    def _process_haul_to_transect_mapping_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processes the haul to transect mapping data by
        * setting the ``haul_num`` column as the Dataframe index
        * sorting the ``haul_num`` index in ascending order

        Parameters
        ----------
        df : pd.Dataframe
            Dataframe holding the haul to transect mapping data

        Returns
        -------
        pd.DataFrame
            Processed haul to transect mapping Dataframe
        """

        # TODO: Implement processing of all-age data (including age 1)
        #    Though I (EM) don't think it applies to the haul-to-transect data files
        if self.survey.params["exclude_age1"] is False:
            raise NotImplementedError("Including age 1 data has not been implemented!")

        # set haul_num as index and sort it
        df.set_index("haul_num", inplace=True)
        df.sort_index(inplace=True)

        return df

    def _load_length_data(self) -> None:
        """
        Loads and prepares data associated with a station
        that records the length and sex of the animal.
        Additionally, it sets survey.length_df using the
        final processed dataframe.
        """

        if self.survey.params["source"] == 3:
            df_us = check_and_read(
                "biological/length/US",
                self.len_cols_types,
                self.survey.params
            )

            df_can = check_and_read(
                "biological/length/CAN",
                self.len_cols_types,
                self.survey.params
            )

            # process US and Canada dataframes
            length_us_df = self._process_length_data_df(df_us, 0)
            length_can_df = self._process_length_data_df(
                df_can, self.survey.params["CAN_haul_offset"]
            )

            # Construct full length dataframe from US and Canada sections
            self.survey.length_df = pd.concat([length_us_df, length_can_df])
        else:
            raise NotImplementedError(
                f"Source of {self.survey.params['source']} not implemented yet."
            )

    def _load_specimen_data(self) -> None:
        """
        Loads and prepares data associated with a station
        that records the length, weight, age, and sex of
        the animal. Additionally, it sets survey.specimen_df
        using the final processed dataframe.
        """

        if self.survey.params["source"] == 3:
            df_us = check_and_read(
                "biological/specimen/US",
                self.spec_cols_types,
                self.survey.params
            )

            df_can = check_and_read(
                "biological/specimen/CAN",
                self.spec_cols_types,
                self.survey.params
            )

            # process US and Canada dataframes
            specimen_us_df = self._process_specimen_data(df_us, 0)
            specimen_can_df = self._process_specimen_data(
                df_can, self.survey.params["CAN_haul_offset"]
            )

            # Construct full specimen dataframe from US and Canada sections
            self.survey.specimen_df = pd.concat([specimen_us_df, specimen_can_df])
        else:
            raise NotImplementedError(
                f"Source of {self.survey.params['source']} not implemented yet."
            )

    def _load_catch_data(self):
        """
        Loads and prepares data associated with a station
        that records the catch data of a particular haul.
        Additionally, it sets survey.catch_df using the
        final processed dataframe.
        """

        if self.survey.params["source"] == 3:
            df_us = check_and_read(
                "biological/catch/US",
                self.catch_cols_types,
                self.survey.params
            )

            df_can = check_and_read(
                "biological/catch/CAN",
                self.catch_cols_types,
                self.survey.params
            )

            # process US and Canada dataframes
            catch_us_df = self._process_catch_data(df_us, 0)
            catch_can_df = self._process_catch_data(
                df_can, self.survey.params["CAN_haul_offset"]
            )

            # Construct full catch dataframe from US and Canada sections
            self.survey.catch_df = pd.concat([catch_us_df, catch_can_df])
        else:

            raise NotImplementedError(
                f"Source of {self.survey.params['source']} not implemented yet."
            )

    def _load_haul_to_transect_mapping_data(self) -> None:
        """
        Loads and prepares the data that maps each ``haul_num`` to a ``transect_num``.
        Additionally, it sets survey.haul_to_transect_mapping_df using the final
        processed dataframe.

        Notes
        -----
        This data is necessary for obtaining subsets of data during transect selection.
        """

        if self.survey.params["source"] == 3:
            df_us = check_and_read(
                "biological/haul_to_transect/US",
                self.haul_to_transect_mapping_cols_types,
                self.survey.params
            )

            df_can = check_and_read(
                "biological/haul_to_transect/CAN",
                self.haul_to_transect_mapping_cols_types,
                self.survey.params
            )

            haul_to_transect_mapping_us_df = self._process_haul_to_transect_mapping_data(df_us)
            haul_to_transect_mapping_can_df = self._process_haul_to_transect_mapping_data(df_can)

            # transect offset is set to zero since we will not have overlapping transects
            # TODO: Is this a necessary variable? If so, we should make it an input to the function.
            CAN_Transect_offset = 0

            # add Canada transect and haul offset
            haul_to_transect_mapping_can_df.index = (
                haul_to_transect_mapping_can_df.index
                + self.survey.params["CAN_haul_offset"]
            )
            haul_to_transect_mapping_can_df["transect_num"] = (
                haul_to_transect_mapping_can_df["transect_num"] + CAN_Transect_offset
            )

            # combine US & CAN data
            self.survey.haul_to_transect_mapping_df = pd.concat(
                [haul_to_transect_mapping_us_df, haul_to_transect_mapping_can_df]
            )
        else:
            raise NotImplementedError(
                f"Source of {self.survey.params['source']} not implemented yet."
            )
