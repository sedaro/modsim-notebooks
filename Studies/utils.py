



import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
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
        