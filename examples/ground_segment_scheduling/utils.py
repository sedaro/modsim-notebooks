import datetime as dt
import json
from collections import defaultdict
from functools import cache
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
import sedaro
from sedaro import SedaroApiClient

if TYPE_CHECKING:
    from sedaro import SedaroAgentResult
    from sedaro.branches import AgentTemplateBranch


def sedaroLogin():
    '''
    Utility for credentialed access to the sedaro client
    '''
    with open('../../secrets.json', 'r') as file:
        API_KEY = json.load(file)['API_KEY']
    return SedaroApiClient(API_KEY)


def _parse_tuple_stream(field, key):
    '''
    Helper function to parse the data from the client until we improve this.
    '''
    zero = field.__getattr__(key).__getattr__('0').values
    one = field.__getattr__(key).__getattr__('1').values
    return list(zip(zero, one))


def schedule_table(gs_template: 'AgentTemplateBranch', ground_segment_results: 'SedaroAgentResult', use_interfaces: list[str] = None):
    '''
    Get schedule data in an easily plottable form
    '''
    scheduler = gs_template.ContactScheduler.get_first()
    ai_field = ground_segment_results.block(scheduler.id).activeInterfaces
    ts = ai_field.elapsed_time
    start_dt = sedaro.modsim.mjd_to_datetime(ai_field.mjd[0])

    # Get the interfaces associated with the scheduler
    interfaces = [i.id for i in scheduler.interfaces.keys()]
    if use_interfaces is not None:
        interfaces = [i for i in interfaces if i in use_interfaces]
    # Reconstruct dict from stream
    active_interfaces_dict = {}
    for id_ in interfaces:
        active_interfaces_dict[id_] = _parse_tuple_stream(ai_field, id_)

    # Helper function to get block names
    @cache
    def id_to_name(id_):
        return ground_segment_results.block(id_).name

    # Get table rows
    rows = []
    for interface_id, series in active_interfaces_dict.items():
        start = None
        active_target = None
        active_antenna = None
        for i, (target_id, antenna) in enumerate(series):
            if pd.isna(target_id):
                target_id = None
            # Start tracking
            if active_target is None and target_id is not None:
                start = ts[i]
                active_target = target_id
                active_antenna = antenna
            # Cut off tracking for old target and start new tracking
            elif active_target != target_id:
                if active_target is not None:
                    rows.append({
                        'start': start_dt + dt.timedelta(seconds=start),
                        'end': start_dt + dt.timedelta(seconds=ts[i]),
                        'target': id_to_name(active_target),
                        'antenna': id_to_name(active_antenna),
                        'interface': interface_id
                    })
                start = ts[i]
                active_target = target_id
                active_antenna = antenna
            # Continue tracking
            else:
                pass
    rows.sort(key=lambda x: x['target'])  # allows for the legend to be in target order
    return pd.DataFrame(rows)


def _space_target_ids(model_dict: dict) -> list[str]:
    '''
    Helper function to get the ids of all space targets
    '''
    ids = []
    for block in model_dict['blocks'].values():
        if block['type'] == 'NetworkSpaceTarget':
            ids.append(block['id'])
    return ids


def target_analytics(ground_segment_results: 'SedaroAgentResult'):
    # Get targets (some are generated for TG)
    model_dict = ground_segment_results._SedaroAgentResult__initial_state
    target_ids = _space_target_ids(model_dict)
    target_rows = {}

    # Helper function to get block names
    @cache
    def id_to_name(id_):
        return ground_segment_results.block(id_).name

    for i in range(len(target_ids)):
        target_results = ground_segment_results.block(target_ids[i])
        access_per_antenna = target_results.accessPerCommDevice.values
        ts = target_results.accessPerCommDevice.elapsed_time
        start_dt = sedaro.modsim.mjd_to_datetime(target_results.accessPerCommDevice.mjd[0])

        def get_ranges(series: list[bool]) -> list[tuple[int, int]]:
            ranges = []
            start = None
            for i, value in enumerate(series):
                if value and start is None:
                    start = i
                elif not value and start is not None:
                    ranges.append((start, i))
                    start = None
            if start is not None:
                ranges.append((start, -1))
            return ranges

        def to_rows(per_antenna, key=None):
            rows = []

            for antenna_id, series in per_antenna.items():
                for start, stop in get_ranges(series):
                    rows.append({
                        'start': start_dt + dt.timedelta(seconds=ts[start]),
                        'end': start_dt + dt.timedelta(seconds=ts[stop]),
                        'antenna': id_to_name(antenna_id),
                        'type': key
                    })
            return rows

        access_rows = to_rows(access_per_antenna, 'access')
        inFov_rows = to_rows(target_results.inFovPerCommDevice.values, 'inFov')
        connected_rows = to_rows(target_results.connectedPerCommDevice.values, 'connected')
        df = pd.DataFrame(access_rows + inFov_rows + connected_rows)

        target_rows[target_results.name] = df

    return target_rows


