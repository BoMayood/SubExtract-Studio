# SubExtract Studio — Developed by NoYz
# Intellectual Property & Copyright (c) 2026 NoYz. All Rights Reserved.
# High Performance Subtitle Translation Engine with 2026 Gemini 3 Series & OpenAI Support

import json
import re
import time
import requests
from PyQt6.QtCore import QThread, pyqtSignal
from core.subtitle_parser import SubtitleCue, SubtitleParser
from core.i18n import I18n

LINE_DELIMITER = "\n[[--SUB_BREAK--]]\n"

SUPPORTED_LANGUAGES = [
    ("ar", "Arabic (العربية)"),
    ("en", "English"),
    ("fr", "French (Français)"),
    ("es", "Spanish (Español)"),
    ("de", "German (Deutsch)"),
    ("it", "Italian (Italiano)"),
    ("ja", "Japanese (日本語)"),
    ("ko", "Korean (한국어)"),
    ("zh-CN", "Chinese Simplified (简体中文)"),
    ("ru", "Russian (Русский)"),
    ("tr", "Turkish (Türkçe)"),
    ("pt", "Portuguese (Português)"),
    ("hi", "Hindi (हिन्दी)"),
    ("id", "Indonesian (Bahasa Indonesia)"),
    ("fa", "Persian (فارسی)"),
    ("ur", "Urdu (اردو)")
]

# 2026 Active Google Gemini Models (Ordered by speed & reliability)
GEMINI_ACTIVE_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-3.6-flash",
    "gemini-flash-latest",
    "gemini-3.8-flash",
    "gemini-3.7-flash"
]

OPENAI_ACTIVE_MODELS = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-3.5-turbo"
]

def clean_model_name(name: str) -> str:
    if not name:
        return "gemini-3.5-flash"
    m = name.strip()
    if m.startswith("models/"):
        m = m[len("models/"):]
    return m


