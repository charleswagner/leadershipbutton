"""
Sound and Music Suggestion Engine

Select up to N sound/music files that best match an utterance intent.
- Stateless per request; reads CSV on init; optional sidecar embeddings file
- Fast lexical prefilter + optional embedding rerank + diversity (MMR)
"""

from __future__ import annotations

import os
import re
import json
import time
import logging
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except Exception:
    NUMPY_AVAILABLE = False

# Optional deps; guarded (we import where used)
PANDAS_AVAILABLE = True

try:
    from sentence_transformers import SentenceTransformer

    ST_AVAILABLE = True
except Exception:
    ST_AVAILABLE = False

try:
    from rapidfuzz.fuzz import partial_ratio  # lightweight fuzzy boost

    FUZZ_AVAILABLE = True
except Exception:
    FUZZ_AVAILABLE = False

LOGGER = logging.getLogger(__name__)


DEFAULT_CSV_PATH = "helpers/soundscripts/data/soundlibrary.csv"
DEFAULT_SIDECAR_PATH = "helpers/soundscripts/data/soundlibrary_embeddings.parquet"
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Minimal denylist for safety
DENY_TAGS = {
    "gun",
    "gunshot",
    "weapon",
    "horror",
    "scream",
    "blood",
    "violence",
}

STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "of",
    "in",
    "on",
    "for",
    "with",
    "at",
    "from",
    "by",
    "is",
    "it",
    "that",
    "this",
    "was",
    "are",
    "be",
}


def _safe_lower(s: Any) -> str:
    return str(s).lower() if s is not None else ""


def _tokens(text: str) -> List[str]:
    text_l = _safe_lower(text)
    text_l = re.sub(r"[^a-z0-9\s]", " ", text_l)
    raw = [t for t in text_l.split() if t and t not in STOPWORDS]
    # light stemming-ish: remove common plural 's'
    norm = [t[:-1] if t.endswith("s") and len(t) > 3 else t for t in raw]
    return norm


def _filename_tokens(filename: str) -> List[str]:
    name = _safe_lower(filename)
    # strip extension
    name = re.sub(r"\.[a-z0-9]+$", "", name)
    # remove vendor prefixes and numeric ids like mixkit-xxx-123
    name = re.sub(r"^mixkit-", "", name)
    name = re.sub(r"-[0-9]+$", "", name)
    name = name.replace("_", " ").replace("-", " ")
    return _tokens(name)


def _jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    sa = set(a)
    sb = set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / float(len(sa | sb))


def _cosine(a: Any, b: Any) -> float:
    if not NUMPY_AVAILABLE:
        return 0.0
    va = np.asarray(a, dtype=np.float32)
    vb = np.asarray(b, dtype=np.float32)
    na = np.linalg.norm(va)
    nb = np.linalg.norm(vb)
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(va, vb) / (na * nb))


