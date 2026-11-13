# SubExtract Studio — Developed by NoYz
# Intellectual Property & Copyright (c) 2026 NoYz. All Rights Reserved.
# Online Subtitle Search, Verification & Downloader Engine (Multi-Source + Anime)

import os
import re
import gzip
import struct
import urllib.parse
import requests
from typing import List, Dict, Optional, Tuple
from core.subtitle_parser import SubtitleParser, SubtitleCue

# Language mappings ISO 639-1 to OpenSubtitles 3-letter codes
LANG_MAP_TO_3 = {
    "ar": "ara",
    "en": "eng",
    "fr": "fre",
    "es": "spa",
    "de": "ger",
    "it": "ita",
    "pt": "por",
    "ru": "rus",
    "tr": "tur",
    "ja": "jpn",
    "ko": "kor",
    "zh": "chi",
    "hi": "hin",
    "fa": "per",
    "ur": "urd",
    "id": "ind",
    "nl": "dut",
    "pl": "pol",
    "sv": "swe",
    "el": "ell"
}

MEDIA_EXTENSIONS = {".mkv", ".mp4", ".avi", ".mov", ".webm", ".m4v", ".ts", ".flv"}

class MediaTitleCleaner:
    """Intelligently cleans media filenames (Movies, TV Series & Anime) to construct optimal search queries."""

    TAGS_TO_REMOVE = [
        r'\b1080p\b', r'\b720p\b', r'\b480p\b', r'\b2160p\b', r'\b4k\b', r'\buhd\b',
        r'\bbluray\b', r'\bblu-ray\b', r'\bweb-dl\b', r'\bwebdl\b', r'\bwebrip\b', r'\bweb\b',
        r'\bhdtv\b', r'\bdvdrip\b', r'\bhdrip\b', r'\bx264\b', r'\bx265\b', r'\bhevc\b',
        r'\bh\.264\b', r'\bh\.265\b', r'\baac\b', r'\baac2\.0\b', r'\bddp5\.1\b', r'\bdd5\.1\b',
        r'\batmos\b', r'\bdts\b', r'\btruehd\b', r'\brepack\b', r'\bproper\b', r'\bextended\b',
        r'\bunrated\b', r'\bremastered\b', r'\bimax\b', r'\bhdr\b', r'\bhdr10\b', r'\bdv\b',
        r'\bflac\b', r'\beac3\b', r'\bav1\b', r'\bopus\b', r'\bmulti\b', r'\bdual\.audio\b',
        r'\bremux\b', r'\bhybrid\b', r'\bcomplete\b', r'\bseason\b', r'\bbatch\b'
    ]

    @classmethod
    def clean(cls, filename_or_path: str) -> dict:
        """Cleans filename and extracts title, year, season/episode, and English title from path."""
        full_path = os.path.abspath(filename_or_path)
        base_name = os.path.basename(filename_or_path)
        name, ext = os.path.splitext(base_name)
        if ext.lower() not in MEDIA_EXTENSIONS and "." in name:
            name, _ = os.path.splitext(name)

        original_clean = name

        # Try to extract English title from parentheses BEFORE stripping them
        english_title = ""
        paren_matches = re.findall(r'\(([^)]{4,})\)', name)
        for pm in paren_matches:
            # Check if it looks like an English title (has English alpha chars, not just a year or tag)
            stripped = pm.strip()
            if (re.search(r'[a-zA-Z]{3,}', stripped) and
                not re.match(r'^(19|20)\d{2}$', stripped) and
                stripped.lower() not in ['extended', 'unrated', 'remastered', 'uncensored', 'complete']):
                english_title = stripped
                break

        # Also check parent folder for English title in parentheses
        if not english_title:
            parent_dir = os.path.basename(os.path.dirname(full_path))
            if parent_dir:
                folder_paren = re.findall(r'\(([^)]{4,})\)', parent_dir)
                for fp in folder_paren:
                    stripped = fp.strip()
                    if (re.search(r'[a-zA-Z]{3,}', stripped) and
                        not re.match(r'^(19|20)\d{2}$', stripped) and
                        stripped.lower() not in ['extended', 'unrated', 'remastered']):
                        english_title = stripped
                        break

        # 1. Extract 4-digit Year in parentheses or brackets e.g. (2023) or [2021]
        year = None
        year_match = re.search(r'[\(\[]\s*(19\d{2}|20\d{2})\s*[\)\]]', name)
        if year_match:
            year = int(year_match.group(1))
            name = name[:year_match.start()] + " " + name[year_match.end():]

        # 2. Extract Season & Episode e.g. S01E02 or S1E2 or 1x02 or " - 01" (anime episode)
        season = None
        episode = None
        se_match = re.search(r'\b[sS](\d{1,2})[eE](\d{1,3})\b', name)
        if se_match:
            season = int(se_match.group(1))
            episode = int(se_match.group(2))
            name = name[:se_match.start()] + " " + name[se_match.end():]
        else:
            x_match = re.search(r'\b(\d{1,2})x(\d{1,3})\b', name)
            if x_match:
                season = int(x_match.group(1))
                episode = int(x_match.group(2))
                name = name[:x_match.start()] + " " + name[x_match.end():]
            else:
                # Anime episode pattern: " - 01" or " - 001" or " Episode 01"
                ep_match = re.search(r'\s+-\s+(\d{1,3})(?:\s|$|\[)', name)
                if ep_match:
                    episode = int(ep_match.group(1))
                    season = 1  # Assume season 1 for anime
                    name = name[:ep_match.start()] + " " + name[ep_match.end():]
                else:
                    ep_match2 = re.search(r'\b[Ee]pisode\s*(\d{1,3})\b', name)
                    if ep_match2:
                        episode = int(ep_match2.group(1))
                        season = 1
                        name = name[:ep_match2.start()] + " " + name[ep_match2.end():]

        # 3. Strip bracketed groups e.g. [Judas], [Erai-raws], [YTS.MX], [1080p]
        name = re.sub(r'\[[^\]]*\]', ' ', name)
        name = re.sub(r'\([^\)]*\)', ' ', name)

        # 4. Strip release team tags at end (e.g. -EVO, -NAISU, -RARBG)
        name = re.sub(r'-[a-zA-Z0-9_]+$', ' ', name)

        # 5. Strip dots, underscores, dashes
        name = re.sub(r'[\._\-+]+', ' ', name)

        # 6. Strip technical video/audio tags
        for tag in cls.TAGS_TO_REMOVE:
            name = re.sub(tag, ' ', name, flags=re.IGNORECASE)

        # 7. Check if year wasn't in parentheses but as standalone word
        if not year:
            year_match2 = re.search(r'\b(19\d{2}|20\d{2})\b', name)
            if year_match2:
                year = int(year_match2.group(1))
                name = name[:year_match2.start()] + " " + name[year_match2.end():]

        clean_title = re.sub(r'\s+', ' ', name).strip()
        if not clean_title:
            clean_title = re.sub(r'[\._\-+]+', ' ', original_clean).strip()

        # Build optimal query
        query_parts = [clean_title]
        if season is not None and episode is not None:
            query_parts.append(f"S{season:02d}E{episode:02d}")
        elif year:
            query_parts.append(str(year))

        search_query = " ".join(query_parts)

        return {
            "original_filename": base_name,
            "clean_title": clean_title,
            "english_title": english_title,
            "year": year,
            "season": season,
            "episode": episode,
            "search_query": search_query
        }


