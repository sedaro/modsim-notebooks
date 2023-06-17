# Modeling & Simulation Jupyter Notebooks

A collection of helpful modeling and simulation related Jupyter Notebooks that consume the sedaro service.

For help installing the `sedaro` python client, see [here](https://github.com/sedaro/sedaro-python).

## Table of Contents

1. [Hello, World!](./hello_world.ipynb)
1. [Results API Demo](./results_api_demo.ipynb)
1. [Build SuperDove Constellation](./build_superdove_constellation.ipynb)

More to come soon!

### Important: Read Before Running

These notebooks make changes to agent and scenario branches in your account. Ensure any changes to the target branches are saved prior to running any code. Sedaro recommends committing current work and creating new branches in the target repositories to avoid loss of work.

These notebook also require that you have previously generated an API key in the web UI. That key should be stored in a file called `secrets.json` in the same directory as these notebooks with the following format:

```json
{
  "API_KEY": "<API_KEY>"
}
```

API keys grant full access to your repositories and should never be shared. If you think your API key has been compromised, you can revoke it in the user settings interface on the Sedaro website.
