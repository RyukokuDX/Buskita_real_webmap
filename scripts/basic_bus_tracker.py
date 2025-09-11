#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本的なバス追跡アプリ
チュートリアル用のサンプルコード
"""

import requests
import json
import time
from datetime import datetime

class SimpleBusTracker:
    def __init__(self):
        self.base_url = "https://api.buskita.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
            'Accept': 'application/json'
        }
    
    def get_active_buses(self, site_id=9):
        """全アクティブバスを取得"""
        url = f"{self.base_url}/get-buses"
        params = {'language': 1, 'siteId': site_id}
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"エラー: {e}")
            return None
    
    def track_bus(self, work_no, site_id=9):
        """特定バスの位置を追跡"""
        url = f"{self.base_url}/get-bus"
        params = {
            'language': 1,
            'siteId': site_id,
            'workNo': work_no
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                bus = data[0]
                print(f"バス {work_no}:")
                print(f"  位置: ({bus['lat']}, {bus['lng']})")
                print(f"  更新時刻: {bus['updateTime']}")
                print(f"  速度: {bus.get('speed', 'N/A')} km/h")
                print(f"  方向: {bus.get('direction', 'N/A')}°")
                
            return data
        except Exception as e:
            print(f"エラー: {e}")
            return None
    
    def get_companies(self):
        """バス会社一覧を取得"""
        url = f"{self.base_url}/get-companies-dictionary"
        params = {'language': 1, 'siteId': 1}
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"エラー: {e}")
            return None
    
    def continuous_tracking(self, work_no, site_id=9, interval=30):
        """継続的なバス追跡"""
        print(f"バス {work_no} の継続追跡を開始します（{interval}秒間隔）")
        print("Ctrl+C で停止")
        
        try:
            while True:
                print(f"\n--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
                self.track_bus(work_no, site_id)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n追跡を停止しました")

def main():
    """メイン関数"""
    tracker = SimpleBusTracker()
    
    print("=== バス追跡アプリ ===")
    
    # バス会社一覧を表示
    print("\n1. バス会社情報を取得中...")
    companies = tracker.get_companies()
    if companies:
        print(f"登録バス会社数: {len(companies)}")
        for company in companies[:5]:  # 最初の5社を表示
            print(f"  - {company.get('name', 'N/A')} (ID: {company.get('siteId', 'N/A')})")
    
    # アクティブなバスを取得（滋賀帝産バス）
    print("\n2. アクティブなバスを取得中...")
    buses = tracker.get_active_buses(site_id=9)
    if buses:
        print(f"アクティブなバス数: {len(buses)}")
        
        # 最初のバスの詳細を表示
        if len(buses) > 0:
            print("\n3. 最初のバスの位置を追跡:")
            work_no = buses[0]['workNo']
            tracker.track_bus(work_no, site_id=9)
            
            # 継続追跡の選択
            choice = input(f"\nバス {work_no} を継続追跡しますか？ (y/N): ")
            if choice.lower() == 'y':
                tracker.continuous_tracking(work_no, site_id=9)
    else:
        print("現在アクティブなバスがありません")

if __name__ == "__main__":
    main() 