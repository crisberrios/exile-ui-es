# exile_ui_es/patcher.py
import json
import re
from pathlib import Path
from deepdiff import DeepDiff


_PATH_KEY_RE = re.compile(r"root\['([^']*)'\]")


def _parse_path(path: str) -> str:
    """Extract the top-level key from a DeepDiff path like root['key']."""
    m = _PATH_KEY_RE.match(path)
    if m:
        return m.group(1)
    return path


def generate_patch(original: dict[str, str], translated: dict[str, str]) -> dict:
    """Generate a JSON-serializable patch from original to translated.

    Uses DeepDiff internally and returns a dict suitable for JSON serialization.
    The patch includes the full translated dict so that added keys retain their values.
    Returns an empty dict when there are no changes.
    """
    diff = DeepDiff(original, translated, ignore_order=True)
    result: dict = {}

    dd = diff.to_dict()

    if "values_changed" in dd:
        result["values_changed"] = dd["values_changed"]

    if "dictionary_item_added" in dd:
        added = dd["dictionary_item_added"]
        if isinstance(added, str):
            # "SetOrdered([...])" string representation
            result["dictionary_item_added"] = list(_PATH_KEY_RE.findall(added))
        elif hasattr(added, "__iter__") and not isinstance(added, (dict, str)):
            result["dictionary_item_added"] = [str(p) for p in added]
        else:
            result["dictionary_item_added"] = list(added)

    if "dictionary_item_removed" in dd:
        removed = dd["dictionary_item_removed"]
        if isinstance(removed, str):
            result["dictionary_item_removed"] = list(
                _PATH_KEY_RE.findall(removed)
            )
        elif hasattr(removed, "__iter__") and not isinstance(removed, (dict, str)):
            result["dictionary_item_removed"] = [
                _parse_path(str(p)) for p in removed
            ]
        else:
            result["dictionary_item_removed"] = list(removed)

    # Store the full translated dict so added-key values are recoverable
    if result:
        result["_translated"] = dict(translated)

    return result


def apply_patch(original: dict[str, str], patch: dict) -> dict[str, str]:
    """Apply a patch (produced by generate_patch) to original strings."""
    result = dict(original)

    if "values_changed" in patch:
        for path, change in patch["values_changed"].items():
            key = _parse_path(path)
            result[key] = change["new_value"]

    if "dictionary_item_removed" in patch:
        for key_path in patch["dictionary_item_removed"]:
            key = key_path.replace("root['", "").replace("']", "")
            result.pop(key, None)

    if "dictionary_item_added" in patch and "_translated" in patch:
        translated = patch["_translated"]
        for key_path in patch["dictionary_item_added"]:
            key = key_path.replace("root['", "").replace("']", "")
            if key in translated:
                result[key] = translated[key]

    return result


def save_patch(patch: dict, filepath: Path) -> None:
    """Save a patch dict to disk as JSON."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(
        json.dumps(patch, indent=2, ensure_ascii=False), encoding="utf-8"
    )