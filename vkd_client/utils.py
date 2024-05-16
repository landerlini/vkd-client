from vkd_client import YamlProcessor
from typing import Collection, List, Literal
import os 
import jinja2 
import logging
import json, re

FileSystemType = Literal['nfs', 'juicefs', 'rclone']

def process_form_template(template: str, **kwargs):
    """
    Simple utility function to process a YAML template and submit it.
    """
    processor = YamlProcessor()
    logging.info(f"Processing template {template}, setting variables: [{', '.join(kwargs.keys())}]")
    with open(os.path.join(os.path.dirname(__file__), 'templates', f'{template}.yaml')) as template_file:
        template = jinja2.Environment().from_string(template_file.read())
    return processor.process(template.render(**kwargs))



def get_snakemake_job_properties(filepath: str):
    """
    Parse a Snakemake script file and return the dictionary of the job properties.
    """
    with open(filepath) as jobscript_file:
        groups = re.findall(
            "# properties = ([^\n]+)\n", 
            [line for line in jobscript_file if line.startswith("# properties")][0]
            )

        if len(groups) == 0:
            raise IOError("Cannot parse Snakemake script file. Properties not found.")
        if len(groups) > 1:
            raise IOError("Invalid Snakemake script. Too many definition for properties.")

        return json.loads(groups[0])


def get_volumes_from_filenames(filenames: Collection[str], filesystem_type: FileSystemType) -> List[str]:
    """
    Explore `/proc/mounts` to identify NFS mount-points providing files in `filenames`.
    """
    ## Identify nfs volumes
    import pandas as pd 
    mounts = pd.read_csv("/proc/mounts", sep=" ", header=None)
    mounts.columns = ['device', 'mount_point', 'fs', 'options', 'dummy', 'dummy']
    selected_mounts = mounts[mounts.fs.str.contains(filesystem_type)].mount_point.values
    required_mounts = []
    for filename in filenames:
        abs_path = os.path.abspath(filename)
        required_mounts += [mp for mp in selected_mounts if abs_path.startswith(mp)]
    
    return list(set(required_mounts))
