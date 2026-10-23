#!/usr/bin/env python3
"""Expand compact CSS into one-declaration-per-line, 4-space style.

Usage: css-expand.py FILE        print the expanded CSS to stdout
       css-expand.py -i FILE     rewrite FILE in place

Handles nested at-rules (@media, @keyframes), comments on their own line,
selector lists (one selector per line), blank line before every rule, and
shortens #rrggbb hex colors that have a 3-digit form. No external deps.
"""
import re
import sys


def tokenize(src):
    i, n, buf, out = 0, len(src), "", []
    while i < n:
        c = src[i]
        if src.startswith("/*", i):
            j = src.index("*/", i) + 2
            if buf.strip():
                raise SystemExit("comment inside a prelude or declaration list")
            out.append(("comment", src[i:j]))
            i = j
        elif c in "{}":
            out.append(("open" if c == "{" else "close", buf.strip()))
            buf = ""
            i += 1
        elif c in "\"'":
            j = src.index(c, i + 1) + 1
            buf += src[i:j]
            i = j
        else:
            buf += c
            i += 1
    if buf.strip():
        raise SystemExit("trailing content after last block")
    return out


def split_decls(body):
    parts, depth, cur = [], 0, ""
    for ch in body:
        depth += (ch == "(") - (ch == ")")
        if ch == ";" and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [re.sub(r"\s+", " ", p).strip() for p in parts if p.strip()]


def parse(tokens):
    root = {"children": [], "decls": []}
    stack = [root]
    for kind, text in tokens:
        top = stack[-1]
        if kind == "comment":
            top["children"].append({"type": "comment", "text": text})
        elif kind == "open":
            node = {"type": "block", "prelude": text, "children": [], "decls": []}
            top["children"].append(node)
            stack.append(node)
        else:
            if text:
                top["decls"] = split_decls(text)
            stack.pop()
    return root


def shorten_hex(decl):
    def repl(m):
        h = m.group(1).lower()
        if all(h[k] == h[k + 1] for k in (0, 2, 4)):
            return "#" + h[0] + h[2] + h[4]
        return m.group(0)

    return re.sub(r"#([0-9a-fA-F]{6})\b", repl, decl)


def emit(node, depth, lines):
    pad = "    " * depth
    first, after_comment = True, False
    for ch in node["children"]:
        if ch["type"] == "comment":
            if not first:
                lines.append("")
            lines.append(pad + ch["text"])
            first, after_comment = False, True
            continue
        if not first and not after_comment:
            lines.append("")
        first, after_comment = False, False
        prelude = re.sub(r"\s+", " ", ch["prelude"]).strip()
        if prelude.startswith("@"):
            lines.append(pad + prelude + " {")
        else:
            sels = [s.strip() for s in prelude.split(",")]
            for k, s in enumerate(sels):
                lines.append(pad + s + ("," if k < len(sels) - 1 else " {"))
        for d in ch["decls"]:
            lines.append(pad + "    " + shorten_hex(d) + ";")
        emit(ch, depth + 1, lines)
        lines.append(pad + "}")


def main(argv):
    in_place = "-i" in argv
    paths = [a for a in argv if a != "-i"]
    if len(paths) != 1:
        raise SystemExit(__doc__)
    path = paths[0]
    with open(path, encoding="utf-8") as f:
        root = parse(tokenize(f.read()))
    lines = []
    emit(root, 0, lines)
    out = "\n".join(lines) + "\n"
    if in_place:
        with open(path, "w", encoding="utf-8") as f:
            f.write(out)
    else:
        sys.stdout.write(out)


main(sys.argv[1:])
