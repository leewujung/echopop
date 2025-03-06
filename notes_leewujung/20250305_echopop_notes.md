# Echopop notes - March 2025


## 2025/03/05

### References to get workflow running
- reference script and notebook:
    - `/echopop/test_survey.py`
        - this does not run in this directory due to parent reference problem
        - made a new copy outside of `/echopop` (at the root directory of the repo) then it can run -- this is `/test_survey_new.py` below
    - `/test_survey_new.py`
        - made various tweaks and was able to get it to run
        - the gigantic loop in the second half of the workflow runs the following combinations (2x2x2=8)
            - KS and INPFC stratification
            - include or exclude age-1
            - extrapolation or no-extrapolation when kriging
    - RT's testing notebook
        - `/202502_echopop_test/Results_by_year.ipynb`

### Run Echopop workflow for 2021 as an example
- made notebook `echopop_workflow_2021.ipynb`
    - this notebook combines what I found out from `test_survey_new.py` and `/202502_echopop_test/Results_by_year.ipynb`
- updated config files with local directories
    - `config_files/initialization_config_2021.yml`
    - `config_files/survey_year_2021_config.yml`

### Text sent to Alicia
- use the supplied `survey_year_2021_config.yml` and `initialization_config_2021.yml` when instantiating a `Survey` object in the notebook
- in `survey_year_2021_config.yml`:
    - make sure to change `report_path` and `data_root_dir`
        - `report_path` can be overwritten later when using `survey.generate_report()` at the end of the notebook
        - but `data_root_dir` needs to match the input file structure exactly
    - the content of this file should match the structure of the folder I sent
    - the paths specified under the `NASC` entry are generated using `survey.load_acoustic_data()` in the notebook (there's some weird repetition in `load_acoustic_data()` that should be refactored)
- input file structure:
    - `Biological`: biological data (Brandyn has not changed the code to use the master spreadsheet you sent yet)
    - `Exports`: this is an empty folder, and files will be generated here using `survey.load_acoustic_data(ingest_exports="echoview", ...)`. These files can also be supplied directly if they have been generated previously.
    - `Kriging_files`: kriging parameters, nothing needs to change here, though I think there are quite a few redundant files
    - `Raw_NASC`: these are Echoview NASC exports. These files get organized when calling `survey.load_acoustic_data(ingest_exports="echoview", ...)`, which generates the files under the `Exports` folder above
    - `Stratification`: stratification files, nothing needs to change here, though I think there are quite a few redundant files
- from what I saw, missing directories don't get generated automatically (we should fix this in refactoring), so before running `generate_report()`, make sure the target folder already exists. This folder is specified by `report_path` in `survey_year_2021_config.yml`, which can be overwritten by calling `survey.generate_reports(save_directory=report_path)`