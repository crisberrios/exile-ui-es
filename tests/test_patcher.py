# tests/test_patcher.py
import json
from pathlib import Path
import tempfile

from exile_ui_es.patcher import generate_patch, apply_patch, save_patch


def test_generate_patch_values_changed():
    """Generates a patch capturing changed values."""
    original = {"key1": "Hello", "key2": "World"}
    translated = {"key1": "Hola", "key2": "Mundo"}
    patch = generate_patch(original, translated)
    assert "values_changed" in patch
    assert patch["values_changed"]["root['key1']"]["new_value"] == "Hola"
    assert patch["values_changed"]["root['key2']"]["new_value"] == "Mundo"


def test_generate_patch_item_added():
    """Generates a patch capturing added keys as a list of paths."""
    original = {"key1": "Hello"}
    translated = {"key1": "Hello", "key2": "New Key"}
    patch = generate_patch(original, translated)
    assert "dictionary_item_added" in patch
    assert "root['key2']" in str(patch["dictionary_item_added"])
    # The translated value is stored in _translated
    assert "_translated" in patch
    assert patch["_translated"]["key2"] == "New Key"


def test_generate_patch_item_removed():
    """Generates a patch capturing removed keys as a list of paths."""
    original = {"key1": "Hello", "key2": "Removed"}
    translated = {"key1": "Hello"}
    patch = generate_patch(original, translated)
    assert "dictionary_item_removed" in patch


def test_generate_patch_no_changes():
    """Returns an empty dict when there are no changes."""
    original = {"key1": "Same", "key2": "Also same"}
    translated = {"key1": "Same", "key2": "Also same"}
    patch = generate_patch(original, translated)
    assert patch == {}


def test_apply_patch_values_changed():
    """apply_patch reconstructs the translated dict from a values_changed patch."""
    original = {"key1": "Hello", "key2": "World"}
    translated = {"key1": "Hola", "key2": "Mundo"}
    patch = generate_patch(original, translated)
    result = apply_patch(original, patch)
    assert result == translated


def test_apply_patch_item_added():
    """apply_patch adds new keys from a dictionary_item_added patch."""
    original = {"key1": "Hello"}
    translated = {"key1": "Hello", "key2": "New"}
    patch = generate_patch(original, translated)
    result = apply_patch(original, patch)
    assert result == translated


def test_apply_patch_item_removed():
    """apply_patch removes keys from a dictionary_item_removed patch."""
    original = {"key1": "Hello", "key2": "Removed"}
    translated = {"key1": "Hello"}
    patch = generate_patch(original, translated)
    result = apply_patch(original, patch)
    assert result == translated


def test_apply_patch_idempotent():
    """Applying the same patch twice gives the same result."""
    original = {"key1": "Hello"}
    translated = {"key1": "Hola"}
    patch = generate_patch(original, translated)
    result1 = apply_patch(original, patch)
    result2 = apply_patch(result1, patch)
    assert result1 == result2


def test_apply_patch_does_not_mutate_original():
    """apply_patch returns a new dict, leaving the original unchanged."""
    original = {"key1": "Hello"}
    orig_copy = dict(original)
    translated = {"key1": "Hola"}
    patch = generate_patch(original, translated)
    apply_patch(original, patch)
    assert original == orig_copy


def test_save_patch_roundtrip():
    """save_patch writes valid JSON that can be reloaded."""
    patch = {
        "values_changed": {
            "root['key1']": {"new_value": "Hola", "old_value": "Hello"}
        },
        "_translated": {"key1": "Hola"},
    }
    with tempfile.TemporaryDirectory() as tmp:
        filepath = Path(tmp) / "test.patch.json"
        save_patch(patch, filepath)
        assert filepath.exists()
        loaded = json.loads(filepath.read_text(encoding="utf-8"))
        assert loaded == patch