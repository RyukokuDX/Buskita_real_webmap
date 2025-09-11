import requests
import json
import time
from datetime import datetime
from urllib.parse import quote

def get_ohmi_bus_location(from_station="南草津駅【近江鉄道・湖国バス】", to_station="松ヶ丘五丁目【近江鉄道・湖国バス】", 
                         route_name="南草津飛島線：パナソニック【近江鉄道・湖国バス】", departure_time="18:39"):
    """
    近江鉄道バスの位置情報を取得する
    
    Args:
        from_station (str): 出発駅名（【近江鉄道・湖国バス】付き）
        to_station (str): 到着駅名（【近江鉄道・湖国バス】付き）
        route_name (str): 路線名
        departure_time (str): 出発時刻（HH:MM形式）
    
    Returns:
        dict: バスの位置情報
    """
    # セッションを作成（Cookieを保持するため）
    session = requests.Session()
    
    # 現在の日時を取得してフォーマット
    current_time = datetime.now()
    formatted_date = current_time.strftime("%Y%m%d")
    
    # 初期リクエストのURL（実際のブラウザの動作を模倣）
    base_url = 'https://ohmitetudo-bus.jorudan.biz/busloca'
    
    # from_stationとto_stationから【近江鉄道・湖国バス】を削除
    from_station_simple = from_station.replace("【近江鉄道・湖国バス】", "")
    to_station_simple = to_station.replace("【近江鉄道・湖国バス】", "")
    
    # 初期リクエストのパラメータ
    params = {
        'mode': '0',
        'fr': from_station,
        'frsk': 'B',
        'to': to_station,
        'tosk': 'B',
        'dt': f"{formatted_date}{departure_time.replace(':', '')}",
        'p': '0,1,2',
        'bl': f"{from_station_simple},{to_station_simple},{route_name},{departure_time}"
    }
    
    # リクエストヘッダー
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ja',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        # 初期リクエストを送信
        init_response = session.get(base_url, params=params, headers=headers)
        init_response.raise_for_status()
        
        # バス位置情報取得用のリクエスト
        update_url = 'https://ohmitetudo-bus.jorudan.biz/buslocaupd'
        
        # リクエストボディ（全体を1つの文字列としてエンコード）
        bl_param = f"{from_station_simple},{to_station_simple},{route_name},{departure_time}"
        data = f"bl={quote(bl_param)}&qry="
        
        # POSTリクエストを送信
        response = session.post(update_url, headers=headers, data=data)
        response.raise_for_status()
        
        # レスポンスをJSONとして解析
        result = response.json()
        
        # 現在時刻を取得
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # 結果をJSONファイルとして保存
        output_file = f"ohmi_bus_location_{current_time}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching bus location: {e}")
        return None

def main():
    # バスの位置情報を取得
    result = get_ohmi_bus_location(
        from_station="南草津駅【近江鉄道・湖国バス】",
        to_station="松ヶ丘五丁目【近江鉄道・湖国バス】",
        route_name="南草津飛島線：パナソニック【近江鉄道・湖国バス】",
        departure_time="18:55"
    )
    if result:
        print("バスの位置情報を取得しました。")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("バスの位置情報の取得に失敗しました。")

if __name__ == '__main__':
    main()
