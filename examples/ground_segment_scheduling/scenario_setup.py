'''
This is the script I used to create a Walker Delta constellation of peripheral space points in my scenario. You don't
need to run this script to view the analytics or perform cosimulation, but it could be helpful for creating a new,
similar scenario.
'''
import numpy as np
from utils import sedaroLogin

# Settings
scenario_branch_id = 'PP7kL8dmDjB5k7kprBqpZG'
walker_i = 60.
walker_t = 24
walker_p = 3
walker_f = 3


# This is a function that computes all the orbital elements for a Walker Delta constellation
def walker_delta_elements(i: float, t: int, p: int, f: int, a: float = 7000., raan: float = 0.) -> list[dict]:
    elements = []
    sats_per_plane = int(t/p)
    for plane_n, plane_raan in enumerate(np.linspace(0, 360, p, endpoint=False)):
        for sat_nu in np.linspace(0, 360, sats_per_plane, endpoint=False):
            elements.append({
                'a': a,
                'e': 0,
                'inc': i,
                'raan': (raan + plane_raan) % 360,
                'om': 0,
                'nu': (sat_nu + plane_n*f*360/t) % 360
            })
    return elements


# We'll make the constellation and add the satellites in each plane to an agent group
client = sedaroLogin()
scenario = client.scenario(scenario_branch_id)

# Clear out any existing agents
ids_to_delete = [ag.id for ag in scenario.AgentGroup.get_all()]
for agent in scenario.PeripheralSpacePoint.get_all():
    ids_to_delete.append(agent.id)
    ids_to_delete.append(agent.kinematics.id)
scenario.crud(delete=ids_to_delete)

created_agent_ids = []
sats_per_plane = int(walker_t/walker_p)
elements = walker_delta_elements(walker_i, walker_t, walker_p, walker_f)
i = 0
for plane_n in range(walker_p):
    plane_agent_ids = []
    for satellite_number in range(sats_per_plane):
        # Create the orbit block using the orbital elements
        orbit = scenario.PropagatedOrbitKinematics.create(
            initialStateDefType='ORBITAL_ELEMENTS',
            initialStateDefParams=elements[i]
        )
        i += 1
        # Create the agent with this orbit
        agent = scenario.PeripheralSpacePoint.create(
            name=f'Spacecraft {plane_n+1}-{satellite_number+1}',
            kinematics=orbit.id
        )
        plane_agent_ids.append(agent.id)
    # Create the agent group for this plane
    group = scenario.AgentGroup.create(
        name=f'Plane {plane_n+1}',
        agentAssociations={id_: {'priority': i} for i, id_ in enumerate(plane_agent_ids)},
        agentType='SpaceTarget'
    )
