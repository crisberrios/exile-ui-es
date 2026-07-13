import json
from pathlib import Path


def _load_terms() -> dict:
    path = Path(__file__).parent.parent / "data" / "poe_terms_es.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_poe_terms_valid_json():
    path = Path(__file__).parent.parent / "data" / "poe_terms_es.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert "currency" in data
    assert "item_classes" in data
    assert "leagues" in data
    assert "masters" in data
    assert "skill_gems" in data
    assert "mod_types" in data


def test_poe_terms_non_empty():
    data = _load_terms()
    assert len(data["currency"]) > 0
    assert len(data["leagues"]) > 0
    assert len(data["item_classes"]) > 0
    assert len(data["masters"]) > 0
    assert len(data["skill_gems"]) > 0
    assert len(data["mod_types"]) > 0


def test_poe_terms_all_str_str():
    """Every category's values must be str→str mappings."""
    data = _load_terms()
    for category_name, category in data.items():
        for en, es in category.items():
            assert isinstance(en, str), f"{category_name}.{en} key not str"
            assert isinstance(es, str), f"{category_name}.{en} value not str"
            assert len(en) > 0, f"{category_name} has empty key"
            assert len(es) > 0, f"{category_name}.{en} has empty value"


def test_poe_terms_key_currencies():
    """Verify specific key currencies are present."""
    data = _load_terms()
    assert data["currency"]["Chaos Orb"] == "Orbe del Caos"
    assert data["currency"]["Divine Orb"] == "Orbe Divino"
    assert data["currency"]["Exalted Orb"] == "Orbe Exaltado"
    assert data["currency"]["Mirror of Kalandra"] == "Espejo de Kalandra"


def test_poe_terms_key_leagues():
    data = _load_terms()
    assert data["leagues"]["Betrayal"] == "Traición"
    assert data["leagues"]["Breach"] == "Brecha"
    assert data["leagues"]["Abyss"] == "Abismo"


def test_poe_terms_key_item_classes():
    data = _load_terms()
    assert data["item_classes"]["Body Armour"] == "Armadura Corporal"
    assert data["item_classes"]["Helmet"] == "Casco"
    assert data["item_classes"]["Boots"] == "Botas"


def test_poe_terms_master_names_unchanged():
    """Most master names stay the same; It That Fled is the exception."""
    data = _load_terms()
    assert data["masters"]["Aisling"] == "Aisling"
    assert data["masters"]["Cameria"] == "Cameria"
    assert data["masters"]["Elreon"] == "Elreon"
    assert data["masters"]["It That Fled"] == "Aquello que Huyó"


def test_poe_terms_mod_types():
    data = _load_terms()
    assert data["mod_types"]["Prefix"] == "Prefijo"
    assert data["mod_types"]["Suffix"] == "Sufijo"