



from os import path
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import flatten_json
from fuzzywuzzy import fuzz

from typing import TypeAlias
Quaternion: TypeAlias =  np.ndarray

# in python 3.12, you can use the type statement directly
# type Quaternion =  np.ndarray


def quaternionConjugate(quaternion):
    quaternionConj = np.array(-quaternion)
    quaternionConj[3] = -quaternionConj[3]

    return quaternionConj

def quaternionDot(q1, q2):
    '''
    REF 1: Eq. 2.82b, preserves the order of active rotation matrix multiplication
    '''
    return np.array([q1[3] * q2[0] + q1[0] * q2[3] + q1[1] * q2[2] - q1[2] * q2[1],
                        q1[3] * q2[1] - q1[0] * q2[2] + q1[1] * q2[3] + q1[2] * q2[0],
                        q1[3] * q2[2] + q1[0] * q2[1] - q1[1] * q2[0] + q1[2] * q2[3],
                        q1[3] * q2[3] - q1[0] * q2[0] - q1[1] * q2[1] - q1[2] * q2[2]])

def quaternionConjugate(quaternion):
    quaternionConj = np.array(-quaternion)
    quaternionConj[3] = -quaternionConj[3]

    return quaternionConj

def differenceQuaternion(q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
    '''Calculate quaternion describing rotation from q1 to q2.

    Args:
        q1: Origin quaternion with shape (4,).
        q2: Destination quaternion with shape (4,).

    Returns:
        Quaternion with shape (4,).
    '''
    return quaternionDot(q1, quaternionConjugate(q2))

def angleBetweenQuaternion(q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
    '''Calculate the angle between two quaternion attitudes.

    Args:
        q1: Quaternion with shape (4,).
        q2: Quaternion with shape (4,)

    Returns:
        Angle between the two quaternions, in radians.
    '''
    return 2 * np.arccos(min(abs(differenceQuaternion(q1, q2)[-1]), 1))

def createSimIdToListParameterDataframe(list_data, columnNames, start_index=1):
    return { sim_id: pd.DataFrame(series.values[start_index:], columns=columnNames) for (sim_id, series) in list_data.items()  } 

def plotStudySeries(job_id_to_dataframe):
    for sim_id, dataframe in job_id_to_dataframe.items():
        plt.plot( dataframe[sim_id].values, label=sim_id,linestyle='', marker='D', markersize=2 )
    plt.legend(bbox_to_anchor=(1, 1))
    plt.show()


def plotStudySubSeries(job_id_to_dataframe, subseries):
    for sim_id, dataframe in job_id_to_dataframe.items():
        plt.plot( dataframe[subseries].values, label=sim_id,linestyle='', marker='D', markersize=2 )
    plt.legend(bbox_to_anchor=(1, 1))
    plt.show()

def plotStudySeriesSubPlots(job_id_to_dataframe, series):
    fig, axs = plt.subplots(len(job_id_to_dataframe), sharex=True, sharey=True)
    for i, (sim_id, dataframe) in enumerate(job_id_to_dataframe.items()):
        axs[i].plot( dataframe[series].values, label=sim_id,linestyle='', marker='D', markersize=2 )
        axs[i].legend(bbox_to_anchor=(1, 1))
    plt.show()

def studyStats(job_id_to_dataframe, series):
    data = { sim_id: dataframe[series].values for sim_id, dataframe in job_id_to_dataframe.items()}
    study_roll_df = pd.DataFrame(data)
    return study_roll_df.describe()

def workspaceStudyJobStatus(sedaroAPI, scenario_branch_id):
     study_resource_url = f'/simulations/branches/{scenario_branch_id}/control/study/'
     return [ (study['id'], study['status']) for study in sedaroAPI.request.get(  study_resource_url) ]

def runStudy(sedaroAPI, scenario_branch_id, iterations, overridesID):
    create_study_resource_url = f'/simulations/branches/{scenario_branch_id}/control/study/'
    new_studyjob = sedaroAPI.request.post(  create_study_resource_url,
                                            body={
                                                "iterations": iterations,
                                                "overrideID": overridesID
                                                })
    return new_studyjob

def getStudyStatus(sedaroAPI, scenario_branch_id, study_id):
     study_control_resource = f'/simulations/branches/{scenario_branch_id}/control/study/{study_id}'
     study_status = sedaroAPI.request.get(study_control_resource)
     return study_status

def getStudySimJobsStatus(sedaroAPI, scenario_branch_id, study_id):
     study_status = getStudyStatus(sedaroAPI, scenario_branch_id, study_id)
     study_job_ids = study_status['jobs']
     return [ ( f"SimJob ID: {job['id']}", f"Status: {job['status']}", f"Progress:", job['progress']) 
        for job_id in study_job_ids 
        for job in [sedaroAPI.request.get(f'/simulations/branches/{scenario_branch_id}/control/{job_id}')] ]



class AgentModelParametersOverridePaths():
    def __init__(self, scenario_branch, agent_branch, agent_name='Wildfire'):
        self.scenario_branch = scenario_branch
        self.agent_branch    = agent_branch
        self.agent_id_name_map, self.agent_name_id_map = self.create_agent_name_id_maps()
        self.path_to_agent_key = self.create_path_to_agent_dict(agent_name)

    def create_agent_name_id_maps(self): 
        self.scenario_flat  = flatten_json.flatten( self.scenario_branch.data, '.') 
        agent_id_name_map   = { key.split('.')[1]: value for (key,value) in self.scenario_flat.items() if key.endswith('name') } 
        agent_name_id_map   = { value: key.split('.')[1] for (key,value) in self.scenario_flat.items() if key.endswith('name') } 
        return agent_id_name_map, agent_name_id_map

        # create the reverse dict:  path to agent_key
        path_to_agent_key   = { value: key for (key,value) in agent_key_to_path.items() }
        return agent_key_to_path,path_to_agent_key 

    def create_path_to_agent_dict(self, agent_name='Wildfire'):
        agent_flat = flatten_json.flatten( self.agent_branch.data, '.') 

        self.agent_branches_flat = { f"{self.agent_name_id_map[agent_name]}.data.{key}": value for (key,value) in agent_flat.items() }

        agent_block_id_name  = { blockID: block['name'] for (blockID, block) in self.agent_branch['data']['blocks'].items() 
                                                        if 'name' in block }
 
        agent_block_id_type  = { blockID: block['type'] for (blockID, block) in self.agent_branch['data']['blocks'].items() 
                                                        if 'type' in block }
        # block parameters
        agent_key_to_path  = { f"{agentID}.data.blocks.{blockID}.{parameter_key}":  f"{self.agent_id_name_map[agentID]}/{block_label}/{'/'.join(parameter_key.split('.'))}"                                                                  
                            for (agentID, agentData) in self.agent_branch.items()
                            for (blockID, block) in agentData['data']['blocks'].items() 
                            for block_label in [agent_block_id_name[blockID] if blockID in agent_block_id_name else agent_block_id_type[blockID]]
                            for parameter_key in flatten_json.flatten(block, ".").keys() }
        
        # agent non-block parameters
        filter_list = ('blocks', 'index', '_')
        agent_root_param_to_path = { f"{agentID}.data.{parameter_key}": f"{ self.agent_id_name_map[agentID] }/root/{'/'.join(parameter_key.split('.'))}"
                                     for (agentID, agentData) in self.agent_branch.items()
                                     for parameter_key in flatten_json.flatten(agentData['data'], '.').keys() 
                                     if not parameter_key.startswith(filter_list) }
        # Combine them
        agent_key_to_path  |= agent_root_param_to_path

        path_to_agent_key   = { value: key for (key,value) in agent_key_to_path.items() }
        return path_to_agent_key
    
    def listPaths(self):
            return list(self.path_to_agent_key.keys())

    def findBestMatch(self, search_for_path:str) -> str:
            return max(self.path_to_agent_key.keys(), key=lambda path: fuzz.ratio(search_for_path, path ))

    def findValueOf(self, path):
            if path in self.path_to_agent_key:
                    return self.agent_branches_flat[ self.path_to_agent_key[path] ]
            else:
                    return { "NotFoundPath": f"{path}", "Did you mean": max(self.path_to_agent_key.keys(), key=lambda aPath: fuzz.ratio( path, aPath )) } 

