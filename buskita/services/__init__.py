import requests
import json
import os
from concurrent.futures import ThreadPoolExecutor
from flask import current_app

# --- 補助関数 (データ処理) ---

def group_schedules_by_hour(schedules):
    """
    時刻オブジェクトのリストを時間ごとにグループ化する
    """
    # ... (内容は web_map_app.py からそのままコピー)
    grouped = {}
    if not schedules:
        return []
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
    
    return sorted(grouped.items(), key=lambda item: int(item[0]))

def filter_and_format_buses(bus_list):
    """バスのリストを受け取り、位置情報があるものだけを抽出・整形する"""
    locations = []
    if not bus_list:
        return locations
    for bus in bus_list:
        if bus and 'position' in bus and 'latitude' in bus['position'] and 'longitude' in bus['position']:
            try:
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

# --- 外部API連携 ---

def get_bus_details(work_no, api_base_url, site_id, headers):
    """個別のバスの詳細情報を取得する"""
    try:
        endpoint = f"{api_base_url}/get-bus"
        payload = {"language": 1, "workNo": str(work_no), "siteId": site_id}
        response = requests.post(endpoint, json=payload, headers=headers, timeout=3)
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
        # 0. 設定値を変数に読み込む
        api_base_url = current_app.config['API_BASE_URL']
        site_id = current_app.config['SITE_ID']
        headers = current_app.config['HEADERS']
        backup_file = current_app.config['BACKUP_FILE']

        # 1. 全バスの位置情報を取得
        endpoint = f"{api_base_url}/get-buses"
        payload = {"language": 1, "siteId": site_id}
        response = requests.post(endpoint, json=payload, headers=headers, timeout=5)
        response.raise_for_status()
        
        buses_with_location = response.json().get('buses', [])
        if not buses_with_location:
            return []

        # 2. 各バスの詳細情報を並行して取得
        detailed_buses = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_work_no = {
                executor.submit(get_bus_details, bus.get('workNo'), api_base_url, site_id, headers): bus.get('workNo') 
                for bus in buses_with_location
            }
            
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
            os.makedirs(os.path.dirname(backup_file), exist_ok=True)
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(merged_buses, f, ensure_ascii=False, indent=2)
        
        return merged_buses
        
    except requests.exceptions.RequestException as e:
        print(f"APIリクエストエラー (get-buses): {e}")
        backup_file = current_app.config['BACKUP_FILE']
        if os.path.exists(backup_file):
            print("バックアップからデータを読み込みます。")
            with open(backup_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
