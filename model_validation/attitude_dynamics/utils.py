import json
from typing import Tuple

import numpy as np


def progress_bar(progress):
    """Prints a progress bar to the console"""
    if progress is not None:
        blocks = int(progress * 50)
        bar = '[' + ('■' * blocks + '□' * (50 - blocks)
                     ).ljust(50) + f'] ({100*progress:.2f}%)'
        print(bar, end='\r')


def mrp_to_quaternion(mrp):
    '''
    Convert a MRP to a quaternion
    '''
    p_array = np.array(mrp)
    q = np.concatenate((2 * p_array, [1 - np.dot(p_array, p_array)]))
    return q / (1 + np.dot(p_array, p_array))


def quaternionConjugate(quaternion):
    quaternionConj = np.array(-quaternion)
    quaternionConj[3] = -quaternionConj[3]

    return quaternionConj


def quaternionDot(q1, q2):
    '''
    REF 1: Eq. 2.82b, preserves the order of active rotation matrix multiplication
    '''
    return np.array([q1[3] * q2[0] + q1[0] * q2[3] + q1[1] * q2[2] - q1[2] * q2[1],
                     q1[3] * q2[1] - q1[0] * q2[2] +
                     q1[1] * q2[3] + q1[2] * q2[0],
                     q1[3] * q2[2] + q1[0] * q2[1] -
                     q1[1] * q2[0] + q1[2] * q2[3],
                     q1[3] * q2[3] - q1[0] * q2[0] - q1[1] * q2[1] - q1[2] * q2[2]])


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


def findClosestIndex(t: float, ts_2: np.ndarray):
    '''
    Find the closest value to t in ts_2
    '''
    # Get the index of the closest timestamp in ts_2
    index = np.searchsorted(ts_2, t)
    if index == len(ts_2):
        index -= 1
    elif index > 0 and t - ts_2[index - 1] < ts_2[index] - t:
        index -= 1

    return index


def angleBetweenClosestQuaternions(q_1: np.ndarray, t_1: float,
                                   qs_2: Tuple[np.ndarray, ...], ts_2: np.ndarray) -> float:
    '''Calculate the angle between the two closest quaternions in each list.

    Args:
        q_1: Quaternions with shape (4,).
        ts_1: Timestamp corresponding to q_1.
        qs_2: List of quaternions with shape (4,).
        ts_2: List of timestamps corresponding to qs_2.

    Returns:
        Angle between the two closest quaternions, in radians.
    '''
    # Calculate the angle between the two closest quaternions
    return angleBetweenQuaternion(q_1, qs_2[findClosestIndex(t_1, ts_2)])


def sedaroLogin():
    from sedaro import SedaroApiClient

    # FIXME
    with open('/Users/richard/sedaro/satellite-app/secrets.json', 'r') as file:
        API_KEY = json.load(file)['fleetwood']
    # return SedaroApiClient(API_KEY, host='http://localhost')
    return SedaroApiClient(API_KEY, host='http://api.astage.sedaro.com')
    # with open('../../secrets.json', 'r') as file: FIXME
    #     API_KEY = json.load(file)['API_KEY_LOCAL']
