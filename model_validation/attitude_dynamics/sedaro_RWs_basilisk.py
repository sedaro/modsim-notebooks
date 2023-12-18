'''
This simulation script uses the Sedaro data to run an open-loop simulation in Basilisk, software framework for 
astrodynamics simulations developed by the Autonomous Vehicle Systems Lab and Laboratory for Atmospheric and Space
Physics at CU Boulder. More information about Basilisk can be found here: https://hanspeterschaub.info/basilisk/
It is not necessary to run this script unless you want to validate your own scenario against Basilisk, as the results 
for our validation are included at reference_data/basilisk_results.json

The setup for the reaction wheel simulation is modified from Basilisk's example simulation scenarioAttitudeFeedbackRW.py
'''
#
#  ISC License
#
#  Copyright (c) 2016, Autonomous Vehicle Systems Lab, University of Colorado at Boulder
#
#  Permission to use, copy, modify, and/or distribute this software for any
#  purpose with or without fee is hereby granted, provided that the above
#  copyright notice and this permission notice appear in all copies.
#
#  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
#  WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
#  ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
#  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
#  ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
#  OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

import json
import os

import numpy as np
from Basilisk import __path__
from Basilisk.architecture import messaging
from Basilisk.fswAlgorithms import inertial3D
from Basilisk.simulation import GravityGradientEffector, reactionWheelStateEffector, simpleNav, spacecraft
from Basilisk.utilities import SimulationBaseClass, macros, simIncludeGravBody, simIncludeRW, unitTestSupport
from utils import progress_bar

bskPath = __path__[0]
fileName = os.path.basename(os.path.splitext(__file__)[0])

def load_sedaro_data(data_file_in:str) -> dict:
    with open(data_file_in, 'rb') as f:
        sedaro_data = json.load(f)
    return sedaro_data

def format_basilisk_results(cumulative_results, id_, times, attitude, omegas, motor_torques, gg_torque):
    cumulative_results[id_] = {
        'time': times.tolist(),
        'attitude_mrp': attitude.tolist(),
        'gg_torque': gg_torque.tolist(),
    }
    omegas = np.array(omegas)
    cumulative_results[id_] |= {f'rw_{d}_omega': omegas[i, :].tolist() for i, d in enumerate('xyz')}
    motor_torques = np.array(motor_torques)
    cumulative_results[id_] |= {f'motor_{d}': motor_torques[i, :].tolist() for i, d in enumerate('xyz')}
    
