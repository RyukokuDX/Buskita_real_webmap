from flask import current_app, jsonify, render_template
import json
import os
import requests

from . import services

@current_app.route('/')
def index():
    """メインのマップページ"""
    return render_template('index.html')

@current_app.route('/api/bus_locations')
def api_bus_locations():
    """バスの位置情報を返すAPI"""
    locations_raw = services.get_live_bus_data()
    is_stale = False

    if not locations_raw:
        current_app.logger.warning("APIから有効なデータが取得できませんでした。バックアップを試みます。")
        backup_file = current_app.config['BACKUP_FILE']
        if os.path.exists(backup_file):
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    locations_raw = json.load(f)
                is_stale = True
                current_app.logger.info("バックアップファイルを使用しました。")
            except (json.JSONDecodeError, IOError) as e:
                current_app.logger.error(f"バックアップファイルの読み込みに失敗しました: {e}")
                locations_raw = []
        else:
            current_app.logger.warning("バックアップファイルが見つかりませんでした。")

    locations = services.filter_and_format_buses(locations_raw)
    
    if not is_stale:
        current_app.logger.info(f"APIから {len(locations)} 台の有効なバス情報を取得しました。")

    return jsonify({
        'buses': locations,
        'is_stale': is_stale
    })

@current_app.route('/timetable')
def timetable_page():
    """時刻表ページを表示する"""
    try:
        # Note: 'static/timetable.json' is relative to the instance folder or root.
        # For blueprint structure, url_for('static', filename='timetable.json') is better.
        with open(os.path.join(current_app.static_folder, 'timetable.json'), 'r', encoding='utf-8') as f:
            raw_timetable_data = json.load(f)

        timetable_data = {}
        for route_id, data in raw_timetable_data.items():
            processed_schedules = {}
            for day, times in data.get('schedules', {}).items():
                processed_schedules[day] = services.group_schedules_by_hour(times)
            
            timetable_data[route_id] = {
                'routeName': data['routeName'],
                'schedules': processed_schedules
            }
            
    except (FileNotFoundError, json.JSONDecodeError) as e:
        current_app.logger.error(f"Error loading timetable: {e}")
        timetable_data = {}
        
    return render_template('timetable.html', timetable_data=timetable_data)

@current_app.route('/api/landmarks')
def api_landmarks():
    """固定のランドマーク情報を返す"""
    landmarks = [
        {"name": "龍谷大学 瀬田キャンパス", "lat": 34.964307, "lng": 135.939629, "type": "university"},
        {"name": "JR瀬田駅", "lat": 34.986964, "lng": 135.925364, "type": "station"}
    ]
    return jsonify(landmarks)

@current_app.route('/api/timetable_data')
def api_timetable_data():
    """静的な時刻表JSONをそのまま返す"""
    try:
        with open(os.path.join(current_app.static_folder, 'timetable.json'), 'r', encoding='utf-8') as f:
            timetable_data = json.load(f)
        return jsonify(timetable_data)
    except Exception as e:
        current_app.logger.error(f"Error serving timetable json: {e}")
        return jsonify({}), 500

@current_app.route('/api/network_test')
def api_network_test():
    """VPN環境でのネットワーク接続テスト"""
    test_urls = [
        'https://tile.openstreetmap.org/14/14000/6800.png',
        'https://maps.wikimedia.org/osm-intl/14/14000/6800.png',
        'https://www.openstreetmap.org/'
    ]
    
    results = {}
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            results[url] = {
                'status': response.status_code,
                'accessible': response.status_code == 200
            }
        except Exception as e:
            results[url] = { 'status': 'error', 'accessible': False, 'error': str(e) }
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'vpn_detected': not any(result['accessible'] for result in results.values())
    })
