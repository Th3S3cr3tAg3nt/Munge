#!/usr/bin/env python3
"""
 _ __ ___  _   _ _ __   __ _  ___   _ __  _   _
| '_ ' _ \\| | | | '_ \\ / _` |/ _ \\ | '_ \\| | | |
| | | | | | |_| | | | | (_| |  __/_| |_) | |_| |
|_| |_| |_|\\__,_|_| |_|\\__, |\\___(_) .__/ \\__, |
                       |___/       |_|    |___/

Dirty little word munger by Th3 S3cr3t Ag3nt.

Features:
- TOML-configured levels: leet_sets + suffix_sets
- Streaming generation (low RAM)
- Fast transforms (str.translate for leet)
- Policy pruning:
    - min_len / max_len
    - require_upper / require_lower / require_digit / require_special
    - optional special_charset (defaults to "not alnum")
- Mode:
    - munge  : generate candidates from input tokens
    - policy : filter input tokens to those that match policy (no munging)
- Input exclude/stopwords filter (runs before munge/policy):
    - from TOML [exclude] and/or CLI --exclude / --exclude-file
    - CLI escape hatches:
        --no-exclude          : disable all exclude filtering (ignore TOML + CLI excludes)
        --no-default-exclude  : ignore TOML [exclude], but still apply CLI excludes

Requires: Python 3.11+ (tomllib in stdlib)
"""

from __future__ import annotations

import argparse
import heapq
import os
import sys
import tempfile
from dataclasses import dataclass
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    print("ERROR: Python 3.11+ required (tomllib not found).", file=sys.stderr)
    sys.exit(2)


# ----------------------------
# Transform primitives
# ----------------------------

def iter_case_variants(s: str) -> Iterator[str]:
    """Yield unique casing variants with minimal overhead."""
    yield s
    up = s.upper()
    if up != s:
        yield up
    cap = s.capitalize()
    if cap != s and cap != up:
        yield cap
    low = s.lower()
    if low != s and low != up and low != cap:
        yield low


def build_translate_table(mapping: Dict[str, str]) -> Dict[int, str]:
    """Build a str.translate table from a char->string mapping."""
    return {ord(k): v for k, v in mapping.items()}


def iter_leet_variants(s: str, tables: Sequence[Dict[int, str]]) -> Iterator[str]:
    """Yield leet-transformed variants for string s."""
    for t in tables:
        yield s.translate(t)


# ----------------------------
# Policy
# ----------------------------

@dataclass(frozen=True)
class Policy:
    min_len: Optional[int] = None
    max_len: Optional[int] = None
    require_upper: bool = False
    require_lower: bool = False
    require_digit: bool = False
    require_special: bool = False
    # If provided, "special" means membership in this set; otherwise "special" means not alnum.
    special_charset: Optional[str] = None

    def matches(self, s: str) -> bool:
        n = len(s)
        if self.min_len is not None and n < self.min_len:
            return False
        if self.max_len is not None and n > self.max_len:
            return False

        has_upper = has_lower = has_digit = has_special = False

        if self.special_charset is None:
            # Default: special = not alphanumeric
            for ch in s:
                if not has_upper and ch.isupper():
                    has_upper = True
                elif not has_lower and ch.islower():
                    has_lower = True
                elif not has_digit and ch.isdigit():
                    has_digit = True
                elif not has_special and (not ch.isalnum()):
                    has_special = True

                if ((not self.require_upper or has_upper) and
                    (not self.require_lower or has_lower) and
                    (not self.require_digit or has_digit) and
                    (not self.require_special or has_special)):
                    return True
        else:
            special_set = set(self.special_charset)
            for ch in s:
                if not has_upper and ch.isupper():
                    has_upper = True
                elif not has_lower and ch.islower():
                    has_lower = True
                elif not has_digit and ch.isdigit():
                    has_digit = True
                elif not has_special and (ch in special_set):
                    has_special = True

                if ((not self.require_upper or has_upper) and
                    (not self.require_lower or has_lower) and
                    (not self.require_digit or has_digit) and
                    (not self.require_special or has_special)):
                    return True

        if self.require_upper and not has_upper:
            return False
        if self.require_lower and not has_lower:
            return False
        if self.require_digit and not has_digit:
            return False
        if self.require_special and not has_special:
            return False
        return True