def compute_movie_hash(filepath: str) -> Optional[str]:
    """Computes OpenSubtitles movie hash (file_size + first 64KB + last 64KB as little-endian int64 sums)."""
    try:
        file_size = os.path.getsize(filepath)
        if file_size < 131072:  # Need at least 128KB
            return None

        hash_val = file_size
        with open(filepath, "rb") as f:
            # Read first 64KB
            for _ in range(8192):
                buf = f.read(8)
                if len(buf) < 8:
                    break
                hash_val += struct.unpack('<q', buf)[0]
                hash_val &= 0xFFFFFFFFFFFFFFFF

            # Read last 64KB
            f.seek(max(0, file_size - 65536))
            for _ in range(8192):
                buf = f.read(8)
                if len(buf) < 8:
                    break
                hash_val += struct.unpack('<q', buf)[0]
                hash_val &= 0xFFFFFFFFFFFFFFFF

        return f"{hash_val:016x}"
    except Exception:
        return None


class SubtitleDownloader:
    """Searches, verifies, and downloads subtitles from online subtitle databases (Movies, Series & Anime)."""

    USER_AGENT = "SubExtractStudio v2.5 (NoYz Edition)"
    HEADERS = {
        "User-Agent": "TemporaryUserAgent",
        "Accept": "application/json"
    }

    @classmethod
    def _search_opensubtitles(cls, query: str, lang_3: str, season: Optional[int] = None,
                               episode: Optional[int] = None) -> List[Dict]:
        """Single OpenSubtitles REST API search call. Returns raw parsed results."""
        encoded_q = urllib.parse.quote(query.strip())
        if not encoded_q:
            return []

        url = f"https://rest.opensubtitles.org/search/query-{encoded_q}/sublanguageid-{lang_3}"
        if season is not None and episode is not None:
            url += f"/season-{season}/episode-{episode}"

        try:
            resp = requests.get(url, headers=cls.HEADERS, timeout=12)
            if resp.status_code != 200:
                return []
            data = resp.json()
            if not isinstance(data, list):
                return []
            return data
        except Exception:
            return []

    @classmethod
    def _search_by_hash(cls, filepath: str, lang_3: str) -> List[Dict]:
        """Search by OpenSubtitles movie hash for exact file matching."""
        movie_hash = compute_movie_hash(filepath)
        if not movie_hash:
            return []

        file_size = os.path.getsize(filepath)
        url = f"https://rest.opensubtitles.org/search/moviebytesize-{file_size}/moviehash-{movie_hash}/sublanguageid-{lang_3}"

        try:
            resp = requests.get(url, headers=cls.HEADERS, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    return data
        except Exception:
            pass
        return []

    @classmethod
    def _parse_results(cls, raw_data: List[Dict], query: str, bonus_score: float = 0.0) -> List[Dict]:
        """Parses OpenSubtitles raw JSON items into standardized result dicts."""
        clean_q = query.strip().lower()
        results = []
        seen_ids = set()

        for item in raw_data:
            sub_id = item.get("IDSubtitleFile", "")
            if sub_id in seen_ids:
                continue
            seen_ids.add(sub_id)

            sub_file = item.get("SubFileName") or ""
            movie_name = item.get("MovieName") or item.get("MovieReleaseName") or ""
            movie_year = item.get("MovieYear") or ""
            downloads = int(item.get("SubDownloadsCnt", 0) or 0)
            rating = float(item.get("SubRating", 0.0) or 0.0)
            dl_link = item.get("SubDownloadLink") or ""
            fmt = item.get("SubFormat", "srt").lower()

            # Calculate match score
            score = 50.0 + bonus_score
            if clean_q in sub_file.lower() or clean_q in movie_name.lower():
                score += 30.0
            if downloads > 1000:
                score += 15.0
            elif downloads > 100:
                score += 5.0
            if rating >= 8.0:
                score += 5.0

            results.append({
                "id": sub_id,
                "sub_filename": sub_file,
                "movie_name": f"{movie_name} ({movie_year})" if movie_year else movie_name,
                "release_name": item.get("MovieReleaseName") or sub_file,
                "language": item.get("LanguageName", ""),
                "lang_code": item.get("ISO639", ""),
                "format": fmt,
                "downloads": downloads,
                "rating": rating,
                "download_url": dl_link,
                "match_score": min(100.0, score)
            })

        return results

    @classmethod
    def search(cls, query: str, lang_code: str = "ar", season: Optional[int] = None,
               episode: Optional[int] = None, video_path: str = None,
               english_title: str = None) -> List[Dict]:
        """
        Multi-strategy intelligent subtitle search with fallbacks for anime, series & movies.
        Tries: hash → exact+season/ep → title-only → english title → shortened title → english fallback.
        """
        lang_3 = LANG_MAP_TO_3.get(lang_code.lower().split("-")[0], "ara")
        clean_q = query.strip()
        if not clean_q:
            return []

        # If query contains S01E01, parse them if not already provided, and get title_q
        se_match = re.search(r'\b[sS](\d{1,2})[eE](\d{1,3})\b', clean_q)
        if se_match:
            if season is None:
                season = int(se_match.group(1))
            if episode is None:
                episode = int(se_match.group(2))
            title_q = re.sub(r'\b[sS]\d{1,2}[eE]\d{1,3}\b', '', clean_q).strip()
        else:
            title_q = clean_q

        if not title_q:
            title_q = clean_q

        all_results = []
        seen_ids = set()

        def merge_results(new_items: List[Dict]):
            for item in new_items:
                if item["id"] not in seen_ids:
                    seen_ids.add(item["id"])
                    all_results.append(item)

        # Strategy 0: Hash-based search (exact file match — highest confidence)
        if video_path and os.path.exists(video_path):
            hash_raw = cls._search_by_hash(video_path, lang_3)
            if hash_raw:
                merge_results(cls._parse_results(hash_raw, title_q, bonus_score=20.0))

        # Strategy 1: Title query with season/episode URL params
        if season is not None and episode is not None:
            raw1 = cls._search_opensubtitles(title_q, lang_3, season, episode)
            merge_results(cls._parse_results(raw1, title_q, bonus_score=10.0))

        # Strategy 2: Title-only without season/episode (broader search for anime)
        if len(all_results) < 5:
            raw2 = cls._search_opensubtitles(title_q, lang_3)
            merge_results(cls._parse_results(raw2, title_q))

        # Strategy 3: English title from folder/filename parentheses
        if len(all_results) < 5 and english_title:
            eng_q = english_title.strip()
            if eng_q.lower() != clean_q.lower():
                raw3 = cls._search_opensubtitles(eng_q, lang_3, season, episode)
                merge_results(cls._parse_results(raw3, eng_q, bonus_score=5.0))
                # Also try without season/episode
                if len(all_results) < 5:
                    raw3b = cls._search_opensubtitles(eng_q, lang_3)
                    merge_results(cls._parse_results(raw3b, eng_q))

        # Strategy 4: Shortened title (first 2-3 significant words — helps with long anime titles)
        if len(all_results) < 3:
            words = clean_q.split()
            if len(words) > 3:
                short_q = " ".join(words[:3])
                raw4 = cls._search_opensubtitles(short_q, lang_3, season, episode)
                merge_results(cls._parse_results(raw4, short_q, bonus_score=-5.0))

        # Strategy 5: English language fallback (if primary language has <3 results)
        if len(all_results) < 3 and lang_3 != "eng":
            eng_raw = cls._search_opensubtitles(clean_q, "eng", season, episode)
            eng_results = cls._parse_results(eng_raw, clean_q, bonus_score=-10.0)
            for r in eng_results:
                r["language"] = f"English (fallback)"
            merge_results(eng_results[:15])

            # Also try English title in English
            if english_title and len(all_results) < 5:
                eng_raw2 = cls._search_opensubtitles(english_title, "eng", season, episode)
                eng_results2 = cls._parse_results(eng_raw2, english_title, bonus_score=-10.0)
                for r in eng_results2:
                    r["language"] = f"English (fallback)"
                merge_results(eng_results2[:10])

        # Sort by match score and downloads
        all_results.sort(key=lambda x: (x["match_score"], x["downloads"]), reverse=True)
        return all_results

    @classmethod
    def download_and_verify(cls, download_url: str, save_path: str) -> dict:
        """
        Downloads the subtitle archive/file, decompresses gzip, verifies subtitle
        syntax and cues, adds NoYz copyright branding as valid cue, and saves as clean UTF-8.
        """
        if not download_url:
            raise ValueError("Empty download URL.")

        headers = {
            "User-Agent": "TemporaryUserAgent",
            "Referer": "https://www.opensubtitles.org/"
        }

        resp = requests.get(download_url, headers=headers, timeout=20)
        if resp.status_code != 200:
            raise RuntimeError(f"Download failed with HTTP status {resp.status_code}")

        raw_bytes = resp.content

        # Decompress if gzip format (magic number 1f 8b)
        if raw_bytes[:2] == b'\x1f\x8b':
            try:
                raw_bytes = gzip.decompress(raw_bytes)
            except Exception as e:
                raise RuntimeError(f"Failed to decompress gzip subtitle: {e}")

        # Decode using prioritized charset decoding
        charsets = ["utf-8", "cp1256", "iso-8859-6", "windows-1252", "latin-1"]
        decoded_text = ""
        used_charset = "utf-8"

        for enc in charsets:
            try:
                decoded_text = raw_bytes.decode(enc)
                used_charset = enc
                break
            except UnicodeDecodeError:
                continue

        if not decoded_text:
            decoded_text = raw_bytes.decode("utf-8", errors="replace")
            used_charset = "utf-8-fallback"

        # Verification step: parse cues to ensure subtitle integrity
        if "[Script Info]" in decoded_text or "[V4+ Styles]" in decoded_text:
            cues = SubtitleParser.parse_ass_text(decoded_text)
        elif "WEBVTT" in decoded_text:
            cues = SubtitleParser.parse_vtt_text(decoded_text)
        else:
            cues = SubtitleParser.parse_srt_text(decoded_text)

        if not cues:
            # Try auto-detecting any cues
            cues = SubtitleParser.parse_srt_text(decoded_text)

        if not cues:
            raise ValueError("Downloaded subtitle contains no valid cues or timestamps.")

        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

        # Inject player-compatible branding cue without breaking any video players
        cues = SubtitleParser.inject_branding_cues(cues)
        formatted_srt = SubtitleParser.cues_to_srt(cues)

        with open(save_path, "w", encoding="utf-8") as f:
            f.write(formatted_srt)

        return {
            "success": True,
            "save_path": save_path,
            "cue_count": len(cues),
            "first_cue_time": SubtitleParser.ms_to_srt_time(cues[0].start_ms),
            "last_cue_time": SubtitleParser.ms_to_srt_time(cues[-1].end_ms),
            "encoding": used_charset,
            "file_size": os.path.getsize(save_path)
        }
