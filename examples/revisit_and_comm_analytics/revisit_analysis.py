from datetime import datetime
from itertools import groupby

import pandas as pd
from IPython.display import display
from ipywidgets import IntProgress
from sedaro import SedaroAgentResult
from sedaro.modsim import mjd_to_datetime


def target_revisit_results(
    observer_results: dict[str, SedaroAgentResult],
    revisit_condition_ids: dict[str, str],
    target_names_by_id: dict[str, str],
    observer_to_target_mapping: dict[str, dict[str, str]],
) -> pd.DataFrame:
    """Extract revisit data from observer results."""

    bar = IntProgress(min=0, max=len(observer_results), layout={'width': '100%'})
    display(bar)

    revisits: list[dict[str, datetime | str]] = []
    for agent, agent_results in observer_results.items():
        condition_compliance_results = agent_results.block(revisit_condition_ids[agent]).targetCompliance
        compliance_values: dict[str, list[bool]] = condition_compliance_results.values
        compliance_times = [mjd_to_datetime(t) for t in condition_compliance_results.mjd]  # datetimes for each point
        for target_id, compliance_series in compliance_values.items():
            # group consecutive compliance values
            for compliance, group in groupby(enumerate(compliance_series), key=lambda x: x[1]):
                if compliance:
                    revisit_indices: list[int] = [index for index, _ in group]  # indices where compliance is True
                    # if the last compliance is not the last in the series
                    if revisit_indices[-1] < len(compliance_series) - 1:
                        revisit_indices.append(revisit_indices[-1] + 1)  # add the index after the last compliance
                    revisit_start_time = compliance_times[revisit_indices[0]]
                    revisit_end_time = compliance_times[revisit_indices[-1]]
                    real_target_id = observer_to_target_mapping[agent].get(target_id, target_id)
                    revisits.append({
                        "Agent": agent,
                        "Target": target_names_by_id[real_target_id],
                        "Start": revisit_start_time,
                        "End": revisit_end_time,
                        "Duration": revisit_end_time - revisit_start_time
                    })

        bar.value += 1

    return pd.DataFrame(revisits)


def target_revisit_statistics(
    revisits: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate revisit statistics for each target and the total."""

    unique_targets = revisits["Target"].unique()

    bar = IntProgress(min=0, max=len(unique_targets) + 1, layout={'width': '100%'})
    display(bar)

    revisits.sort_values(by=["Start", "End"], inplace=True)
    revisit_statistics: list[dict[str, float]] = []
    for target in unique_targets:
        target_revisits: pd.DataFrame = revisits[revisits["Target"] == target]
        if not target_revisits.empty:
            revisit_statistics.append({
                "Target": target,
                "Average Duration": target_revisits["Duration"].mean(),
                "Total Duration": target_revisits["Duration"].sum(),
                "Number of Revisits": target_revisits["Duration"].count(),
                "Min. Time Between Revisits": target_revisits["Start"].diff().min(),
                "Max. Time Between Revisits": target_revisits["Start"].diff().max(),
            })

        bar.value += 1

    revisit_statistics.append({
        "Target": "Total",
        "Average Duration": revisits["Duration"].mean(),
        "Total Duration": revisits["Duration"].sum(),
        "Number of Revisits": revisits["Duration"].count(),
        "Min. Time Between Revisits": revisits["Start"].diff().min(),
        "Max. Time Between Revisits": revisits["Start"].diff().max(),
    })

    bar.value += 1

    return pd.DataFrame(revisit_statistics)
