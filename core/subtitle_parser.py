# SubExtract Studio — Developed by NoYz
# Intellectual Property & Copyright (c) 2026 NoYz. All Rights Reserved.
# Subtitle Parser, Formatter, Time Shifter, and Converter Engine

import re
import os
from dataclasses import dataclass

BRANDING_COMMENT = "Translated & Processed by SubExtract Studio | NoYz"

def hex_to_ass_color(hex_str: str, default: str = "&H00FFFFFF") -> str:
    """Converts #RRGGBB hex string to &H00BBGGRR (ASS BGR format)."""
    if not hex_str:
        return default
    c = hex_str.strip().lstrip('#')
    if len(c) == 6:
        r, g, b = c[0:2], c[2:4], c[4:6]
        return f"&H00{b.upper()}{g.upper()}{r.upper()}"
    return default

@dataclass
class SubtitleCue:
    index: int
    start_ms: int
    end_ms: int
    text: str

    @property
    def start_str_srt(self) -> str:
        return SubtitleParser.ms_to_srt_time(self.start_ms)

    @property
    def end_str_srt(self) -> str:
        return SubtitleParser.ms_to_srt_time(self.end_ms)

    @property
    def start_str_vtt(self) -> str:
        return SubtitleParser.ms_to_vtt_time(self.start_ms)

    @property
    def end_str_vtt(self) -> str:
        return SubtitleParser.ms_to_vtt_time(self.end_ms)

    @property
    def start_str_ass(self) -> str:
        return SubtitleParser.ms_to_ass_time(self.start_ms)

    @property
    def end_str_ass(self) -> str:
        return SubtitleParser.ms_to_ass_time(self.end_ms)


