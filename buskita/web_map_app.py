import requests
from flask import Flask, jsonify, render_template
from datetime import datetime
import json
import os
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# --- グローバル定数 ---
API_BASE_URL = "https://api.buskita.com"
SITE_ID = 9
BACKUP_FILE = 'archive/last_known_buses.json'
HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'
}

# --- 補助関数 ---
def group_schedules_by_hour(schedules):
    """
    時刻オブジェクトのリストを時間ごとにグループ化する
    [{'time': '07:30', 'is_direct': True}] -> [('7', ['30(直)'])]
    """
    grouped = {}
    if not schedules:
        return [] # 空のリストを返す
    for schedule_item in schedules:
        try:
            time_str = schedule_item['time']
            is_direct = schedule_item['is_direct']
            hour, minute = time_str.split(':')
            hour_key = str(int(hour))

            if hour_key not in grouped:
                grouped[hour_key] = []
            
            display_minute = f"{minute}(直)" if is_direct else minute
            grouped[hour_key].append(display_minute)

        except (ValueError, KeyError):
            continue
    
    # 時間でソートしたタプルのリストを返す
    return sorted(grouped.items(), key=lambda item: int(item[0]))

def filter_and_format_buses(bus_list):
    """バスのリストを受け取り、位置情報があるものだけを抽出・整形する"""
    locations = []
    if not bus_list:
        return locations
    for bus in bus_list:
        if bus and 'position' in bus and 'latitude' in bus['position'] and 'longitude' in bus['position']:
            try:
                # 行き先情報は routeNames の '1' から取得する
                dest_name = bus.get('routeNames', {}).get('1', '情報なし')
                
                locations.append({
                    'id': bus.get('workNo'),
                    'lat': float(bus['position']['latitude']),
                    'lng': float(bus['position']['longitude']),
                    'dest': dest_name,
                    'delayMinutes': bus.get('delayMinutes', 0),
                    'passenger': bus.get('passenger', 0)
                })
            except (ValueError, TypeError):
                continue
    return locations

def get_bus_details(work_no):
    """個別のバスの詳細情報を取得する"""
    try:
        endpoint = f"{API_BASE_URL}/get-bus"
        payload = {"language": 1, "workNo": str(work_no), "siteId": SITE_ID}
        response = requests.post(endpoint, json=payload, headers=HEADERS, timeout=3)
        if response.status_code == 200:
            buses = response.json().get('bus', [])
            if buses:
                return buses[0]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching details for workNo {work_no}: {e}")
    return None

def get_live_bus_data():
    """運行中の全バスの位置情報と詳細情報を取得する"""
    try:
        # 1. 全バスの位置情報を取得
        endpoint = f"{API_BASE_URL}/get-buses"
        payload = {"language": 1, "siteId": SITE_ID}
        response = requests.post(endpoint, json=payload, headers=HEADERS, timeout=5)
        response.raise_for_status()
        
        buses_with_location = response.json().get('buses', [])
        if not buses_with_location:
            return []

        # 2. 各バスの詳細情報を並行して取得
        detailed_buses = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_work_no = {executor.submit(get_bus_details, bus.get('workNo')): bus.get('workNo') for bus in buses_with_location}
            
            for future in future_to_work_no:
                work_no = future_to_work_no[future]
                detail = future.result()
                if detail:
                    detailed_buses[work_no] = detail
        
        # 3. 位置情報と詳細情報をマージ
        merged_buses = []
        for bus in buses_with_location:
            work_no = bus.get('workNo')
            if work_no in detailed_buses:
                bus.update(detailed_buses[work_no])
            merged_buses.append(bus)

        if merged_buses:
            os.makedirs(os.path.dirname(BACKUP_FILE), exist_ok=True)
            with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
                json.dump(merged_buses, f, ensure_ascii=False, indent=2)
        
        return merged_buses
        
    except requests.exceptions.RequestException as e:
        print(f"APIリクエストエラー (get-buses): {e}")
        # APIが不調の場合、バックアップから読み込む
        if os.path.exists(BACKUP_FILE):
            print("バックアップからデータを読み込みます。")
            with open(BACKUP_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

# --- Flask ルート定義 ---

@app.route('/')
def index():
    """メインのマップページ"""
    return render_template('index.html')

@app.route('/api/bus_locations')
def api_bus_locations():
    """バスの位置情報を返すAPI"""
    locations_raw = get_live_bus_data()
    is_stale = False # APIからのデータが古い場合にTrueになるフラグ

    # APIからのデータ取得に失敗した場合
    if not locations_raw:
        print(f"[{datetime.now()}] APIから有効なデータが取得できませんでした。バックアップを試みます。")
        if os.path.exists(BACKUP_FILE):
            try:
                with open(BACKUP_FILE, 'r', encoding='utf-8') as f:
                    locations_raw = json.load(f)
                is_stale = True
                print(f"[{datetime.now()}] バックアップファイルを使用しました。")
            except (json.JSONDecodeError, IOError) as e:
                print(f"バックアップファイルの読み込みに失敗しました: {e}")
                locations_raw = [] # バックアップも失敗した場合は空リスト
        else:
            print(f"[{datetime.now()}] バックアップファイルが見つかりませんでした。")

    # フィルタリングと整形
    locations = filter_and_format_buses(locations_raw)
    
    if not is_stale:
        print(f"[{datetime.now()}] APIから {len(locations)} 台の有効なバス情報を取得しました。")

    return jsonify({
        'buses': locations,
        'is_stale': is_stale
    })

@app.route('/timetable')
def timetable_page():
    """時刻表ページを表示する"""
    try:
        with open('static/timetable.json', 'r', encoding='utf-8') as f:
            raw_timetable_data = json.load(f)

        timetable_data = {}
        for route_id, data in raw_timetable_data.items():
            processed_schedules = {}
            for day, times in data.get('schedules', {}).items():
                processed_schedules[day] = group_schedules_by_hour(times)
            
            timetable_data[route_id] = {
                'routeName': data['routeName'],
                'schedules': processed_schedules
            }
            
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading timetable: {e}")
        timetable_data = {}
        
    return render_template('timetable.html', timetable_data=timetable_data)


@app.route('/api/landmarks')
def api_landmarks():
    """固定のランドマーク情報を返す"""
    landmarks = [
        {
            "name": "龍谷大学 瀬田キャンパス",
            "lat": 34.964307,
            "lng": 135.939629,
            "type": "university"
        },
        {
            "name": "JR瀬田駅",
            "lat": 34.986964, 
            "lng": 135.925364,
            "type": "station"
        }
    ]
    return jsonify(landmarks)

@app.route('/api/timetable_data')
def api_timetable_data():
    """静的な時刻表JSONをそのまま返す"""
    try:
        with open('static/timetable.json', 'r', encoding='utf-8') as f:
            timetable_data = json.load(f)
        return jsonify(timetable_data)
    except Exception as e:
        print(f"Error serving timetable json: {e}")
        return jsonify({}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 