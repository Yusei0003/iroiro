#!/usr/bin/env python3
"""広報取り込みアプリを1つのHTMLファイルに組み立てる。

使い方:
    python3 build.py

webapp/src/template.html に、webapp/seed/ 以下のデータと
webapp/vendor/pdfjs/ の pdf.js 一式を埋め込み、
webapp/dist/koho-app.html を生成する。
外部ネットワークへのアクセスは不要(すべてこのリポジトリ内のファイルで完結する)。
"""
import base64
import glob
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


def read_json(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return json.load(f)


def main():
    bunbetsu = [
        read_json(p.replace(ROOT + os.sep, ""))
        for p in sorted(glob.glob(os.path.join(ROOT, "seed/bunbetsu/*.json")))
    ]
    seed = {
        "bunbetsu": bunbetsu,
        "gomiItems": read_json("seed/gomi-items.json"),
        "koho": read_json("seed/koho-issues.json"),
        "headlines": read_json("seed/headlines.json"),
        "gomi": read_json("seed/gomi-schedule.json"),
    }
    seed_json = json.dumps(seed, ensure_ascii=False, separators=(",", ":"))

    lib = read("vendor/pdfjs/pdf.min.js")
    worker = read("vendor/pdfjs/pdf.worker.min.js")
    with open(os.path.join(ROOT, "vendor/pdfjs/Adobe-Japan1-UCS2.bcmap"), "rb") as f:
        cmap_b64 = base64.b64encode(f.read()).decode()

    html = read("src/template.html")
    parts = {
        "__SEED_JSON__": seed_json,
        "__PDFJS_LIB__": lib,
        "__PDFJS_WORKER__": worker,
        "__CMAP_B64__": cmap_b64,
    }
    for key, value in parts.items():
        if key not in html:
            raise SystemExit(f"テンプレートにプレースホルダーが見つかりません: {key}")
        html = html.replace(key, value)

    out_path = os.path.join(ROOT, "koho-app.html")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"書き出しました: {out_path} ({len(html.encode()) // 1024} KB)")


if __name__ == "__main__":
    main()
