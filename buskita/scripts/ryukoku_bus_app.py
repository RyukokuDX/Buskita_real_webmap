#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
龍谷大学バス運行アプリ
学生向けバス遅延・発車時刻確認システム
"""

import requests
import sqlite3
from datetime import datetime, timedelta
import json
import math

# 龍谷大学バス路線定義
RYUKOKU_BUS_ROUTES = {
    "瀬田駅-龍谷大学": {
        "route_id": "seta_ryukoku",
        "stops": [
            {"name": "瀬田駅", "lat": 34.9667, "lng": 135.9167},
            {"name": "龍谷大学前", "lat": 34.9456, "lng": 135.9123},
            {"name": "龍谷大学", "lat": 34.9445, "lng": 135.9134}
        ],
        "schedule": {
            "平日": ["7:30", "8:00", "8:30", "9:00", "16:30", "17:00", "17:30"],
            "土曜": ["8:00", "9:00", "16:00", "17:00"],
            "日祝": []
        }
    },
    "石山駅-龍谷大学": {
        "route_id": "ishiyama_ryukoku", 
        "stops": [
            {"name": "石山駅", "lat": 34.9667, "lng": 135.9000},
            {"name": "龍谷大学", "lat": 34.9445, "lng": 135.9134}
        ],
        "schedule": {
            "平日": ["7:45", "8:15", "8:45", "16:45", "17:15", "17:45"],
            "土曜": ["8:15", "16:45"],
            "日祝": []
        }
    }
}

class RyukokuBusApp:
    def __init__(self):
        self.api_base = "https://api.buskita.com"
        self.site_id = 9  # 滋賀帝産バス
        self.db_path = "ryukoku_bus.db"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
            'Accept': 'application/json'
        }
        self.init_database()
        
    def init_database(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # バス位置履歴テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bus_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_no INTEGER,
                latitude REAL,
                longitude REAL,
                speed REAL,
                update_time TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 遅延記録テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS delay_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_name TEXT,
                scheduled_time TEXT,
                actual_time TEXT,
                delay_minutes INTEGER,
                date DATE,
                weather TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_current_buses(self):
        """現在運行中のバスを取得"""
        # url = f"{self.api_base}/get-buses"
        # params = {'language': 1, 'siteId': self.site_id}
        
        # NOTE: get-busesは存在しないため、APIドキュメントに基づきPOSTリクエストに変更。
        #       動作確認のため、一時的に get-companies-dictionary を使用する。
        url = f"{self.api_base}/get-companies-dictionary"
        payload = {'language': 1}

        try:
            # response = requests.get(url, params=params, headers=self.headers)
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            # APIのレスポンス形式が異なるため、ここでは空のリストを返す
            # return response.json()
            print("API接続テスト成功:", response.json())
            return []
        except Exception as e:
            print(f"バス情報取得エラー: {e}")
            return []
    
    def calculate_distance(self, lat1, lng1, lat2, lng2):
        """2点間の距離を計算（km）"""
        R = 6371  # 地球の半径（km）
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lng/2) * math.sin(delta_lng/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def is_bus_at_campus(self, bus, campus_coords, threshold_km=0.2):
        """バスがキャンパス付近にいるかチェック"""
        campus_lat, campus_lng = campus_coords
        distance = self.calculate_distance(
            bus['lat'], bus['lng'], 
            campus_lat, campus_lng
        )
        return distance <= threshold_km
    
    def find_buses_near_campus(self):
        """キャンパス周辺のバスを検索"""
        buses = self.get_current_buses()
        campus_coords = (34.9445, 135.9134)  # 龍谷大学瀬田キャンパス
        
        nearby_buses = []
        for bus in buses:
            if self.is_bus_at_campus(bus, campus_coords):
                # 追加情報を計算
                distance = self.calculate_distance(
                    bus['lat'], bus['lng'],
                    campus_coords[0], campus_coords[1]
                )
                
                bus_info = bus.copy()
                bus_info['distance_to_campus'] = round(distance * 1000)  # メートル単位
                bus_info['is_stopped'] = bus.get('speed', 0) == 0
                
                nearby_buses.append(bus_info)
        
        return nearby_buses
    
    def calculate_delay(self, current_time_str, scheduled_times):
        """遅延時間を計算"""
        try:
            current_time = datetime.strptime(current_time_str, "%H:%M")
        except:
            current_time = datetime.now()
            current_time_str = current_time.strftime("%H:%M")
        
        delays = []
        for scheduled in scheduled_times:
            try:
                scheduled_dt = datetime.strptime(scheduled, "%H:%M")
                
                # 同日での時間差を計算
                time_diff_minutes = (current_time.hour * 60 + current_time.minute) - \
                                  (scheduled_dt.hour * 60 + scheduled_dt.minute)
                
                # 予定時刻から30分以内の範囲で確認
                if 0 <= time_diff_minutes <= 30:
                    delays.append({
                        'scheduled': scheduled,
                        'actual': current_time_str,
                        'delay_minutes': time_diff_minutes,
                        'status': self.get_delay_status(time_diff_minutes)
                    })
            except ValueError:
                continue
        
        return delays
    
    def get_delay_status(self, delay_minutes):
        """遅延状況を分類"""
        if delay_minutes <= 2:
            return "定刻"
        elif delay_minutes <= 5:
            return "軽微な遅延"
        elif delay_minutes <= 10:
            return "遅延"
        else:
            return "大幅遅延"
    
    def estimate_departure_time(self, bus, bus_stop_coords):
        """発車時刻を予測"""
        if self.is_bus_at_campus(bus, bus_stop_coords):
            # 停車時間の予測（平均2-3分）
            base_stop_time = 2
            
            # 速度が0の場合は停車中
            if bus.get('speed', 0) == 0:
                estimated_departure = datetime.now() + timedelta(minutes=base_stop_time)
                return estimated_departure
        
        return None
    
    def get_next_buses(self, route_name=None):
        """次のバスの時刻表"""
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        next_buses = []
        
        routes_to_check = [route_name] if route_name else RYUKOKU_BUS_ROUTES.keys()
        
        for route in routes_to_check:
            if route not in RYUKOKU_BUS_ROUTES:
                continue
                
            route_info = RYUKOKU_BUS_ROUTES[route]
            
            # 平日スケジュールを使用（実際は曜日判定が必要）
            schedule = route_info['schedule'].get('平日', [])
            
            for time_str in schedule:
                try:
                    bus_hour, bus_minute = map(int, time_str.split(':'))
                    
                    # 現在時刻より後のバスを検索
                    if bus_hour > current_hour or (bus_hour == current_hour and bus_minute > current_minute):
                        minutes_until = (bus_hour - current_hour) * 60 + (bus_minute - current_minute)
                        
                        next_buses.append({
                            'route': route,
                            'scheduled_time': time_str,
                            'minutes_until': minutes_until
                        })
                except ValueError:
                    continue
        
        # 時間順にソート
        next_buses.sort(key=lambda x: x['minutes_until'])
        return next_buses
    
    def save_bus_position(self, bus):
        """バス位置をデータベースに保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bus_history 
            (work_no, latitude, longitude, speed, update_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            bus.get('workNo'),
            bus.get('lat'),
            bus.get('lng'),
            bus.get('speed'),
            bus.get('updateTime')
        ))
        
        conn.commit()
        conn.close()
    
    def get_campus_bus_status(self):
        """キャンパスバス状況の総合情報"""
        campus_buses = self.find_buses_near_campus()
        next_buses = self.get_next_buses()
        
        # 遅延状況を計算
        current_time = datetime.now().strftime("%H:%M")
        delay_info = {}
        
        for route_name, route_info in RYUKOKU_BUS_ROUTES.items():
            scheduled_times = route_info['schedule'].get('平日', [])
            delays = self.calculate_delay(current_time, scheduled_times)
            if delays:
                delay_info[route_name] = delays
        
        return {
            'campus_buses': campus_buses,
            'next_buses': next_buses[:5],  # 次の5本
            'delay_info': delay_info,
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

def main():
    """メイン関数 - デモ実行"""
    app = RyukokuBusApp()
    
    print("🚌 龍谷大学バス運行情報システム")
    print("=" * 50)
    
    # 総合状況を取得
    status = app.get_campus_bus_status()
    
    # キャンパス内バス
    print("\n🏫 キャンパス内バス:")
    if status['campus_buses']:
        for bus in status['campus_buses']:
            print(f"  バス {bus['workNo']}")
            print(f"    位置: ({bus['lat']:.4f}, {bus['lng']:.4f})")
            print(f"    キャンパスまで: {bus['distance_to_campus']}m")
            print(f"    状態: {'停車中' if bus['is_stopped'] else '走行中'}")
            print(f"    速度: {bus.get('speed', 0)} km/h")
    else:
        print("  現在キャンパス内にバスはありません")
    
    # 次のバス
    print("\n🕐 次のバス:")
    for bus in status['next_buses']:
        print(f"  {bus['route']}: {bus['scheduled_time']} ({bus['minutes_until']}分後)")
    
    # 遅延情報
    print("\n⏰ 遅延状況:")
    if status['delay_info']:
        for route, delays in status['delay_info'].items():
            print(f"  {route}:")
            for delay in delays:
                print(f"    {delay['scheduled']} → {delay['actual']} ({delay['status']}, {delay['delay_minutes']}分遅延)")
    else:
        print("  現在遅延情報はありません")
    
    print(f"\n最終更新: {status['last_updated']}")

if __name__ == "__main__":
    main() 