def get_ranges(series: list[bool]) -> list[tuple[int, int]]:
    ranges = []
    start = None
    for i, value in enumerate(series):
        if value and start is None:
            start = i
        elif not value and start is not None:
            ranges.append((start, i))
            start = None
    if start is not None:
        ranges.append((start, len(series)-1))
    return ranges


def contact_booleans_to_intervals(
        projected_contacts: dict[str, dict[str, list[bool]]],
        tg_targets: list[tuple[str, list[str], list[str]]]
    ) -> tuple[
        dict[tuple[str, str], list[tuple[int, int]]],
        list[tuple[int, int]],
        dict[str, list[int]],
        dict[str, list[int]]]:
    '''
    Following section 2.1 of Eddy et al
    '''
    # Create a map of each target to its target group
    mapped_tgs = []
    target_map = {}
    for tg_id, target_ids, _ in tg_targets:
        if tg_id not in mapped_tgs:
            for target_id in target_ids:
                target_map[target_id] = tg_id
    # Reshape dictionary to be list of intervals for each target-antenna pair
    c_t = {}
    # Also create a flat version with views per location and satellite
    C = []
    contact_pairs = []
    durations = []
    c_location = defaultdict(list)
    c_satellite = defaultdict(list)
    c_tg = defaultdict(list)
    i = 0
    for antenna, per_target in projected_contacts.items():
        for sat, contact_series in per_target.items():
            pair = (antenna, sat)
            ranges = get_ranges(contact_series)
            c_t[pair] = ranges
            C.extend(ranges)
            durations.extend([stop - start for start, stop in ranges])
            range_indices = list(range(i, i + len(ranges)))
            c_location[antenna].extend(range_indices)
            c_satellite[sat].extend(range_indices)
            c_tg[target_map[sat]].extend(range_indices)
            contact_pairs.extend(pair for _ in range(len(ranges)))
            i += len(ranges)
    return c_t, C, c_location, c_satellite, c_tg, durations, contact_pairs


def selected_contacts_to_schedule(
    selected_contacts: list[bool],
    all_contact_intervals: list[tuple[int, int]],
    contact_labels: list[tuple[str, str]],
    target_series: dict[str, list[np.ndarray]],
    interface_ids_type: list[tuple[str, str]],
    tg_targets: list[tuple[str, list[str], list[str]]],
    mjd_start: float,
    resolution_seconds: float,
) -> list[dict[str, Any]]:
    # Create a lookup for target to agent
    target_data = defaultdict(dict)
    for i, (tg_id, target_ids, agent_ids) in enumerate(tg_targets):
        for target_id, agent_id in zip(target_ids, agent_ids):
            target_data[target_id]['agentId'] = agent_id
            interface_id, interface_type = interface_ids_type[i]
            if 'Receive' in interface_type:
                target_data[target_id]['downlinkInterface'] = interface_id
            else:
                target_data[target_id]['uplinkInterface'] = interface_id
    # Loop through the selected contacts and create a schedule
    n_windows = len(contact_labels)
    schedule = []
    for i, selected in enumerate(selected_contacts):
        if selected:
            antenna, target = contact_labels[i % n_windows]
            start_i, end_i = all_contact_intervals[i % n_windows]
            start_mjd = mjd_start + start_i * resolution_seconds / 86400
            end_mjd = mjd_start + end_i * resolution_seconds / 86400
            entry = {
                'groundCommDevice': antenna,
                'targetId': target,
                'agentId': target_data[target]['agentId'],
                'targetPosition': target_series[target][start_i].tolist(),
                'activeInterval': (start_mjd, end_mjd),
            }
            if i < n_windows:  # Downlink
                entry['interfaceId'] = target_data[target]['downlinkInterface']
            else:
                entry['interfaceId'] = target_data[target]['uplinkInterface']
            schedule.append(entry)
    return schedule
