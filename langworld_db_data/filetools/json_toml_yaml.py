import json
from collections import Counter
from pathlib import Path
import re
from typing import Union

import toml
import yaml
from yaml.parser import ParserError

YAML_INDENT = " " * 2


def check_yaml_file(path_to_file: Path, verbose: bool = True) -> None:
    """Checks YAML file and throws exception if some problem occurs while
    reading YAML data.
    """
    if verbose:
        print("Checking", path_to_file.name)

    with path_to_file.open(encoding="utf-8") as yaml_file:
        data = yaml_file.read()

    # YAML parser does not catch duplicate dict keys, it keeps the value of the last key it sees.
    # For my purposes, a check of only top-level keys will be enough:
    # an optional hyphen, a colon after the key.
    # The key can be anything but a space or a hyphen (to avoid catching lower-level keys).
    pattern_for_top_level_dict_keys = re.compile(r"^(- )?(?P<key>[^\s-]+)\s?:.*")

    top_level_dict_keys = [
        pattern_for_top_level_dict_keys.match(line).group("key")
        for line in data.splitlines()
        if pattern_for_top_level_dict_keys.match(line) is not None
    ]

    counter = Counter(top_level_dict_keys)
    for key in counter:
        if counter[key] > 1:
            raise ParserError(
                f"File {path_to_file} contains more than one dictionary key <{key}> at the top level"
            )

    try:
        yaml_loaded = yaml.load(data, Loader=yaml.Loader)
    except ParserError as e:
        print(
            e
        )  # to make sure it's printed nicely and shows the user where the problem in file is
        raise ParserError(f"Error reading YAML from file {path_to_file}")

    assert isinstance(yaml_loaded, (list, dict))

    if verbose:
        print("TEST: YAML DATA", yaml_loaded)


def read_json_toml_yaml(path_to_file: Path) -> Union[dict, list]:
    if not path_to_file.exists():
        raise FileNotFoundError(
            f"Cannot read JSON, TOML or YAML from non-existent file {path_to_file}"
        )

    extension = path_to_file.suffix.replace(".", "")

    if extension == "yaml":
        check_yaml_file(path_to_file, verbose=False)

    data = None

    with path_to_file.open(encoding="utf-8") as fh:
        content = fh.read()
        # I could make the following more concise and avoid repetition
        # by binding extension to name of module, but what if modules change?
        # This will seem to be an unstable construct.
        if extension == "json":
            data = json.loads(content)
        elif extension == "toml":
            data = toml.loads(content)
        elif extension == "yaml":
            data = yaml.load(content, Loader=yaml.Loader)
        else:
            raise TypeError(f"File {path_to_file.name} cannot be converted")

    if not isinstance(data, (dict, list)):
        raise ParserError(
            f"Could not convert file {path_to_file} because of malformed data"
        )

    return data
