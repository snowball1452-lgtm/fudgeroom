"""Play sheets (ADR-0004): verified knowledge the Voice selects from.

A sheet is a JSON document with three parts:

  facts:    verified knowledge entries, each with an id, trigger tags,
            and plane-separated diction. THIS IS ALL THE VOICE MAY SAY.
  policies: cooldown, separation window, confidence floor.
  meta:     sheet semver, game, session the facts were verified in.

The Voice never free-forms gameplay knowledge; if it isn't in the sheet,
it isn't said. Sheets are authored offline and taste-verified (ADR-0004).
"""

import json
from pathlib import Path

REQUIRED = ("sheet_version", "game", "facts", "policies")


class SheetError(ValueError):
    pass


def load(path) -> dict:
    sheet = json.loads(Path(path).read_text())
    missing = [k for k in REQUIRED if k not in sheet]
    if missing:
        raise SheetError(f"sheet missing required keys: {missing}")
    for fact in sheet["facts"]:
        if "id" not in fact or "diction" not in fact:
            raise SheetError(f"fact missing id or diction: {fact}")
    return sheet
