import secrets
from pathlib import Path

import pytest
from hamcrest import assert_that, equal_to

from gost_espd_checker.rules import Rules


def test_renders_violation_with_severity_id_and_clause(tmp_path: Path) -> None:
    key = f"ESPD-{secrets.randbelow(900) + 100}-{secrets.randbelow(90) + 10}"
    path = tmp_path / "правила.yaml"
    path.write_text(
        "- id: ESPD-106-01\n  clause: ГОСТ 19.106-78, п. 1.5\n"
        "  severity: ошибка\n"
        f"- id: {key}\n  clause: ГОСТ 19.505-79, п. 1.2\n"
        "  severity: предупреждение\n",
        encoding="utf-8",
    )
    assert_that(
        Rules(path).rule(key).line("раздел 4", "нет раздела"),
        equal_to(
            f"раздел 4: предупреждение {key}: нет раздела"
            " (ГОСТ 19.505-79, п. 1.2)"
        ),
        "violation was not rendered with the severity, the id and the clause",
    )


def test_rejects_rule_missing_from_table(tmp_path: Path) -> None:
    path = tmp_path / "правила.yaml"
    path.write_text(
        "- id: ESPD-106-01\n  clause: ГОСТ 19.106-78, п. 1.5\n"
        "  severity: ошибка\n",
        encoding="utf-8",
    )
    with pytest.raises(KeyError, match="ESPD-999-99"):
        Rules(path).rule("ESPD-999-99")
