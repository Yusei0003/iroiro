#!/usr/bin/env python3
"""見出し用フォント(M PLUS Rounded 1c)を、アプリで使う文字だけに絞って取得する。

使い方:
    python3 tools/fetch_fonts.py

src/template.html と seed/ 以下に出てくる文字(+かな・英数字)を集め、
Google Fonts の text= 指定でその文字だけを含む woff2 を受け取って
vendor/fonts/ に保存する(どのファイルにどの文字が入っているかは vendor/fonts/fonts.json)。
インターネット接続が必要なのはこのスクリプトだけで、build.py は保存済みのファイルを埋め込むだけ。

テンプレートの見出し・ボタン・タブの文言を変えて新しい漢字が増えたら、
これを実行し直してから build.py を実行する(足りない字は端末の標準フォントで表示される)。
"""
import glob
import json
import os
import re
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEIGHTS = (500, 700, 800)
CHUNK = 500
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def used_chars():
    texts = [open(os.path.join(ROOT, "src/template.html"), encoding="utf-8").read()]
    for path in glob.glob(os.path.join(ROOT, "seed/**/*.json"), recursive=True):
        texts.append(open(path, encoding="utf-8").read())
    chars = set("".join(texts))
    chars |= {chr(c) for c in range(0x20, 0x7F)}      # 英数字・記号
    chars |= {chr(c) for c in range(0x3041, 0x3097)}  # ひらがな
    chars |= {chr(c) for c in range(0x30A1, 0x30FB)}  # カタカナ
    chars |= set("ー・、。「」『』()()【】〜~:/!?％%号版月年日令和平成昭和")
    return "".join(sorted(c for c in chars if c.isprintable() and not c.isspace()))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as res:
        return res.read()


def unicode_range(chars):
    """文字の集まりを @font-face の unicode-range の書式にする。"""
    cps = sorted(ord(c) for c in chars)
    spans, start, prev = [], cps[0], cps[0]
    for cp in cps[1:] + [None]:
        if cp is not None and cp == prev + 1:
            prev = cp
            continue
        spans.append(f"U+{start:X}" if start == prev else f"U+{start:X}-{prev:X}")
        if cp is not None:
            start = prev = cp
    return ",".join(spans)


def main():
    text = used_chars()
    # text= は長すぎると無視されるので、CHUNK 文字ずつに分けて受け取り、unicode-range で振り分ける
    chunks = [text[i:i + CHUNK] for i in range(0, len(text), CHUNK)]
    out_dir = os.path.join(ROOT, "vendor/fonts")
    os.makedirs(out_dir, exist_ok=True)
    for old in glob.glob(os.path.join(out_dir, "*.woff2")):
        os.remove(old)
    manifest = []
    for w in WEIGHTS:
        for i, chunk in enumerate(chunks):
            query = urllib.parse.urlencode({"family": f"M PLUS Rounded 1c:wght@{w}", "text": chunk, "display": "swap"})
            css = fetch("https://fonts.googleapis.com/css2?" + query).decode()
            urls = re.findall(r"url\((https://[^)]+)\)", css)
            if len(urls) != 1:
                raise SystemExit(f"フォントのURLを特定できませんでした(weight {w} / {i}): {len(urls)}件")
            data = fetch(urls[0])
            if data[:4] != b"wOF2":
                raise SystemExit(f"woff2 ではないファイルが返ってきました(weight {w} / {i})")
            name = f"mplus-rounded-1c-{w}-{i}.woff2"
            with open(os.path.join(out_dir, name), "wb") as f:
                f.write(data)
            manifest.append({"weight": w, "file": name, "unicodeRange": unicode_range(chunk)})
            print(f"保存しました: {name} ({len(data) // 1024} KB)")
    with open(os.path.join(out_dir, "fonts.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print(f"収録した文字数: {len(text)}")


if __name__ == "__main__":
    main()
