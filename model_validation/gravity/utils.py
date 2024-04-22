'''
Miscellaneous tools for performing the validation analysis.
'''
import re

import matplotlib.pyplot as plt


def progress_bar(progress):
    """Prints a progress bar to the console"""
    if progress is not None:
        blocks = int(progress * 50 / 100)
        bar = '[' + ('■' * blocks + '□'*(50 - blocks)).ljust(50) + f'] ({progress:.2f}%)'
        print(bar, end='\r')


def plot_results(data, name, plot_description):
    count = 0
    for agent_name in data:
        if re.match(f'{name}_\\d+', agent_name):
            count += 1
            plt.scatter(
                data[agent_name]['elapsed_hours'],
                data[agent_name]['error'],
                label=agent_name,
                s=.1,
                c='k'
            )

    plt.title(f'Propagation Error - {count} {plot_description}')
    plt.ylabel('Propagated Position Error (m)')
    plt.xlabel('Elapsed Time (hr)')
    plt.xlim(0, 24 * 7)
    plt.gca().set_yscale('log')
    plt.grid()
    plt.show()


# GMAT Satellite Script Snippet
SATELLITE = '''
Create Spacecraft <SAT_NAME>;
GMAT <SAT_NAME>.Id = '<SAT_NAME>';
GMAT <SAT_NAME>.DateFormat = UTCGregorian;
GMAT <SAT_NAME>.Epoch = '20 Nov 2023 00:00:00.000';
GMAT <SAT_NAME>.CoordinateSystem = EarthICRF;
GMAT <SAT_NAME>.DisplayStateType = Keplerian;
GMAT <SAT_NAME>.SMA = <SMA>;
GMAT <SAT_NAME>.ECC = <ECC>;
GMAT <SAT_NAME>.INC = <INC>;
GMAT <SAT_NAME>.RAAN = <RAAN>;
GMAT <SAT_NAME>.AOP = 0;
GMAT <SAT_NAME>.TA = 0;
GMAT <SAT_NAME>.DryMass = 1000;
GMAT <SAT_NAME>.Cd = 2.0;
GMAT <SAT_NAME>.Cr = 1.4;
GMAT <SAT_NAME>.DragArea = <DRAG_AREA>;
GMAT <SAT_NAME>.SRPArea = <SRP_AREA>;
'''

# GMAT Ephemeris Script Snippet
EPHEMERIS = '''
Create EphemerisFile <EPHEM_NAME>;
GMAT <EPHEM_NAME>.Spacecraft = <SAT_NAME>;
GMAT <EPHEM_NAME>.Filename = './<EPHEM_NAME>.oem';
GMAT <EPHEM_NAME>.FileFormat = CCSDS-OEM;
GMAT <EPHEM_NAME>.EpochFormat = UTCGregorian;
GMAT <EPHEM_NAME>.InitialEpoch = InitialSpacecraftEpoch;
GMAT <EPHEM_NAME>.FinalEpoch = FinalSpacecraftEpoch;
GMAT <EPHEM_NAME>.StepSize = 60;
GMAT <EPHEM_NAME>.Interpolator = Lagrange;
GMAT <EPHEM_NAME>.InterpolationOrder = 7;
GMAT <EPHEM_NAME>.CoordinateSystem = EarthICRF;
GMAT <EPHEM_NAME>.OutputFormat = LittleEndian;
GMAT <EPHEM_NAME>.IncludeCovariance = None;
GMAT <EPHEM_NAME>.WriteEphemeris = true;
'''


# GMAT Propagator Script Snippet
FORCE_MODEL = '''
Create ForceModel DefaultProp_ForceModel;
GMAT DefaultProp_ForceModel.CentralBody = Earth;
GMAT DefaultProp_ForceModel.PrimaryBodies = {Earth};
GMAT DefaultProp_ForceModel.PointMasses = {Luna, Sun};

GMAT DefaultProp_ForceModel.Drag.AtmosphereModel = JacchiaRoberts;
GMAT DefaultProp_ForceModel.Drag.HistoricWeatherSource = 'ConstantFluxAndGeoMag';
GMAT DefaultProp_ForceModel.Drag.PredictedWeatherSource = 'ConstantFluxAndGeoMag';
GMAT DefaultProp_ForceModel.Drag.CSSISpaceWeatherFile = 'SpaceWeather-All-v1.2.txt';
GMAT DefaultProp_ForceModel.Drag.SchattenFile = 'SchattenPredict.txt';
GMAT DefaultProp_ForceModel.Drag.F107 = 150;
GMAT DefaultProp_ForceModel.Drag.F107A = 150;
GMAT DefaultProp_ForceModel.Drag.MagneticIndex = 3;
GMAT DefaultProp_ForceModel.Drag.SchattenErrorModel = 'Nominal';
GMAT DefaultProp_ForceModel.Drag.SchattenTimingModel = 'NominalCycle';
GMAT DefaultProp_ForceModel.Drag.DragModel = 'Spherical';

GMAT DefaultProp_ForceModel.SRP = On;
GMAT DefaultProp_ForceModel.SRP.Flux = 1367;
GMAT DefaultProp_ForceModel.SRP.SRPModel = Spherical;
GMAT DefaultProp_ForceModel.SRP.Nominal_Sun = 149597870.691;

GMAT DefaultProp_ForceModel.RelativisticCorrection = Off;
GMAT DefaultProp_ForceModel.ErrorControl = RSSStep;
GMAT DefaultProp_ForceModel.GravityField.Earth.Degree = 40;
GMAT DefaultProp_ForceModel.GravityField.Earth.Order = 40;
GMAT DefaultProp_ForceModel.GravityField.Earth.StmLimit = 100;
GMAT DefaultProp_ForceModel.GravityField.Earth.PotentialFile = 'EGM2008.cof';
GMAT DefaultProp_ForceModel.GravityField.Earth.TideModel = 'None';

Create Propagator DefaultProp;
GMAT DefaultProp.FM = DefaultProp_ForceModel;
GMAT DefaultProp.Type = RungeKutta89;
GMAT DefaultProp.InitialStepSize = 60;
GMAT DefaultProp.Accuracy = 9.999999999999999e-12;
GMAT DefaultProp.MinStep = 0.001;
GMAT DefaultProp.MaxStep = 60;
GMAT DefaultProp.MaxStepAttempts = 50;
GMAT DefaultProp.StopIfAccuracyIsViolated = true;
'''
