import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

class BusIDExplorer:
    """バスID情報を探索するクラス"""
    
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
                    print(f"Response: {response.text[:200]}")
                return None
        except Exception as e:
            print(f"リクエストエラー: {str(e)}")
            return None
    
    def explore_bus_endpoint_variations(self):
        """get-busエンドポイントの様々なパラメータを試す"""
        print("🚌 get-bus エンドポイントの詳細調査")
        print("=" * 60)
        
        # 基本的なバリエーション
        test_cases = [
            # 既知のパラメータ
            {"name": "標準パラメータ", "data": {"language": 1, "workNo": "48385", "siteId": 9}},
            
            # workNoの変更
            {"name": "workNo なし", "data": {"language": 1, "siteId": 9}},
            {"name": "workNo 空文字", "data": {"language": 1, "workNo": "", "siteId": 9}},
            {"name": "workNo 数値", "data": {"language": 1, "workNo": 48385, "siteId": 9}},
            
            # 追加パラメータの試行
            {"name": "routeNo指定", "data": {"language": 1, "siteId": 9, "routeNo": "1"}},
            {"name": "busStopNo指定", "data": {"language": 1, "siteId": 9, "busStopNo": 1}},
            {"name": "companyNo指定", "data": {"language": 1, "siteId": 9, "companyNo": "tkt"}},
            
            # 時間関連パラメータ
            {"name": "現在時刻指定", "data": {"language": 1, "siteId": 9, "time": datetime.now().strftime("%H:%M")}},
            {"name": "日付指定", "data": {"language": 1, "siteId": 9, "date": datetime.now().strftime("%Y-%m-%d")}},
            
            # 位置関連パラメータ
            {"name": "位置指定", "data": {"language": 1, "siteId": 9, "latitude": 35.0, "longitude": 135.9}},
            {"name": "範囲指定", "data": {"language": 1, "siteId": 9, "latitude": 35.0, "longitude": 135.9, "radius": 1000}},
            
            # 別のサイトID
            {"name": "サイトID=1", "data": {"language": 1, "workNo": "48385", "siteId": 1}},
            {"name": "サイトID=3", "data": {"language": 1, "workNo": "48385", "siteId": 3}},
        ]
        
        results = {}
        for test_case in test_cases:
            print(f"\n📋 {test_case['name']}")
            print(f"   パラメータ: {json.dumps(test_case['data'], ensure_ascii=False)}")
            
            result = self._make_request('get-bus', test_case['data'])
            if result:
                bus_count = len(result.get('bus', []))
                is_cached = result.get('isCached', False)
                print(f"   ✓ 成功: バス{bus_count}台, キャッシュ:{is_cached}")
                
                if bus_count > 0:
                    print(f"   🎯 バス発見！ データ: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    
                results[test_case['name']] = result
            else:
                print(f"   ✗ 失敗")
                results[test_case['name']] = None
        
        return results
    
    def explore_potential_bus_endpoints(self):
        """バス関連の潜在的なエンドポイントを探索"""
        print("\n\n🔍 潜在的なバスエンドポイントの探索")
        print("=" * 60)
        
        potential_endpoints = [
            # バス関連エンドポイント候補
            {"endpoint": "get-buses", "data": {"language": 1, "siteId": 9}},
            {"endpoint": "get-bus-list", "data": {"language": 1, "siteId": 9}},
            {"endpoint": "get-bus-info", "data": {"language": 1, "siteId": 9}},
            {"endpoint": "get-bus-status", "data": {"language": 1, "siteId": 9}},
            {"endpoint": "get-active-buses", "data": {"language": 1, "siteId": 9}},
            {"endpoint": "get-running-buses", "data": {"language": 1, "siteId": 9}},
            
            # ルート関連
            {"endpoint": "get-routes", "data": {"language": 1, "siteId": 9}},
            {"endpoint": "get-route-buses", "data": {"language": 1, "siteId": 9, "routeNo": "1"}},
            {"endpoint": "get-bus-routes", "data": {"language": 1, "siteId": 9}},
            
            # バス停関連
            {"endpoint": "get-busstops", "data": {"language": 1, "siteId": 9}},
            {"endpoint": "get-busstop-buses", "data": {"language": 1, "siteId": 9, "busStopNo": 1}},
            
            # スケジュール関連
            {"endpoint": "get-timetable", "data": {"language": 1, "siteId": 9}},
            {"endpoint": "get-schedule", "data": {"language": 1, "siteId": 9}},
            {"endpoint": "get-bus-schedule", "data": {"language": 1, "siteId": 9}},
        ]
        
        results = {}
        for item in potential_endpoints:
            endpoint = item['endpoint']
            data = item['data']
            print(f"\n🔎 {endpoint}")
            print(f"   パラメータ: {json.dumps(data, ensure_ascii=False)}")
            
            result = self._make_request(endpoint, data)
            if result:
                print(f"   ✓ 成功！ データサイズ: {len(str(result))}文字")
                print(f"   レスポンス構造: {list(result.keys()) if isinstance(result, dict) else 'リスト形式'}")
                
                # バス情報が含まれているかチェック
                if isinstance(result, dict):
                    for key, value in result.items():
                        if 'bus' in key.lower() and isinstance(value, list):
                            print(f"   🚌 バス関連データ発見: {key} = {len(value)}件")
                
                results[endpoint] = result
            else:
                results[endpoint] = None
        
        return results
    
    def analyze_existing_data_for_bus_ids(self):
        """既存のAPIデータからバスID情報を分析"""
        print("\n\n📊 既存データからのバスID分析")
        print("=" * 60)
        
        # バス停グルーピング情報からバス停番号を取得
        grouping_result = self._make_request('get-busstops-grouping', {'language': 1, 'siteId': 9})
        if grouping_result and 'groupings' in grouping_result:
            print(f"\n🚏 バス停グルーピング情報: {len(grouping_result['groupings'])}件")
            
            # ユニークなバス停番号を抽出
            bus_stop_nos = set()
            companies = set()
            for item in grouping_result['groupings']:
                bus_stop_nos.add(item['bus_stop_no'])
                companies.add(item['company_no'])
            
            print(f"   バス停番号: {sorted(bus_stop_nos)}")
            print(f"   会社コード: {sorted(companies)}")
            
            # 各バス停でバス情報を検索
            print(f"\n🔍 各バス停でのバス検索:")
            for bus_stop_no in sorted(bus_stop_nos)[:5]:  # 最初の5つのみ
                for company in companies:
                    print(f"   バス停{bus_stop_no} ({company})での検索...")
                    result = self._make_request('get-bus', {
                        'language': 1, 
                        'siteId': 9, 
                        'busStopNo': bus_stop_no,
                        'companyNo': company
                    })
                    if result and result.get('bus', []):
                        print(f"   🎯 バス発見！ {len(result['bus'])}台")
                        return result
    
    def test_bus_with_company_combinations(self):
        """バス会社との組み合わせでバス情報を検索"""
        print("\n\n🏢 バス会社別検索")
        print("=" * 60)
        
        # バス会社情報を取得
        companies_result = self._make_request('get-companies-dictionary', {'language': 1})
        if not companies_result or 'companiesDictionary' not in companies_result:
            print("バス会社情報の取得に失敗")
            return
        
        companies = companies_result['companiesDictionary']
        print(f"対象バス会社: {len(companies)}社")
        
        # 各バス会社でバス情報を検索
        for company in companies[:10]:  # 最初の10社のみ
            company_no = company['company_no']
            company_name = company['name']
            print(f"\n🚌 {company_name} ({company_no})")
            
            # 複数のパターンでテスト
            test_patterns = [
                {'language': 1, 'companyNo': company_no},
                {'language': 1, 'siteId': 9, 'companyNo': company_no},
                {'language': 1, 'company_no': company_no},
                {'language': 1, 'siteId': 9, 'company_no': company_no},
            ]
            
            for i, data in enumerate(test_patterns, 1):
                result = self._make_request('get-bus', data)
                if result and result.get('bus', []):
                    bus_count = len(result['bus'])
                    print(f"   ✓ パターン{i}: {bus_count}台のバス発見！")
                    
                    # バス詳細情報を表示
                    for j, bus in enumerate(result['bus'][:3], 1):  # 最初の3台
                        print(f"     バス{j}: {json.dumps(bus, ensure_ascii=False)}")
                    
                    return result
    
    def explore_different_sites(self):
        """異なるサイトIDでのバス検索"""
        print("\n\n🌐 異なるサイトIDでの検索")
        print("=" * 60)
        
        # サイトID 1-20 でテスト
        for site_id in range(1, 21):
            print(f"\n📍 サイトID: {site_id}")
            
            result = self._make_request('get-bus', {
                'language': 1, 
                'siteId': site_id,
                'workNo': '48385'
            })
            
            if result:
                bus_count = len(result.get('bus', []))
                if bus_count > 0:
                    print(f"   🎯 {bus_count}台のバス発見！")
                    print(f"   データ: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    return result
                else:
                    print(f"   バス: {bus_count}台")
    
    def save_results(self, all_results: Dict[str, Any]):
        """結果を保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'bus_id_exploration_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 調査結果を保存: {filename}")

def main():
    explorer = BusIDExplorer()
    
    print("🚌 バスID情報探索開始")
    print("=" * 80)
    
    all_results = {}
    
    # 1. get-busエンドポイントの詳細調査
    bus_variations = explorer.explore_bus_endpoint_variations()
    all_results['bus_endpoint_variations'] = bus_variations
    
    # 2. 潜在的なエンドポイントの探索
    potential_endpoints = explorer.explore_potential_bus_endpoints()
    all_results['potential_endpoints'] = potential_endpoints
    
    # 3. 既存データからの分析
    explorer.analyze_existing_data_for_bus_ids()
    
    # 4. バス会社別検索
    explorer.test_bus_with_company_combinations()
    
    # 5. 異なるサイトIDでの検索
    explorer.explore_different_sites()
    
    # 結果を保存
    explorer.save_results(all_results)
    
    print(f"\n\n📋 調査完了サマリー")
    print("=" * 60)
    print("バスIDを取得するための推奨方法:")
    print("1. 異なるサイトIDでの get-bus 呼び出し")
    print("2. バス会社コードとの組み合わせ")
    print("3. 時間帯を変えての呼び出し（運行時間中）")
    print("4. 新しいエンドポイントの存在確認")

if __name__ == '__main__':
    main() 