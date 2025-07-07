import requests
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd

class BusDataStructureAnalyzer:
    """バスデータ構造の詳細分析クラス"""
    
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
                return None
        except Exception as e:
            return None
    
    def get_all_active_buses(self):
        """全ての運行中バスを取得"""
        print("🚌 運行中バス一覧取得")
        print("=" * 60)
        
        active_sites = [1, 2, 6, 7, 11, 12, 19]  # 前回の分析で特定されたアクティブサイト
        all_buses = []
        
        for site_id in active_sites:
            result = self._make_request('get-buses', {
                'language': 1, 
                'siteId': site_id
            })
            
            if result and 'buses' in result:
                buses = result['buses']
                if buses:
                    print(f"📍 サイトID {site_id}: {len(buses)}台")
                    for bus in buses:
                        bus['siteId'] = site_id  # サイトIDを追加
                        all_buses.append(bus)
        
        print(f"\n合計: {len(all_buses)}台のバス")
        return all_buses
    
    def analyze_bus_id_structure(self, buses: List[Dict[str, Any]]):
        """バスIDの構造を詳細分析"""
        print(f"\n🎯 バスID構造分析 ({len(buses)}台)")
        print("=" * 60)
        
        if not buses:
            print("分析対象のバスがありません")
            return
        
        # 共通フィールドを確認
        all_fields = set()
        for bus in buses:
            all_fields.update(bus.keys())
        
        print(f"🔍 全バスの共通フィールド: {len(all_fields)}個")
        print(f"  {sorted(all_fields)}")
        
        # ID候補フィールドを特定
        id_candidates = []
        for field in all_fields:
            if any(keyword in field.lower() for keyword in ['id', 'no', 'number', 'work']):
                id_candidates.append(field)
        
        print(f"\n🎯 バスID候補フィールド: {id_candidates}")
        
        # 各ID候補の詳細分析
        for field in id_candidates:
            values = [bus.get(field) for bus in buses if field in bus]
            unique_values = list(set(values))
            
            print(f"\n📊 {field}:")
            print(f"  - 全{len(values)}個の値")
            print(f"  - ユニーク値: {len(unique_values)}個")
            print(f"  - 値の例: {unique_values[:5]}")
            print(f"  - データ型: {type(values[0]).__name__}")
            
            # 値の分布を確認
            if len(unique_values) == len(values):
                print(f"  ✅ 全て一意 - 主要バスIDの可能性大")
            else:
                print(f"  ⚠️  重複あり - 補助IDの可能性")
        
        return id_candidates
    
    def create_bus_summary_table(self, buses: List[Dict[str, Any]]):
        """バス情報の要約テーブル作成"""
        print(f"\n📋 バス情報要約テーブル")
        print("=" * 60)
        
        bus_data = []
        for i, bus in enumerate(buses, 1):
            summary = {
                'No': i,
                'サイトID': bus.get('siteId', 'N/A'),
                'workNo': bus.get('workNo', 'N/A'),
                'device_uid': bus.get('device_uid', 'N/A'),
                'バス会社': bus.get('companyNo', 'N/A'),
                '路線名': bus.get('routeNames', {}).get('1', 'N/A'),
                '緯度': bus.get('position', {}).get('latitude', 'N/A'),
                '経度': bus.get('position', {}).get('longitude', 'N/A'),
                '遅延(分)': bus.get('delayMinutes', 'N/A'),
                'バリアフリー': bus.get('barrierFree', 'N/A'),
                '乗車率': bus.get('occupancyStatus', 'N/A'),
            }
            bus_data.append(summary)
        
        # テーブル形式で表示
        if bus_data:
            print(f"{'No':<3} {'サイト':<4} {'workNo':<8} {'device_uid':<15} {'会社':<5} {'路線名':<20}")
            print("-" * 70)
            
            for row in bus_data:
                print(f"{row['No']:<3} {row['サイトID']:<4} {row['workNo']:<8} {row['device_uid']:<15} {row['バス会社']:<5} {row['路線名']:<20}")
        
        return bus_data
    
    def analyze_bus_companies_and_routes(self, buses: List[Dict[str, Any]]):
        """バス会社と路線の分析"""
        print(f"\n🏢 バス会社・路線分析")
        print("=" * 60)
        
        # 会社別統計
        companies = {}
        routes = {}
        
        for bus in buses:
            company = bus.get('companyNo', 'unknown')
            route = bus.get('routeNames', {}).get('1', 'unknown')
            
            companies[company] = companies.get(company, 0) + 1
            routes[route] = routes.get(route, 0) + 1
        
        print(f"📊 バス会社別運行台数:")
        for company, count in sorted(companies.items()):
            print(f"  {company}: {count}台")
        
        print(f"\n📊 路線別運行台数:")
        for route, count in sorted(routes.items()):
            print(f"  {route}: {count}台")
    
    def analyze_position_data(self, buses: List[Dict[str, Any]]):
        """位置データの分析"""
        print(f"\n📍 位置データ分析")
        print("=" * 60)
        
        positions = []
        for bus in buses:
            pos = bus.get('position', {})
            if pos:
                positions.append({
                    'workNo': bus.get('workNo'),
                    'latitude': pos.get('latitude'),
                    'longitude': pos.get('longitude'),
                    'company': bus.get('companyNo'),
                    'route': bus.get('routeNames', {}).get('1', 'N/A')
                })
        
        if positions:
            # 位置データの統計
            latitudes = [p['latitude'] for p in positions if p['latitude']]
            longitudes = [p['longitude'] for p in positions if p['longitude']]
            
            print(f"📊 位置データ統計:")
            print(f"  緯度範囲: {min(latitudes):.6f} ~ {max(latitudes):.6f}")
            print(f"  経度範囲: {min(longitudes):.6f} ~ {max(longitudes):.6f}")
            
            # 各バスの位置情報
            print(f"\n📍 各バスの位置:")
            for pos in positions:
                print(f"  {pos['workNo']}: ({pos['latitude']:.6f}, {pos['longitude']:.6f}) - {pos['route']}")
    
    def create_bus_id_mapping_guide(self, buses: List[Dict[str, Any]], id_candidates: List[str]):
        """バスID対応表・利用ガイド作成"""
        print(f"\n📖 バスID利用ガイド")
        print("=" * 60)
        
        guide_content = f"""
# バスID取得・利用ガイド

## 概要
buskita.com APIから路線を走る各バスのID情報を取得する方法

## 利用可能なAPIエンドポイント

### 1. get-buses (推奨)
- **URL**: https://api.buskita.com/get-buses
- **メソッド**: POST
- **パラメータ**: {{"language": 1, "siteId": [サイトID]}}
- **特徴**: 運行中の全バス一覧を取得

### 2. get-bus (特定バス)
- **URL**: https://api.buskita.com/get-bus
- **メソッド**: POST
- **パラメータ**: {{"language": 1, "siteId": [サイトID], "workNo": "[workNo]"}}
- **特徴**: 特定のworkNoのバス情報を取得

## バスIDの種類

### 主要ID
"""
        
        for field in id_candidates:
            if field in ['workNo', 'device_uid']:
                values = [bus.get(field) for bus in buses if field in bus]
                unique_count = len(set(values))
                
                guide_content += f"""
### {field}
- **用途**: {'主要バスID' if unique_count == len(values) else '補助ID'}
- **形式**: {type(values[0]).__name__}
- **例**: {values[0] if values else 'N/A'}
- **ユニーク性**: {unique_count}/{len(values)} ({'✅ 一意' if unique_count == len(values) else '⚠️ 重複あり'})
"""
        
        guide_content += f"""

## 現在運行中のバス一覧 ({len(buses)}台)

| No | サイト | workNo | device_uid | 会社 | 路線名 |
|----|--------|--------|------------|------|--------|
"""
        
        for i, bus in enumerate(buses, 1):
            guide_content += f"| {i} | {bus.get('siteId', 'N/A')} | {bus.get('workNo', 'N/A')} | {bus.get('device_uid', 'N/A')} | {bus.get('companyNo', 'N/A')} | {bus.get('routeNames', {}).get('1', 'N/A')} |\n"
        
        guide_content += f"""

## 利用例

### Python実装例
```python
import requests

def get_bus_by_work_no(work_no, site_id=1):
    url = "https://api.buskita.com/get-bus"
    headers = {{
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ja',
        'Content-Type': 'application/json'
    }}
    
    data = {{
        'language': 1,
        'siteId': site_id,
        'workNo': work_no
    }}
    
    response = requests.post(url, headers=headers, json=data)
    return response.json() if response.status_code == 200 else None

# 使用例
bus_info = get_bus_by_work_no("291940", 1)
```

## アクティブなサイトID
- サイトID 1: JR北海道バス系統 (7台)
- サイトID 2: (1台)
- サイトID 6: (1台)  
- サイトID 7: (5台)
- サイトID 11: (1台)
- サイトID 12: (1台)
- サイトID 19: (2台)

## 更新頻度
リアルタイム更新。30秒間隔での監視推奨。

## 注意事項
- バスの運行状況により台数は変動
- 非運行時間帯は0台の場合あり
- workNoは数値型とstring型が混在

"""
        
        # ガイドをファイルに保存
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'bus_id_guide_{timestamp}.md'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print(f"💾 バスID利用ガイド保存: {filename}")
        print(guide_content)
        
        return guide_content

