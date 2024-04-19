import math
import numpy as np

Earth_radius_km = 6378.1363
earth_u_ER = 1
sec_per_TU = 806.811
g = 9.80665 # m/s**2

# helper functions
def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))  


# Circular Coplanar Phasing (different orbits)

# Resources:
# - Fundamentals of Astrodynamics 1971 (Bate, Mueller, White) pg 163, 362
# - Fundamentals of Astrodynamics and Applications Fifth Edition 2022 (Vallado) pg 329, 367

# note numpy arrays can use @ for dot product
# https://numpy.org/doc/stable/reference/generated/numpy.dot.html


def calc_dot_product_list(list1, list2):  
    return sum([i*j for (i, j) in zip(list1, list2)])


def calc_dot_product(position1, position2):
    from operator import mul
    return sum(map(mul, position1, position2))

def angle_between_positions(position1, position2):
    return math.acos(calc_dot_product(position1, position2) / (position1.norm() * position2.norm()))


def position_to_radius_ER(position):  
    return position.norm() / Earth_radius_km


def calc_radii_canonical_units(radius_km):  
    return radius_km / Earth_radius_km


def calc_circular_mean_motion(radius_ER):
    return math.sqrt(earth_u_ER / (radius_ER**3))


def calc_semi_major_axis_of_transfer_orbit(first_radius_ER, second_radius_ER):
    return (first_radius_ER + second_radius_ER) / 2


def calc_circular_orbit_velocity(radius_ER):
    return math.sqrt(earth_u_ER / radius_ER)


def calc_hohmann_transfer_dvs(chaser_radius_ER, target_radius_ER):
    # calculate the semi-major axis of the transfer orbit
    a_transfer = calc_semi_major_axis_of_transfer_orbit(chaser_radius_ER, target_radius_ER)

    # calculate the velocity of the chaser satellite in its current orbit
    v_chaser = calc_circular_orbit_velocity(chaser_radius_ER)

    # calculate the velocity of the target satellite in its current orbit
    v_target = calc_circular_orbit_velocity(target_radius_ER)

    # calculate the velocity of the chaser satellite at the start transfer orbit point
    v_start_transfer = (math.sqrt(earth_u_ER * ((2 / chaser_radius_ER) - (1 / a_transfer))))

    # calculate the velocity of the target satellite at the end _transfer orbit point
    v_end_transfer = (math.sqrt(earth_u_ER * ((2 / target_radius_ER) - (1 / a_transfer))))

    # calculate the velocity change required for the chaser satellite to enter the transfer orbit
    dv_to_enter_the_transfer_orbit = math.fabs(v_start_transfer - v_chaser)

    # calculate the velocity change required for the chaser satellite to exit the transfer orbit
    dv_to_exit_the_transfer_orbit = math.fabs(v_end_transfer - v_target)

    return dv_to_enter_the_transfer_orbit, dv_to_exit_the_transfer_orbit


def calc_hohmann_transfer_time(chaser_radius_ER, target_radius_ER):
    # calculate the semi-major axis of the transfer orbit
    a_transfer = calc_semi_major_axis_of_transfer_orbit(chaser_radius_ER, target_radius_ER)

    # calculate the period of the transfer orbit
    T_transfer = 2 * math.pi * math.sqrt((a_transfer ** 3) / earth_u_ER)

    # calculate the time to transfer from the chaser orbit to the target orbit
    time_transfer = T_transfer / 2

    return time_transfer


def calc_lead_angle_for_target(chaser_radius_ER, target_radius_ER):
    target_mean_motion = calc_circular_mean_motion(target_radius_ER)
    return calc_hohmann_transfer_time(chaser_radius_ER, target_radius_ER) * target_mean_motion


def phasing_angle_for_target(chaser_radius_ER, target_radius_ER, phase_angle_deg):
    # Depends if the chaser is leading or lagging the target
    if phase_angle_deg < 0.0:  
        return math.pi - calc_lead_angle_for_target(chaser_radius_ER, target_radius_ER)
    else:
        return math.pi + calc_lead_angle_for_target(chaser_radius_ER, target_radius_ER)


def calc_hohmann_transfer_wait_time(chaser_radius_ER, target_radius_ER, phase_angle_deg, k):
    wait_time = (phasing_angle_for_target(chaser_radius_ER, target_radius_ER, phase_angle_deg) - phase_angle_deg*math.pi /
                 180 + 2*math.pi*k) / (calc_circular_mean_motion(chaser_radius_ER) - calc_circular_mean_motion(target_radius_ER))
    return wait_time
