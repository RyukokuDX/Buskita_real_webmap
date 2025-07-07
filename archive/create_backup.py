import requests
import json
import time
from datetime import datetime

API_BASE_URL = "https://api.buskita.com"
SITE_ID = 9
BACKUP_FILE = 'buskita/last_known_buses.json'
HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'
}

def create_initial_backup():
    """
    APIからバス情報を取得できるまで繰り返し試行し、
    成功したらバックアップファイルを作成する。
    """
    print("🚌 バス情報バックアップファイルの作成を開始します。")
    print("APIが正常な応答を返すまで、最大5分間試行します...")

    max_retries = 30  # 10秒ごと * 30回 = 300秒 (5分)
    for i in range(max_retries):
        try:
            print(f"[{i+1}/{max_retries}] APIに問い合わせ中...")
            endpoint = f"{API_BASE_URL}/get-buses"
            payload = {"language": 1, "siteId": SITE_ID}
            response = requests.post(endpoint, json=payload, headers=HEADERS, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                buses = data.get('buses', [])
                
                if len(buses) > 0:
                    print(f"\n✅【成功】{len(buses)}台のバス情報を捕捉しました！")
                    
                    # 必要な情報のみを抽出
                    bus_locations = []
                    for bus in buses:
                        if 'lat' in bus and 'lng' in bus:
                            bus_locations.append({
                                'id': bus.get('workNo'),
                                'lat': bus.get('lat'),
                                'lng': bus.get('lng'),
                                'name': bus.get('r_name'),
                                'speed': bus.get('speed'),
                                'updated_at': bus.get('updateTime')
                            })
                            
                    with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
                        json.dump(bus_locations, f, ensure_ascii=False, indent=2)
                    
                    print(f"バックアップファイルを作成しました: {BACKUP_FILE}")
                    return True
            
            # 10秒待機して再試行
            time.sleep(10)

        except requests.exceptions.RequestException as e:
            print(f"リクエストエラーが発生しました: {e}")
            time.sleep(10)

    print("\n❌ 5分以内に有効なバス情報を取得できませんでした。")
    return False

if __name__ == "__main__":
    create_initial_backup() 