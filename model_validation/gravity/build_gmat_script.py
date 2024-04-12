'''
This script is used to build the GMAT scenario that generates the reference
validation data. This code is part of the repository for reference, but it is
not necessary to run this file to reproduce our validation results.

See the `reference_data` directory for the output of the GMAT script.
'''
import json
from pathlib import Path

from utils import EPHEMERIS, FORCE_MODEL, SATELLITE

PATH = Path(__file__).parent

if __name__ == '__main__':

    # Load the orbit configurations
    with open(PATH / 'orbits.json', 'r') as file:
        orbits = json.load(file)

    # Build satellite and ephemeris sections
    script = ''
    names = []
    # idx = 0
    for name, entry in orbits.items():
        names.append(name)
        template = entry.get('template', None)
        a = (entry['hp'] + 6378.137) / (1 - entry['e'])
        drag_area = 1.0 if 'drag' in name else 0.0
        srp_area = 1.0 if 'srp' in name else 0.0

        sat_section = SATELLITE.replace('<SAT_NAME>', name)
        sat_section = sat_section.replace('<SMA>', f'{a:.12f}')
        sat_section = sat_section.replace('<ECC>', f'{entry["e"]:.12f}')
        sat_section = sat_section.replace('<INC>', f'{entry["i"]:.12f}')
        sat_section = sat_section.replace('<RAAN>', f'{entry["raan"]:.12f}')
        sat_section = sat_section.replace('<DRAG_AREA>', f'{drag_area:.12f}')
        sat_section = sat_section.replace('<SRP_AREA>', f'{srp_area:.12f}')

        ephem_section = EPHEMERIS.replace('<EPHEM_NAME>', f'{name}_ephem')
        ephem_section = ephem_section.replace('<SAT_NAME>', name)

        script += sat_section + ephem_section
        # idx += 1
        # if idx > 20:
        #     break

    # Build remainder of script file
    script += FORCE_MODEL
    script += '\nBeginMissionSequence;\n'
    for name in names:
        script += ''.join((
            'Propagate ',
            f'DefaultProp({name}) ',
            f'{{{name}.ElapsedSecs = 604800.0}};\n'
        ))

    # Write script to file
    with open(PATH / 'reference_data' / 'scenario.script', 'w') as file:
        file.write(script)
