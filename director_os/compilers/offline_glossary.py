"""Offline Chinese→English glossary for cinematic terms.

Provides zero-dependency translation of common film-production vocabulary
when no LLM client is configured. Covers emotions, lighting, color,
camera, composition, wardrobe, atmosphere, and frequently-used phrases
extracted from real Director OS projects.

Strategy (see ``translate_offline``):
    1. Normalize whitespace.
    2. Greedy longest-match against the glossary (sorted by token length
       so multi-character terms win over single characters).
    3. Unmatched CJK runs are passed through unchanged — we never invent
       translations for content we don't recognize.

This is deliberately a *fallback*: when an LLM client IS available, the
LLM path in translation.py produces higher-quality, context-aware output.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Glossary — Chinese term → English.
# Ordered roughly by domain. Multi-word phrases first within each domain
# so the sorter keeps them ahead of their substrings.
# ---------------------------------------------------------------------------

_GLOSSARY: dict[str, str] = {
    # ── Emotions & tone ────────────────────────────────────────────────
    "压抑": "oppressive",
    "克制": "restrained",
    "冷峻": "stern",
    "寒冷": "cold",
    "潮湿": "damp",
    "孤独": "lonely",
    "寂寞": "solitary",
    "恐惧": "fear",
    "害怕": "afraid",
    "愤怒": "anger",
    "悲伤": "sorrow",
    "忧郁": "melancholy",
    "温柔": "tender",
    "温暖": "warm",
    "希望": "hope",
    "绝望": "despair",
    "紧张": "tense",
    "不安": "unease",
    "焦虑": "anxiety",
    "平静": "calm",
    "宁静": "tranquil",
    "神秘": "mysterious",
    "诡异": "eerie",
    "震撼": "awe",
    "震撼力": "impact",
    "梦幻": "dreamy",
    "浪漫": "romantic",
    "怀旧": "nostalgic",
    "凄凉": "bleak",
    "荒凉": "desolate",
    "庄严": "solemn",
    "肃穆": "reverent",
    "压抑的日常": "oppressive routine",
    "隐隐不安": "lingering unease",
    "挥之不去的异样感": "lingering wrongness",
    "无声的压迫": "silent oppression",
    "冰冷的仪式感": "cold ritual",
    "不安的初现": "first stirrings of unease",
    "职业面具下的裂痕": "cracks beneath the professional mask",
    "黑色悬疑": "noir suspense",
    "时代悬疑": "period suspense",
    "历史写实主义": "historical realism",

    # ── Lighting ───────────────────────────────────────────────────────
    "侧光": "side lighting",
    "逆光": "backlight",
    "顶光": "top light",
    "底光": "underlight",
    "顺光": "front lighting",
    "自然光": "natural light",
    "硬光": "hard light",
    "软光": "soft light",
    "高反差": "high contrast",
    "低反差": "low contrast",
    "高饱和度": "high saturation",
    "低饱和度": "low saturation",
    "低饱和度冷灰": "desaturated cold gray",
    "黎明自然光": "dawn natural light",
    "黎明前最后的暗": "last darkness before dawn",
    "黄金时刻": "golden hour",
    "剪影": "silhouette",
    "明暗对比": "chiaroscuro",

    # ── Color & grade ──────────────────────────────────────────────────
    "冷灰": "cold gray",
    "暗绿": "dark green",
    "暗红": "dark red",
    "铁灰": "iron gray",
    "阴影蓝": "shadow blue",
    "暖黄": "warm yellow",
    "冷蓝": "cold blue",
    "暗调": "dark tone",
    "暖调": "warm tone",
    "冷调": "cold tone",
    "胶片质感": "film texture",
    "粗粝的胶片颗粒感": "coarse film grain",
    "胶片颗粒感": "film grain",
    "哑光": "matte",
    "高饱和": "highly saturated",
    "去饱和": "desaturated",
    "单色": "monochrome",

    # ── Camera & shot ──────────────────────────────────────────────────
    "特写": "close-up",
    "近景": "medium close-up",
    "中景": "medium shot",
    "全景": "full shot",
    "远景": "wide shot",
    "大远景": "extreme wide shot",
    "俯拍": "high angle",
    "仰拍": "low angle",
    "平视": "eye-level",
    "荷兰角": "Dutch angle",
    "过肩镜头": "over-the-shoulder",
    "固定机位": "static camera",
    "手持": "handheld",
    "斯坦尼康": "steadicam",
    "推轨": "dolly",
    "拉镜": "dolly out",
    "横移": "tracking",
    "摇镜": "pan",
    "变焦": "zoom",
    "长焦": "telephoto",
    "广角": "wide-angle",
    "虚焦": "defocused",
    "焦点": "focus",
    "景深": "depth of field",
    "空间压缩": "spatial compression",
    "长焦空间压缩感": "telephoto spatial compression",

    # ── Composition & framing ─────────────────────────────────────────
    "前景": "foreground",
    "中景（层次）": "midground",
    "后景": "background",
    "构图": "composition",
    "对称构图": "symmetrical composition",
    "三分法": "rule of thirds",
    "负空间": "negative space",
    "视觉中心": "visual center",

    # ── Atmosphere & environment ──────────────────────────────────────
    "雾": "fog",
    "晨雾": "morning mist",
    "烟": "smoke",
    "烟雾": "haze",
    "雨": "rain",
    "雪": "snow",
    "风": "wind",
    "夜": "night",
    "夜晚": "night",
    "黄昏": "dusk",
    "黎明": "dawn",
    "室内": "interior",
    "室外": "exterior",
    "空地": "open ground",
    "废墟": "ruins",
    "城市": "city",
    "乡村": "countryside",
    "刑场": "execution ground",
    "城墙": "city wall",

    # ── Wardrobe & props ──────────────────────────────────────────────
    "长衫": "long gown",
    "围巾": "scarf",
    "呢帽": "fedora",
    "布鞋": "cloth shoes",
    "军服": "military uniform",
    "囚衣": "prisoner garb",
    "头罩": "hood",
    "黑布": "black cloth",
    "怀表": "pocket watch",
    "烟卷": "cigarette",
    "绳索": "rope",
    "麻绳": "hemp rope",
    "绞刑架": "gallows",
    "绞索": "noose",

    # ── Character & performance ───────────────────────────────────────
    "侦探": "detective",
    "无名侦探": "the nameless detective",
    "死囚": "condemned prisoner",
    "囚犯": "prisoner",
    "刽子手": "executioner",
    "主角": "protagonist",
    "配角": "supporting character",
    "面孔": "face",
    "眼窝": "eye socket",
    "颧骨": "cheekbone",
    "薄唇": "thin lips",
    "瘦削": "gaunt",
    "呼吸声": "breathing",
    "机关声": "mechanism sound",

    # ── Era & setting ─────────────────────────────────────────────────
    "民国": "Republican-era China",
    "民初": "early Republican era",
    "古代": "ancient",
    "现代": "modern",
    "未来": "future",
    "科幻": "sci-fi",
    "奇幻": "fantasy",

    # ── Common verbs & connectors ─────────────────────────────────────
    "的": " ",
    "了": " ",
    "在": "in",
    "与": "and",
    "和": "and",
    "或": "or",
    "但": "but",
    "而": "and",
    "是": "is",
    "不": "not",
    "无": "no",
    "有": "has",
    "一个": "a",
    "一场": "a",
    "走入": "walks into",
    "转身": "turns away",
    "注视": "gazes at",
    "站立": "standing",
    "等待": "waiting",
}

# Pre-sort keys by length (longest first) so greedy matching prefers
# "粗粝的胶片颗粒感" over "胶片颗粒感" over "的".
_SORTED_KEYS: list[str] = sorted(_GLOSSARY.keys(), key=len, reverse=True)
# Build a single regex that matches any glossary term.
_MATCH_RE: re.Pattern[str] = re.compile(
    "(" + "|".join(re.escape(k) for k in _SORTED_KEYS) + ")"
)

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def has_cjk(text: str) -> bool:
    """Return True if *text* contains any CJK ideograph."""
    return bool(_CJK_RE.search(text))


def translate_offline(text: str) -> str:
    """Translate *text* using the static glossary.

    Greedy longest-match: every recognized CJK term is replaced by its
    English equivalent. Unmatched CJK runs and all non-CJK text pass
    through unchanged. Returns the original string if it contains no CJK.

    Quality note: this produces literal, term-by-term output. It is a
    fallback for when no LLM is configured. With an LLM, ``Translator``
    produces fluent, context-aware translations.
    """
    if not text or not has_cjk(text):
        return text

    def _sub(m: re.Match[str]) -> str:
        return _GLOSSARY[m.group(0)]

    result = _MATCH_RE.sub(_sub, text)
    # Tidy up double spaces introduced by single-char filler replacements.
    result = re.sub(r"[ ]{2,}", " ", result).strip()
    return result


def coverage(text: str) -> float:
    """Return the fraction (0.0–1.0) of CJK characters in *text* that
    are covered by a glossary match.

    Useful for the CLI to warn the user when offline translation leaves
    a large amount of Chinese untranslated (i.e. an LLM is recommended).
    """
    if not has_cjk(text):
        return 1.0
    total_cjk = len(_CJK_RE.findall(text))
    if total_cjk == 0:
        return 1.0
    matched_chars = sum(
        len(m.group(0)) for m in _MATCH_RE.finditer(text) if _CJK_RE.search(m.group(0))
    )
    return matched_chars / total_cjk
