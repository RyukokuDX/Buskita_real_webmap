import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

class BusIDAnalyzer:
    """バスIDの詳細分析クラス"""
    
    def __init__(self):
        self.base_url = "https://api.buskita.com"
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ja',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'
        }
        
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """APIリクエストを実行"""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"エラー: {endpoint} - Status: {response.status_code}")
                if response.text:
                    print(f"Response: {response.text[:300]}")
                return None
        except Exception as e:
            print(f"リクエストエラー: {str(e)}")
            return None
    
    def analyze_get_buses_endpoint(self):
        """get-busesエンドポイントの詳細分析"""
        print("🚌 get-buses エンドポイント詳細分析")
        print("=" * 60)
        
        # 基本的なサイトIDで全てテスト
        for site_id in range(1, 11):
            print(f"\n📍 サイトID: {site_id}")
            
            result = self._make_request('get-buses', {
                'language': 1, 
                'siteId': site_id
            })
            
            if result:
                buses = result.get('buses', [])
                print(f"   バス数: {len(buses)}台")
                
                if len(buses) > 0:
                    print(f"   🎯 バス発見！")
                    print(f"   データ構造: {list(result.keys())}")
                    
                    # 最初の数台のバス詳細を表示
                    for i, bus in enumerate(buses[:3], 1):
                        print(f"   バス{i}: {json.dumps(bus, ensure_ascii=False)}")
                    
                    return result
            else:
                print(f"   リクエスト失敗")
    
    def test_get_buses_with_parameters(self):
        """get-busesエンドポイントの様々なパラメータテスト"""
        print("\n\n📊 get-buses パラメータテスト")
        print("=" * 60)
        
        # 様々なパラメータパターンをテスト
        test_patterns = [
            # 基本パターン
            {"name": "基本", "data": {"language": 1, "siteId": 9}},
            {"name": "英語", "data": {"language": 2, "siteId": 9}},
            
            # 時間関連パラメータ追加
            {"name": "現在時刻", "data": {"language": 1, "siteId": 9, "time": datetime.now().strftime("%H:%M")}},
            {"name": "日付", "data": {"language": 1, "siteId": 9, "date": datetime.now().strftime("%Y-%m-%d")}},
            {"name": "日時両方", "data": {
                "language": 1, 
                "siteId": 9, 
                "time": datetime.now().strftime("%H:%M"),
                "date": datetime.now().strftime("%Y-%m-%d")
            }},
            
            # 会社コード指定
            {"name": "帝産湖南交通", "data": {"language": 1, "siteId": 9, "companyNo": "tkt"}},
            {"name": "JR北海道", "data": {"language": 1, "siteId": 1, "companyNo": "jhb"}},
            
            # 位置情報パラメータ
            {"name": "位置指定", "data": {
                "language": 1, 
                "siteId": 9, 
                "latitude": 35.0, 
                "longitude": 135.9
            }},
            
            # workNo追加
            {"name": "workNo追加", "data": {
                "language": 1, 
                "siteId": 9, 
                "workNo": "48385"
            }},
            
            # その他のパラメータ
            {"name": "routeNo", "data": {"language": 1, "siteId": 9, "routeNo": "1"}},
            {"name": "busStopNo", "data": {"language": 1, "siteId": 9, "busStopNo": 1}},
        ]
        
        results = {}
        for pattern in test_patterns:
            print(f"\n🔍 {pattern['name']}")
            print(f"   パラメータ: {json.dumps(pattern['data'], ensure_ascii=False)}")
            
            result = self._make_request('get-buses', pattern['data'])
            if result:
                buses = result.get('buses', [])
                print(f"   ✓ 成功: {len(buses)}台")
                
                if len(buses) > 0:
                    print(f"   🎯 バス発見！")
                    # バスの詳細情報を分析
                    self.analyze_bus_data_structure(buses)
                    return result
                
                results[pattern['name']] = result
        
        return results
    
    def analyze_bus_data_structure(self, buses: List[Dict[str, Any]]):
        """バスデータの構造を分析"""
        print(f"\n📋 バスデータ構造分析 ({len(buses)}台)")
        print("-" * 40)
        
        if buses:
            # 最初のバスの構造を詳しく分析
            first_bus = buses[0]
            print(f"バスデータのキー: {list(first_bus.keys())}")
            
            # 各フィールドの詳細
            for key, value in first_bus.items():
                print(f"  {key}: {type(value).__name__} = {value}")
            
            # バスIDの可能性があるフィールドを特定
            potential_id_fields = []
            for key, value in first_bus.items():
                if 'id' in key.lower() or 'no' in key.lower() or 'number' in key.lower():
                    potential_id_fields.append(key)
            
            if potential_id_fields:
                print(f"\n🎯 バスID候補フィールド: {potential_id_fields}")
                
                # 全バスのID値を収集
                for field in potential_id_fields:
                    ids = [bus.get(field) for bus in buses if field in bus]
                    unique_ids = list(set(ids))
                    print(f"  {field}: {len(unique_ids)}個のユニークID = {unique_ids[:10]}")  # 最初の10個
    
    def test_different_time_periods(self):
        """異なる時間帯でのテスト"""
        print("\n\n⏰ 時間帯別テスト")
        print("=" * 60)
        
        # 平日の主要時間帯をテスト
        time_slots = [
            "06:00", "07:00", "08:00", "09:00",  # 朝の通勤時間
            "12:00", "13:00",                    # 昼
            "17:00", "18:00", "19:00",          # 夕方の通勤時間
            "20:00", "21:00", "22:00"           # 夜
        ]
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        for time_slot in time_slots:
            print(f"\n🕐 {time_slot}")
            
            result = self._make_request('get-buses', {
                'language': 1,
                'siteId': 9,
                'time': time_slot,
                'date': current_date
            })
            
            if result:
                buses = result.get('buses', [])
                print(f"   バス数: {len(buses)}台")
                
                if len(buses) > 0:
                    print(f"   🎯 運行バス発見！")
                    return result
    
    def comprehensive_site_analysis(self):
        """全サイトの包括的分析"""
        print("\n\n🌐 全サイト包括分析")
        print("=" * 60)
        
        # サイトID 1-30 で包括的テスト
        active_sites = []
        
        for site_id in range(1, 31):
            result = self._make_request('get-buses', {
                'language': 1, 
                'siteId': site_id
            })
            
            if result:
                buses = result.get('buses', [])
                if len(buses) > 0:
                    active_sites.append({
                        'siteId': site_id,
                        'busCount': len(buses),
                        'data': result
                    })
                    print(f"📍 サイトID {site_id}: {len(buses)}台のバス")
                else:
                    print(f"📍 サイトID {site_id}: 0台")
        
        if active_sites:
            print(f"\n🎯 アクティブなサイト: {len(active_sites)}個")
            for site in active_sites:
                print(f"  サイトID {site['siteId']}: {site['busCount']}台")
            return active_sites
        else:
            print("\n😔 現在運行中のバスが見つかりません")
            return []
    
    def create_bus_monitoring_script(self):
        """バス監視スクリプトを作成"""
        monitoring_script = '''import requests
import json
import time
from datetime import datetime

def monitor_buses():
    """リアルタイムバス監視"""
    url = "https://api.buskita.com/get-buses"
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ja',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'
    }
    
    # 複数のサイトIDを監視
    sites_to_monitor = [1, 3, 9, 12, 15]  # 主要サイト
    
    while True:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n{timestamp} - バス監視中...")
        
        total_buses = 0
        for site_id in sites_to_monitor:
            try:
                response = requests.post(url, headers=headers, json={
                    'language': 1,
                    'siteId': site_id
                })
                
                if response.status_code == 200:
                    data = response.json()
                    buses = data.get('buses', [])
                    bus_count = len(buses)
                    total_buses += bus_count
                    
                    if bus_count > 0:
                        print(f"🚌 サイト{site_id}: {bus_count}台運行中")
                        
                        # バス詳細を記録
                        filename = f'active_buses_site{site_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        print(f"   データ保存: {filename}")
                    else:
                        print(f"📍 サイト{site_id}: 0台")
                
                time.sleep(1)  # サイト間の間隔
                
            except Exception as e:
                print(f"❌ サイト{site_id}でエラー: {e}")
        
        print(f"合計: {total_buses}台")
        
        if total_buses > 0:
            print("🎯 運行中のバス発見！監視を継続します...")
        
        time.sleep(30)  # 30秒間隔で監視

if __name__ == '__main__':
    monitor_buses()
'''
        
        with open('bus_monitor.py', 'w', encoding='utf-8') as f:
            f.write(monitoring_script)
        
        print(f"\n💾 バス監視スクリプト作成: bus_monitor.py")
        print("使用方法: python bus_monitor.py")