def main():
    analyzer = BusDataStructureAnalyzer()
    
    print("🚌 バスデータ構造詳細分析")
    print("=" * 80)
    
    # 1. 運行中バス取得
    all_buses = analyzer.get_all_active_buses()
    
    if not all_buses:
        print("現在運行中のバスがありません")
        return
    
    # 2. バスID構造分析
    id_candidates = analyzer.analyze_bus_id_structure(all_buses)
    
    # 3. バス情報要約テーブル
    bus_summary = analyzer.create_bus_summary_table(all_buses)
    
    # 4. 会社・路線分析
    analyzer.analyze_bus_companies_and_routes(all_buses)
    
    # 5. 位置データ分析
    analyzer.analyze_position_data(all_buses)
    
    # 6. 利用ガイド作成
    analyzer.create_bus_id_mapping_guide(all_buses, id_candidates)
    
    # 7. 生データ保存
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    raw_data_filename = f'bus_raw_data_{timestamp}.json'
    
    with open(raw_data_filename, 'w', encoding='utf-8') as f:
        json.dump(all_buses, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 生データ保存: {raw_data_filename}")
    
    print(f"\n\n📋 最終サマリー")
    print("=" * 60)
    print(f"🎯 バスID取得方法が判明:")
    print(f"1. 主要ID: workNo (例: 291940)")
    print(f"2. デバイスID: device_uid (例: jhb_5379914)")
    print(f"3. 現在運行中: {len(all_buses)}台")
    print(f"4. 利用可能API: get-buses, get-bus")
    print(f"5. アクティブサイト: 7個")

if __name__ == '__main__':
    main() 