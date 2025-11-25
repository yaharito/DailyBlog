import os
import datetime
import google.generativeai as genai
import time

# 設定
API_KEY = os.environ.get("GEMINI_API_KEY")
TARGET_FILE = "index.html"
# 目印（CSSで隠したdivタグ）
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
        print("Error: API Key is missing.")
        return

    # API設定
    genai.configure(api_key=API_KEY)
    
    # ★修正点：モデル名をより確実なものに変更しました
    # もしこれでもエラーが出る場合は "gemini-pro" に変更してください
    model = genai.GenerativeModel("gemini-1.5-flash-latest") 

    today = datetime.date.today().strftime("%Y.%m.%d")

    try:
        # ファイル読み込み
        with open(TARGET_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: index.html not found.")
        return

    # 初回判定
    if "<article>" not in content:
        print("First post detected.")
        target_prompt = PROMPT_INTRO
    else:
        print("Daily post detected.")
        target_prompt = PROMPT_DAILY

    # 生成実行（エラーハンドリング強化）
    try:
        response = model.generate_content(target_prompt.format(date_str=today))
        
        # 応答が空でないか確認
        if not response.text:
            print("Error: Response text is empty.")
            return

        text = response.text.strip().split("\n")
        
        # タイトルと本文の抽出
        title = "無題"
        body_lines = []
        
        # 簡易的な解析ロジック
        for line in text:
            if line.startswith("タイトル：") or line.startswith("TITLE:"):
                title = line.replace("タイトル：", "").replace("TITLE:", "").strip()
            else:
                if line.strip(): # 空行以外を追加
                    body_lines.append(line)
        
        # タイトルが抽出できなかった場合の保険（1行目をタイトルにする）
        if title == "無題" and len(body_lines) > 0:
             title = body_lines.pop(0)

        body_html = "<br>".join(body_lines)

        # 記事ブロック作成
        new_entry = f"""
        <article>
            <span class="date">{today}</span>
            <h2>{title}</h2>
            <p>{body_html}</p>
            <div class="signature">アカリ</div>
        </article>
        """
        
        # 挿入処理
        if INSERT_POINT in content:
            new_content = content.replace(INSERT_POINT, new_entry + "\n" + INSERT_POINT)
            with open(TARGET_FILE, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("Blog updated successfully!")
        else:
            print(f"Error: Insert point '{INSERT_POINT}' not found in index.html.")
            # デバッグ用にファイル内容の一部を表示
            print(f"File content start: {content[:100]}...")

    except Exception as e:
        print(f"Generative AI Error: {e}")

if __name__ == "__main__":
    main()
