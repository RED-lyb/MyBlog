"""
对文章 Markdown 中的 [embed:html:base64|...] 片段内联 HTML 做服务端清洗。
保留游戏常用的 script/style/canvas 等标签，使用 bleach 剥离 on* 事件、javascript:/data: 等危险属性与嵌套 iframe。
"""
import base64
import re
from typing import Callable, Match

import bleach
from bleach.css_sanitizer import CSSSanitizer

EMBED_HTML_PATTERN = re.compile(
    r"\[embed:html:([^\|\]]+)\|width:([^\|\]]+)\|height:([^\|\]]+)\]",
    re.IGNORECASE,
)

_EMBED_HTML_TAGS = frozenset(
    [
        "p",
        "br",
        "div",
        "span",
        "canvas",
        "script",
        "style",
        "button",
        "input",
        "label",
        "select",
        "option",
        "textarea",
        "form",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "strong",
        "em",
        "b",
        "i",
        "u",
        "s",
        "strike",
        "ul",
        "ol",
        "li",
        "table",
        "thead",
        "tbody",
        "tfoot",
        "tr",
        "th",
        "td",
        "a",
        "img",
        "pre",
        "code",
        "blockquote",
        "hr",
        "header",
        "footer",
        "main",
        "section",
        "article",
        "nav",
        "small",
        "sub",
        "sup",
        "audio",
        "video",
        "source",
    ]
)

_EMBED_ATTRIBUTES = {
    "*": ["class", "id", "title", "lang", "role", "tabindex", "style"],
    "a": ["href", "name", "target", "rel"],
    "img": ["src", "alt", "width", "height", "loading", "decoding"],
    "canvas": ["width", "height", "id", "class", "style"],
    "script": ["src", "type", "async", "defer", "nomodule", "crossorigin"],
    "style": ["type", "media", "scoped"],
    "input": [
        "type",
        "name",
        "value",
        "placeholder",
        "maxlength",
        "min",
        "max",
        "step",
        "checked",
        "disabled",
        "readonly",
        "id",
        "class",
        "style",
        "pattern",
        "inputmode",
        "autocomplete",
    ],
    "textarea": [
        "name",
        "rows",
        "cols",
        "placeholder",
        "disabled",
        "readonly",
        "id",
        "class",
        "style",
    ],
    "form": ["action", "method", "name", "id", "class", "style", "autocomplete"],
    "button": ["type", "name", "value", "disabled", "id", "class", "style"],
    "select": ["name", "disabled", "multiple", "id", "class", "style", "size"],
    "option": ["value", "selected", "disabled", "label"],
    "label": ["for", "id", "class", "style"],
    "video": ["src", "width", "height", "controls", "poster", "preload", "id", "class", "style"],
    "audio": ["src", "controls", "preload", "id", "class", "style"],
    "source": ["src", "type"],
}

# 禁止 data:（易被用于走私 payload）；仅允许远程脚本/图片与相对路径由 https 承载
_EMBED_PROTOCOLS = ["http", "https"]

_css_sanitizer = CSSSanitizer()


def _decode_embed_payload(b64_payload: str) -> str:
    raw = b64_payload.strip()
    pad = "=" * (-len(raw) % 4)
    return base64.b64decode(raw + pad).decode("utf-8", errors="replace")


def _encode_embed_payload(html_str: str) -> str:
    return base64.b64encode(html_str.encode("utf-8")).decode("ascii")


def sanitize_embed_html_fragment(html_fragment: str) -> str:
    """
    对将要放进 iframe srcdoc 的整段 HTML 做 bleach 清洗。
    不添加 iframe/object/embed 等标签，避免嵌套帧。
    """
    return bleach.clean(
        html_fragment,
        tags=_EMBED_HTML_TAGS,
        attributes=_EMBED_ATTRIBUTES,
        protocols=_EMBED_PROTOCOLS,
        strip=True,
        strip_comments=True,
        css_sanitizer=_css_sanitizer,
    )


def sanitize_article_content_embeds(content: str) -> str:
    """
    遍历正文中的 [embed:html:...] 块，将其中的 base64 解码后清洗再写回。
    """

    def _repl(m: Match[str]) -> str:
        b64_inner, width, height = m.group(1), m.group(2), m.group(3)
        try:
            decoded = _decode_embed_payload(b64_inner)
            cleaned = sanitize_embed_html_fragment(decoded)
            new_b64 = _encode_embed_payload(cleaned)
            return f"[embed:html:{new_b64}|width:{width}|height:{height}]"
        except Exception:
            return m.group(0)

    return EMBED_HTML_PATTERN.sub(_repl, content)
