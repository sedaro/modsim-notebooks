## Sedaro Validaton Notebook
### Relative Motion

This notebook exercises relative motion calculations across distributed agents. The Sedaro computation model is unique in that it allows distributed processing of simulated agents spread across many processes, cores, and virtual machines. Distributed processing can impact the ability of agents within the simulation to get timely information about other participants. Sedaro overcomes this difficulty with interpolation and extrapolation from available data. In general, the distributed-agent relative motion error is driven by the relative velocity between the two agents and a smaller time step on the target produces smaller error. This notebook demonstrates that one can drive down relative motion knowledge error by constraining the time steps of participating agents.

Users can control the time step used for simulations through the `timeStepConstraint` field on the root of templated and peripheral agents. Here, we set the maximum time step to 0.1s for all agents in the scenario.

Future versions of Sedaro will include more sophisticated interpolation and extrapolation methods that can provide better precision with larger time steps.


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

After configuring your environment as described above, open `relative_motion.ipynb` and run all cells.
