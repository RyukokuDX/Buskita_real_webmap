# URLのエンドポイント（例: /api/bus_locations）と、それに対応する処理（Python関数）を
# 結びつける役割を持つファイルです。
# Flaskの `current_app` を介して、アプリケーションのルーティングを定義します。

from flask import current_app, jsonify, render_template
from . import main  # Blueprintインスタンスをインポート
import json
import os
import requests
from datetime import datetime
import jpholiday

# services パッケージからビジネスロジックをインポートします。
from buskita import services
from buskita import cache


@main.app_errorhandler(500)
def internal_server_error(e):
    """
    サーバー内部でエラーが発生した場合に、カスタムエラーページを返すハンドラ。
    """
    current_app.logger.error(f"Internal Server Error: {e}")
    return render_template("500.html"), 500


@main.route("/")
def index():
    """
    メインのマップページ (`index.html`) を表示します。
    """
    return render_template("index.html")


@main.route("/api/bus_locations")
def api_bus_locations():
    """
    バスの位置情報をJSON形式で返すAPIエンドポイント。
    フロントエンドのJavaScriptから定期的に呼び出されます。
    ★★★ 新しい設計では、この関数はキャッシュからデータを読み出すだけです ★★★
    """
    # 実際のデータ取得処理は services モジュールに任せます。
    # この関数はキャッシュからデータを高速に読み出すだけです。
    locations_raw = services.get_buses_from_cache()

    # is_stale フラグは、リアルタイム性を重視する今回の設計では不要になる可能性がありますが、
    # バックアップ機能との兼ね合いを考え、一旦ロジックは残します。
    # ただし、バックエンドでキャッシュが更新され続けるため、常に is_stale=False となります。
    is_stale = False

    # APIからデータが取得できなかった場合、バックアップファイルの使用を試みます。
    if not locations_raw:
        # このブロックは、バックグラウンドスレッドがまだ一度もキャッシュを書き込んでいない
        # アプリケーション起動直後などに実行される可能性があります。
        current_app.logger.info(
            "初回アクセス時にキャッシュがまだ生成されていなかったため、バックアップを試みます。"
        )
        backup_file = current_app.config["BACKUP_FILE"]
        if os.path.exists(backup_file):
            try:
                with open(backup_file, "r", encoding="utf-8") as f:
                    locations_raw = json.load(f)
                is_stale = True
                current_app.logger.info("バックアップファイルを使用しました。")
            except (json.JSONDecodeError, IOError) as e:
                current_app.logger.error(
                    f"バックアップファイルの読み込みに失敗しました: {e}"
                )
                locations_raw = []
        else:
            current_app.logger.warning("バックアップファイルが見つかりませんでした。")

    # 取得した生データをフロントエンドで使いやすいように整形します。
    locations = services.filter_and_format_buses(locations_raw)

    if not is_stale:
        current_app.logger.info(
            f"APIから {len(locations)} 台の有効なバス情報を取得しました。"
        )

    # 整形したバス情報と、データが古いかどうかを示すフラグをJSONで返します。
    return jsonify({"buses": locations, "is_stale": is_stale})


@main.route("/api/day_type")
def api_day_type():
    """
    今日の曜日タイプ（平日/土曜/休日）を返すAPI。祝日を考慮します。
    """
    today = datetime.now().date()
    day_type = "weekdays"  # デフォルトは平日
    if jpholiday.is_holiday(today) or today.weekday() == 6:
        day_type = "holidays"
    elif today.weekday() == 5:
        day_type = "saturdays"

    return jsonify({"day_type": day_type})


@main.route("/api/last_updated")
def api_last_updated():
    """
    キャッシュの最終更新時刻を返すAPIエンドポイント。
    """
    last_updated = cache.get("last_updated")
    if last_updated:
        # datetimeオブジェクトをISO 8601形式の文字列に変換
        # ZはUTCを示すために手動で追加
        last_updated_iso = last_updated.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        return jsonify({"last_updated": last_updated_iso})
    else:
        return jsonify({"last_updated": None})


@main.route("/timetable")
def timetable_page():
    """
    時刻表ページ (`timetable.html`) を表示します。
    """
    try:
        # 静的ファイルとして配置されている時刻表JSONを読み込みます。
        with open(
            os.path.join(current_app.static_folder, "timetable.json"),
            "r",
            encoding="utf-8",
        ) as f:
            raw_timetable_data = json.load(f)

        # テンプレートで表示しやすいように、時間ごとにデータをグループ化します。
        timetable_data = {}
        for route_id, data in raw_timetable_data.items():
            processed_schedules = {}
            for day, times in data.get("schedules", {}).items():
                processed_schedules[day] = services.group_schedules_by_hour(times)

            timetable_data[route_id] = {
                "routeName": data["routeName"],
                "schedules": processed_schedules,
            }

    except (FileNotFoundError, json.JSONDecodeError) as e:
        current_app.logger.error(f"Error loading timetable: {e}")
        timetable_data = {}

    return render_template("timetable.html", timetable_data=timetable_data)


@main.route("/api/landmarks")
def api_landmarks():
    """
    地図上に表示する固定のランドマーク（大学、駅）の情報を返すAPI。
    """
    landmarks = [
        {
            "name": "龍谷大学 瀬田キャンパス",
            "lat": 34.964307,
            "lng": 135.939629,
            "type": "university",
        },
        {"name": "JR瀬田駅", "lat": 34.986964, "lng": 135.925364, "type": "station"},
    ]
    return jsonify(landmarks)


@main.route("/api/timetable_data")
def api_timetable_data():
    """
    静的な時刻表JSON (`timetable.json`) をそのままの形で返すAPI。
    （カウントダウン機能などで使用されることを想定）
    """
    try:
        with open(
            os.path.join(current_app.static_folder, "timetable.json"),
            "r",
            encoding="utf-8",
        ) as f:
            timetable_data = json.load(f)
        return jsonify(timetable_data)
    except Exception as e:
        current_app.logger.error(f"Error serving timetable json: {e}")
        return jsonify({}), 500


@main.route("/api/network_test")
def api_network_test():
    """
    クライアント（ブラウザ）が外部の地図タイルサーバーにアクセスできるかを
    テストするための診断用API。VPN接続の問題などを切り分けるのに役立ちます。
    """
    test_urls = [
        "https://tile.openstreetmap.org/14/14000/6800.png",
        "https://maps.wikimedia.org/osm-intl/14/14000/6800.png",
        "https://www.openstreetmap.org/",
    ]

    results = {}
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            results[url] = {
                "status": response.status_code,
                "accessible": response.status_code == 200,
            }
        except Exception as e:
            results[url] = {"status": "error", "accessible": False, "error": str(e)}

    return jsonify(
        {
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "vpn_detected": not any(
                result["accessible"] for result in results.values()
            ),
        }
    )
