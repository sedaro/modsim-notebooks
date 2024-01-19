'''
This script is used to build the validation scenario for this case. This code
is part of the repository for reference, but it is not necessary to run this
file to reproduce our validation results.

Use caution if trying to run this script -- it will make modifications to the
target branch that could result in data loss.
'''
import json
from pathlib import Path

from sedaro import SedaroApiClient

PATH = Path(__file__).parent

SCENARIO_ID = 'PLCPJHKtysym8fHJVxslm3'

if __name__ == '__main__':

    # Load API key
    with open(PATH / '../../secrets.json', 'r') as file:
        API_KEY = json.load(file)['API_KEY']

    # Load the orbit configurations
    with open(PATH / 'orbits.json', 'r') as file:
        orbits = json.load(file)

    # Initialize API client
    sedaro = SedaroApiClient(API_KEY, host='https://api.sedaro.com')
    scenario = sedaro.scenario(SCENARIO_ID)

    # Build new agent blocks
    blocks = []
    for name, entry in orbits.items():
        template = entry.get('template', None)
        a = (entry['hp'] + 6378.137) / (1 - entry['e'])
        orbit = {
            'id': f'${name}',
            'type': 'PropagatedOrbitKinematics',
            'initialStateDefType': 'ORBITAL_ELEMENTS',
            'initialStateDefParams': {
                'a': a,
                'e': entry['e'],
                'inc': entry['i'],
                'raan': entry['raan'],
                'nu': 0,
                'om': 0,
            }
        }
        if template:
            agent = {
                'name': f'{name}',
                'type': 'TemplatedAgent',
                'kinematics': f'${name}',
                'templateRef': template,
            }
        else:
            agent = {
                'name': f'{name}',
                'type': 'PeripheralSpacePoint',
                'kinematics': f'${name}'
            }
        blocks += [orbit, agent]

    # Delete existing agents and create new ones
    existing = scenario.Agent.get_all()
    if existing:
        scenario.crud(delete=[entry.id for entry in existing])
    scenario.crud(blocks=blocks)
