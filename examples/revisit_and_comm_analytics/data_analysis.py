from typing import Any

import pandas as pd
from IPython.display import display
from ipywidgets import IntProgress
from sedaro import SedaroAgentResult
from sedaro.modsim import mjd_to_datetime


def target_data_results(
    agent_templates: dict[str, Any],
    observer_results: dict[str, SedaroAgentResult],
    target_names_by_id: dict[str, str],
    select_data_types: list[str] = [],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Extract data transmission, reception, and storage data from observer results."""

    bar = IntProgress(min=0, max=len(observer_results), layout={'width': '100%'})
    display(bar)

    transmit_data: list[dict[str, float]] = []
    receive_data: list[dict[str, float]] = []
    data_storage_data: list[dict[str, float]] = []
    for agent, agent_template in agent_templates.items():
        agent_results = observer_results[agent]
        results_times_mjd = agent_results.block(agent_template.Routine.get_first().id).isActive.mjd
        results_times = [mjd_to_datetime(t) for t in results_times_mjd]  # datetimes for each point

        for data_interface in agent_template.TransmitInterface.get_all():
            data_interface_results = agent_results.block(data_interface.id)
            valid_data_type_names = [data_type.name for data_type in data_interface.dataTypes.keys()
                                     if not select_data_types or data_type.name in select_data_types]  # filter data types
            for data_type_name in valid_data_type_names:
                for target, bit_rate, t_1, t_2 in zip(data_interface_results.activeLinkTarget.values, data_interface_results.typeBitRates.values[data_type_name], results_times, results_times[1:]):
                    if target in target_names_by_id:
                        transmit_data.append({
                            "Time": t_1,
                            "Bit Rate": bit_rate,
                            "Data Transmitted": bit_rate * (t_2 - t_1).total_seconds(),
                            "Data Type": data_type_name,
                            "Agent": agent,
                            "Target": target_names_by_id[target],
                        })

        for data_interface in agent_template.ReceiveInterface.get_all():
            data_interface_results = agent_results.block(data_interface.id)
            for target, bit_rate, t_1, t_2 in zip(data_interface_results.activeLinkTarget.values, data_interface_results.bitRate.values, results_times, results_times[1:]):
                if target in target_names_by_id:
                    receive_data.append({
                        "Time": t_1,
                        "Bit Rate": bit_rate,
                        "Data Received": bit_rate * (t_2 - t_1).total_seconds(),
                        "Data Type": data_type_name,
                        "Agent": agent,
                        "Target": target_names_by_id[target],
                    })

        data_storage_ids = agent_template.DataStorage.get_all_ids()
        valid_data_types = [data_type for data_type in agent_template.DataType.get_all()
                            if not select_data_types or data_type.name in select_data_types]  # filter data types

        usage_results_by_storage = {storage: agent_results.block(storage).usage.values for storage in data_storage_ids}
        avg_data_age_results_by_storage = {storage: agent_results.block(storage).averageDataAge.values
                                           for storage in data_storage_ids}
        min_data_age_results_by_storage = {storage: agent_results.block(storage).minDataAge.values
                                           for storage in data_storage_ids}
        max_data_age_results_by_storage = {storage: agent_results.block(storage).maxDataAge.values
                                           for storage in data_storage_ids}
        for n, t in enumerate(results_times):
            for data_type in valid_data_types:
                for storage in data_storage_ids:
                    data_storage_data.append({
                        "Time": t,
                        "Usage": usage_results_by_storage[storage][data_type.id][n],
                        "Average Age": avg_data_age_results_by_storage[storage][data_type.id][n],
                        "Min. Age": min_data_age_results_by_storage[storage][data_type.id][n],
                        "Max. Age": max_data_age_results_by_storage[storage][data_type.id][n],
                        "Data Type": data_type.name,
                        "Agent": agent,
                    })

        bar.value += 1

    transmit_dataframe = pd.DataFrame(
        transmit_data, columns=["Time", "Bit Rate", "Data Transmitted", "Data Type", "Agent", "Target"])
    transmit_dataframe.fillna(0, inplace=True)
    receive_dataframe = pd.DataFrame(receive_data, columns=["Time", "Bit Rate", "Data Received", "Agent", "Target"])
    receive_dataframe.fillna(0, inplace=True)
    data_storage_dataframe = pd.DataFrame(data_storage_data, columns=[
                                          "Time", "Usage", "Average Age", "Min. Age", "Max. Age", "Data Type", "Agent"])

    return transmit_dataframe, receive_dataframe, data_storage_dataframe
