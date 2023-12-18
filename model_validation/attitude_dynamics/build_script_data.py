'''
This script is used to prepare the data needed to run the basilisk script, such
as the physical properties of the satellite and the reaction wheel commands
from the Sedaro simulation. This code is part of the repository for reference,
but it is not necessary to run this file to reproduce our validation results.
However, you can run a validation against your own model by editing the values
of scenario_branch and template_branch below.
'''
import json

import numpy as np
from utils import sedaroLogin

# Script settings

scenario_branch = ''
template_branch = ''
outfile = 'simulation_data/sedaro_data.json'

# Initialize the Sedaro API client
sedaro = sedaroLogin()

# Get the ids of the reaction wheels
vehicle = sedaro.agent_template(template_branch)
wheels = vehicle.ReactionWheel.get_all()
x_wheel_id = next(wheel.id for wheel in wheels if 'X' in wheel.name)
y_wheel_id = next(wheel.id for wheel in wheels if 'Y' in wheel.name)
z_wheel_id = next(wheel.id for wheel in wheels if 'Z' in wheel.name)
# Gather satellite mass and inertia from the template
mass = vehicle.mass
inertia = vehicle.inertia
wheel_inertia = vehicle.block(x_wheel_id).inertia

# Next, get the reaction wheel commands from the scenario simulation results
results = {}
simulation_results = sedaro.scenario(scenario_branch).simulation.results()
for i, agent_id in enumerate(simulation_results.templated_agents):
    agent_results = simulation_results.agent(agent_id)
    elapsed_times = agent_results.block(
        x_wheel_id).commandedTorqueMagnitude.elapsed_time
    x_torque = agent_results.block(x_wheel_id).commandedTorqueMagnitude.values
    y_torque = agent_results.block(y_wheel_id).commandedTorqueMagnitude.values
    z_torque = agent_results.block(z_wheel_id).commandedTorqueMagnitude.values
    position = agent_results.block('root').position.eci.values
    velocity = agent_results.block('root').velocity.values
    attitude_body_eci = agent_results.block('root').attitude.body_eci.values
    results[agent_id] = {
        'elapsed_times': elapsed_times,
        'x_torque': x_torque,
        'y_torque': y_torque,
        'z_torque': z_torque,
        'position': position,
        'velocity': velocity,
        'attitude': attitude_body_eci,
    }


# Finally, save the data to a pickle file
with open(outfile, 'w') as file:
    data = json.dump({
        'mass': mass,
        'inertia': inertia,
        'wheel_inertia': wheel_inertia,
        'results': results,
    }, file, indent=2)
