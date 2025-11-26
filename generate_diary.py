import os
import datetime
import google.generativeai as genai

# 設定
API_KEY = os.environ.get("GEMINI_API_KEY")
INDEX_FILE = "index.html"
INSERT_POINT = '<div id="entry-point" style="display:none;"></div>'
MODEL_NAME = "gemini-flash-latest"
POSTS_DIR = "posts"

# テンプレート
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
        <a href="../index.html" class="back-link">← 日誌の一覧に戻る</a>
    </main>
    <footer>&copy; Midnight Log</footer>
</body>
</html>
"""

# プロンプト
PROMPT_DAILY = """
あなたは「アカリ」というキャラクターになりきって、今日の日記を書いてください。
【キャラクター設定】
* 名前：アカリ（24歳・女性）
* 職業：オフィスビルの夜間警備員
* 文体：丁寧な女性語（～です、～ます）。静かで落ち着いたトーン。
* 今日の日付：{date_str}
【条件】
* 今日の天気や季節感を反映。
* 「小さな怪異との交流」または「深夜の静かな出来事」。
* タイトルは小説のような雰囲気で。
【出力形式】
タイトル：[ここにタイトル]
[ここに本文]
"""

def main():
    if not API_KEY:
        print("Error: API Key is missing.")
        return

    os.makedirs(POSTS_DIR, exist_ok=True)

    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(MODEL_NAME)
    
    # ★★★ ここが修正ポイント ★★★
    # サーバーの時間(UTC)を取得し、9時間足して日本時間(JST)にする
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    jst_now = utc_now + datetime.timedelta(hours=9)
    today_date = jst_now.date()
    # ★★★★★★★★★★★★★★★★★

    today_str = today_date.strftime("%Y.%m.%d")
    filename_date = today_date.strftime("%Y-%m-%d")
    
    filename_only = f"diary_{filename_date}.html"
    file_path = os.path.join(POSTS_DIR, filename_only)
    link_path = f"{POSTS_DIR}/{filename_only}"

    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            index_content = f.read()
            if link_path in index_content:
                print(f"Skipping: Diary for {today_str} already exists.")
                return
    except FileNotFoundError:
        print("Error: index.html not found.")
        return

    print(f"Generating diary for {today_str} (JST)...")
    try:
        response = model.generate_content(PROMPT_DAILY.format(date_str=today_str))
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

        page_html = PAGE_TEMPLATE.format(title=title, date=today_str, body=body_html)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(page_html)
        print(f"Saved to {file_path}")

        link_card = f"""
        <article>
            <span class="date">{today_str}</span>
            <h2><a href="{link_path}" style="color:#fff; text-decoration:none;">{title}</a></h2>
            <p style="font-size:0.9em; color:#bbb;">
                {body_lines[0][:60]}... 
                <a href="{link_path}" style="color:#dac8a5; margin-left:10px;">[続きを読む]</a>
            </p>
        </article>
        """

        if INSERT_POINT in index_content:
            new_index_content = index_content.replace(INSERT_POINT, INSERT_POINT + "\n" + link_card)
            with open(INDEX_FILE, "w", encoding="utf-8") as f:
                f.write(new_index_content)
            print("Index updated successfully!")
        else:
            print("Error: Insert point not found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
