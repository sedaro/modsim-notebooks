## Sedaro Validaton Notebook
### Orbit Propagation

This validation notebook covers the Sedaro orbit propagator. We will compare results from a public Sedaro scenario to a reference propagator and visualize the resulting errors. The reference scenario includes 191 space objects spanning orbital configurations between LEO and GEO, with a subset configured to isolate drag and SRP effects.

Reference values for this validation are derived from the NASA General Mission Analysis Tool (GMAT), Version R2022a.

> GMAT is a software system for space mission design, navigation, and optimization applicable to missions anywhere in the solar system ranging from low Earth orbit to lunar, Libration point, and deep space missions. The system contains high-fidelity space system models, optimization and targeting, built-in scripting and programming infrastructure, and customizable plots, reports and data products that enable flexible analysis and solutions for custom and unique applications. GMAT can be driven from a fully featured, interactive Graphical User Interface (GUI) or from a custom script language.

For more information about the reference tool, visit the links below.

- https://opensource.gsfc.nasa.gov/projects/GMAT/index.php
- https://sourceforge.net/projects/gmat/files/GMAT/GMAT-R2022a/

This validation was run against the following public validation scenario, available to all users of Sedaro:

- FIXME: Add shareable link

Steps to reproduce our results fully or in part are included below. For convenience, we include in this repository the fully-populated Python notebook in original and PDF forms.


### Reproducing our Results

To ensure reproducibility, the directory containing this notebook also includes a `requirements.txt` file that specifies the exact package versions that were used. To create a similar environment, use the following sequence of commands with Python `3.11` and the built-in `venv` package. See the [venv documentation](https://docs.python.org/3/library/venv.html) for more details on how this works.

- In a unix-like terminal:

    ```bash
    > python -m venv .venv
    > source .venv/bin/activate
    > pip install -r requirements.txt
    ```

- In a Windows `cmd.exe` terminal:
    ```bat
    C:\> python -m venv .venv
    C:\> .venv\Scripts\activate.bat
    C:\> pip install -r requirements.txt
    ```

- In Windows PowerShell:

    ```bat
    C:\> python -m venv .venv
    C:\> .venv\Scripts\Activate.ps1
    C:\> pip install -r requirements.txt
    ```

After configuring your environment as described above, open `gravity.ipynb` and run all cells.


### Reproducing our GMAT Reference Data

This repository includes pre-generated output from GMAT in the `reference_data/` directory. Reproducing those results as well requires a local install of the GMAT software. The following process creates the GMAT results:

- Remove the files in `reference_data/` as they will be overwritten by the following process.
- Update `generate_orbits.py` variables `DRAG_TEMPLATE` and `SRP_TEMPLATE` to refer to the appropriate spacecraft template branches.
- Run `generate_orbits.py` to create `orbits.json`.
- Run `build_gmat_script.py` to create the `scenario.script` file in the `reference_data/` directory.
- Install the `EGM2008.cof` file in the GMAT `data/gravity/Earth` directory.
- Open `scenario.script` in GMAT and manually run the scenario. This may take a while and use several GB of memory, so ensure that sufficient resources are available prior to running. The ephemeris files will take approximately 325 MB of storage space.


### Reproducing our Sedaro Scenario

After following the process for GMAT above, the `build_scenario.py` script will create the corresponding Sedaro scenario.

- Create a scenario repository in Sedaro. Update the start and stop times to `2023-11-20 00:00:00` and `2023-11-27 00:00:00`, respectively. 
- Update the `SCENARIO_ID` variable in `build_scenario.py` to point to an existing scenario repository.
- WARNING: running this script on a scenario is a destructive action -- it will remove any existing agents. Ensure that the scenario contains no critical data.
- Run `build_scenario.py`.
- Navigate to the scenario repository in Sedaro and click 'Simulate'.

After completing the steps above, open the `gravity.ipynb` notebook, update the `SCENARIO_BRANCH_ID` variable to point to the new scenario, and run all cells.