class SubtitleParser:
    """Handles parsing, serializing, time-shifting, converting, and language detecting subtitles."""

    @staticmethod
    def srt_time_to_ms(time_str: str) -> int:
        """Parses '00:01:23,456' into milliseconds."""
        time_str = time_str.strip().replace('.', ',')
        parts = time_str.split(':')
        if len(parts) == 3:
            h = int(parts[0])
            m = int(parts[1])
            s_ms = parts[2].split(',')
            s = int(s_ms[0])
            ms = int(s_ms[1].ljust(3, '0')[:3])
            return ((h * 3600) + (m * 60) + s) * 1000 + ms
        return 0

    @staticmethod
    def ms_to_srt_time(ms: int) -> str:
        """Formats milliseconds into '00:01:23,456'."""
        if ms < 0:
            ms = 0
        total_seconds = ms // 1000
        millis = ms % 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"

    @staticmethod
    def ms_to_vtt_time(ms: int) -> str:
        """Formats milliseconds into '00:01:23.456'."""
        if ms < 0:
            ms = 0
        total_seconds = ms // 1000
        millis = ms % 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}"

    @staticmethod
    def ms_to_ass_time(ms: int) -> str:
        """Formats milliseconds into '0:01:23.45' (centiseconds)."""
        if ms < 0:
            ms = 0
        total_seconds = ms // 1000
        centis = (ms % 1000) // 10
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:01d}:{minutes:02d}:{seconds:02d}.{centis:02d}"

    @staticmethod
    def ass_time_to_ms(time_str: str) -> int:
        """Parses ASS time '0:01:23.45' into milliseconds."""
        time_str = time_str.strip()
        parts = time_str.split(':')
        if len(parts) == 3:
            h = int(parts[0])
            m = int(parts[1])
            s_cs = parts[2].split('.')
            s = int(s_cs[0])
            cs = int(s_cs[1].ljust(2, '0')[:2]) if len(s_cs) > 1 else 0
            return ((h * 3600) + (m * 60) + s) * 1000 + (cs * 10)
        return 0

    @classmethod
    def parse_file(cls, filepath: str) -> list[SubtitleCue]:
        """Auto-detects format and parses file into a list of SubtitleCue objects."""
        if not os.path.exists(filepath):
            return []
        
        ext = os.path.splitext(filepath)[1].lower()
        # Read file with tolerant encoding
        content = ""
        for encoding in ["utf-8-sig", "utf-8", "cp1256", "cp1252", "latin-1"]:
            try:
                with open(filepath, "r", encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue

        if ext == ".ass" or ext == ".ssa":
            return cls.parse_ass_text(content)
        elif ext == ".vtt":
            return cls.parse_vtt_text(content)
        else:
            return cls.parse_srt_text(content)

    @classmethod
    def parse_srt_text(cls, text: str) -> list[SubtitleCue]:
        """Parses SRT format text."""
        cues = []
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        # Split on blank lines
        blocks = re.split(r'\n\s*\n', text.strip())

        idx_counter = 1
        for block in blocks:
            lines = [ln.strip() for ln in block.strip().split('\n') if ln.strip()]
            if not lines:
                continue
            
            # Find timestamp line
            time_line_idx = -1
            for i, line in enumerate(lines):
                if '-->' in line:
                    time_line_idx = i
                    break
            
            if time_line_idx == -1:
                continue

            time_line = lines[time_line_idx]
            time_parts = time_line.split('-->')
            if len(time_parts) != 2:
                continue

            start_str = time_parts[0].strip()
            # Clean possible trailing VTT cue settings
            end_str = time_parts[1].strip().split(' ')[0]

            start_ms = cls.srt_time_to_ms(start_str)
            end_ms = cls.srt_time_to_ms(end_str)

            # Subtitle text consists of lines following timestamp
            sub_text = "\n".join(lines[time_line_idx + 1:])
            # Filter out comment lines starting with # or ;
            if sub_text.startswith("#") or sub_text.startswith(";"):
                continue

            cues.append(SubtitleCue(
                index=idx_counter,
                start_ms=start_ms,
                end_ms=end_ms,
                text=sub_text
            ))
            idx_counter += 1

        return cues

    @classmethod
    def parse_vtt_text(cls, text: str) -> list[SubtitleCue]:
        """Parses WebVTT format text."""
        # Strip header
        text = re.sub(r'^WEBVTT.*?\n', '', text, flags=re.IGNORECASE)
        # Delegate to SRT parser since cues syntax is identical with comma/period
        return cls.parse_srt_text(text)

    @classmethod
    def parse_ass_text(cls, text: str) -> list[SubtitleCue]:
        """Parses ASS/SSA format dialogue events."""
        cues = []
        lines = text.replace('\r\n', '\n').split('\n')
        idx = 1
        for line in lines:
            line_clean = line.strip()
            if line_clean.startswith("Dialogue:"):
                # Dialogue: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
                content = line_clean[len("Dialogue:"):].strip()
                parts = content.split(',', 9)
                if len(parts) >= 10:
                    start_str = parts[1].strip()
                    end_str = parts[2].strip()
                    raw_text = parts[9]
                    # Clean ASS tags like {\an8}, \N
                    clean_text = re.sub(r'\{.*?\}', '', raw_text).replace(r'\N', '\n').replace(r'\n', '\n')
                    start_ms = cls.ass_time_to_ms(start_str)
                    end_ms = cls.ass_time_to_ms(end_str)
                    cues.append(SubtitleCue(
                        index=idx,
                        start_ms=start_ms,
                        end_ms=end_ms,
                        text=clean_text
                    ))
                    idx += 1
        return cues

    @classmethod
    def inject_branding_cues(cls, cues: list[SubtitleCue]) -> list[SubtitleCue]:
        """
        Safely injects NoYz copyright & processing credits as valid, player-compatible subtitle cues
        without breaking any video player (VLC, MPC, PotPlayer, TVs, web).
        """
        if not cues:
            return cues

        branding_text = "Sub Studio — Developed by NoYz\nتمت المعالجة والضبط بواسطة NoYz | Sub Studio"

        # Check if branding already exists in cues
        for c in cues:
            if "NoYz" in c.text or "Sub Studio" in c.text:
                return cues

        new_cues = list(cues)

        # If opening gap >= 3.5s before speech starts, insert intro cue
        first_start = cues[0].start_ms
        if first_start >= 3500:
            intro_end = min(3500, first_start - 500)
            intro_cue = SubtitleCue(
                index=1,
                start_ms=800,
                end_ms=intro_end,
                text=branding_text
            )
            new_cues.insert(0, intro_cue)
        else:
            # Append outro credit cue at the end after all dialogue finishes
            last_end = cues[-1].end_ms
            outro_cue = SubtitleCue(
                index=len(new_cues) + 1,
                start_ms=last_end + 1000,
                end_ms=last_end + 4500,
                text=branding_text
            )
            new_cues.append(outro_cue)

        # Re-index all cues sequentially
        for i, cue in enumerate(new_cues, 1):
            cue.index = i

        return new_cues

    @classmethod
    def cues_to_srt(cls, cues: list[SubtitleCue], style_config: dict = None) -> str:
        """Serializes cues to standard .srt format with player-compatible styling tags."""
        output = []
        if style_config is None:
            style_config = {}

        font_color = style_config.get("font_color", "").strip()
        font_family = style_config.get("font_family", "").strip()
        is_bold = bool(style_config.get("font_bold", False))
        is_italic = bool(style_config.get("font_italic", False))

        has_custom_color = bool(font_color and font_color.upper() != "#FFFFFF")
        has_custom_font = bool(font_family and font_family != "Segoe UI")

        for i, cue in enumerate(cues, 1):
            output.append(f"{i}")
            output.append(f"{cls.ms_to_srt_time(cue.start_ms)} --> {cls.ms_to_srt_time(cue.end_ms)}")

            raw_text = cue.text.strip()
            styled_text = raw_text
            # Apply font tags if customized and not already present
            if (has_custom_color or has_custom_font) and "<font" not in raw_text.lower():
                attrs = []
                if has_custom_color:
                    attrs.append(f'color="{font_color}"')
                if has_custom_font:
                    attrs.append(f'face="{font_family}"')
                styled_text = f"<font {' '.join(attrs)}>{styled_text}</font>"

            if is_bold and "<b>" not in styled_text.lower():
                styled_text = f"<b>{styled_text}</b>"
            if is_italic and "<i>" not in styled_text.lower():
                styled_text = f"<i>{styled_text}</i>"

            output.append(styled_text)
            output.append("")
        return "\n".join(output)

    @classmethod
    def cues_to_vtt(cls, cues: list[SubtitleCue]) -> str:
        """Serializes cues to standard .vtt format with NoYz copyright header metadata."""
        output = [f"WEBVTT\nNOTE {BRANDING_COMMENT}\n"]
        for i, cue in enumerate(cues, 1):
            output.append(f"{i}")
            output.append(f"{cls.ms_to_vtt_time(cue.start_ms)} --> {cls.ms_to_vtt_time(cue.end_ms)}")
            output.append(cue.text.strip())
            output.append("")
        return "\n".join(output)

    @classmethod
    def cues_to_ass(cls, cues: list[SubtitleCue], style_config: dict = None) -> str:
        """Serializes cues to .ass format with advanced styling and NoYz copyright metadata."""
        if style_config is None:
            style_config = {}

        font_name = style_config.get("font_family", "Segoe UI")
        font_size = style_config.get("font_size", 24)
        primary_color = hex_to_ass_color(style_config.get("font_color", "#FFFFFF"), "&H00FFFFFF")
        outline_color = hex_to_ass_color(style_config.get("outline_color", "#000000"), "&H00000000")
        is_bold = -1 if style_config.get("font_bold", True) else 0
        is_italic = -1 if style_config.get("font_italic", False) else 0
        outline_width = style_config.get("outline_width", 2)
        shadow_depth = style_config.get("shadow_offset", 1)

        # Map alignment
        align_str = style_config.get("subtitle_alignment", "Bottom Center")
        align_val = 2  # Bottom Center default
        if "Top" in align_str:
            align_val = 8
        elif "Middle" in align_str:
            align_val = 5

        # Format header with intellectual property
        header = f"""; Generated by SubExtract Studio | Developed by NoYz
[Script Info]
Title: SubExtract Studio Export
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
Comment: {BRANDING_COMMENT}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{primary_color},&H000000FF,{outline_color},&H00000000,{is_bold},{is_italic},0,0,100,100,0,0,1,{outline_width},{shadow_depth},{align_val},10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        dialogue_lines = []
        for cue in cues:
            start_ass = cls.ms_to_ass_time(cue.start_ms)
            end_ass = cls.ms_to_ass_time(cue.end_ms)
            formatted_text = cue.text.strip().replace('\n', r'\N')
            dialogue_lines.append(f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{formatted_text}")

        return header + "\n".join(dialogue_lines) + "\n"

    @classmethod
    def save_cues(cls, cues: list[SubtitleCue], output_path: str, style_config: dict = None) -> bool:
        """Saves cues to the target file path in the matching extension format."""
        try:
            ext = os.path.splitext(output_path)[1].lower()
            if ext == ".ass":
                content = cls.cues_to_ass(cues, style_config)
            elif ext == ".vtt":
                content = cls.cues_to_vtt(cues)
            else:
                cues_with_brand = cls.inject_branding_cues(cues)
                content = cls.cues_to_srt(cues_with_brand, style_config)

            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"[Error] Failed to save subtitle: {e}")
            return False

    @staticmethod
    def shift_timestamps(cues: list[SubtitleCue], delta_ms: int) -> list[SubtitleCue]:
        """Shifts all cues forward or backward in time by delta_ms."""
        for cue in cues:
            cue.start_ms = max(0, cue.start_ms + delta_ms)
            cue.end_ms = max(0, cue.end_ms + delta_ms)
            if cue.end_ms < cue.start_ms:
                cue.end_ms = cue.start_ms + 1000
        return cues

    @staticmethod
    def find_and_replace(cues: list[SubtitleCue], find_str: str, replace_str: str,
                         match_case: bool = False, whole_word: bool = False) -> tuple[int, list[SubtitleCue]]:
        """Finds and replaces occurrences across all subtitle cues."""
        if not find_str:
            return 0, cues

        total_replacements = 0
        if whole_word:
            pattern = rf"\b{re.escape(find_str)}\b"
        else:
            pattern = re.escape(find_str)

        flags = 0 if match_case else re.IGNORECASE
        regex = re.compile(pattern, flags)

        for cue in cues:
            new_text, count = regex.subn(replace_str, cue.text)
            if count > 0:
                total_replacements += count
                cue.text = new_text

        return total_replacements, cues

    @staticmethod
    def detect_language(cues: list[SubtitleCue]) -> str:
        """Detects language from subtitle cues text."""
        sample_text = " ".join([c.text for c in cues[:30]])
        if not sample_text.strip():
            return "Unknown"

        # Check Arabic Unicode range (\u0600-\u06FF)
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', sample_text))
        total_alpha = len(re.findall(r'\w', sample_text))
        if total_alpha > 0 and (arabic_chars / total_alpha) > 0.25:
            return "Arabic (ar)"

        # Check Japanese (Hiragana/Katakana/Kanji)
        if len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', sample_text)) > 10:
            return "Japanese (ja)"

        # Check Russian/Cyrillic
        if len(re.findall(r'[\u0400-\u04FF]', sample_text)) > 10:
            return "Russian (ru)"

        # Default standard Latin alphabet languages
        return "English / Latin (en)"