# ----------------------------
# Config model
# ----------------------------

@dataclass(frozen=True)
class LevelPlan:
    leet_tables: Tuple[Dict[int, str], ...]
    suffixes: Tuple[str, ...]
    include_base: bool
    policy: Policy


DEFAULT_CONFIG_TOML = r"""# Munge rules config (TOML)
# Edit this file to change leet sets, suffix sets, levels, and policy/excludes.
#
# Schema:
#   [policy]  # optional defaults applied globally unless overridden via CLI
#   min_len = 8
#   max_len = 64
#   require_upper = true
#   require_lower = true
#   require_digit = true
#   require_special = false
#   # If set, "special" means membership in this charset; else special means "not alnum"
#   # special_charset = "!@#$%^&*_-."
#
#   [exclude]  # optional stopwords/excludes before munge/policy mode runs
#   case_sensitive = false
#   words = ["the","and","if"]
#   # files = ["stopwords.txt"]
#
#   [leet_sets.<name>]
#   map = { "a" = "@", "e" = "3", ... }
#
#   [suffix_sets.<name>]
#   values = ["1", "!", "123", ...]
#
#   [levels.<0-9>]
#   leet_sets   = ["set1", "set2"]    # optional
#   suffix_sets = ["common", "years"] # optional
#   include_base = true               # optional (default true)

[policy]
min_len = 8
max_len = 128
require_upper = false
require_lower = false
require_digit = false
require_special = false
# special_charset = "!@#$%^&*_-."

[exclude]
case_sensitive = false
# Top 100 most common words in written English (Oxford English Corpus list).
# Source: Wikipedia “Most common words in English” (OEC top 100).
words = [
  "the","be","to","of","and","a","in","that","have","i","it","for","not","on","with","he","as","you","do","at",
  "this","but","his","by","from","they","we","say","her","she","or","an","will","my","one","all","would","there",
  "their","what","so","up","out","if","about","who","get","which","go","me","when","make","can","like","time","no",
  "just","him","know","take","people","into","year","your","good","some","could","them","see","other","than","then",
  "now","look","only","come","its","over","think","also","back","after","use","two","how","our","work","first","well",
  "way","even","new","want","because","any","these","give","day","most","us"
]
# files = ["stopwords.txt"]

[leet_sets.set1]
map = { e = "3", a = "4", o = "0", i = "1", l = "1", s = "$" }

[leet_sets.set2]
map = { e = "3", a = "@", o = "0", i = "1", l = "1", s = "$" }

[leet_sets.set3]
map = { e = "3", a = "4", o = "0", i = "!", l = "1", s = "$" }

[leet_sets.set4]
map = { e = "3", a = "@", o = "0", i = "!", l = "1", s = "$" }

[leet_sets.set5]
map = { e = "3", a = "4", o = "0", i = "1", l = "1", s = "5" }

[leet_sets.set6]
map = { e = "3", a = "@", o = "0", i = "1", l = "1", s = "5" }

[leet_sets.set7]
map = { e = "3", a = "4", o = "0", i = "!", l = "1", s = "5" }

[leet_sets.set8]
map = { e = "3", a = "@", o = "0", i = "!", l = "1", s = "5" }

[suffix_sets.common]
values = ["1", "123456", "12", "2", "123", "!", "."]

[suffix_sets.more_numbers]
values = ["?", "_", "0", "01", "69", "24", "25", "26", "1234", "8", "9", "10",
          "11", "13", "3", "4", "5", "6", "7"]

[suffix_sets.even_more]
values = ["07", "08", "09", "14", "15", "16", "17", "18", "19", "21", "22", "20",
          "23", "77", "88", "99", "12345", "123456789"]

[suffix_sets.years_and_misc]
values = ["00", "02", "03", "04", "05", "06", "007", "101", "111", "111111", "666", "777",
          "2020", "2021", "2022", "2023", "2024", "2025", "2026",
          "86", "87", "89", "90", "91", "92", "93", "94", "95", "98",
          "1234567", "12345678"]

[levels.0]
include_base = true

[levels.1]
include_base = true

[levels.2]
include_base = true

[levels.3]
include_base = true

[levels.4]
include_base = true

[levels.5]
include_base = true
leet_sets = ["set1"]
suffix_sets = ["common"]

[levels.6]
include_base = true
leet_sets = ["set1", "set2"]
suffix_sets = ["common"]

[levels.7]
include_base = true
leet_sets = ["set1", "set2", "set3"]
suffix_sets = ["common", "more_numbers"]

[levels.8]
include_base = true
leet_sets = ["set1", "set2", "set3", "set4"]
suffix_sets = ["common", "more_numbers", "even_more"]

[levels.9]
include_base = true
leet_sets = ["set1", "set2", "set3", "set4", "set5", "set6", "set7", "set8"]
suffix_sets = ["common", "more_numbers", "even_more", "years_and_misc"]
"""


