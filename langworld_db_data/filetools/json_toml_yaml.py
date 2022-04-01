import json
from pathlib import Path
from typing import Union

import toml
import yaml
from yaml.parser import ParserError

YAML_INDENT = ' ' * 2


def check_yaml_file(path_to_file: Path, verbose: bool = True):
    """Checks YAML file and throws exception if some problem occurs while
    reading YAML data.
    """
    if verbose:
        print('Checking', path_to_file.name)

    with path_to_file.open(mode='r', encoding='utf-8') as yaml_file:
        data = yaml_file.read()

    try:
        yaml_loaded = yaml.load(data, Loader=yaml.Loader)
    except ParserError as e:
        print(e)  # to make sure it's printed nicely and shows the user where the problem in file is
        raise ParserError(f'Error reading YAML from file {path_to_file}')

    assert isinstance(yaml_loaded, (list, dict))

    if verbose:
        print('TEST: YAML DATA', yaml_loaded)


def read_json_toml_yaml(path_to_file: Path) -> Union[dict, list]:
    if not path_to_file.exists():
        raise FileNotFoundError(f'Cannot read JSON, TOML or YAML from non-existent file {path_to_file}')

    extension = path_to_file.suffix.replace('.', '')
    if extension not in {'json', 'toml', 'yaml'}:
        raise TypeError(f'File {path_to_file.name} cannot be converted')

    data = None

    with path_to_file.open(mode='r', encoding='utf-8') as fh:
        content = fh.read()
        # I could make the following more concise and avoid repetition
        # by binding extension to name of module, but what if modules change?
        # This will seem to be an unstable construct.
        if extension == 'json':
            data = json.loads(content)
        elif extension == 'toml':
            data = toml.loads(content)
        elif extension == 'yaml':
            try:
                data = yaml.load(content, Loader=yaml.Loader)
            except ParserError as e:
                print(f'Error parsing YAML in file {path_to_file}:', e)

    if not isinstance(data, (dict, list)):
        raise ValueError(f'Could not convert file {path_to_file} because of malformed data')

    return data


if __name__ == '__main__':
    pass
