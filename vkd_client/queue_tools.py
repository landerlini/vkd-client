import pandas as pd
import numpy as np
import sys
from pprint import pprint
from io import StringIO

from .BaseProcessor import BaseProcessor
from .RestConfigBlock import RestConfigBlock

def update_queues(raw_input: str):
    buffer = StringIO(raw_input)
    df = pd.read_csv(buffer)
    print (df)

    clusterqueues = list()
    for queue_name, queue in df.groupby('name'):
        cohorts = set(queue.cohort.values)
        if len(cohorts) > 1:
            raise ValueError(f"Multiple cohorts defined for queue {queue_name}: {cohorts}")

        clusterqueues.append(
            dict(
                name=queue_name,
                spec=dict(
                    cohort=next(iter(cohorts)),
                    namespaceSelector={},
                    resourceGroups=[
                        dict(
                            coveredResources=["cpu", "memory", "nvidia.com/gpu"],
                            flavors=[
                                dict(
                                    name=f.flavor,
                                    resources=[
                                        dict(
                                            name="cpu", 
                                            nominalQuota=f.cpu_quota, 
                                            **({'borrowingLimit': f.cpu_limit} if np.isfinite(f.cpu_limit) else {})
                                            ),
                                        dict(
                                            name="memory", 
                                            nominalQuota=f.memory_quota, 
                                            **({'borrowingLimit': f.memory_limit} if np.isfinite(f.memory_limit) else {})
                                            ),
                                        dict(
                                            name="nvidia.com/gpu", 
                                            nominalQuota=f.gpu_quota, 
                                            **({'borrowingLimit': f.gpu_limit} if np.isfinite(f.gpu_limit) else {})
                                            ),
                                    ],
                                ) for f in queue.itertuples()
                            ]
                        )
                    ]
                )
            )
        )
    
    pprint (clusterqueues)
    current_queues = BaseProcessor().process(
        RestConfigBlock(method='GET', resource='clusterqueues', select={'name': dict(field='name')})
    )

    BaseProcessor().process([
        RestConfigBlock(method='DELETE', resource='clusterqueues', data=[dict(name=name) for name in current_queues.df.name])
    ])

    BaseProcessor().process([
        RestConfigBlock(method='POST', resource='clusterqueues', data=clusterqueues)
        ])



def format_queues(raw_queues: str): 
    spec_rows = []
    for rq in raw_queues:
        spec_rows += [
            dict(
                cohort=rq.get('spec', {}).get('cohort'),
                name=rq['name'],
                flavor=f['name'],
                cpu_quota={res['name']: res.get('nominalQuota', '0') for res in f['resources']}.get('cpu'),
                memory_quota={res['name']: res.get('nominalQuota', '0') for res in f['resources']}.get('memory'),
                gpu_quota={res['name']: res.get('nominalQuota', '0') for res in f['resources']}.get('nvidia.com/gpu'),
                cpu_limit={res['name']: res.get('borrowingLimit') for res in f['resources']}.get('cpu'),
                memory_limit={res['name']: res.get('borrowingLimit') for res in f['resources']}.get('memory'),
                gpu_limit={res['name']: res.get('borrowingLimit') for res in f['resources']}.get('nvidia.com/gpu'),
            ) for rg in rq.get('spec', {}).get('resourceGroups', []) for f in rg.get('flavors', [])
        ]
    spec_df = pd.DataFrame(spec_rows)
    
    usage_rows = []
    for rq in raw_queues:
        usage_rows += [
            dict(
                name=rq['name'],
                flavor=f['name'],
                cpu_used={res['name']: res.get('total', '0') for res in f['resources']}.get('cpu'),
                memory_used={res['name']: res.get('total', '0') for res in f['resources']}.get('memory'),
                gpu_used={res['name']: res.get('total', '0') for res in f['resources']}.get('nvidia.com/gpu'),
                cpu_borrowed={res['name']: res.get('borrowed', '0') for res in f['resources']}.get('cpu'),
                memory_borrowed={res['name']: res.get('borrowed', '0') for res in f['resources']}.get('memory'),
                gpu_borrowed={res['name']: res.get('borrowed', '0') for res in f['resources']}.get('nvidia.com/gpu'),
            ) for f in rq.get('status', {}).get('flavorsReservation', []) 
        ]
    usage_df = pd.DataFrame(usage_rows)

    df = pd.merge(left=spec_df, right=usage_df, on=["name", "flavor"])
    buffer = StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer.read()
