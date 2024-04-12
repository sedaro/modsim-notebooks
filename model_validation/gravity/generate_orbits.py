import json
from pathlib import Path

import numpy as np

DRAG_TEMPLATE = 'PLCPJGPjTVrxC4fZv3KSZB'
SRP_TEMPLATE = 'PLCPJ4X22Nb6Mz9nJyfQkM'


if __name__ == '__main__':
    orbits = {}

    # LEO Circular
    INC_STEPS = 8
    RAAN_STEPS = 8
    for alt in (500., 1000.):
        for inc in np.linspace(0., 180., INC_STEPS):
            if inc != 0 and inc != 180:
                for raan in np.linspace(0., 360., RAAN_STEPS):
                    name = f'leo_circular_{len(orbits)}'
                    orbits[name] = {'hp': alt, 'e': 0, 'i': inc, 'raan': raan}
            else:
                name = f'leo_circular_{len(orbits)}'
                orbits[name] = {'hp': alt, 'e': 0, 'i': inc, 'raan': 0}

    # LEO Circular (with drag)
    INC_STEPS = 4
    RAAN_STEPS = 4
    alt = 500.
    for inc in np.linspace(0., 180., INC_STEPS):
        if inc != 0 and inc != 180:
            for raan in np.linspace(0., 360., RAAN_STEPS):
                name = f'leo_circular_drag_{len(orbits)}'
                orbits[name] = {'hp': alt, 'e': 0, 'i': inc, 'raan': raan, 'template': DRAG_TEMPLATE}
        else:
            name = f'leo_circular_drag_{len(orbits)}'
            orbits[name] = {'hp': alt, 'e': 0, 'i': inc, 'raan': 0, 'template': DRAG_TEMPLATE}

    # MEO Circular
    INC_STEPS = 4
    RAAN_STEPS = 8
    for inc in np.linspace(0., 90., INC_STEPS):
        if inc != 0 and inc != 180:
            for raan in np.linspace(0., 360., RAAN_STEPS):
                name = f'meo_circular_{len(orbits)}'
                orbits[name] = {'hp': 20000.0, 'e': 0, 'i': inc, 'raan': raan}
        else:
            name = f'meo_circular_{len(orbits)}'
            orbits[name] = {'hp': 20000.0, 'e': 0, 'i': inc, 'raan': 0}

    # Molniya
    RAAN_STEPS = 10
    for raan in np.linspace(0., 360., RAAN_STEPS):
        name = f'molniya_{len(orbits)}'
        orbits[name] = {'hp': 1605, 'e': 0.7, 'i': 63.4, 'raan': raan}

    # Molniya with SRP
    RAAN_STEPS = 10
    for raan in np.linspace(0., 360., RAAN_STEPS):
        name = f'molniya_srp_{len(orbits)}'
        orbits[name] = {'hp': 1605, 'e': 0.7, 'i': 63.4, 'raan': raan, 'template': SRP_TEMPLATE}

    # GEO Circular
    INC_STEPS = 2
    RAAN_STEPS = 8
    for inc in np.linspace(0., 10., INC_STEPS):
        if inc != 0 and inc != 180:
            for raan in np.linspace(0., 360., RAAN_STEPS):
                name = f'geo_circular_{len(orbits)}'
                orbits[name] = {'hp': 35786.0, 'e': 0, 'i': inc, 'raan': raan}
        else:
            name = f'geo_circular_{len(orbits)}'
            orbits[name] = {'hp': 35786.0, 'e': 0, 'i': inc, 'raan': 0}

    # GEO Circular with SRP
    INC_STEPS = 2
    RAAN_STEPS = 8
    for inc in np.linspace(0., 10., INC_STEPS):
        if inc != 0 and inc != 180:
            for raan in np.linspace(0., 360., RAAN_STEPS):
                name = f'geo_circular_srp_{len(orbits)}'
                orbits[name] = {'hp': 35786.0, 'e': 0, 'i': inc, 'raan': raan, 'template': SRP_TEMPLATE}
        else:
            name = f'geo_circular_srp_{len(orbits)}'
            orbits[name] = {'hp': 35786.0, 'e': 0, 'i': inc, 'raan': 0, 'template': SRP_TEMPLATE}

    # GEO Transfer
    INC_STEPS = 2
    RAAN_STEPS = 8
    for inc in np.linspace(0., 10., INC_STEPS):
        if inc != 0 and inc != 180:
            for raan in np.linspace(0., 360., RAAN_STEPS):
                name = f'geo_transfer_{len(orbits)}'
                orbits[name] = {'hp': 400., 'e': 0.723, 'i': inc, 'raan': raan}
        else:
            name = f'geo_transfer_{len(orbits)}'
            orbits[name] = {'hp': 400., 'e': 0.723, 'i': inc, 'raan': 0}

    # GEO Transfer with SRP
    INC_STEPS = 2
    RAAN_STEPS = 8
    for inc in np.linspace(0., 10., INC_STEPS):
        if inc != 0 and inc != 180:
            for raan in np.linspace(0., 360., RAAN_STEPS):
                name = f'geo_transfer_srp_{len(orbits)}'
                orbits[name] = {'hp': 400., 'e': 0.723, 'i': inc, 'raan': raan, 'template': SRP_TEMPLATE}
        else:
            name = f'geo_transfer_srp_{len(orbits)}'
            orbits[name] = {'hp': 400., 'e': 0.723, 'i': inc, 'raan': 0, 'template': SRP_TEMPLATE}

    # Write to file
    file_path = Path(__file__).parent / 'orbits.json'
    with open(file_path, 'w') as file:
        file.write(json.dumps(orbits, indent=4))

    # Report
    print(f'Wrote {len(orbits)} orbits to {file_path}.')
