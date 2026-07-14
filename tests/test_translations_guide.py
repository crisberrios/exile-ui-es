# tests/test_translations_guide.py
from exile_ui_es.translations.guide import translate_instruction, translate_guide


class TestTranslateInstruction:
    def test_kill_proper_name(self):
        assert translate_instruction("kill hillock") == "matar a hillock"

    def test_enter_area(self):
        result = translate_instruction("enter areaid1_1_town ;; lioneye's watch")
        assert "entrar en" in result
        assert "areaid1_1_town" in result
        assert "lioneye's watch" in result

    def test_preserves_markup(self):
        result = translate_instruction("(img:quest)nessa: <mercy_mission>")
        assert "(img:quest)" in result
        assert "nessa" in result
        assert "<mercy_mission>" in result

    def test_preserves_quest_item(self):
        result = translate_instruction(
            "follow streams for (img:quest) (quest:3_glyphs)"
        )
        assert "(quest:3_glyphs)" in result
        assert "(img:quest)" in result

    def test_find_and_enter(self):
        result = translate_instruction("find & enter areaid1_1_4_0")
        assert "buscar" in result
        assert "entrar en" in result
        assert "areaid1_1_4_0" in result

    def test_activate_waypoint(self):
        result = translate_instruction("leaguestart: activate (img:waypoint)")
        assert "leaguestart:" in result
        assert "activar" in result
        assert "(img:waypoint)" in result

    def test_preserves_arena_ref(self):
        result = translate_instruction(
            "(hint)__ (color:cc99ff)start and arena:dweller:opposite corners"
        )
        assert "arena:dweller" in result

    def test_empty_string(self):
        assert translate_instruction("") == ""

    def test_no_markup_simple(self):
        result = translate_instruction("go straight")
        assert "ir" in result.lower() or "recto" in result.lower()

    def test_proper_names_preserved(self):
        """Hillock, Nessa, Tarkleigh, Brutus should not be translated."""
        for name in ["hillock", "nessa", "tarkleigh", "brutus", "oak"]:
            result = translate_instruction(f"kill {name}")
            assert name in result.lower()

    def test_area_ids_preserved(self):
        result = translate_instruction("enter areaid1_1_7_1 ;; lower prison")
        assert "areaid1_1_7_1" in result

    def test_angle_brackets_preserved(self):
        result = translate_instruction(
            "tarkleigh: <enemy_at_the_gate>"
        )
        assert "<enemy_at_the_gate>" in result


class TestTranslateGuide:
    def test_translates_nested_structure(self):
        data = [
            [
                ["kill hillock", "enter areaid1_1_town ;; lioneye's watch"],
                {
                    "condition": ["league-start", "yes"],
                    "lines": ["leaguestart: activate (img:waypoint)"],
                },
            ]
        ]
        result = translate_guide(data)
        # First step, first line
        assert "matar a hillock" == result[0][0][0]
        # First step, condition preserved
        assert result[0][1]["condition"] == ["league-start", "yes"]
        # Condition line translated
        assert "activar" in result[0][1]["lines"][0]

    def test_empty_guide(self):
        assert translate_guide([]) == []
        assert translate_guide({}) == {}

    def test_non_string_leaves_preserved(self):
        data = [{"condition": ["league-start", "yes"], "lines": ["kill brutus"]}]
        result = translate_guide(data)
        assert result[0]["condition"] == ["league-start", "yes"]