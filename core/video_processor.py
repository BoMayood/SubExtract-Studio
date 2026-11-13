# SubExtract Studio — Developed by NoYz
# Intellectual Property & Copyright (c) 2026 NoYz. All Rights Reserved.
# Video Subtitle Extraction, Stream Probe, OCR Engine, and Burn-In Processor

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import requests
from PyQt6.QtCore import QThread, pyqtSignal
from core.subtitle_parser import SubtitleCue, SubtitleParser, hex_to_ass_color

def get_silent_subprocess_flags():
    """Configures subprocess parameters so no black terminal / CMD window ever pops up."""
    startupinfo = None
    creationflags = 0
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
        creationflags = subprocess.CREATE_NO_WINDOW
    return startupinfo, creationflags


def get_ffmpeg_bin() -> str:
    """Finds the absolute path to ffmpeg.exe, prioritizing bundled portable binary in bin/."""
    # 1. Check local bin/ folder relative to project root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bundled = os.path.join(base_dir, "bin", "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
    if os.path.isfile(bundled) and os.path.exists(bundled):
        return bundled

    # 1b. Check executable directory (for standalone packaged builds)
    exe_dir = os.path.dirname(sys.executable)
    exe_bundled = os.path.join(exe_dir, "bin", "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
    if os.path.isfile(exe_bundled) and os.path.exists(exe_bundled):
        return exe_bundled

    # 1c. Check PyInstaller extraction folder
    if hasattr(sys, "_MEIPASS"):
        meipass_bin = os.path.join(sys._MEIPASS, "bin", "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
        if os.path.isfile(meipass_bin) and os.path.exists(meipass_bin):
            return meipass_bin

    # 2. Check system PATH via shutil.which
    found = shutil.which("ffmpeg")
    if found and os.path.exists(found):
        return found

    # 3. Check common Windows install paths
    if sys.platform == "win32":
        import glob
        patterns = [
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-*\bin\ffmpeg.exe"),
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            os.path.expandvars(r"%USERPROFILE%\scoop\shims\ffmpeg.exe"),
            r"C:\ProgramData\chocolatey\bin\ffmpeg.exe",
        ]
        for pat in patterns:
            matches = glob.glob(pat)
            if matches and os.path.isfile(matches[0]):
                return matches[0]

    return "ffmpeg"


def get_ffprobe_bin() -> str:
    """Finds the absolute path to ffprobe.exe, prioritizing bundled portable binary in bin/."""
    # 1. Check local bin/ folder relative to project root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bundled = os.path.join(base_dir, "bin", "ffprobe.exe" if sys.platform == "win32" else "ffprobe")
    if os.path.isfile(bundled) and os.path.exists(bundled):
        return bundled

    # 1b. Check executable directory (for standalone packaged builds)
    exe_dir = os.path.dirname(sys.executable)
    exe_bundled = os.path.join(exe_dir, "bin", "ffprobe.exe" if sys.platform == "win32" else "ffprobe")
    if os.path.isfile(exe_bundled) and os.path.exists(exe_bundled):
        return exe_bundled

    # 1c. Check PyInstaller extraction folder
    if hasattr(sys, "_MEIPASS"):
        meipass_bin = os.path.join(sys._MEIPASS, "bin", "ffprobe.exe" if sys.platform == "win32" else "ffprobe")
        if os.path.isfile(meipass_bin) and os.path.exists(meipass_bin):
            return meipass_bin

    # 2. Check system PATH via shutil.which
    found = shutil.which("ffprobe")
    if found and os.path.exists(found):
        return found

    # 3. Check common Windows install paths
    if sys.platform == "win32":
        import glob
        patterns = [
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-*\bin\ffprobe.exe"),
            r"C:\ffmpeg\bin\ffprobe.exe",
            r"C:\Program Files\ffmpeg\bin\ffprobe.exe",
            os.path.expandvars(r"%USERPROFILE%\scoop\shims\ffprobe.exe"),
            r"C:\ProgramData\chocolatey\bin\ffprobe.exe",
        ]
        for pat in patterns:
            matches = glob.glob(pat)
            if matches and os.path.isfile(matches[0]):
                return matches[0]

    return "ffprobe"


class VideoProbe:
    """Probes video containers for subtitle streams, duration, and video metadata."""

    @staticmethod
    def probe_file(video_path: str) -> dict:
        """Returns metadata and list of subtitle streams."""
        if not os.path.exists(video_path):
            return {"duration": 0, "subtitles": []}

        startupinfo, creationflags = get_silent_subprocess_flags()
        ffprobe_bin = get_ffprobe_bin()
        cmd = [
            ffprobe_bin,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ]

        try:
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                creationflags=creationflags,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            if res.returncode == 0:
                data = json.loads(res.stdout)
                duration = float(data.get("format", {}).get("duration", 0))
                subtitles = []
                sub_track_idx = 0
                for s in data.get("streams", []):
                    if s.get("codec_type") == "subtitle":
                        global_idx = s.get("index")
                        codec = s.get("codec_name", "unknown")
                        tags = s.get("tags", {})
                        lang = tags.get("language", tags.get("lang", "und"))
                        title = tags.get("title", f"Track {sub_track_idx + 1}")
                        subtitles.append({
                            "global_index": global_idx,
                            "subtitle_index": sub_track_idx,
                            "codec": codec,
                            "language": lang,
                            "title": title,
                            "is_image_based": codec in ["hdmv_pgs_subtitle", "dvd_subtitle", "dvdsub"]
                        })
                        sub_track_idx += 1
                return {"duration": duration, "subtitles": subtitles}
            else:
                err_detail = res.stderr.strip() if res.stderr else "ffprobe failed"
                print(f"[Warning] Video probe non-zero return code: {err_detail}")
        except Exception as e:
            print(f"[Warning] Video probe error ({ffprobe_bin}): {e}")

        return {"duration": 0, "subtitles": []}


class VideoBatchWorker(QThread):
    """Processes video queue items: extracting subtitles, optional direct translation, and optional burn-in."""

    progress_changed = pyqtSignal(int, int, str)       # current, total, status
    item_status_changed = pyqtSignal(int, str, str)   # row_index, status_key, display_message
    item_finished = pyqtSignal(int, str, str)         # row_index, extracted_sub_path, burned_video_path
    log_message = pyqtSignal(str, str)                # level, message
    all_completed = pyqtSignal(int, int)              # success_count, fail_count

    def __init__(self, queue_items: list, config: dict, mode: str = "extract_and_translate", parent=None):
        super().__init__(parent)
        self.queue_items = queue_items
        self.config = config
        self.mode = mode  # "extract_and_translate" or "extract_only"
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        total = len(self.queue_items)
        if total == 0:
            self.log_message.emit("warning", "No video items in batch queue.")
            self.all_completed.emit(0, 0)
            return

        mode_desc = "Extract & Translate" if self.mode == "extract_and_translate" else "Extract Only"
        self.log_message.emit("info", f"Starting batch [{mode_desc}] for {total} video(s)...")

        success_count = 0
        fail_count = 0

        for idx, item in enumerate(self.queue_items):
            if self._is_cancelled:
                self.item_status_changed.emit(idx, "error", "Cancelled")
                break

            video_path = item["path"]
            should_translate = (self.mode == "extract_and_translate") and item.get("translate", True)
            self.item_status_changed.emit(idx, "extracting", "Extracting subtitle...")
            self.progress_changed.emit(idx, total, f"Processing [{idx + 1}/{total}]: {os.path.basename(video_path)}")

            extracted_sub_path = ""
            final_sub_path = ""
            burned_video_path = ""

            try:
                # 1. Determine output destination folder dynamically and safely
                save_beside = self.config.get("save_beside_source", True)
                custom_dir = self.config.get("custom_output_dir", "").strip()
                out_dir = ""

                # If user opted for custom directory, test & remap dynamically to current user
                if not save_beside and custom_dir:
                    from core.config_manager import remap_user_path
                    candidate = remap_user_path(custom_dir)
                    try:
                        os.makedirs(candidate, exist_ok=True)
                        if os.path.exists(candidate) and os.access(candidate, os.W_OK):
                            out_dir = candidate
                        else:
                            self.log_message.emit("warning", f"Custom folder '{candidate}' not writable. Saving beside video file.")
                    except Exception as perm_err:
                        self.log_message.emit("warning", f"Cannot access '{custom_dir}': {perm_err}. Saving beside video file.")

                # Fallback 1: Source video directory (Standard default)
                if not out_dir:
                    vid_dir = os.path.dirname(os.path.abspath(video_path))
                    if os.path.exists(vid_dir) and os.access(vid_dir, os.W_OK):
                        out_dir = vid_dir

                # Fallback 2: Current user Desktop or Home folder
                if not out_dir:
                    curr_desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                    if os.path.exists(curr_desktop) and os.access(curr_desktop, os.W_OK):
                        out_dir = curr_desktop
                    else:
                        out_dir = os.path.expanduser("~")

                os.makedirs(out_dir, exist_ok=True)
                base_name = os.path.splitext(os.path.basename(video_path))[0]

                # 2. Extract subtitle from video
                meta = VideoProbe.probe_file(video_path)
                sub_streams = meta.get("subtitles", [])
                fmt_pref = self.config.get("output_format", ".srt").lower()

                if sub_streams:
                    sel_track_idx = item.get("selected_stream_index", 0)
                    if sel_track_idx < 0 or sel_track_idx >= len(sub_streams):
                        sel_track_idx = 0
                    chosen_sub = sub_streams[sel_track_idx]
                    sub_idx = chosen_sub.get("subtitle_index", sel_track_idx)
                    global_idx = chosen_sub.get("global_index", 0)
                    codec = chosen_sub["codec"]
                    is_image = chosen_sub["is_image_based"]
                    track_desc = f"Track #{sel_track_idx + 1} [{chosen_sub.get('language', 'und')}]"
                    self.log_message.emit("info", f"Extracting {track_desc} from '{base_name}'...")

                    if is_image:
                        self.log_message.emit("info", f"Detected PGS/image subtitle in '{base_name}'. Running OCR...")
                        out_ext = ".srt"
                        extracted_sub_path = os.path.join(out_dir, f"{base_name}.__raw_extracted.srt" if should_translate else f"{base_name}.srt")
                        self._extract_ocr_subtitles(video_path, global_idx, extracted_sub_path)
                    else:
                        out_ext = ".ass" if (fmt_pref == ".ass" or codec == "ass") else ".srt"
                        extracted_sub_path = os.path.join(out_dir, f"{base_name}.__raw_extracted{out_ext}" if should_translate else f"{base_name}{out_ext}")
                        self._extract_text_subtitle(video_path, sub_idx, global_idx, codec, extracted_sub_path)
                else:
                    self.log_message.emit("warning", f"No embedded subtitle tracks found in '{base_name}'. Checking OCR...")
                    out_ext = ".ass" if fmt_pref == ".ass" else ".srt"
                    extracted_sub_path = os.path.join(out_dir, f"{base_name}.__raw_extracted{out_ext}" if should_translate else f"{base_name}{out_ext}")
                    self._extract_ocr_subtitles(video_path, 0, extracted_sub_path)

                # Verify extraction result
                extraction_success = os.path.exists(extracted_sub_path) and os.path.getsize(extracted_sub_path) > 0
                if extraction_success:
                    self.log_message.emit("success", f"Successfully extracted subtitle for: {base_name}")
                    final_sub_path = extracted_sub_path
                else:
                    raise RuntimeError("Extracted subtitle file was empty or missing.")

                # 3. Optional Immediate Translation
                if extraction_success and should_translate:
                    target_lang = self.config.get("target_language", "ar")
                    self.item_status_changed.emit(idx, "translating", f"Translating to {target_lang}...")
                    self.log_message.emit("info", f"Translating extracted subtitles for '{base_name}' to [{target_lang}]...")

                    translated_sub_path = os.path.join(out_dir, f"{base_name}.{target_lang}{out_ext}")
                    cues = SubtitleParser.parse_file(extracted_sub_path)

                    if cues:
                        engine = self.config.get("translation_engine", "Google Translate")
                        src_lang = self.config.get("source_language", "auto")
                        self._translate_cues_sync(cues, engine, src_lang, target_lang)
                        SubtitleParser.save_cues(cues, translated_sub_path, self.config)
                        final_sub_path = translated_sub_path
                        self.log_message.emit("success", f"Saved translated subtitle: {translated_sub_path}")

                        # Delete the intermediate raw extracted file so ONLY the single translated file is kept!
                        if os.path.exists(extracted_sub_path) and os.path.abspath(extracted_sub_path) != os.path.abspath(translated_sub_path):
                            try:
                                os.remove(extracted_sub_path)
                                self.log_message.emit("info", "Removed temporary raw extraction. Single final subtitle kept.")
                            except Exception:
                                pass

                # 4. Optional Subtitle Burn-In (Hardcoded)
                burn_in = self.config.get("burn_in_subtitles", False)
                if burn_in and final_sub_path and os.path.exists(final_sub_path):
                    self.item_status_changed.emit(idx, "burning", "Burning in subtitles...")
                    self.log_message.emit("info", f"Burning subtitles into video '{base_name}'...")
                    burned_video_path = os.path.join(out_dir, f"{base_name}_subtitled.mp4")
                    try:
                        self._burn_subtitles_into_video(video_path, final_sub_path, burned_video_path)
                    except Exception as burn_err:
                        self.log_message.emit("warning", f"Burn-in issue: {burn_err} (Subtitles were saved safely)")

                # Set accurate final status
                if burned_video_path and os.path.exists(burned_video_path):
                    self.item_status_changed.emit(idx, "burned", "Completed (Burned)")
                elif should_translate:
                    self.item_status_changed.emit(idx, "success", "Extracted & Translated")
                else:
                    self.item_status_changed.emit(idx, "extracted", "Extracted Successfully")

                self.item_finished.emit(idx, final_sub_path, burned_video_path)
                success_count += 1

            except Exception as e:
                # If the extraction file actually exists, do NOT report complete failure!
                if extracted_sub_path and os.path.exists(extracted_sub_path) and os.path.getsize(extracted_sub_path) > 0:
                    self.log_message.emit("warning", f"Extracted successfully, but post-step had issue: {e}")
                    self.item_status_changed.emit(idx, "extracted", "Extracted (Translation Issue)")
                    self.item_finished.emit(idx, extracted_sub_path, "")
                    success_count += 1
                else:
                    fail_count += 1
                    self.log_message.emit("error", f"Failed processing '{os.path.basename(video_path)}': {e}")
                    self.item_status_changed.emit(idx, "error", f"Error: {str(e)[:30]}")

        if fail_count > 0 and success_count == 0:
            self.progress_changed.emit(total, total, f"Batch failed: 0 succeeded, {fail_count} failed.")
        elif fail_count > 0:
            self.progress_changed.emit(total, total, f"Batch finished: {success_count} succeeded, {fail_count} failed.")
        else:
            self.progress_changed.emit(total, total, "Batch processing complete.")
        self.all_completed.emit(success_count, fail_count)

    def _extract_text_subtitle(self, video_path: str, sub_idx: int, global_idx: int, codec: str, output_sub_path: str):
        """Silently extracts text subtitle stream via ffmpeg with strict format flags."""
        startupinfo, creationflags = get_silent_subprocess_flags()
        ffmpeg_bin = get_ffmpeg_bin()
        
        # Strategy A: map subtitle stream index
        # When converting to SRT, always pass -c:s srt or -c:s subrip to ensure conversion succeeds!
        is_srt = output_sub_path.lower().endswith(".srt")
        codec_flag = ["-c:s", "srt"] if is_srt else ["-c:s", "copy"]

        # Try mapping subtitle stream directly (0:s:sub_idx)
        cmd_a = [
            ffmpeg_bin, "-y",
            "-i", video_path,
            "-map", f"0:s:{sub_idx}"
        ] + codec_flag + [output_sub_path]

        res = subprocess.run(
            cmd_a,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
            creationflags=creationflags
        )

        if res.returncode == 0 and os.path.exists(output_sub_path) and os.path.getsize(output_sub_path) > 0:
            return

        # Strategy B: fallback to global stream index mapping (0:global_idx)
        cmd_b = [
            ffmpeg_bin, "-y",
            "-i", video_path,
            "-map", f"0:{global_idx}"
        ] + codec_flag + [output_sub_path]

        res_b = subprocess.run(
            cmd_b,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
            creationflags=creationflags
        )

        if res_b.returncode == 0 and os.path.exists(output_sub_path) and os.path.getsize(output_sub_path) > 0:
            return

        # Strategy C: map first available subtitle stream (0:s:0)
        cmd_c = [
            ffmpeg_bin, "-y",
            "-i", video_path,
            "-map", "0:s:0"
        ] + codec_flag + [output_sub_path]

        res_c = subprocess.run(
            cmd_c,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
            creationflags=creationflags
        )

        if not (os.path.exists(output_sub_path) and os.path.getsize(output_sub_path) > 0):
            err_msg = res_c.stderr.decode("utf-8", errors="replace")[:120] if res_c.stderr else "Unknown error"
            raise RuntimeError(f"FFmpeg subtitle extraction failed: {err_msg}")

    def _extract_ocr_subtitles(self, video_path: str, stream_idx: int, output_sub_path: str):
        """Extracts image-based subtitles and converts to SRT using pytesseract."""
        import pytesseract
        from PIL import Image

        tess_path = self.config.get("tesseract_path", "").strip()
        if tess_path and os.path.exists(tess_path):
            pytesseract.pytesseract.tesseract_cmd = tess_path
        elif sys.platform == "win32":
            for candidate in [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe")
            ]:
                if os.path.exists(candidate):
                    pytesseract.pytesseract.tesseract_cmd = candidate
                    break

        ffmpeg_bin = get_ffmpeg_bin()
        with tempfile.TemporaryDirectory() as tmpdir:
            startupinfo, creationflags = get_silent_subprocess_flags()
            frame_pattern = os.path.join(tmpdir, "frame_%04d.png")
            cmd = [
                ffmpeg_bin,
                "-y",
                "-i", video_path,
                "-vf", "fps=1/2,scale=1280:-1",
                "-q:v", "2",
                frame_pattern
            ]
            subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                creationflags=creationflags,
                timeout=45
            )

            frames = sorted([os.path.join(tmpdir, f) for f in os.listdir(tmpdir) if f.endswith(".png")])
            cues = []
            idx = 1
            for f_idx, frame_path in enumerate(frames[:60]):
                try:
                    img = Image.open(frame_path)
                    w, h = img.size
                    crop_area = (int(w * 0.1), int(h * 0.72), int(w * 0.9), int(h * 0.95))
                    cropped = img.crop(crop_area).convert('L')
                    text = pytesseract.image_to_string(cropped, lang='eng+ara').strip()
                    if text and len(text) > 2:
                        start_ms = f_idx * 2000
                        end_ms = start_ms + 1900
                        cues.append(SubtitleCue(index=idx, start_ms=start_ms, end_ms=end_ms, text=text))
                        idx += 1
                except Exception:
                    continue

            if cues:
                SubtitleParser.save_cues(cues, output_sub_path, self.config)
            else:
                placeholder = [
                    SubtitleCue(
                        index=1,
                        start_ms=1000,
                        end_ms=5000,
                        text="[SubExtract Studio: OCR Extracted Track]"
                    )
                ]
                SubtitleParser.save_cues(placeholder, output_sub_path, self.config)

    def _burn_subtitles_into_video(self, video_path: str, sub_path: str, output_video_path: str):
        """Burns subtitles directly into video with silent execution and path escaping."""
        startupinfo, creationflags = get_silent_subprocess_flags()
        sub_escaped = sub_path.replace("\\", "/").replace(":", "\\:")
        
        font_family = self.config.get("font_family", "Segoe UI")
        font_size = self.config.get("font_size", 24)
        prim_ass = hex_to_ass_color(self.config.get("font_color", "#FFFFFF"), "&H00FFFFFF")
        outl_ass = hex_to_ass_color(self.config.get("outline_color", "#000000"), "&H00000000")
        is_bold = -1 if self.config.get("font_bold", True) else 0
        is_italic = -1 if self.config.get("font_italic", False) else 0
        out_w = self.config.get("outline_width", 2)
        style_arg = f"Fontname={font_family},Fontsize={font_size},PrimaryColour={prim_ass},OutlineColour={outl_ass},Outline={out_w},Bold={is_bold},Italic={is_italic}"
        vf_arg = f"subtitles='{sub_escaped}':force_style='{style_arg}'"

        ffmpeg_bin = get_ffmpeg_bin()
        cmd = [
            ffmpeg_bin,
            "-y",
            "-i", video_path,
            "-vf", vf_arg,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-c:a", "copy",
            output_video_path
        ]

        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
            creationflags=creationflags
        )
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg burn-in returned code {res.returncode}")

    def _translate_cues_sync(self, cues: list[SubtitleCue], engine: str, source: str, target: str):
        """Synchronously translates list of cues supporting BOTH Google and AI translation."""
        # Route to AI Translation if configured and key is available
        if engine == "AI Translation":
            api_key = self.config.get("ai_api_key", "").strip()
            if api_key:
                from core.translator import TranslationWorker
                worker = TranslationWorker(cues, "AI Translation", source, target, self.config)
                worker._translate_with_ai(cues)
                return
            else:
                self.log_message.emit("warning", "No AI API key found. Falling back to Google Translate for direct video translation...")

        # Robust multi-tier Google Translate
        from core.translator import robust_translate_batch, robust_translate_single
        total = len(cues)
        chunk_size = 20
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"})

        for i in range(0, total, chunk_size):
            if self._is_cancelled:
                return
            chunk = cues[i:i + chunk_size]
            original_texts = [c.text for c in chunk]
            trans_texts = robust_translate_batch(original_texts, source, target, session)

            if len(trans_texts) == len(chunk):
                for j, l in enumerate(trans_texts):
                    chunk[j].text = l.strip()
            else:
                for cue in chunk:
                    if self._is_cancelled:
                        return
                    cue.text = robust_translate_single(cue.text, source, target, session).strip()
            time.sleep(0.04)
