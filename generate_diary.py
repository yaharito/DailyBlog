import os
import datetime
import google.generativeai as genai

# 設定
API_KEY = os.environ.get("GEMINI_API_KEY")
TARGET_FILE = "index.html"
# ★ここを変更しました：新しい目印の定義
INSERT_POINT = '<div id="entry-point" style="display:none;"></div>'

# --- プロンプト定義 ---
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
2. 自己紹介。なぜ書き始めたか。
3. 読者への控えめな挨拶。
【出力形式】
タイトル：[ここにタイトル]
[ここに本文]
"""

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
        print("API Key is missing.")
        return

    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    today = datetime.date.today().strftime("%Y.%m.%d")

    try:
        with open(TARGET_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: index.html not found.")
        return

    # 記事が存在するかチェック
    if "<article>" not in content:
        print("First post detected.")
        target_prompt = PROMPT_INTRO
    else:
        print("Daily post detected.")
        target_prompt = PROMPT_DAILY

    try:
        response = model.generate_content(target_prompt.format(date_str=today))
        text = response.text.strip().split("\n")
        
        title = text[0].replace("タイトル：", "").replace("TITLE:", "").strip()
        body_lines = [line for line in text[1:] if line.strip()]
        body_html = "<br>".join(body_lines)

        # 新しい記事のブロック
        new_entry = f"""
        <article>
            <span class="date">{today}</span>
            <h2>{title}</h2>
            <p>{body_html}</p>
            <div class="signature">アカリ</div>
        </article>
        """
        
        # ★目印の直前に記事を挿入し、目印自体も残す
        if INSERT_POINT in content:
            new_content = content.replace(INSERT_POINT, new_entry + "\n" + INSERT_POINT)
            with open(TARGET_FILE, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("Blog updated successfully!")
        else:
            print("Error: Insert point div not found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
