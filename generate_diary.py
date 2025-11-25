import os
import datetime
import google.generativeai as genai

# 設定
API_KEY = os.environ.get("GEMINI_API_KEY")
TARGET_FILE = "index.html"

# アカリさんのプロンプト
PROMPT = """
あなたは「アカリ」というキャラクターになりきって、今日の日記を書いてください。

【キャラクター設定】
* 名前：アカリ（24歳・女性）
* 職業：オフィスビルの夜間警備員
* 性格：おっとりしているが芯は強い。
* 世界観：怪異が日常に溶け込んでいる世界。
* 文体：丁寧な女性語（～です、～ます）。静かで落ち着いたトーン。
* 今日の日付：{date_str}

【条件】
* 今日の天気や季節感を反映してください。
* 「小さな怪異との交流」または「深夜の静かな出来事」を含めてください。
* タイトルは小説のような雰囲気でつけてください。
* 最初の行にタイトル、次の行から本文を書いてください。
"""

def main():
    if not API_KEY:
        print("API Key is missing.")
        return

    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    today = datetime.date.today().strftime("%Y.%m.%d")

    try:
        response = model.generate_content(PROMPT.format(date_str=today))
        text = response.text.strip().split("\n")
        title = text[0].replace("タイトル：", "").strip()
        body_lines = [line for line in text[1:] if line.strip()]
        body_html = "<br>".join(body_lines)

        new_entry = f"""
        <article>
            <span class="date">{today}</span>
            <h2>{title}</h2>
            <p>{body_html}</p>
            <div class="signature">アカリ</div>
        </article>
        """

        with open(TARGET_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        if "" in content:
            new_content = content.replace("", new_entry)
            with open(TARGET_FILE, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("Diary updated!")
        else:
            print("Error: Anchor point not found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
