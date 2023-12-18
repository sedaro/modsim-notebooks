## Sedaro Validation Notebook: _Attitude Dynamics_

This directory provides the tools necessary to compare the attitude propagation in Sedaro to that in Basilisk. Basilisk is a software framework for 
astrodynamics simulations developed by the Autonomous Vehicle Systems Lab and Laboratory for Atmospheric and Space
Physics at CU Boulder. More information about Basilisk can be found here: https://hanspeterschaub.info/basilisk/

The method for validating Sedaro's attitude propagation is to run a simulation in Sedaro where three reaction wheels are used to perform attitude maneuvers as a part of a closed-loop feedback algorithm.
We then use the Sedaro results API to get the time series of commanded reaction wheel motor torques (`build_script_data.py`). We then create a Basilisk simulation for each Agent in the Sedaro simulation. The satellite set up in Basilisk will
have the same design specifications as in Sedaro. We will use the commanded torques from Sedaro to command the satellite in Basilisk - an effective open loop system. (`sedaro_RWs_basilisk.py`)

Since the control in Basilisk is open-loop (that is to say, the wheel torques are not dependent on the attitude but are pre-programmed), we expect the attitude to diverge from Sedaro eventually. 
This analogous to commanding the physical twin of the Sedaro model without feedback. How long can we count on Sedaro to reproduce the "true" behavior, and how precisely? 
To find out, we use the Sedaro results API to get the time series of attitude of each agent and compare the results to the Basilisk simulations (`attitude_dynamics.ipynb`).

We've already run two official scenarios as a validation exercise, the results of which are included in the `plots` directory. If you would like to conduct your own validation, there are instructions to do so under "Custom Validation".

### Official Scenario and Included Plots
Each of our official validation scenarios contains 10 Agents which orbit Earth at varying inclinations in LEO. The first scenario (FIXME: sharable link) uses an attitude control algorithm to point the satellite's +Z axis towards the train station which it is the most directly overhead, maximally aligning the +X axis to nadir. The Sedaro simulation results for this scenario can be found at `simulation_data/sedaro_data_active.json`, the Basilisk results are found at `reference_data/basilisk_results_active.json`, and the validation plots at `plots/active_control`.

Sedaro uses the quaternion representation of attitude, while Basilisk reports the Modified Rodrigues Parameters, each as described by Markley and Crassidis [1]. A given attitude quaternion q is equivalently represented as -q. In the attitude plots, we plot q and -q from Sedaro, as the converted attitudes from Basilisk sometimes flip representations. This flipping has no effect on the attitude error plot (`attitude_error.png`).

In the second official validation scenario (FIXME: sharable link), no control is applied to the satellites, such that the attitude only evolves from kinematics and passive dynamics (specifically gravity gradient torque, in this case). In addition to the attitude plots, we have also plotted the wheel speed over time. The wheel speed does not change from motor torques on the wheel (as these are all zero) but  is instead induced from rotation of the satellite body, in agreement with the Basilisk results.

### Custom Plots

The plots found in `plots/` were generated by the notebook `attitude_dynamics.ipynb`. In order to do so, you'll need the python modules in `requirements.txt`; instructions on how to set up a `venv` with these modules included is included in `attitude_dynamics.ipynb`

If you run the notebook without editing it, new directories will be created and populated with the plots found in `plots/active_control`. You can edit this notebook to plot any other parameters of interest. For example, the Basilisk and Sedaro results notably both include gravity gradient torque, which could easily be plotted by modifying the notebook.

### Custom Validation

If you would like to conduct validation of attitude dynamics with your own model, you can use the scripts and notebooks included in this directory to prepare a Sedaro model, retrieve your simulation results, run a Basilisk simulation, and create new comparison plots. This will require you to install Basilisk manually, as it cannot be installed with pip. Instructions to do so can be found here: https://hanspeterschaub.info/basilisk/Install.html. You will also need to install the python modules in `requirements.txt`.

First, you'll need an Agent with three reaction wheels with body frame vectors along the X, Y, and Z axes (alternatively, you can change the reaction wheel instantiation in `sedaro_RWs_basilisk.py` to use your reaction wheel configuration) with "X", "Y", and "Z" in their respective names. (Once again, you can violate this by changing the `next` searches in `attitude_dynamics.ipynb` and `build_script_data.py`.) 

For the best results, the timesteps utilized by Sedaro and Basilisk should be the same. You can use `configure_agent_template.ipynb` to set the Sedaro GNC to be constant, and then set `simulationTimeStep` in `sedaro_RWs_basilisk.py` to the same value. If you'd like to add the train stations (or a similar target deck) to your scenario, you can use `build_scenario.ipynb` to load the stations stored in `reference_data/stations.csv`.

Once your Agent Template and Scenario are set up, simulate your Scenario. Then do the following:
1. Edit `build_script_data.py` to use the branch IDs of your Scenario and template branches as `scenario_branch` and `template_branch`. Then run the script `python build_script_data.py`. You should see `outfile = 'simulation_data/sedaro_data.json` populated with your simulation data.
2. Run `sedaro_RWs_basilisk.py`, which builds and executes the Basilisk simulation. You should see the simulation results at `results_file_out = 'reference_data/basilisk_results.json'`.
3. Edit `attitude_dynamics.ipynb` to use your `scenario_branch_id`, `template_branch`,  and `basilisk_results_file = 'reference_data/basilisk_results.json'`. Then run the notebook, and you should see your plots appear in `plots/attitude` and `plots/wheels`.

### References
[1] Markley, Landis & Crassidis, John. (2014). Fundamentals of Spacecraft Attitude Determination and Control. 10.1007/978-1-4939-0802-8. 