def test_ai_connection(api_key: str, model: str = None, endpoint: str = None) -> tuple[bool, str, list, str]:
    """
    Tests an AI API Key, dynamically queries available models from the provider,
    and returns (success_bool, detailed_message, list_of_available_models, best_working_model).
    Bilingual (English and Arabic) based on active I18n language.
    """
    api_key = (api_key or "").strip()
    if not api_key:
        return False, I18n.t("api_key_empty"), [], ""

    model = clean_model_name(model)
    start_time = time.time()
    is_ar = (I18n.current_lang == "ar")
    test_word_prompt = "Translate the single word 'Hello' to Arabic in one word." if is_ar else "Respond with the single word 'Connected' if you are online."

    is_gemini = api_key.startswith("AQ.") or api_key.startswith("AIza") or (endpoint and "generativelanguage" in endpoint)

    # =========================================================================
    # Route 1: Google Gemini API (2026 Dynamic Discovery & Multi-Model Testing)
    # =========================================================================
    if is_gemini:
        # Step 1: Query models list from Google
        list_url = "https://generativelanguage.googleapis.com/v1beta/models"
        available_models = []
        try:
            r_models = requests.get(list_url, params={"key": api_key}, timeout=12)
            if r_models.status_code == 200:
                data = r_models.json()
                for item in data.get("models", []):
                    m_name = clean_model_name(item.get("name", ""))
                    methods = item.get("supportedGenerationMethods", [])
                    if "generateContent" in methods and m_name:
                        available_models.append(m_name)
            elif r_models.status_code == 400:
                err_text = r_models.json().get("error", {}).get("message", "API Key Invalid")
                return False, I18n.t("api_err_invalid").format(error=err_text), [], ""
            elif r_models.status_code == 403:
                return False, I18n.t("api_err_forbidden"), [], ""
        except requests.exceptions.Timeout:
            return False, I18n.t("api_err_timeout"), [], ""
        except Exception:
            pass

        # Candidate models to try in order of performance
        candidates_to_try = []
        if model and (model in GEMINI_ACTIVE_MODELS or model in available_models):
            candidates_to_try.append(model)
        for m in GEMINI_ACTIVE_MODELS:
            if m not in candidates_to_try:
                candidates_to_try.append(m)

        # Step 2: Test translation call via OpenAI-compatible endpoint
        chat_url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "x-goog-api-key": api_key,
            "Content-Type": "application/json"
        }

        last_error = ""
        for cand in candidates_to_try:
            payload = {
                "model": cand,
                "messages": [{"role": "user", "content": test_word_prompt}]
            }
            try:
                resp = requests.post(chat_url, headers=headers, json=payload, timeout=15)
                latency = int((time.time() - start_time) * 1000)

                if resp.status_code == 200:
                    data = resp.json()
                    trans_text = data["choices"][0]["message"]["content"].strip()
                    notice = ""
                    if cand != model and model not in GEMINI_ACTIVE_MODELS:
                        notice = I18n.t("api_notice_switched").format(model=cand)

                    msg = I18n.t("api_test_success_gemini").format(
                        model=cand,
                        notice=notice,
                        response=trans_text,
                        latency=latency
                    )
                    combo_models = GEMINI_ACTIVE_MODELS
                    return True, msg, combo_models, cand
                elif resp.status_code == 429:
                    last_error = I18n.t("api_err_quota")
                elif resp.status_code == 503:
                    last_error = I18n.t("api_err_busy").format(model=cand)
                else:
                    # Second chance: try native Gemini generateContent endpoint
                    try:
                        native_url = f"https://generativelanguage.googleapis.com/v1beta/models/{cand}:generateContent?key={api_key}"
                        n_resp = requests.post(native_url, json={"contents": [{"parts": [{"text": test_word_prompt}]}]}, timeout=12)
                        if n_resp.status_code == 200:
                            n_data = n_resp.json()
                            trans_text = n_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                            latency = int((time.time() - start_time) * 1000)
                            notice = ""
                            if cand != model and model not in GEMINI_ACTIVE_MODELS:
                                notice = I18n.t("api_notice_switched").format(model=cand)
                            msg = I18n.t("api_test_success_gemini").format(
                                model=cand,
                                notice=notice,
                                response=trans_text,
                                latency=latency
                            )
                            return True, msg, GEMINI_ACTIVE_MODELS, cand
                    except Exception:
                        pass

                    try:
                        last_error = resp.json().get("error", {}).get("message", resp.text[:100])
                    except Exception:
                        last_error = resp.text[:100]
            except Exception as e:
                last_error = str(e)

        return False, I18n.t("api_test_failed_gemini").format(error=last_error), GEMINI_ACTIVE_MODELS, "gemini-3.5-flash"

    # =========================================================================
    # Route 2: OpenAI / OpenRouter / Custom Endpoints
    # =========================================================================
    else:
        ep = endpoint if endpoint else "https://api.openai.com/v1/chat/completions"
        if not ep.endswith("/chat/completions"):
            ep = f"{ep.rstrip('/')}/chat/completions"

        target_model = model if model else "gpt-4o-mini"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": target_model,
            "messages": [{"role": "user", "content": test_word_prompt}],
            "max_tokens": 10
        }
        try:
            resp = requests.post(ep, headers=headers, json=payload, timeout=14)
            latency = int((time.time() - start_time) * 1000)

            if resp.status_code == 200:
                data = resp.json()
                trans_text = data["choices"][0]["message"]["content"].strip()
                msg = I18n.t("api_test_success_openai").format(
                    model=target_model,
                    response=trans_text,
                    latency=latency
                )
                return True, msg, OPENAI_ACTIVE_MODELS, target_model
            else:
                err_msg = ""
                try:
                    err_msg = resp.json().get("error", {}).get("message", resp.text[:120])
                except Exception:
                    err_msg = resp.text[:120]
                return False, I18n.t("api_test_failed_openai").format(status=resp.status_code, error=err_msg), OPENAI_ACTIVE_MODELS, target_model
        except Exception as e:
            return False, I18n.t("api_test_err_network").format(error=str(e)), OPENAI_ACTIVE_MODELS, target_model


LANG_NAME_MAP = {
    "ar": "arabic", "en": "english", "fr": "french", "es": "spanish",
    "de": "german", "it": "italian", "ja": "japanese", "ko": "korean",
    "zh-CN": "chinese (simplified)", "zh": "chinese (simplified)",
    "ru": "russian", "tr": "turkish", "pt": "portuguese", "hi": "hindi",
    "id": "indonesian", "fa": "persian", "ur": "urdu"
}