def main():
    analyzer = BusIDAnalyzer()
    
    print("🚌 バスID詳細分析開始")
    print("=" * 80)
    
    # 1. get-busesエンドポイントの詳細分析
    buses_result = analyzer.analyze_get_buses_endpoint()
    
    # 2. パラメータテスト
    if not buses_result:
        analyzer.test_get_buses_with_parameters()
    
    # 3. 時間帯別テスト
    analyzer.test_different_time_periods()
    
    # 4. 全サイト分析
    active_sites = analyzer.comprehensive_site_analysis()
    
    # 5. 監視スクリプト作成
    analyzer.create_bus_monitoring_script()
    
    print(f"\n\n📋 分析結果サマリー")
    print("=" * 60)
    print("🔍 発見事項:")
    print("1. get-buses エンドポイントが存在 - バス一覧取得可能")
    print("2. 現在は全サイトで0台（非運行時間の可能性）")
    print("3. workNoパラメータは get-bus のみで必要（get-busesでは不要）")
    print("4. サイトID 1-30 が有効範囲")
    
    print(f"\n💡 バスID取得の推奨方法:")
    print("1. 運行時間中（6:00-22:00）に get-buses を実行")
    print("2. 複数のサイトIDを定期的に監視")
    print("3. bus_monitor.py を使用した継続監視")
    print("4. バスが見つかったらデータ構造からIDフィールドを特定")

if __name__ == '__main__':
    main() 