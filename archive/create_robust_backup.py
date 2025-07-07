import requests
import json
import time

API_BASE_URL = "https://api.buskita.com"
SITE_ID = 9
BACKUP_FILE = 'buskita/last_known_buses.json'
HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'
}

def create_robust_backup():
    """
    APIからバス情報を取得できるまで繰り返し試行し、
    成功したら、フィルタリングせずに生のバス情報をバックアップする。
    """
    print("🚌 堅牢なバス情報バックアップ作成を開始します。")
    print("APIが有効な応答を返すまで最大5分間試行します...")

    max_retries = 30
    for i in range(max_retries):
        try:
            print(f"[{i+1}/{max_retries}] APIに問い合わせ中...")
            endpoint = f"{API_BASE_URL}/get-buses"
            payload = {"language": 1, "siteId": SITE_ID}
            response = requests.post(endpoint, json=payload, headers=HEADERS, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                buses = data.get('buses', [])
                
                # デバッグ用に生のAPI応答の一部を表示
                print("\n--- RAW API RESPONSE (first 3 buses) ---")
                print(json.dumps(buses[:3], ensure_ascii=False, indent=2))
                print("---------------------------------------\n")
                
                if len(buses) > 0:
                    print(f"✅【成功】{len(buses)}台のバス情報を捕捉しました！")
                    
                    with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
                        # フィルタリングせず、生のバス情報リストを保存
                        json.dump(buses, f, ensure_ascii=False, indent=2)
                    
                    print(f"生のバス情報を含むバックアップファイルを作成しました: {BACKUP_FILE}")
                    return True
            
            time.sleep(10)
        except requests.exceptions.RequestException as e:
            print(f"リクエストエラー: {e}")
            time.sleep(10)

    print("\n❌ 5分以内に有効なバス情報を取得できませんでした。")
    return False

if __name__ == "__main__":
    create_robust_backup() 