def robust_translate_batch(lines: list[str], source: str = "auto", target: str = "ar", session: requests.Session = None) -> list[str]:
    """
    Translates a list of subtitle strings reliably using a resilient multi-tier pipeline:
    Tier 1: clients5.google.com with dict-chrome-ex (high throughput, no 429 rate limit)
    Tier 2: Individual line fallback via dict-chrome-ex
    Tier 3: translate.googleapis.com client=gtx
    Tier 4: deep_translator.MyMemoryTranslator (100% free guaranteed backup)
    """
    if not lines:
        return []
    if session is None:
        session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    })

    src = "auto" if not source or source == "auto" else source
    tgt = target.lower()
    if tgt.startswith("zh"):
        tgt = "zh-CN"

    delimiter = "\n[[--SUB_BREAK--]]\n"
    # Filter empty or pure-whitespace lines safely
    safe_lines = [l.strip() if l.strip() else "..." for l in lines]
    joined_text = delimiter.join(safe_lines)

    # =========================================================================
    # Tier 1: clients5.google.com dict-chrome-ex batch POST/GET
    # =========================================================================
    try:
        url = f"https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl={src}&tl={tgt}"
        resp = session.post(url, data={"q": joined_text}, timeout=14)
        if resp.status_code == 200:
            data = resp.json()
            raw_text = ""
            if isinstance(data, list) and len(data) > 0:
                first = data[0]
                if isinstance(first, list) and len(first) > 0 and isinstance(first[0], str):
                    raw_text = first[0]
                elif isinstance(first, str):
                    raw_text = first
            parts = raw_text.split("[[--SUB_BREAK--]]")
            if len(parts) == len(lines):
                return [p.strip() for p in parts]
    except Exception:
        pass

    # =========================================================================
    # Tier 2: Individual lines via dict-chrome-ex
    # =========================================================================
    results = []
    tier2_failed = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            results.append("")
            continue
        try:
            url = f"https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl={src}&tl={tgt}"
            r = session.get(url, params={"q": stripped}, timeout=8)
            if r.status_code == 200:
                d = r.json()
                t = ""
                if isinstance(d, list) and len(d) > 0:
                    first = d[0]
                    t = first[0] if (isinstance(first, list) and len(first) > 0 and isinstance(first[0], str)) else (first if isinstance(first, str) else str(first))
                results.append(t.strip())
            else:
                tier2_failed = True
                break
        except Exception:
            tier2_failed = True
            break

    if not tier2_failed and len(results) == len(lines):
        return results

    # =========================================================================
    # Tier 3: translate.googleapis.com single gtx
    # =========================================================================
    try:
        gtx_results = []
        tier3_failed = False
        url_gtx = "https://translate.googleapis.com/translate_a/single"
        for line in lines:
            stripped = line.strip()
            if not stripped:
                gtx_results.append("")
                continue
            r = session.get(url_gtx, params={"client": "gtx", "sl": src, "tl": tgt, "dt": "t", "q": stripped}, timeout=6)
            if r.status_code == 200:
                d = r.json()
                if isinstance(d, list) and len(d) > 0 and isinstance(d[0], list):
                    t = "".join([part[0] for part in d[0] if part and len(part) > 0 and part[0]])
                    gtx_results.append(t.strip())
                else:
                    tier3_failed = True
                    break
            else:
                tier3_failed = True
                break
        if not tier3_failed and len(gtx_results) == len(lines):
            return gtx_results
    except Exception:
        pass

    # =========================================================================
    # Tier 4: MyMemoryTranslator fallback
    # =========================================================================
    try:
        from deep_translator import MyMemoryTranslator
        m_src = LANG_NAME_MAP.get(src, "english")
        m_tgt = LANG_NAME_MAP.get(tgt, "arabic")
        mem_trans = MyMemoryTranslator(source=m_src, target=m_tgt)
        return [mem_trans.translate(l.strip()) if l.strip() else "" for l in lines]
    except Exception:
        pass

    return lines


def robust_translate_single(text: str, source: str = "auto", target: str = "ar", session: requests.Session = None) -> str:
    """Translates a single line of text with multi-tier fallback."""
    if not text or not text.strip():
        return text
    res = robust_translate_batch([text], source=source, target=target, session=session)
    return res[0] if res else text


