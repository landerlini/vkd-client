from vkd_client import YamlProcessor
import os 
import jinja2 
import logging
import json, re


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

