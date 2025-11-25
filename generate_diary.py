import os
import datetime
import google.generativeai as genai

# 設定
API_KEY = os.environ.get("GEMINI_API_KEY")
INDEX_FILE = "index.html"
INSERT_POINT = '<div id="entry-point" style="display:none;"></div>'
MODEL_NAME = "gemini-flash-latest"

# テンプレート（前回と同じ）
PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | 夜勤警備員の日誌</title>
    <style>
        body {{ background-color: #151b2b; color: #f0e6d2; font-family: "Yu Mincho", serif; line-height: 1.9; margin: 0; padding: 0; }}
        header {{ text-align: center; padding: 40px 20px; background: linear-gradient(to bottom, #0f131f, #151b2b); border-bottom: 1px solid #2c3e50; }}
        h1 {{ font-size: 1.4em; letter-spacing: 0.15em; color: #fff; margin: 0; }}
        main {{ max-width: 760px; margin: 0 auto; padding: 40px 20px; }}
        article {{ background-color: rgba(255, 255, 255, 0.03); padding: 40px; margin-bottom: 60px; border-radius: 4px; }}
        h2 {{ font-size: 1.6em; margin: 0 0 25px 0; color: #fff; border-bottom: 1px solid #3d4c63; padding-bottom: 15px; }}
        p {{ margin-bottom: 1.8em; text-align: justify; }}
        .date {{ display: block; color: #6c8598; font-size: 0.85em; margin-bottom: 10px; }}
        .back-link {{ display: block; margin-top: 40px; text-align: center; color: #dac8a5; text-decoration: none; }}
        .back-link:hover {{ color: #fff; }}
        footer {{ text-align: center; padding: 50px 20px; font-size: 0.75em; color: #4a5f70; }}
    </style>
</head>
<body>
    <header>
        <h1>夜勤警備員の日誌</h1>
    </header>
    <main>
        <article>
            <span class="date">{date}</span>
            <h2>{title}</h2>
            <div>{body}</div>
            <div style="text-align:right; font-style:italic; color:#6c8598; margin-top:30px;">アカリ</div>
        </article>
        <a href="index.html" class="back-link">← 日誌の一覧に戻る</a>
    </main>
    <footer>&copy; Midnight Log</footer>
</body>
</html>
"""

# ★ここが特別仕様：自己紹介用プロンプト
PROMPT_INTRO = """
あなたは「アカリ」というキャラクターになりきって、ブログの第1回目の記事を書いてください。
【キャラクター設定】
* 名前：アカリ（24歳・女性）
* 職業：オフィスビルの夜間警備員
* 性格：おっとりしているが芯は強い。
* 世界観：怪異が日常に溶け込んでいる世界。
* 文体：丁寧な女性語（～です、～ます）。静かで落ち着いたトーン。
* 日付：{date_str}

【内容】
1. タイトルは「夜勤警備員の日誌、はじめます」のような始まりを感じさせるもの。
2. 自己紹介（夜の警備員であること）。
3. なぜこの日記を書き始めたのか（夜の不思議な出来事を忘れないため、等）。
4. 読者への控えめな挨拶。

【出力形式】
タイトル：[ここにタイトル]
[ここに本文]
"""

def main():
    if not API_KEY:
        print("Error: API Key is missing.")
        return

    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(MODEL_NAME)
    
    # ★ここが特別仕様：強制的に「昨日」の日付にする
    today_date = datetime.date.today() - datetime.timedelta(days=1)
    
    today_str = today_date.strftime("%Y.%m.%d")
    filename_date = today_date.strftime("%Y-%m-%d")
    
    new_filename = f"diary_{filename_date}.html"

    # 生成開始
    print(f"Generating intro diary for {today_str}...")
    try:
        response = model.generate_content(PROMPT_INTRO.format(date_str=today_str))
        text = response.text.strip().split("\n")
        
        title = "無題"
        body_lines = []
        for line in text:
            clean_line = line.strip()
            if clean_line.startswith("タイトル：") or clean_line.startswith("TITLE:"):
                title = clean_line.replace("タイトル：", "").replace("TITLE:", "").strip()
            elif clean_line:
                body_lines.append(clean_line)
        
        if title == "無題" and len(body_lines) > 0:
             title = body_lines.pop(0)

        body_html = "<br>".join(body_lines)

        # 個別ページ保存
        page_html = PAGE_TEMPLATE.format(title=title, date=today_str, body=body_html)
        with open(new_filename, "w", encoding="utf-8") as f:
            f.write(page_html)

        # index.html更新
        link_card = f"""
        <article>
            <span class="date">{today_str}</span>
            <h2><a href="{new_filename}" style="color:#fff; text-decoration:none;">{title}</a></h2>
            <p style="font-size:0.9em; color:#bbb;">
                {body_lines[0][:60]}... 
                <a href="{new_filename}" style="color:#dac8a5; margin-left:10px;">[続きを読む]</a>
            </p>
        </article>
        """

        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            index_content = f.read()

        if INSERT_POINT in index_content:
            new_index_content = index_content.replace(INSERT_POINT, INSERT_POINT + "\n" + link_card)
            with open(INDEX_FILE, "w", encoding="utf-8") as f:
                f.write(new_index_content)
            print("Intro post created successfully!")
        else:
            print("Error: Insert point not found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