class TranslationWorker(QThread):
    """Worker thread that executes batch subtitle translations smoothly in the background."""

    progress_changed = pyqtSignal(int, int, str)
    cue_translated = pyqtSignal(int, str)
    batch_completed = pyqtSignal(list, str)
    log_message = pyqtSignal(str, str)
    error_occurred = pyqtSignal(str)

    def __init__(self, cues: list[SubtitleCue], engine: str, source_lang: str, target_lang: str,
                 config: dict, output_path: str = None, parent=None):
        super().__init__(parent)
        self.cues = cues
        self.engine = engine
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.config = config
        self.output_path = output_path
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            total = len(self.cues)
            if total == 0:
                self.log_message.emit("warning", "No subtitle lines to translate.")
                self.batch_completed.emit([], self.output_path or "")
                return

            self.log_message.emit("info", f"Starting translation of {total} lines with [{self.engine}] to [{self.target_lang}]...")
            self.progress_changed.emit(0, total, "Initializing translation engine...")

            working_cues = [
                SubtitleCue(index=c.index, start_ms=c.start_ms, end_ms=c.end_ms, text=c.text)
                for c in self.cues
            ]

            if self.engine == "AI Translation":
                self._translate_with_ai(working_cues)
            else:
                self._translate_with_google(working_cues)

            if self._is_cancelled:
                self.log_message.emit("warning", "Translation was cancelled by user.")
                return

            if self.output_path:
                save_ok = SubtitleParser.save_cues(working_cues, self.output_path, self.config)
                if save_ok:
                    self.log_message.emit("success", f"Saved translated subtitle file to: {self.output_path}")
                else:
                    self.log_message.emit("error", f"Failed to write output subtitle: {self.output_path}")

            self.progress_changed.emit(total, total, "Completed successfully")
            self.batch_completed.emit(working_cues, self.output_path or "")

        except Exception as e:
            self.log_message.emit("error", f"Translation error: {str(e)}")
            self.error_occurred.emit(str(e))

    def _translate_with_google(self, working_cues: list[SubtitleCue]):
        """Translates lines using Google Translate with batch chunking to avoid rate limits."""
        total = len(working_cues)
        chunk_size = 20

        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        })

        for i in range(0, total, chunk_size):
            if self._is_cancelled:
                return

            chunk = working_cues[i:i + chunk_size]
            original_texts = [c.text for c in chunk]

            translated_texts = robust_translate_batch(original_texts, self.source_lang, self.target_lang, session)

            if len(translated_texts) == len(chunk):
                for j, translated_text in enumerate(translated_texts):
                    chunk[j].text = translated_text.strip()
                    self.cue_translated.emit(chunk[j].index, chunk[j].text)
            else:
                for cue in chunk:
                    if self._is_cancelled:
                        return
                    single_res = robust_translate_single(cue.text, self.source_lang, self.target_lang, session)
                    cue.text = single_res.strip()
                    self.cue_translated.emit(cue.index, cue.text)
                    time.sleep(0.04)

            current_done = min(i + chunk_size, total)
            self.progress_changed.emit(current_done, total, f"Translated {current_done}/{total} lines...")
            time.sleep(0.05)

    def _google_call(self, text: str, source: str, target: str, session: requests.Session) -> str:
        return robust_translate_single(text, source, target, session)

    def _translate_with_ai(self, working_cues: list[SubtitleCue]):
        """Translates lines using OpenAI or 2026 Google Gemini 3 series with automatic candidate model fallbacks."""
        api_key = self.config.get("ai_api_key", "").strip()
        if not api_key:
            raise ValueError("No AI API Key provided! Please set your API key in Settings (⚙ الإعدادات).")

        model = clean_model_name(self.config.get("ai_model", "gemini-3.5-flash"))
        is_gemini = api_key.startswith("AQ.") or api_key.startswith("AIza") or "generativelanguage" in self.config.get("ai_endpoint", "")

        total = len(working_cues)
        chunk_size = 20

        # Candidate fallback models
        candidates = [model]
        if is_gemini:
            for m in GEMINI_ACTIVE_MODELS:
                if m not in candidates:
                    candidates.append(m)
        else:
            for m in OPENAI_ACTIVE_MODELS:
                if m not in candidates:
                    candidates.append(m)

        chat_url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions" if is_gemini else self.config.get("ai_endpoint", "https://api.openai.com/v1/chat/completions")
        if not chat_url.endswith("/chat/completions"):
            chat_url = f"{chat_url.rstrip('/')}/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "x-goog-api-key": api_key,
            "Content-Type": "application/json"
        }

        active_model = model

        for i in range(0, total, chunk_size):
            if self._is_cancelled:
                return

            chunk = working_cues[i:i + chunk_size]
            prompt_lines = "\n".join([f"[{c.index}]: {c.text.strip()}" for c in chunk])

            prompt = (
                f"You are a professional subtitle translator. Translate each numbered line from {self.source_lang} "
                f"to {self.target_lang}.\n"
                f"RULES:\n"
                f"1. Keep the exact index tag prefix for each line: '[NUMBER]: Translated line'\n"
                f"2. Keep subtitles natural, concise, and easy to read on screen.\n"
                f"3. Translate every single line.\n\n"
                f"Lines to translate:\n{prompt_lines}"
            )

            translated_content = ""

            # Try candidate models until a model responds successfully
            for cand in candidates[:3]:
                if self._is_cancelled:
                    return

                payload = {
                    "model": cand,
                    "messages": [
                        {"role": "system", "content": "You are an elite, highly accurate subtitle translator."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2
                }
                try:
                    resp = requests.post(chat_url, headers=headers, json=payload, timeout=25)
                    if resp.status_code == 200:
                        data = resp.json()
                        translated_content = data["choices"][0]["message"]["content"]
                        active_model = cand
                        break
                    elif resp.status_code in [404, 503]:
                        # Try next candidate model
                        continue
                    elif is_gemini:
                        # Try native Gemini endpoint as second chance
                        native_url = f"https://generativelanguage.googleapis.com/v1beta/models/{cand}:generateContent?key={api_key}"
                        n_payload = {"contents": [{"parts": [{"text": prompt}]}]}
                        n_resp = requests.post(native_url, json=n_payload, timeout=25)
                        if n_resp.status_code == 200:
                            n_data = n_resp.json()
                            translated_content = n_data["candidates"][0]["content"]["parts"][0]["text"]
                            active_model = cand
                            break
                    else:
                        self.log_message.emit("warning", f"AI API returned HTTP {resp.status_code}: {resp.text[:120]}")
                except Exception as e:
                    self.log_message.emit("warning", f"AI request with {cand} failed: {e}")

            # Parse translated lines with multi-pattern regex
            unmatched_cues = []
            if translated_content:
                for cue in chunk:
                    # Pattern 1: [1]: Text
                    match = re.search(rf"\[{cue.index}\]:\s*(.+?)(?=\n\[\d+\]:|\Z)", translated_content, re.DOTALL)
                    # Pattern 2: **[1]**: Text
                    if not match:
                        match = re.search(rf"\*+\[?{cue.index}\]?\*+[:.]\s*(.+?)(?=\n\*+\[?\d+|\Z)", translated_content, re.DOTALL)
                    # Pattern 3: 1: Text or 1. Text
                    if not match:
                        match = re.search(rf"(?:^|\n)\s*{cue.index}[:.)-]\s*(.+?)(?=\n\s*\d+[:.)-]|\Z)", translated_content, re.DOTALL)

                    if match:
                        cue.text = match.group(1).strip()
                        self.cue_translated.emit(cue.index, cue.text)
                    else:
                        unmatched_cues.append(cue)
            else:
                unmatched_cues = chunk

            # Safe fallback for any unmatched cues so no lines are skipped
            if unmatched_cues:
                self.log_message.emit("info", f"Using fast fallback for {len(unmatched_cues)} subtitle cue(s)...")
                fallback_texts = robust_translate_batch([c.text for c in unmatched_cues], self.source_lang, self.target_lang)
                for c_idx, trans in enumerate(fallback_texts):
                    if trans and trans.strip():
                        unmatched_cues[c_idx].text = trans.strip()
                        self.cue_translated.emit(unmatched_cues[c_idx].index, unmatched_cues[c_idx].text)

            current_done = min(i + chunk_size, total)
            self.progress_changed.emit(current_done, total, f"AI Translated {current_done}/{total} lines ({active_model})...")
            time.sleep(0.1)
