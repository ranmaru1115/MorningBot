import json
import requests

# ==========================================
# 1. 設定エリア（利用者の環境に合わせて書き換えてください）
# ==========================================
# LINE Developersの「Messaging API設定」にある長いトークンを入れてください
ACCESS_TOKEN = "YOUR_LINE_CHANNEL_ACCESS_TOKEN"

# 送信先のLINEユーザーIDまたはグループIDを入れてください（Cから始まる文字列など）
GROUP_ID = "YOUR_LINE_GROUP_ID"

# 天気を取得したい地域のコード（デフォルトは東京：130010）
# ※ご自身の地域のコードは、同梱の area_code.xml 等から各自で調べて書き換えてください
AREA_CODE = "130010"


# ==========================================
# 2. 天気予報の取得処理
# ==========================================
def get_weather_data(city_code):
    # お天気API（ライブドア天気互換API）を利用
    weather_url = f"https://weather.tsukumijima.net/api/forecast/city/{city_code}"

    try:
        response = requests.get(weather_url)
        response.raise_for_status()
        weather_data = response.json()

        title = weather_data.get("title", "お天気予報")
        forecasts = weather_data.get("forecasts", [])

        if not forecasts:
            return "天気データの取得に失敗しました（データが空です）。"

        # 今日の天気を取得
        today = forecasts[0]
        date_label = today.get("dateLabel", "今日")
        telop = today.get("telop", "不明")

        # 最高気温の取得（夜間など発表データに値がない場合の対策）
        temp_max_data = today.get("temperature", {}).get("max", {})
        temp_max = (
            temp_max_data.get("celsius")
            if temp_max_data and temp_max_data.get("celsius")
            else "--"
        )

        # メッセージ本文の組み立て
        msg = f"【{title}】\n"
        msg += f"{date_label}の天気: {telop}\n"
        msg += f"最高気温: {temp_max}度\n\n"
        msg += "今日も一日頑張りましょう！"
        msg += "※これだけを頼りにしないでね"

        return msg

    except Exception as e:
        return f"天気情報の取得中にエラーが発生しました: {e}"


# ==========================================
# 3. LINEへのメッセージ送信機能
# ==========================================
def send_line_message(text_content):
    line_url = "https://api.line.me/v2/bot/message/push"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    payload = {
        "to": GROUP_ID,
        "messages": [{"type": "text", "text": text_content}],
    }

    try:
        response = requests.post(
            line_url, headers=headers, data=json.dumps(payload)
        )

        if response.status_code == 200:
            print("🎉 LINEへの天気送信に成功しました！")
        else:
            print(f"❌ LINEからエラーが返ってきました（コード: {response.status_code}）")
            print(response.text)

    except Exception as e:
        print(f"通信エラーが発生しました: {e}")


# ==========================================
# 4. 実行
# ==========================================
if __name__ == "__main__":
    print("🌤️ 天気予報を取得中...")
    weather_message = get_weather_data(AREA_CODE)

    print("\n--- 送信内容 ---")
    print(weather_message)
    print("----------------\n")

    print("🚀 LINEへ送信します...")
    send_line_message(weather_message)
