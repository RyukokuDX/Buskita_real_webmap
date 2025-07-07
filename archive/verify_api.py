import requests
from datetime import datetime

API_BASE_URL = "https://api.buskita.com"
HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'
}

def check_live_buses(site_id):
    """指定されたsiteIdで運行中のバスを確認"""
    endpoint = f"{API_BASE_URL}/get-buses"
    payload = {"language": 1, "siteId": site_id}
    try:
        response = requests.post(endpoint, json=payload, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return len(data.get('buses', []))
        else:
            return -1 # -1はHTTPエラーを示す
    except requests.exceptions.RequestException:
        return -2 # -2はリクエスト自体のエラーを示す

def main():
    print("🚌 buskita.com APIの有効性 再検証を開始します...")
    print(f"検証時刻: {datetime.now()}")
    print("ユーザー様の「バスは実際に動いている」とのご指摘に基づき、全サイトIDを徹底的に調査します。")
    print("="*60)

    results = {}
    # サイトID 1から25までを調査
    site_ids_to_check = range(1, 26) 

    for site_id in site_ids_to_check:
        print(f"調査中... siteId: {site_id}", end='\r')
        num_buses = check_live_buses(site_id)
        results[site_id] = num_buses
        
    print("\n\n--- 検証結果 ---")
    
    found_buses_count = sum(1 for v in results.values() if v > 0)
    
    if found_buses_count > 0:
        print("✅ APIは正常に稼働しており、運行情報を返しているサイトIDが複数見つかりました。")
        print("バスが運行中のサイトID:")
        for sid, count in results.items():
            if count > 0:
                print(f"  - siteId: {sid} ({count}台)")
    else:
        print("❌ 現在、調査した全てのサイトIDで運行中のバスが1台も取得できませんでした。")

    print("\n--- 滋賀エリア(siteId: 9)についての分析 ---")
    shiga_buses = results.get(9, -1)
    if shiga_buses == 0:
        print("現在、APIは siteId: 9 (滋賀エリア) にて「運行バス0台」と応答しています。")
        print("ユーザー様のご指摘通りバスが動いている場合、APIが滋賀エリアの情報を正しく返していない可能性があります。")
    elif shiga_buses > 0:
         print(f"✅【朗報】siteId: 9 (滋賀エリア)で {shiga_buses} 台のバスが捕捉できました！")
         print("Webアプリを再起動すれば、今度はバスが表示されるはずです。")
    else:
        print("❌ siteId: 9 (滋賀エリア)のデータ取得時にエラーが発生しました。")


if __name__ == "__main__":
    main() 