# Modeling & Simulation Jupyter Notebooks

A collection of helpful modeling and simulation related Jupyter Notebooks that consume the sedaro service.

For help installing the `sedaro` python client, see [here](https://github.com/sedaro/sedaro-python).

## Table of Contents

### Getting Started

These notebooks focus on interactions with the Sedaro API from Python.

1. [Hello, World!](examples/hello_world.ipynb)
2. [Results API Demo](examples/results_api_demo.ipynb)
3. [Flower Constellations](examples/flower_constellation.ipynb)
4. [Build SuperDove Constellation](examples/build_superdove_constellation.ipynb)
5. [Wildfire Cosimulation Game](examples/wildfire_cosimulation_game.ipynb)
5. [Routines](examples/routines.ipynb)
6. [Hohmann Transfer](examples/coplanar_rendezvous/thrust_maneuver.ipynb)

### Model Validation

These notebooks demonstrate the accuracy of Sedaro models through interaction with public Sedaro scenarios. Each notebook focuses on a specific subset of our models to prove their accuracy in realistic situations.

As our model selection expands, we will continue to add new validation notebooks here.

1. [Attitude Dynamics](model_validation/attitude_dynamics/attitude_dynamics.ipynb)
2. [Gravity Model](model_validation/gravity/gravity.ipynb)

### Important: Read Before Running

These notebooks may make changes to agent and scenario branches in your account. Ensure any changes to the target branches are saved prior to running any code. Sedaro recommends committing current work and creating new branches in the target repositories to avoid loss of work.

These notebook also require that you have previously generated an API key in the web UI. That key should be stored in a file called `secrets.json` in the same directory as these notebooks with the following format:

```json
{
  "API_KEY": "<API_KEY>"
}
```

API keys grant full access to your repositories and should never be shared. If you think your API key has been compromised, you can revoke it in the user settings interface on the Sedaro website.
