# SubExtract Studio — Developed by NoYz
# Intellectual Property & Copyright (c) 2026 NoYz. All Rights Reserved.

import json
import os
import sys
import re

def remap_user_path(path: str) -> str:
    """
    If a path contains a hardcoded user directory from another machine (e.g. C:/Users/NoYz/...),
    dynamically remaps it to the current user's profile on this machine.
    """
    if not path or not isinstance(path, str):
        return path
    normalized = path.replace("\\", "/")
    m = re.match(r"^([a-zA-Z]:/Users/)([^/]+)(/.*)?$", normalized, re.IGNORECASE)
    if m:
        base_prefix, foreign_user, subpath = m.group(1), m.group(2), m.group(3) or ""
        curr_user = os.environ.get("USERNAME") or os.path.basename(os.path.expanduser("~"))
        if foreign_user.lower() != curr_user.lower():
            curr_home = os.path.expanduser("~").replace("\\", "/")
            return curr_home + subpath
    return path

DEFAULT_CONFIG = {
    "app_name": "SubExtract Studio",
    "developer": "NoYz",
    "theme": "Steam Gaming Style",
    "language": "ar",  # Default to Arabic for user
    "translation_engine": "AI Translation",
    "ai_provider": "Google Gemini",
    "ai_api_key": "",
    "ai_model": "gemini-3.5-flash",
    "ai_endpoint": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "source_language": "auto",
    "target_language": "ar",
    "output_format": ".srt",
    "burn_in_subtitles": False,
    "save_beside_source": True,
    "custom_output_dir": "",
    "font_family": "Segoe UI",
    "font_size": 24,
    "font_color": "#FFFFFF",
    "outline_color": "#000000",
    "outline_width": 2,
    "shadow_offset": 1,
    "font_bold": True,
    "font_italic": False,
    "subtitle_alignment": "Bottom Center",
    "tesseract_path": "",
    "sound_alerts": True,
    "last_video_queue": [],
    "last_sub_queue": []
}

class ConfigManager:
    """Manages application settings, persistent state, and secure API key wiping."""
    
    def __init__(self, filename="config.json"):
        if os.path.isabs(filename):
            self.config_path = filename
        else:
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.config_path = os.path.join(base_dir, filename)
        self.data = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        """Loads configuration from JSON file. Restores defaults if missing or corrupted."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        # Upgrade deprecated models to 2026 active models
                        if loaded.get("ai_model") in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash"]:
                            loaded["ai_model"] = "gemini-3.5-flash"

                        # Remap and validate custom_output_dir dynamically across different user machines
                        custom_dir = loaded.get("custom_output_dir", "")
                        if custom_dir:
                            remapped_dir = remap_user_path(custom_dir)
                            try:
                                os.makedirs(remapped_dir, exist_ok=True)
                                if os.path.exists(remapped_dir) and os.access(remapped_dir, os.W_OK):
                                    loaded["custom_output_dir"] = remapped_dir
                                else:
                                    loaded["custom_output_dir"] = ""
                                    loaded["save_beside_source"] = True
                            except Exception:
                                loaded["custom_output_dir"] = ""
                                loaded["save_beside_source"] = True

                        self.data.update(loaded)
            except Exception as e:
                print(f"[Warning] Failed to load config file: {e}. Using defaults.")
        else:
            self.save()

    def save(self):
        """Saves current configuration to JSON file."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[Error] Failed to save config: {e}")
            return False

    def get(self, key, default=None):
        return self.data.get(key, default if default is not None else DEFAULT_CONFIG.get(key))

    def set(self, key, value):
        self.data[key] = value

    def clear_api_key(self):
        """Dedicated security action: wipes the AI translation API key from memory and file immediately."""
        self.data["ai_api_key"] = ""
        return self.save()

    def reset_styles_to_default(self):
        """Resets all typography and subtitle style options to default values."""
        self.data["font_family"] = DEFAULT_CONFIG["font_family"]
        self.data["font_size"] = DEFAULT_CONFIG["font_size"]
        self.data["font_color"] = DEFAULT_CONFIG["font_color"]
        self.data["outline_color"] = DEFAULT_CONFIG["outline_color"]
        self.data["outline_width"] = DEFAULT_CONFIG["outline_width"]
        self.data["shadow_offset"] = DEFAULT_CONFIG["shadow_offset"]
        self.data["font_bold"] = DEFAULT_CONFIG["font_bold"]
        self.data["font_italic"] = DEFAULT_CONFIG["font_italic"]
        self.data["subtitle_alignment"] = DEFAULT_CONFIG["subtitle_alignment"]
        self.save()
