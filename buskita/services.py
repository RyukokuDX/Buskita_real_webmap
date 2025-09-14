# 外部APIとの通信や、取得したデータの加工など、アプリケーションのビジネスロジックを担当するファイルです。
# routes.py から呼び出されて、具体的な処理を実行します。

import requests
import json
import os
from concurrent.futures import ThreadPoolExecutor
from flask import current_app
# __init__.py で作成したグローバルなキャッシュインスタンスをインポート
from buskita import cache

# --- データ整形・補助関数 ---


def group_schedules_by_hour(schedules):
    """
    時刻オブジェクトのリストを時間ごとにグループ化するヘルパー関数。
    例: [{'time': '07:30', 'is_direct': True}] -> [('7', ['30(直)'])]
    """
    grouped = {}
    if not schedules:
        return []
    for schedule_item in schedules:
        try:
            time_str = schedule_item["time"]
            is_direct = schedule_item["is_direct"]
            hour, minute = time_str.split(":")
            hour_key = str(int(hour))

            if hour_key not in grouped:
                grouped[hour_key] = []

            display_minute = f"{minute}(直)" if is_direct else minute
            grouped[hour_key].append(display_minute)

        except (ValueError, KeyError):
            continue

    return sorted(grouped.items(), key=lambda item: int(item[0]))


def filter_and_format_buses(bus_list):
    """
    APIから取得したバスのリストから、必要な情報（緯度経度、行き先など）だけを抽出し、
    フロントエンドで使いやすい形式に整形する関数。
    """
    locations = []
    if not bus_list:
        return locations
    for bus in bus_list:
        if (
            bus
            and "position" in bus
            and "latitude" in bus["position"]
            and "longitude" in bus["position"]
        ):
            try:
                # 行き先情報は routeNames の '1' から取得する
                dest_name = bus.get("routeNames", {}).get("1", "情報なし")

                locations.append(
                    {
                        "id": bus.get("workNo"),
                        "lat": float(bus["position"]["latitude"]),
                        "lng": float(bus["position"]["longitude"]),
                        "dest": dest_name,
                        "delayMinutes": bus.get("delayMinutes", 0),
                        "passenger": bus.get("passenger"),
                    }
                )
            except (ValueError, TypeError):
                continue
    return locations


# --- 外部API連携関数 ---


def get_buses_from_cache():
    """
    キャッシュからバスの生データを取得する。
    API通信は行わない。
    """
    return cache.get('live_bus_data') or []


def fetch_and_cache_bus_data():
    """
    運行中の全バスの位置情報と詳細情報を取得し、結果をキャッシュに保存する。
    この関数はバックグラウンドスレッドから定期的に呼び出される。
    """

    def get_bus_details(work_no, api_base_url, site_id, headers):
        """
        個別のバスの詳細情報をAPIから取得する内部関数。
        ThreadPoolExecutor内で並列処理される。
        """
        try:
            endpoint = f"{api_base_url}/get-bus"
            payload = {"language": 1, "workNo": str(work_no), "siteId": site_id}
            response = requests.post(
                endpoint, json=payload, headers=headers, timeout=3)
            if response.status_code == 200:
                buses = response.json().get("bus", [])
                if buses:
                    return buses[0]
        except requests.exceptions.RequestException:
            # エラー時はNoneを返し、呼び出し元でログを記録する
            pass
        return None

    try:
        # 0. アプリケーションコンテキストから設定値を変数に読み込みます。
        api_base_url = current_app.config["API_BASE_URL"]
        site_id = current_app.config["SITE_ID"]
        headers = current_app.config["HEADERS"]
        backup_file = current_app.config["BACKUP_FILE"]

        # 1. まず、全バスの基本情報（位置情報など）を取得します。
        endpoint = f"{api_base_url}/get-buses"
        payload = {"language": 1, "siteId": site_id}
        response = requests.post(
            endpoint, json=payload, headers=headers, timeout=5)
        response.raise_for_status()

        buses_with_location = response.json().get("buses", [])

        if not buses_with_location:
            return []

        # 2. 次に、各バスの詳細情報（行き先など）を並列で取得し、処理を高速化します。
        detailed_buses = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            # get_bus_details関数に、必要な設定値を引数として渡します。
            future_to_work_no = {
                executor.submit(
                    get_bus_details, bus.get(
                        "workNo"), api_base_url, site_id, headers
                ): bus.get("workNo")
                for bus in buses_with_location
            }

            for future in future_to_work_no:
                work_no = future_to_work_no[future]
                detail = future.result()
                if detail:
                    detailed_buses[work_no] = detail
                else:
                    # 詳細情報の取得に失敗したバスをログに記録
                    current_app.logger.info(
                        f"バス詳細情報の取得に失敗しました (workNo: {work_no})"
                    )

        # 3. 最後に、基本情報と詳細情報をマージ（結合）します。
        merged_buses = []
        for bus in buses_with_location:
            work_no = bus.get("workNo")
            if work_no in detailed_buses:
                bus.update(detailed_buses[work_no])
            merged_buses.append(bus)

        # 取得した最新のバス情報をバックアップファイルとして保存します。
        if merged_buses:
            os.makedirs(os.path.dirname(backup_file), exist_ok=True)
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(merged_buses, f, ensure_ascii=False, indent=2)

        # ★★★ 新しい設計の核心 ★★★
        # APIから取得・整形した最終的なバスの生データをキャッシュに保存する
        cache.set('live_bus_data', merged_buses)
        
        return merged_buses

    except requests.exceptions.RequestException as e:
        endpoint = f"{current_app.config['API_BASE_URL']}/get-buses"
        current_app.logger.error(f"APIリクエストエラー (endpoint: {endpoint}): {e}")
        # APIリクエストが失敗した場合は、キャッシュを更新せずに処理を終了します。
        # これにより、一時的なネットワークエラーなどが発生した場合でも、
        # 古いキャッシュデータを表示し続けることで、サービスの完全な停止を防ぎます。
        return