class SoundSuggester:
    def __init__(
        self,
        csv_path: str = DEFAULT_CSV_PATH,
        sidecar_path: str = DEFAULT_SIDECAR_PATH,
        embedding_model_name: str = DEFAULT_EMBEDDING_MODEL,
    ) -> None:
        self.csv_path = csv_path
        self.sidecar_path = sidecar_path
        self.embedding_model_name = embedding_model_name
        self.rows: List[Dict[str, Any]] = self._load_csv_rows(csv_path)
        self.embeddings_index: Dict[str, Any] = self._load_sidecar(sidecar_path)
        self.model = self._load_model(embedding_model_name) if ST_AVAILABLE else None
        LOGGER.info(
            "SoundSuggester initialized: rows=%d, sidecar=%s, model=%s",
            len(self.rows),
            "loaded" if self.embeddings_index else "none",
            embedding_model_name if self.model else "none",
        )

    # ---------- Public API ----------
    def suggest(self, intent: Dict[str, Any], limit: int = 20) -> List[Dict[str, Any]]:
        start = time.time()
        palette_terms, query_text, target_music, target_sfx = self._build_query(intent)

        # Prefilter
        candidates = self._prefilter(self.rows, palette_terms)
        # Rerank
        ranked = self._rerank(candidates, query_text, palette_terms)
        # Select with diversity and quotas
        picks = self._select_diverse(ranked, target_music, target_sfx, limit)
        LOGGER.info(
            "SoundSuggester: intent terms=%d candidates=%d picks=%d (%.2fms)",
            len(palette_terms),
            len(candidates),
            len(picks),
            (time.time() - start) * 1000.0,
        )
        return picks

    # Optional: build sidecar for all rows
    def build_sidecar(self, out_path: Optional[str] = None) -> int:
        if not (ST_AVAILABLE and PANDAS_AVAILABLE and NUMPY_AVAILABLE):
            LOGGER.warning("Cannot build sidecar: missing deps")
            return 0
        if self.model is None:
            self.model = self._load_model(self.embedding_model_name)
            if self.model is None:
                return 0
        texts = [self._row_text(r) for r in self.rows]
        LOGGER.info("Embedding %d rows with %s", len(texts), self.embedding_model_name)
        vectors = self.model.encode(texts, normalize_embeddings=False)
        import pandas as pd  # type: ignore

        df = pd.DataFrame(
            {
                "filename": [r.get("filename", "") for r in self.rows],
                "embedding": [json.dumps(list(map(float, v))) for v in vectors],
                "model": self.embedding_model_name,
                "dim": len(vectors[0]) if len(vectors) else 0,
            }
        )
        out = out_path or self.sidecar_path
        os.makedirs(os.path.dirname(out), exist_ok=True)
        try:
            df.to_parquet(out, index=False)
            LOGGER.info("Saved sidecar embeddings: %s", out)
            # refresh in-memory index
            self.embeddings_index = self._load_sidecar(out)
            return len(df)
        except Exception as exc:
            LOGGER.warning("Failed saving sidecar: %s", exc)
            return 0

    # ---------- Internals ----------
    def _load_csv_rows(self, path: str) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        if PANDAS_AVAILABLE:
            try:
                import pandas as pd  # type: ignore

                df = pd.read_csv(path)
                rows = df.fillna("").to_dict(orient="records")  # type: ignore
                return rows
            except Exception as exc:
                LOGGER.warning("Pandas CSV load failed: %s; falling back", exc)
        # Fallback minimal CSV loader
        import csv

        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append({k: (v or "") for k, v in row.items()})
        except Exception as exc:
            LOGGER.error("Failed to read CSV %s: %s", path, exc)
        return rows

    def _load_sidecar(self, path: str) -> Dict[str, Any]:
        if not (PANDAS_AVAILABLE and os.path.exists(path)):
            return {}
        try:
            import pandas as pd  # type: ignore

            df = pd.read_parquet(path)
            index: Dict[str, Any] = {}
            for _, row in df.iterrows():  # type: ignore
                fn = str(row["filename"]) if "filename" in row else ""
                emb_json = row.get("embedding", "[]")
                try:
                    vec = json.loads(emb_json)
                except Exception:
                    vec = []
                index[fn] = vec
            return index
        except Exception as exc:
            LOGGER.warning("Failed to load sidecar: %s", exc)
            return {}

    def _load_model(self, model_name: str):
        try:
            return SentenceTransformer(model_name)
        except Exception as exc:
            LOGGER.warning("Embedding model load failed: %s", exc)
            return None

    def _build_query(self, intent: Dict[str, Any]) -> Tuple[List[str], str, int, int]:
        request = _safe_lower(intent.get("request", ""))
        tone = _safe_lower(intent.get("tone", ""))
        ctx = intent.get("context", "") or ""
        pieces = intent.get("pieces", []) or []

        # Palette terms from context + pieces + rule expansion
        terms = set(_tokens(ctx))
        for p in pieces[:6]:
            terms.update(_tokens(str(p.get("name", ""))))
            terms.update(_tokens(str(p.get("description", ""))))
        # Rule expansion
        expanded = self._rule_expand(terms, tone)
        terms.update(expanded)

        # Build query text for embedding
        query_text = f"request:{request} tone:{tone} context:{ctx} terms:" + " ".join(
            sorted(terms)
        )

        # Target mix
        if request == "story":
            tm, ts = 14, 6
        elif request == "advice":
            tm, ts = 10, 10
        else:
            tm, ts = 12, 8

        return list(terms), query_text, tm, ts

    def _rule_expand(self, terms: Iterable[str], tone: str) -> List[str]:
        tset = set(terms)
        out: List[str] = []
        # Weather / ambience guesses
        if {"rain", "storm", "cloud"} & tset or "gentle" in tone:
            out += ["rain", "drizzle", "soft_thunder"]
        if {"night", "sleep", "bedtime", "moon"} & tset:
            out += ["night", "cricket", "lullaby", "soft_piano"]
        if {"castle", "cave", "dragon"} & tset:
            out += ["wind", "fire", "wing", "cavern", "drip"]
        # Tone → music styles
        tone_map = {
            "gentle": ["soft_piano", "lullaby", "pads", "ambient"],
            "upbeat": ["kids", "happy", "ukulele", "pop"],
            "serious": ["calm", "ambient"],
        }
        for k, vs in tone_map.items():
            if k in tone:
                out += vs
        return out

    def _prefilter(
        self, rows: List[Dict[str, Any]], terms: List[str]
    ) -> List[Dict[str, Any]]:
        tset = set(terms)
        cands: List[Tuple[float, Dict[str, Any]]] = []
        for r in rows:
            fn = _safe_lower(r.get("filename", ""))
            title = _safe_lower(r.get("kit_title", ""))
            tags = _safe_lower(r.get("kit_tags", ""))
            cat = _safe_lower(r.get("kit_category", ""))
            # url unused here; kept in final output only

            # Safety gate
            hay = " ".join([fn, title, tags, cat])
            if any(bad in hay for bad in DENY_TAGS):
                continue

            # Duration gate
            try:
                dur = float(r.get("duration", 0) or 0)
            except Exception:
                dur = 0.0
            a_type = _safe_lower(r.get("audio_type", ""))
            is_music = a_type == "song"
            if is_music and not (8.0 <= dur <= 90.0):
                continue
            if (not is_music) and not (0.2 <= dur <= 10.0):
                continue

            item_terms = (
                set(_tokens(title))
                | set(_filename_tokens(fn))
                | set(_tokens(tags))
                | ({cat} if cat else set())
            )
            overlap = len(item_terms & tset)
            # Fuzzy bonus for pieces names
            fuzzy_bonus = 0
            if FUZZ_AVAILABLE and terms:
                for q in terms[:6]:
                    for tok in list(item_terms)[:12]:
                        try:
                            if partial_ratio(q, tok) >= 90:
                                fuzzy_bonus += 1
                                break
                        except Exception:
                            pass
            score = overlap + 0.25 * fuzzy_bonus
            if score > 0 or not tset:
                cands.append((score, r))
        # Keep top 300 by lexical score
        cands.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in cands[:300]]

    def _row_text(self, r: Dict[str, Any]) -> str:
        parts = [
            str(r.get("kit_title", "")),
            str(r.get("kit_category", "")),
            str(r.get("kit_tags", "")),
            _safe_lower(r.get("filename", "")),
        ]
        return " ".join([p for p in parts if p]).strip()

    def _rerank(
        self, candidates: List[Dict[str, Any]], query_text: str, terms: List[str]
    ) -> List[Tuple[float, Dict[str, Any], Dict[str, Any]]]:
        # Compute base lexical features
        tset = set(terms)
        base: List[Tuple[float, Dict[str, Any], Dict[str, Any]]] = []
        for r in candidates:
            fn = _safe_lower(r.get("filename", ""))
            title = _safe_lower(r.get("kit_title", ""))
            tags = _safe_lower(r.get("kit_tags", ""))
            cat = _safe_lower(r.get("kit_category", ""))
            item_terms = (
                set(_tokens(title))
                | set(_filename_tokens(fn))
                | set(_tokens(tags))
                | ({cat} if cat else set())
            )
            overlap = len(item_terms & tset)
            # duration fit
            try:
                dur = float(r.get("duration", 0) or 0)
            except Exception:
                dur = 0.0
            a_type = _safe_lower(r.get("audio_type", ""))
            is_music = a_type == "song"
            dur_fit = self._duration_fit(dur, is_music)
            tone_fit = 0.5 if cat in ("ambient", "kids", "calm", "lullaby") else 0.0
            base_score = (
                0.3 * (overlap / max(len(tset), 1)) + 0.15 * dur_fit + 0.05 * tone_fit
            )
            base.append((base_score, r, {"overlap": overlap, "dur_fit": dur_fit}))

        # Embedding similarity (optional)
        if self.model is None or not ST_AVAILABLE or not NUMPY_AVAILABLE:
            return base
        try:
            qv = self.model.encode([query_text])[0]
        except Exception as exc:
            LOGGER.warning("Query embedding failed: %s", exc)
            return base

        enriched: List[Tuple[float, Dict[str, Any], Dict[str, Any]]] = []
        for base_score, r, meta in base:
            fn = r.get("filename", "")
            vec = self.embeddings_index.get(fn)
            if vec is None and ST_AVAILABLE:
                # Compute on the fly (not persisted)
                try:
                    vec = list(map(float, self.model.encode([self._row_text(r)])[0]))
                except Exception:
                    vec = None
            sim = _cosine(qv, vec) if vec is not None else 0.0
            final_score = 0.5 * sim + base_score
            meta["emb_sim"] = float(sim)
            enriched.append((final_score, r, meta))
        enriched.sort(key=lambda x: x[0], reverse=True)
        return enriched

    def _duration_fit(self, dur: float, is_music: bool) -> float:
        if dur <= 0:
            return 0.0
        if is_music:
            # ideal around 25s within 12–45s
            if dur < 12 or dur > 45:
                return 0.0
            center = 25.0
            span = 13.0
        else:
            # ideal around 1.5s within 0.5–3s
            if dur < 0.5 or dur > 3.0:
                return 0.0
            center = 1.5
            span = 1.0
        return max(0.0, 1.0 - abs(dur - center) / span)

    def _select_diverse(
        self,
        ranked: List[Tuple[float, Dict[str, Any], Dict[str, Any]]],
        target_music: int,
        target_sfx: int,
        limit: int,
    ) -> List[Dict[str, Any]]:
        # Split by type
        music = [t for t in ranked if _safe_lower(t[1].get("audio_type", "")) == "song"]
        sfx = [t for t in ranked if _safe_lower(t[1].get("audio_type", "")) != "song"]

        picks: List[Dict[str, Any]] = []
        picks = self._mmr_pick(music, target_music) + self._mmr_pick(sfx, target_sfx)
        if len(picks) < limit:
            # fill remainder by highest remaining
            remaining = [r for r in ranked if r[1] not in picks]
            for _, r, _ in remaining[: max(0, limit - len(picks))]:
                picks.append(r)

        # Shape output
        out: List[Dict[str, Any]] = []
        for r in picks[:limit]:
            # Ensure a cloud URL is present; fall back to cwsounds bucket if missing
            url = r.get("google_cloud_url", "") or ""
            if not url:
                fn = r.get("filename", "")
                folder = "google"
                fn_l = _safe_lower(fn)
                if "mixkit" in fn_l:
                    folder = "mixkit"
                elif "filmcow" in fn_l:
                    folder = "filmcow"
                url = f"https://storage.googleapis.com/cwsounds/{folder}/{fn}"
            out.append(
                {
                    "filename": r.get("filename", ""),
                    "display_title": r.get("kit_title", "")
                    or os.path.splitext(r.get("filename", ""))[0],
                    "type": (
                        "music"
                        if _safe_lower(r.get("audio_type", "")) == "song"
                        else "sfx"
                    ),
                    "tags": r.get("kit_tags", ""),
                    "duration": float(r.get("duration", 0) or 0.0),
                    "url": url,
                    "category": r.get("kit_category", ""),
                }
            )
        return out

    def _mmr_pick(
        self, items: List[Tuple[float, Dict[str, Any], Dict[str, Any]]], k: int
    ) -> List[Dict[str, Any]]:
        selected: List[Tuple[float, Dict[str, Any], Dict[str, Any]]] = []
        used: set = set()
        while items and len(selected) < k:
            best_idx = -1
            best_mmr = -1e9
            for idx, (score, r, meta) in enumerate(items):
                if id(r) in used:
                    continue
                sim_max = 0.0
                for _, rr, _ in selected:
                    sim = self._item_sim(r, rr)
                    if sim > sim_max:
                        sim_max = sim
                mmr = 0.8 * score - 0.2 * sim_max
                if mmr > best_mmr:
                    best_mmr = mmr
                    best_idx = idx
            if best_idx < 0:
                break
            chosen = items.pop(best_idx)
            selected.append(chosen)
            used.add(id(chosen[1]))
        return [r for _, r, _ in selected]

    def _item_sim(self, a: Dict[str, Any], b: Dict[str, Any]) -> float:
        a_terms = set(_tokens(a.get("kit_tags", ""))) | set(
            _filename_tokens(a.get("filename", ""))
        )
        b_terms = set(_tokens(b.get("kit_tags", ""))) | set(
            _filename_tokens(b.get("filename", ""))
        )
        cat_sim = (
            1.0
            if _safe_lower(a.get("kit_category", ""))
            == _safe_lower(b.get("kit_category", ""))
            else 0.0
        )
        return 0.6 * _jaccard(a_terms, b_terms) + 0.4 * cat_sim
