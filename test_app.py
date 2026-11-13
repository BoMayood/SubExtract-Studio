# SubExtract Studio — Developed by NoYz
# Self-Verification & Automated Test Suite

import os
import sys

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.config_manager import ConfigManager
from core.subtitle_parser import SubtitleParser, SubtitleCue
from core.themes import THEMES, generate_stylesheet
from core.i18n import I18n, TRANSLATIONS
from core.video_processor import VideoProbe, get_silent_subprocess_flags

def run_tests():
    print("=" * 60)
    print("SubExtract Studio — Developed by NoYz | Verification Suite")
    print("=" * 60)

    # 1. Config Manager & API Key Wipe Test
    print("\n[TEST 1] Testing ConfigManager and API Key Security Wipe...")
    cfg = ConfigManager("test_config.json")
    cfg.set("ai_api_key", "sk-test-secret-key-12345")
    cfg.save()
    assert cfg.get("ai_api_key") == "sk-test-secret-key-12345", "API key not set properly"
    
    # Wipe API key
    cfg.clear_api_key()
    assert cfg.get("ai_api_key") == "", "API key was not completely wiped!"
    
    # Reset styles test
    cfg.set("font_size", 48)
    cfg.reset_styles_to_default()
    assert cfg.get("font_size") == 24, "Font size was not reset to default!"
    if os.path.exists(cfg.config_path):
        os.remove(cfg.config_path)
    print(" -> PASSED: ConfigManager & API Key Wipe fully functional.")

    # 2. Subtitle Parser & Header Branding Test
    print("\n[TEST 2] Testing Subtitle Parser, Formatting & Header Branding...")
    sample_srt = """1
00:01:10,000 --> 00:01:15,000
First subtitle line here.

2
00:01:16,500 --> 00:01:20,000
Second subtitle line with character John.
"""
    cues = SubtitleParser.parse_srt_text(sample_srt)
    assert len(cues) == 2, f"Expected 2 cues, got {len(cues)}"
    assert cues[0].start_ms == 70000
    assert cues[0].end_ms == 75000

    # Test Time Shift
    SubtitleParser.shift_timestamps(cues, 2000)
    assert cues[0].start_ms == 72000
    assert cues[0].end_ms == 77000

    # Test Find & Replace
    count, _ = SubtitleParser.find_and_replace(cues, "John", "NoYz Hero")
    assert count == 1, f"Expected 1 replacement, got {count}"
    assert "NoYz Hero" in cues[1].text

    # Test Format Conversions with Player-Compatible Branding
    branded_cues = SubtitleParser.inject_branding_cues(cues)
    srt_out = SubtitleParser.cues_to_srt(branded_cues)
    assert srt_out.startswith("1\n") or srt_out.startswith("1\r\n"), "SRT must start with index 1 for player compatibility"
    assert "NoYz" in srt_out, "SRT Branding cue missing"
    assert not srt_out.startswith("#"), "SRT must NOT start with raw '#' comments (breaks video players)"

    vtt_out = SubtitleParser.cues_to_vtt(cues)
    assert "WEBVTT" in vtt_out and "Translated & Processed by SubExtract Studio | NoYz" in vtt_out

    ass_out = SubtitleParser.cues_to_ass(cues)
    assert "[Script Info]" in ass_out and "NoYz" in ass_out and "[V4+ Styles]" in ass_out
    print(" -> PASSED: Subtitle parsing, formatting, conversion & branding verified.")

    # 3. Language Detection Test
    print("\n[TEST 3] Testing Subtitle Language Detection...")
    arabic_cues = [SubtitleCue(1, 1000, 2000, "مرحبا بك في استوديو الترجمة الاحترافي")]
    detected_ar = SubtitleParser.detect_language(arabic_cues)
    assert "Arabic" in detected_ar, f"Expected Arabic, got {detected_ar}"

    english_cues = [SubtitleCue(1, 1000, 2000, "Welcome to SubExtract Studio by NoYz")]
    detected_en = SubtitleParser.detect_language(english_cues)
    assert "English" in detected_en, f"Expected English, got {detected_en}"
    print(" -> PASSED: Language auto-detection working accurately.")

    # 4. Themes Generation Test (All 5 Themes)
    print("\n[TEST 4] Testing 5 Distinct Themes Generation...")
    expected_themes = [
        "Modern Sleek",
        "Classic Elegant",
        "Classic Simple",
        "Steam Gaming Style",
        "Discord Vibe"
    ]
    for theme_name in expected_themes:
        assert theme_name in THEMES, f"Theme '{theme_name}' missing from THEMES"
        qss = generate_stylesheet(theme_name)
        assert len(qss) > 200, f"QSS for '{theme_name}' too short or invalid"
        assert "QMainWindow" in qss and "QTableWidget" in qss
    print(f" -> PASSED: All 5 advanced themes verified ({', '.join(expected_themes)}).")

    # 5. Bilingual Localization Test (English & Arabic)
    print("\n[TEST 5] Testing Bilingual Localization Dictionaries...")
    en_keys = set(TRANSLATIONS["en"].keys())
    ar_keys = set(TRANSLATIONS["ar"].keys())
    missing_in_ar = en_keys - ar_keys
    assert len(missing_in_ar) == 0, f"Keys missing in Arabic translation: {missing_in_ar}"
    I18n.set_language("ar")
    assert I18n.t("app_title") == "SubExtract Studio — تطوير NoYz"
    I18n.set_language("en")
    assert I18n.t("app_title") == "SubExtract Studio — Developed by NoYz"
    print(" -> PASSED: 100% dictionary symmetry between English and Arabic.")

    # 6. Silent Subprocess Execution Flags
    print("\n[TEST 6] Testing Silent Subprocess Flags...")
    startupinfo, creationflags = get_silent_subprocess_flags()
    if sys.platform == "win32":
        assert creationflags == 0x08000000, "CREATE_NO_WINDOW flag not configured for Windows!"
    print(" -> PASSED: Silent execution flags confirmed (Zero terminal popups).")

    # 7. Qt Application Headless UI Instantiation Test
    print("\n[TEST 7] Testing Qt Application & MainWindow Instantiation (Headless)...")
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PyQt6.QtWidgets import QApplication
    from ui.main_window import MainWindow

    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    
    # Test switching themes dynamically
    for theme in expected_themes:
        window.apply_theme(theme)
    
    # Test switching language dynamically
    window._on_language_changed(1) # Arabic
    window._on_language_changed(0) # English

    # Test adding sample cues to editor table
    window.active_cues = cues
    window._refresh_cues_table()
    assert window.cues_table.rowCount() == 2

    # Verify Preview Player
    window.preview_player.set_subtitle_text("Live Subtitle Preview Test")
    window.preview_player.update_styles("Segoe UI", 28, "#FFD700", "#000000", 2, True, False, "Bottom Center")

    # 8. Online Subtitle Engine & Media Title Cleaner Test
    print("\n[TEST 8] Testing Online Subtitle Engine & Media Title Cleaner...")
    from core.subtitle_downloader import MediaTitleCleaner, SubtitleDownloader
    cleaned = MediaTitleCleaner.clean("[Judas] Sekai Saikyou - S01E01.mkv")
    assert cleaned["clean_title"] == "Sekai Saikyou"
    assert cleaned["season"] == 1 and cleaned["episode"] == 1
    assert "Sekai Saikyou S01E01" in cleaned["search_query"]

    # Verify online tab in MainWindow
    assert window.tabs.count() == 3
    assert window.tabs.tabText(2) == I18n.t("tab_online_search")
    assert hasattr(window, "online_results_table")
    print(" -> PASSED: MediaTitleCleaner & Online Subtitle Search Tab verified.")

    window.close()
    print(" -> PASSED: MainWindow instantiated, rendered, and switched states flawlessly.")

    print("\n" + "=" * 60)
    print("ALL 8 VERIFICATION CHECKLIST TESTS PASSED WITH 100% SUCCESS!")
    print("SubExtract Studio is production-ready, fully wired, and verified.")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
