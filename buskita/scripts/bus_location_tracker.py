import requests
import json
import time
from datetime import datetime

def get_bus_location(work_no='48385', site_id=9, language=1):
    # APIのエンドポイント
    url = 'https://api.buskita.com/get-bus'
    
    # リクエストヘッダー
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ja',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15'
    }
    
    # リクエストボディ
    data = {
        'language': language,
        'workNo': work_no,
        'siteId': site_id
    }
    
    try:
        # POSTリクエストを送信
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Status code {response.status_code}")
            if response.text:
                print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None

def main():
    # while True:
        # バスの位置情報を取得
        location_data = get_bus_location()
        
        if location_data:
            # 現在時刻を取得
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            
            # データをファイルに保存
            filename = f'bus_location_{timestamp}.json'
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(location_data, f, ensure_ascii=False, indent=2)
            
            print(f"Location data saved to {filename}")
        # print a formatted json
        print(json.dumps(location_data, indent=2, ensure_ascii=False))
        
        # 30秒待機
    # time.sleep(30)

if __name__ == '__main__':
    main()