def build_basilisk_sim(sedaro_data, agent_id):
    # Create simulation variable names
    simTaskName = "simTask"
    simProcessName = "simProcess"
    #  Create a sim module as an empty container
    scSim = SimulationBaseClass.SimBaseClass()
    #  create the simulation process
    dynProcess = scSim.CreateNewProcess(simProcessName)
    # create the dynamics task and specify the integration update time
    simulationTimeStep = macros.sec2nano(1.)
    dynProcess.addTask(scSim.CreateNewTask(simTaskName, simulationTimeStep))

    # initialize spacecraft object and set properties
    scObject = spacecraft.Spacecraft()
    scObject.ModelTag = "sedaro-Sat"
    # define the simulation inertia
    I = np.array(sedaro_data['inertia']).flatten()
    scObject.hub.mHub = sedaro_data['mass']  # kg - spacecraft mass
    scObject.hub.r_BcB_B = [[0.0], [0.0], [0.0]]  # m - position vector of body-fixed point B relative to CM
    scObject.hub.IHubPntBc_B = unitTestSupport.np2EigenMatrix3d(I)
    # add spacecraft object to the simulation process
    scSim.AddModelToTask(simTaskName, scObject, 1)
    
    ## Set up gravitation
    # clear prior gravitational body and SPICE setup definitions
    gravFactory = simIncludeGravBody.gravBodyFactory()
    # setup Earth Gravity Body
    earth = gravFactory.createEarth()
    earth.isCentralBody = True  # ensure this is the central gravitational body
    mu = earth.mu
    # attach gravity model to spacecraft
    scObject.gravField.gravBodies = spacecraft.GravBodyVector(list(gravFactory.gravBodies.values()))
    # Same for gravity gradient
    ggEff = GravityGradientEffector.GravityGradientEffector()
    ggEff.modelTag = scObject.ModelTag
    ggEff.addPlanetName(earth.planetName)
    scObject.addDynamicEffector(ggEff)
    scSim.AddModelToTask(simTaskName, ggEff)
    # create message to specify translational motion
    rv_messageData = messaging.TransRefMsgPayload()
    rv_messageData.r_RN_N = np.array(sedaro_data['results'][agent_id]['position'][0])*1000
    rv_messageData.v_RN_N = np.array(sedaro_data['results'][agent_id]['velocity'][0])*1000
    rv_message = messaging.TransRefMsg().write(rv_messageData)

    ## Reaction wheels
    # Add reaction wheels
    rwFactory = simIncludeRW.rwFactory()
    varRWModel = messaging.BalancedWheels
    RW1 = rwFactory.create('Honeywell_HR16', [1, 0, 0], maxMomentum=50., Omega=0., RWModel=varRWModel
                           )
    RW2 = rwFactory.create('Honeywell_HR16', [0, 1, 0], maxMomentum=50., Omega=0., RWModel=varRWModel
                           )
    RW3 = rwFactory.create('Honeywell_HR16', [0, 0, 1], maxMomentum=50., Omega=0., RWModel=varRWModel
                           )
    for rw in [RW1, RW2, RW3]:
        rw.Js = sedaro_data['wheel_inertia']
        rw.useRWfriction = False
        rw.useMinTorque = False
        rw.useMaxTorque = False

    numRW = rwFactory.getNumOfDevices()
    # Set up RW effector
    rwStateEffector = reactionWheelStateEffector.ReactionWheelStateEffector()
    rwStateEffector.ModelTag = "RW_cluster"
    rwFactory.addToSpacecraft(scObject.ModelTag, rwStateEffector, scObject)
    scSim.AddModelToTask(simTaskName, rwStateEffector, 2)
    # create message to command reaction wheel torque
    rwCommand_messageData = messaging.ArrayMotorTorqueMsgPayload()
    rwCommand_messageData.motorTorque = [0.0]*numRW
    rwCommand_message = messaging.ArrayMotorTorqueMsg().write(rwCommand_messageData)

    ## Add navigation
    sNavObject = simpleNav.SimpleNav()
    sNavObject.ModelTag = "SimpleNavigation"
    scSim.AddModelToTask(simTaskName, sNavObject)
    # setup inertial3D guidance module
    inertial3DObj = inertial3D.inertial3D()
    inertial3DObj.ModelTag = "inertial3D"
    scSim.AddModelToTask(simTaskName, inertial3DObj)
    # Set initial attitude. MRP is the first 3 quaternion elements/ (1+q4)
    inertial3DObj.sigma_R0N = np.array(
        sedaro_data['results'][agent_id]['attitude'][0][:3]
        ) / (1 + sedaro_data['results'][agent_id]['attitude'][0][3])


    ## Add message logging
    samplingTime = macros.sec2nano(1.)
    snAttLog = sNavObject.attOutMsg.recorder(samplingTime)
    ggLog = ggEff.gravityGradientOutMsg.recorder(samplingTime)
    scSim.AddModelToTask(simTaskName, snAttLog)
    scSim.AddModelToTask(simTaskName, ggLog)
    rwLogs = []
    for item in range(numRW):
        rwLogs.append(rwStateEffector.rwOutMsgs[item].recorder(samplingTime))
        scSim.AddModelToTask(simTaskName, rwLogs[item])

    ## Link messages
    sNavObject.scStateInMsg.subscribeTo(scObject.scStateOutMsg)
    scObject.transRefInMsg.subscribeTo(rv_message)
    rwStateEffector.rwMotorCmdInMsg.subscribeTo(rwCommand_message)

    scSim.InitializeSimulation()

    ## Run a sim for each Sedaro timestep
    for i in range(nsteps := len(sedaro_data['results'][agent_id]['elapsed_times'])-1):
        # Sedaro propagates to the next timestep using the current torques, etc.
        scSim.ConfigureStopTime(macros.sec2nano(sedaro_data['results'][agent_id]['elapsed_times'][i+1]))
        rv_messageData.r_RN_N = np.array(sedaro_data['results'][agent_id]['position'][i])*1000
        rv_messageData.v_RN_N = np.array(sedaro_data['results'][agent_id]['velocity'][i])*1000
        rv_message.write(rv_messageData)
        rwCommand_messageData.motorTorque = [
            sedaro_data['results'][agent_id]['x_torque'][i],
            sedaro_data['results'][agent_id]['y_torque'][i],
            sedaro_data['results'][agent_id]['z_torque'][i],
        ]
        rwCommand_message.write(rwCommand_messageData)
        scSim.ExecuteSimulation()
        progress_bar((i+1)/nsteps)
    # Return after progress bar completes
    print()

    times = snAttLog.timeTag
    attitude = snAttLog.sigma_BN
    omegas = [w.Omega for w in rwLogs]
    motor_torques = [w.u_current for w in rwLogs]
    gg_torque = ggLog.gravityGradientTorque_B
    
    return times, attitude, omegas, motor_torques, gg_torque

def main():
    # Load Sedaro data
    data_file_in = 'simulation_data/sedaro_data.json'
    results_file_out = 'reference_data/basilisk_results.json'
    sedaro_data = load_sedaro_data(data_file_in)
    basilisk_results = {}
    # Run Basilisk sim for each sedaro agent
    for agent_id, results in sedaro_data['results'].items():
        # Run the sim
        results = build_basilisk_sim(sedaro_data, agent_id)
        # Add this sim's results
        format_basilisk_results(basilisk_results, agent_id, *results)
    # Save the results to file
    print(f'Saving results to {results_file_out}...')
    with open(results_file_out, 'w') as file:
        json.dump(basilisk_results, file, indent=2)


if __name__ == '__main__':
    main()


    
