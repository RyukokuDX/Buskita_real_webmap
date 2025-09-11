import requests
import json
import time
from datetime import datetime


def monitor_buses():
    """リアルタイムバス監視"""
    url = "https://api.buskita.com/get-buses"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ja",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
    }

    # 複数のサイトIDを監視
    sites_to_monitor = [1, 3, 9, 12, 15]  # 主要サイト

    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{timestamp} - バス監視中...")

        total_buses = 0
        for site_id in sites_to_monitor:
            try:
                response = requests.post(
                    url, headers=headers, json={
                        "language": 1, "siteId": site_id}
                )

                if response.status_code == 200:
                    data = response.json()
                    buses = data.get("buses", [])
                    bus_count = len(buses)
                    total_buses += bus_count

                    if bus_count > 0:
                        print(f"🚌 サイト{site_id}: {bus_count}台運行中")

                        # バス詳細を記録
                        filename = f'active_buses_site{site_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                        with open(filename, "w", encoding="utf-8") as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        print(f"   データ保存: {filename}")
                    else:
                        print(f"📍 サイト{site_id}: 0台")

                time.sleep(1)  # サイト間の間隔

            except Exception as e:
                print(f"❌ サイト{site_id}でエラー: {e}")

        print(f"合計: {total_buses}台")

        if total_buses > 0:
            print("🎯 運行中のバス発見！監視を継続します...")

        time.sleep(30)  # 30秒間隔で監視


if __name__ == "__main__":
    monitor_buses()
