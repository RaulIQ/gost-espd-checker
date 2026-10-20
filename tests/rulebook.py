from pathlib import Path

import gost_espd_checker
from gost_espd_checker.rules import Rules


def rulebook() -> Rules:
    return Rules(Path(gost_espd_checker.__file__).with_name("rules.yaml"))