def load_config_toml(path: str) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def stable_dedupe_preserve_order(items: Iterable[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


# ----------------------------
# Exclude/stopwords
# ----------------------------

def parse_exclude_from_cfg(cfg: dict) -> Tuple[set[str], bool, List[str]]:
    """
    Returns: (exclude_words, case_sensitive, files)
    """
    ex = cfg.get("exclude", {})
    if ex is None:
        ex = {}
    if not isinstance(ex, dict):
        raise ValueError("[exclude] must be a table/object if present.")

    case_sensitive = bool(ex.get("case_sensitive", False))

    words = ex.get("words", []) or []
    if not isinstance(words, list) or not all(isinstance(x, str) for x in words):
        raise ValueError("[exclude].words must be a list of strings.")

    files = ex.get("files", []) or []
    if not isinstance(files, list) or not all(isinstance(x, str) for x in files):
        raise ValueError("[exclude].files must be a list of strings.")

    if case_sensitive:
        exclude_set = {w.strip() for w in words if w.strip()}
    else:
        exclude_set = {w.strip().lower() for w in words if w.strip()}

    return exclude_set, case_sensitive, files


def load_exclude_files(paths: List[str], case_sensitive: bool) -> set[str]:
    out: set[str] = set()
    for p in paths:
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                w = line.strip()
                if not w:
                    continue
                out.add(w if case_sensitive else w.lower())
    return out


def build_effective_exclude(
    cfg: dict,
    cli_exclude: List[str],
    cli_files: List[str],
    cli_case_sensitive: bool,
    no_exclude: bool,
    no_default_exclude: bool,
) -> Tuple[set[str], bool]:
    """
    Merge config + CLI excludes.

    Returns: (exclude_set, case_sensitive)

    Modes:
      - --no-exclude: disable all excludes (ignore TOML + CLI)
      - --no-default-exclude: ignore TOML [exclude], but still apply CLI excludes
    """
    if no_exclude:
        return set(), False

    cfg_set: set[str] = set()
    cfg_case_sensitive = False
    cfg_files: List[str] = []

    if not no_default_exclude:
        cfg_set, cfg_case_sensitive, cfg_files = parse_exclude_from_cfg(cfg)

    case_sensitive = cli_case_sensitive or cfg_case_sensitive

    # If config was case-sensitive but CLI chooses case-insensitive, normalize
    if not case_sensitive and cfg_case_sensitive:
        cfg_set = {w.lower() for w in cfg_set}

    merged = set(cfg_set)

    # files: config + CLI
    file_paths = list(cfg_files) + list(cli_files)
    if file_paths:
        merged |= load_exclude_files(file_paths, case_sensitive)

    # CLI words
    for w in cli_exclude:
        w = (w or "").strip()
        if not w:
            continue
        merged.add(w if case_sensitive else w.lower())

    return merged, case_sensitive


def iter_filtered_input_words(words: Iterable[str], exclude: set[str], case_sensitive: bool) -> Iterator[str]:
    """
    Filters input tokens/lines by:
    - stripping whitespace
    - excluding stopwords (case-insensitive by default)
    Yields stripped strings.
    """
    for w in words:
        s = w.strip()
        if not s:
            continue
        key = s if case_sensitive else s.lower()
        if exclude and key in exclude:
            continue
        yield s


# ----------------------------
# Policy from config + CLI merge
# ----------------------------

def parse_policy_from_cfg(cfg: dict) -> Policy:
    p = cfg.get("policy", {})
    if p is None:
        p = {}
    if not isinstance(p, dict):
        raise ValueError("[policy] must be a table/object if present.")

    def opt_int(key: str) -> Optional[int]:
        v = p.get(key, None)
        if v is None:
            return None
        if not isinstance(v, int):
            raise ValueError(f"[policy].{key} must be an integer.")
        return v

    min_len = opt_int("min_len")
    max_len = opt_int("max_len")

    require_upper = bool(p.get("require_upper", False))
    require_lower = bool(p.get("require_lower", False))
    require_digit = bool(p.get("require_digit", False))
    require_special = bool(p.get("require_special", False))

    special_charset = p.get("special_charset", None)
    if special_charset is not None and not isinstance(special_charset, str):
        raise ValueError("[policy].special_charset must be a string if provided.")

    return Policy(
        min_len=min_len,
        max_len=max_len,
        require_upper=require_upper,
        require_lower=require_lower,
        require_digit=require_digit,
        require_special=require_special,
        special_charset=special_charset,
    )


def merge_policy(base: Policy, overrides: Policy) -> Policy:
    """Override only fields that are not None / True-ish in overrides (CLI)."""
    return Policy(
        min_len=overrides.min_len if overrides.min_len is not None else base.min_len,
        max_len=overrides.max_len if overrides.max_len is not None else base.max_len,
        require_upper=overrides.require_upper or base.require_upper,
        require_lower=overrides.require_lower or base.require_lower,
        require_digit=overrides.require_digit or base.require_digit,
        require_special=overrides.require_special or base.require_special,
        special_charset=overrides.special_charset if overrides.special_charset is not None else base.special_charset,
    )


# ----------------------------
# Compile level plan
# ----------------------------

def compile_level_plan(cfg: dict, level: int, effective_policy: Policy) -> LevelPlan:
    if "levels" not in cfg or not isinstance(cfg["levels"], dict):
        raise ValueError("Config missing [levels] table.")

    levels_tbl = cfg["levels"]
    level_key = str(level)
    if level_key not in levels_tbl:
        raise ValueError(f"Config has no [levels.{level}] section.")

    level_cfg = levels_tbl[level_key]
    if not isinstance(level_cfg, dict):
        raise ValueError(f"[levels.{level}] must be a table/object.")

    include_base = bool(level_cfg.get("include_base", True))

    leet_sets_tbl = cfg.get("leet_sets", {})
    suffix_sets_tbl = cfg.get("suffix_sets", {})

    leet_names = level_cfg.get("leet_sets", []) or []
    if not isinstance(leet_names, list) or not all(isinstance(x, str) for x in leet_names):
        raise ValueError(f"[levels.{level}].leet_sets must be a list of strings.")

    tables: List[Dict[int, str]] = []
    for name in leet_names:
        if name not in leet_sets_tbl:
            raise ValueError(f"Unknown leet set '{name}' referenced by [levels.{level}].")
        entry = leet_sets_tbl[name]
        if not isinstance(entry, dict) or "map" not in entry or not isinstance(entry["map"], dict):
            raise ValueError(f"[leet_sets.{name}] must contain a 'map' table.")
        mapping: Dict[str, str] = {}
        for k, v in entry["map"].items():
            if not isinstance(k, str) or not isinstance(v, str):
                raise ValueError(f"[leet_sets.{name}].map must have string keys/values.")
            if not k:
                raise ValueError(f"[leet_sets.{name}].map has empty key.")
            mapping[k] = v
        tables.append(build_translate_table(mapping))

    suffix_names = level_cfg.get("suffix_sets", []) or []
    if not isinstance(suffix_names, list) or not all(isinstance(x, str) for x in suffix_names):
        raise ValueError(f"[levels.{level}].suffix_sets must be a list of strings.")

    suffixes: List[str] = []
    for name in suffix_names:
        if name not in suffix_sets_tbl:
            raise ValueError(f"Unknown suffix set '{name}' referenced by [levels.{level}].")
        entry = suffix_sets_tbl[name]
        if not isinstance(entry, dict) or "values" not in entry or not isinstance(entry["values"], list):
            raise ValueError(f"[suffix_sets.{name}] must contain 'values' = [..].")
        for v in entry["values"]:
            if not isinstance(v, str):
                raise ValueError(f"[suffix_sets.{name}].values must be strings.")
            if v != "":
                suffixes.append(v)

    suffixes = stable_dedupe_preserve_order(suffixes)

    return LevelPlan(
        leet_tables=tuple(tables),
        suffixes=tuple(suffixes),
        include_base=include_base,
        policy=effective_policy,
    )


# ----------------------------
# Streaming generation + pruning
# ----------------------------

def iter_munge_for_seed(seed: str, plan: LevelPlan) -> Iterator[str]:
    """Generate munge(seed) as a stream, pruned by policy as early as possible."""
    for cv in iter_case_variants(seed):
        if plan.policy.matches(cv):
            yield cv
        if plan.leet_tables:
            for lv in iter_leet_variants(cv, plan.leet_tables):
                if plan.policy.matches(lv):
                    yield lv


def iter_candidates_for_word(word: str, plan: LevelPlan) -> Iterator[str]:
    w = word.strip()
    if not w:
        return
    base = w.lower()

    if plan.include_base:
        yield from iter_munge_for_seed(base, plan)

    for suf in plan.suffixes:
        yield from iter_munge_for_seed(base + suf, plan)


def iter_candidates_for_words(words: Iterable[str], plan: LevelPlan) -> Iterator[str]:
    for w in words:
        yield from iter_candidates_for_word(w, plan)


def iter_policy_filter(words: Iterable[str], policy: Policy) -> Iterator[str]:
    """Policy-only mode: filter input tokens by policy (no munging)."""
    for w in words:
        s = w.strip()
        if not s:
            continue
        if policy.matches(s):
            yield s


# ----------------------------
# Dedupe strategies
# ----------------------------

def dedupe_in_memory(stream: Iterable[str], max_seen: int) -> Iterator[str]:
    """
    In-memory dedupe up to max_seen uniques.
    If the set reaches max_seen, we stop deduping and pass through remaining items.
    """
    seen = set()
    it = iter(stream)
    for s in it:
        if s in seen:
            continue
        yield s
        seen.add(s)
        if len(seen) >= max_seen:
            break
    for s in it:
        yield s


def external_sort_unique_to_file(stream: Iterable[str], out_path: str, tmp_dir: Optional[str], chunk_lines: int) -> None:
    """
    External sort + unique (bounded RAM):
      - write sorted+uniq chunks to temp files
      - k-way merge to out_path with global uniq
    """
    tmpfiles: List[str] = []
    try:
        chunk: List[str] = []

        def flush_chunk(lines: List[str]) -> None:
            lines.sort()
            fd, p = tempfile.mkstemp(prefix="munge_chunk_", dir=tmp_dir, text=True)
            with os.fdopen(fd, "w", encoding="utf-8", errors="ignore") as f:
                prev = None
                for line in lines:
                    if line != prev:
                        f.write(line)
                        f.write("\n")
                        prev = line
            tmpfiles.append(p)

        for s in stream:
            chunk.append(s)
            if len(chunk) >= chunk_lines:
                flush_chunk(chunk)
                chunk = []
        if chunk:
            flush_chunk(chunk)

        if not tmpfiles:
            open(out_path, "w").close()
            return

        if len(tmpfiles) == 1:
            os.replace(tmpfiles[0], out_path)
            tmpfiles.pop()
            return

        fps = [open(p, "r", encoding="utf-8", errors="ignore") for p in tmpfiles]
        try:
            heap: List[Tuple[str, int]] = []
            for i, fp in enumerate(fps):
                line = fp.readline()
                if line:
                    heap.append((line.rstrip("\n"), i))
            heapq.heapify(heap)

            with open(out_path, "w", encoding="utf-8", errors="ignore") as out:
                prev = None
                while heap:
                    val, i = heapq.heappop(heap)
                    if val != prev:
                        out.write(val + "\n")
                        prev = val
                    nxt = fps[i].readline()
                    if nxt:
                        heapq.heappush(heap, (nxt.rstrip("\n"), i))
        finally:
            for fp in fps:
                fp.close()
    finally:
        for p in tmpfiles:
            try:
                os.remove(p)
            except OSError:
                pass


# ----------------------------
# CLI / Main
# ----------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''\
 _ __ ___  _   _ _ __   __ _  ___   _ __  _   _
| '_ ' _ \\| | | | '_ \\ / _` |/ _ \\ | '_ \\| | | |
| | | | | | |_| | | | | (_| |  __/_| |_) | |_| |
|_| |_| |_|\\__,_|_| |_|\\__, |\\___(_) .__/ \\__, |
                       |___/       |_|    |___/

Dirty little word munger by Th3 S3cr3t Ag3nt.

Example usage:

Generate password candidates.
$ ./munge.py -i dictionary.txt -o munged.txt

Optimise password list.
$ ./munge.py --mode policy -i munged.txt -o optimised.txt

'''
    )
    parser.add_argument("word", metavar="word", nargs="?", help="word to munge")
    parser.add_argument("-i", "--input", help="input file (one word per line)")
    parser.add_argument("-o", "--output", help="output file")
    parser.add_argument("-l", "--level", type=int, default=5, help="munge level [0-9] (default 5)")

    parser.add_argument("-c", "--config", default="munge_rules.toml",
                        help="TOML config file path (default: munge_rules.toml)")
    parser.add_argument("--write-default-config", metavar="PATH",
                        help="write a default TOML config to PATH and exit")

    # Policy overrides (CLI) — override/augment [policy] in config.
    parser.add_argument("--min-len", type=int, default=None, help="minimum length (policy override)")
    parser.add_argument("--max-len", type=int, default=None, help="maximum length (policy override)")
    parser.add_argument("--require-upper", action="store_true", help="require at least one uppercase letter")
    parser.add_argument("--require-lower", action="store_true", help="require at least one lowercase letter")
    parser.add_argument("--require-digit", action="store_true", help="require at least one digit")
    parser.add_argument("--require-special", action="store_true", help="require at least one special character")
    parser.add_argument("--special-charset", default=None,
                        help='define what counts as "special" (e.g. "!@#$%%_-."), overrides config')

    # Mode
    parser.add_argument("--mode", choices=["munge", "policy"], default="munge",
                        help="munge (default) generates candidates; policy filters input by policy only")
    parser.add_argument("--policy-only", action="store_true", help="alias for --mode policy")

    # Exclusion / stopwords
    parser.add_argument("--exclude", action="append", default=[],
                        help="exclude a word before processing (repeatable)")
    parser.add_argument("--exclude-file", action="append", default=[],
                        help="path to newline-separated exclude words (repeatable)")
    parser.add_argument("--exclude-case-sensitive", action="store_true",
                        help="treat exclude words as case-sensitive (default: case-insensitive)")
    parser.add_argument("--no-exclude", action="store_true",
                        help="disable all excludes (ignore TOML + CLI excludes)")
    parser.add_argument("--no-default-exclude", action="store_true",
                        help="ignore TOML [exclude], but still apply CLI excludes")

    # Perf / RAM controls
    parser.add_argument("--dedupe", choices=["auto", "memory", "sort", "none"], default="auto",
                        help="dedupe strategy: auto (default), memory, sort (external), none")
    parser.add_argument("--max-seen", type=int, default=2_000_000,
                        help="max uniques to keep in RAM for memory dedupe (default 2,000,000)")
    parser.add_argument("--chunk-lines", type=int, default=1_000_000,
                        help="lines per chunk for external sort (default 1,000,000)")
    parser.add_argument("--tmp-dir", default=None,
                        help="temp directory for external sort chunks (default: system temp)")

    args = parser.parse_args()
    args.level = max(0, min(int(args.level), 9))
    if args.policy_only:
        args.mode = "policy"
    return args


def read_words(args: argparse.Namespace) -> List[str]:
    if args.word:
        return [args.word]
    if args.input:
        with open(args.input, "r", encoding="utf-8", errors="ignore") as f:
            return f.readlines()
    return []


def write_stream_to_output(stream: Iterable[str], output: Optional[str]) -> None:
    if output:
        with open(output, "w", encoding="utf-8", errors="ignore") as f:
            for s in stream:
                f.write(s + "\n")
        print(f"Written to: {output}")
    else:
        for s in stream:
            print(s)


def main() -> None:
    args = parse_args()

    if args.write_default_config:
        with open(args.write_default_config, "w", encoding="utf-8") as f:
            f.write(DEFAULT_CONFIG_TOML)
        print(f"Wrote default config to: {args.write_default_config}")
        return

    raw_words = read_words(args)
    if not raw_words:
        print("Nothing to do!!\nTry -h for help.", file=sys.stderr)
        return

    # Load config
    try:
        cfg = load_config_toml(args.config)
        base_policy = parse_policy_from_cfg(cfg)
    except Exception as e:
        print(f"ERROR loading config '{args.config}': {e}", file=sys.stderr)
        print("Tip: generate a starter config with --write-default-config munge_rules.toml", file=sys.stderr)
        sys.exit(2)

    # Excludes: config + CLI with escape hatches
    exclude_set, exclude_case_sensitive = build_effective_exclude(
        cfg=cfg,
        cli_exclude=args.exclude,
        cli_files=args.exclude_file,
        cli_case_sensitive=args.exclude_case_sensitive,
        no_exclude=args.no_exclude,
        no_default_exclude=args.no_default_exclude,
    )

    filtered_words_iter = iter_filtered_input_words(raw_words, exclude_set, exclude_case_sensitive)

    # Effective policy (config + CLI overrides)
    cli_policy = Policy(
        min_len=args.min_len,
        max_len=args.max_len,
        require_upper=args.require_upper,
        require_lower=args.require_lower,
        require_digit=args.require_digit,
        require_special=args.require_special,
        special_charset=args.special_charset,
    )
    effective_policy = merge_policy(base_policy, cli_policy)

    # Build candidate stream
    if args.mode == "policy":
        stream = iter_policy_filter(filtered_words_iter, effective_policy)
    else:
        try:
            plan = compile_level_plan(cfg, args.level, effective_policy)
        except Exception as e:
            print(f"ERROR compiling level plan: {e}", file=sys.stderr)
            sys.exit(2)
        stream = iter_candidates_for_words(filtered_words_iter, plan)

    # Dedupe strategy:
    # - If writing to file, auto prefers external sort for true global dedupe with bounded RAM.
    # - If stdout, auto uses memory-capped dedupe.
    if args.dedupe == "none":
        write_stream_to_output(stream, args.output)
        return

    if args.output:
        if args.dedupe in ("auto", "sort"):
            external_sort_unique_to_file(stream, args.output, args.tmp_dir, args.chunk_lines)
            print(f"Written to: {args.output}")
        elif args.dedupe == "memory":
            write_stream_to_output(dedupe_in_memory(stream, args.max_seen), args.output)
        else:
            raise ValueError("Unknown dedupe mode")
    else:
        if args.dedupe in ("auto", "memory"):
            write_stream_to_output(dedupe_in_memory(stream, args.max_seen), None)
        elif args.dedupe == "sort":
            fd, tmp_out = tempfile.mkstemp(prefix="munge_out_", dir=args.tmp_dir, text=True)
            os.close(fd)
            try:
                external_sort_unique_to_file(stream, tmp_out, args.tmp_dir, args.chunk_lines)
                with open(tmp_out, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        print(line.rstrip("\n"))
            finally:
                try:
                    os.remove(tmp_out)
                except OSError:
                    pass


if __name__ == "__main__":
    main()
