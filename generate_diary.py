import os
import datetime
import google.generativeai as genai

# 設定
API_KEY = os.environ.get("GEMINI_API_KEY")
TARGET_FILE = "index.html"

# --- プロンプト定義 ---

# 【A】初回用：自己紹介のプロンプト
PROMPT_INTRO = """
あなたは「アカリ」というキャラクターになりきって、ブログの記念すべき「第1回目の記事」を書いてください。

【キャラクター設定】
* 名前：アカリ（24歳・女性）
* 職業：オフィスビルの夜間警備員
* 性格：おっとりしているが芯は強い。
* 世界観：怪異が日常に溶け込んでいる世界。
* 文体：丁寧な女性語（～です、～ます）。静かで落ち着いたトーン。
* 今日の日付：{date_str}

【内容】
1. タイトルは「夜勤警備員の日誌、はじめます」のような始まりを感じさせるもの。
2. 自己紹介（夜の警備員であること）。
3. なぜこの日記を書き始めたのか（夜の不思議な出来事を忘れないため、等）。
4. 読者への控えめな挨拶。

【出力形式】
タイトル：[ここにタイトル]
[ここに本文]
"""

# 【B】2回目以降用：通常の日記プロンプト
PROMPT_DAILY = """
あなたは「アカリ」というキャラクターになりきって、今日の日記を書いてください。

【キャラクター設定】
* 名前：アカリ（24歳・女性）
* 職業：オフィスビルの夜間警備員
* 文体：丁寧な女性語（～です、～ます）。静かで落ち着いたトーン。
* 今日の日付：{date_str}

【条件】
* 今日の天気や季節感を反映してください。
* 「小さな怪異との交流」または「深夜の静かな出来事」を含めてください。
* タイトルは小説のような雰囲気でつけてください。

【出力形式】
タイトル：[ここにタイトル]
[ここに本文]
"""

def main():
    if not API_KEY:
        print("API Key is missing.")
        return

    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    today = datetime.date.today().strftime("%Y.%m.%d")

    # --- 1. HTMLを読んで、初回かどうか判断する ---
    try:
        with open(TARGET_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: index.html not found.")
        return

    # <article>タグがまだ無ければ「初回」と判断
    if "<article>" not in content:
        print("First post detected. Generating Self-Introduction...")
        target_prompt = PROMPT_INTRO
    else:
        print("Existing posts detected. Generating Daily Diary...")
        target_prompt = PROMPT_DAILY

    # --- 2. Geminiで生成 ---
    try:
        response = model.generate_content(target_prompt.format(date_str=today))
        text = response.text.strip().split("\n")
        
        # タイトルと本文の抽出（"タイトル："の文字を除去）
        title = text[0].replace("タイトル：", "").replace("TITLE:", "").strip()
        body_lines = [line for line in text[1:] if line.strip()]
        body_html = "<br>".join(body_lines)

        # HTML整形
        new_entry = f"""
        <article>
            <span class="date">{today}</span>
            <h2>{title}</h2>
            <p>{body_html}</p>
            <div class="signature">アカリ</div>
        </article>
        """

        # --- 3. 保存 ---
        if "" in content:
            new_content = content.replace("", new_entry)
            with open(TARGET_FILE, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("Blog updated successfully!")
        else:
            print("Error: Anchor point not found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
