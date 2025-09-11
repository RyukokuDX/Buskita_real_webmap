# 外部APIとの通信や、取得したデータの加工など、アプリケーションのビジネスロジックを担当するファイルです。
# routes.py から呼び出されて、具体的な処理を実行します。

import requests
import json
import os
from concurrent.futures import ThreadPoolExecutor
from flask import current_app

# --- データ整形・補助関数 ---

def group_schedules_by_hour(schedules):
    """
    時刻オブジェクトのリストを時間ごとにグループ化するヘルパー関数。
    例: [{'time': '07:30', 'is_direct': True}] -> [('7', ['30(直)'])]
    """
    # ... (関数の実装は省略)
    # ...
    return sorted(grouped.items(), key=lambda item: int(item[0]))

def filter_and_format_buses(bus_list):
    """
    APIから取得したバスのリストから、必要な情報（緯度経度、行き先など）だけを抽出し、
    フロントエンドで使いやすい形式に整形する関数。
    """
    # ... (関数の実装は省略)
    # ...
    return locations

# --- 外部API連携関数 ---

def get_bus_details(work_no, api_base_url, site_id, headers):
    """
    個別のバスの詳細情報をAPIから取得します。
    get_live_bus_data内で、並列処理される個々のタスクです。
    """
    try:
        endpoint = f"{api_base_url}/get-bus"
        payload = {"language": 1, "workNo": str(work_no), "siteId": site_id}
        response = requests.post(endpoint, json=payload, headers=headers, timeout=3)
        if response.status_code == 200:
            buses = response.json().get('bus', [])
            if buses:
                return buses[0]
    except requests.exceptions.RequestException as e:
        # APIリクエストでエラーが発生した場合は、エラーログを記録します。
        current_app.logger.error(f"Error fetching details for workNo {work_no}: {e}")
    return None

def get_live_bus_data():
    """
    運行中の全バスの位置情報と詳細情報を取得する、このアプリケーションのコア機能。
    """
    try:
        # 0. アプリケーションコンテキストから設定値を変数に読み込みます。
        #    (スレッドに渡すために必要)
        api_base_url = current_app.config['API_BASE_URL']
        site_id = current_app.config['SITE_ID']
        headers = current_app.config['HEADERS']
        backup_file = current_app.config['BACKUP_FILE']

        # 1. まず、全バスの基本情報（位置情報など）を取得します。
        endpoint = f"{api_base_url}/get-buses"
        payload = {"language": 1, "siteId": site_id}
        response = requests.post(endpoint, json=payload, headers=headers, timeout=5)
        response.raise_for_status() # HTTPエラーがあれば例外を発生させます。
        
        buses_with_location = response.json().get('buses', [])
        if not buses_with_location:
            return []

        # 2. 次に、各バスの詳細情報（行き先など）を並列で取得し、処理を高速化します。
        detailed_buses = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            # get_bus_details関数に、必要な設定値を引数として渡します。
            future_to_work_no = {
                executor.submit(get_bus_details, bus.get('workNo'), api_base_url, site_id, headers): bus.get('workNo') 
                for bus in buses_with_location
            }
            
            for future in future_to_work_no:
                work_no = future_to_work_no[future]
                detail = future.result()
                if detail:
                    detailed_buses[work_no] = detail
        
        # 3. 最後に、基本情報と詳細情報をマージ（結合）します。
        merged_buses = []
        for bus in buses_with_location:
            work_no = bus.get('workNo')
            if work_no in detailed_buses:
                bus.update(detailed_buses[work_no])
            merged_buses.append(bus)

        # 取得した最新のバス情報をバックアップファイルとして保存します。
        if merged_buses:
            os.makedirs(os.path.dirname(backup_file), exist_ok=True)
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(merged_buses, f, ensure_ascii=False, indent=2)
        
        return merged_buses
        
    except requests.exceptions.RequestException as e:
        # メインのAPIリクエストが失敗した場合のフォールバック処理。
        current_app.logger.error(f"APIリクエストエラー (get-buses): {e}")
        backup_file = current_app.config['BACKUP_FILE']
        if os.path.exists(backup_file):
            # バックアップファイルが存在すれば、そこからデータを読み込みます。
            current_app.logger.info("バックアップからデータを読み込みます。")
            with open(backup_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
