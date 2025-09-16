# 🚌 buskita.com バスID取得完全ガイド

## 📋 概要

buskita.com APIから路線を走る各バスに振られているID情報を取得する方法の完全解説です。
**現在17台のバスが運行中**で、2つの主要なIDシステムが判明しました。

## 🎯 主要なバスID

### 1. workNo (作業番号)
- **形式**: 数値 (例: 291940, 292630)
- **特徴**: 各バスに一意に割り当てられた作業番号
- **用途**: `get-bus` APIでの特定バス検索に使用
- **ユニーク性**: ✅ 完全に一意 (17台すべて異なる値)

### 2. device_uid (デバイスUID)
- **形式**: 文字列 (例: "jhb_5379914", "27cce26e9adfb1df")
- **特徴**: バス会社コード + 車両番号、またはハッシュ値
- **用途**: システム内部での車両識別
- **ユニーク性**: ✅ 完全に一意

## 🔌 利用可能なAPIエンドポイント

### 1. get-buses (全バス取得 - 推奨)

```bash
curl -X POST https://api.buskita.com/get-buses \
  -H "Content-Type: application/json" \
  -H "Accept-Language: ja" \
  -d '{"language": 1, "siteId": 1}'
```

### 2. get-bus (特定バス取得)

```bash
curl -X POST https://api.buskita.com/get-bus \
  -H "Content-Type: application/json" \
  -H "Accept-Language: ja" \
  -d '{"language": 1, "siteId": 1, "workNo": "291940"}'
```

## 🌍 アクティブなサイトID一覧

| サイトID | 運行台数 | 主要バス会社 | 地域 |
|---------|----------|------------|------|
| 1 | 7台 | JR北海道バス (jhb) | 北海道札幌周辺 |
| 2 | 1台 | 琴参バス (ksb) | 香川県 |
| 6 | 1台 | じょうてつバス (jtb) | 北海道札幌 |
| 7 | 4台 | 旭川電気軌道 (adk) | 北海道旭川 |
| 11 | 1台 | 富士急静岡バス (fcb) | 静岡県 |
| 12 | 1台 | 富士急バス (fjb) | 山梨県 |
| 19 | 2台 | 北海道中央バス (hkt) | 北海道札幌 |

**合計: 17台 (7社)**

## 💻 Pythonでの実装例

### 基本的なバス情報取得

```python
import requests
import json
from typing import Dict, Any, List, Optional

class BuskitaAPI:
    def __init__(self):
        self.base_url = "https://api.buskita.com"
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ja',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'
        }
    
    def get_all_buses(self, site_id: int = 1) -> Optional[List[Dict[str, Any]]]:
        """指定サイトの全バス取得"""
        response = requests.post(
            f"{self.base_url}/get-buses",
            headers=self.headers,
            json={'language': 1, 'siteId': site_id}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('buses', [])
        return None
    
    def get_bus_by_work_no(self, work_no: str, site_id: int = 1) -> Optional[Dict[str, Any]]:
        """workNoで特定バスを取得"""
        response = requests.post(
            f"{self.base_url}/get-bus",
            headers=self.headers,
            json={'language': 1, 'siteId': site_id, 'workNo': work_no}
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_all_active_buses(self) -> List[Dict[str, Any]]:
        """全アクティブサイトから運行中バスを取得"""
        active_sites = [1, 2, 6, 7, 11, 12, 19]
        all_buses = []
        
        for site_id in active_sites:
            buses = self.get_all_buses(site_id)
            if buses:
                for bus in buses:
                    bus['siteId'] = site_id
                    all_buses.append(bus)
        
        return all_buses

# 使用例
api = BuskitaAPI()

# 全運行中バス取得
all_buses = api.get_all_active_buses()
print(f"現在運行中: {len(all_buses)}台")

# 特定バス検索
bus_info = api.get_bus_by_work_no("291940", 1)
if bus_info:
    print(f"バス情報: {bus_info}")
```

### バスIDの抽出とリスト化

```python
def extract_bus_ids(buses: List[Dict[str, Any]]) -> Dict[str, List]:
    """バスIDを抽出してリスト化"""
    work_nos = []
    device_uids = []
    
    for bus in buses:
        work_no = bus.get('workNo')
        device_uid = bus.get('device_uid')
        
        if work_no:
            work_nos.append(work_no)
        if device_uid:
            device_uids.append(device_uid)
    
    return {
        'workNos': work_nos,
        'deviceUIDs': device_uids,
        'count': len(buses)
    }

# 使用例
bus_ids = extract_bus_ids(all_buses)
print(f"workNo一覧: {bus_ids['workNos']}")
print(f"deviceUID一覧: {bus_ids['deviceUIDs']}")
```

### リアルタイム監視システム

```python
import time
from datetime import datetime

def monitor_bus_ids(interval_seconds: int = 30):
    """バスIDをリアルタイム監視"""
    api = BuskitaAPI()
    
    while True:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n{timestamp} - バス監視中...")
        
        try:
            buses = api.get_all_active_buses()
            if buses:
                print(f"運行中バス: {len(buses)}台")
                
                # 新しいバスIDをチェック
                bus_ids = extract_bus_ids(buses)
                print(f"workNo: {len(bus_ids['workNos'])}個")
                print(f"最新workNo: {bus_ids['workNos'][-3:] if bus_ids['workNos'] else []}")
                
                # データ保存
                filename = f"bus_ids_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(buses, f, ensure_ascii=False, indent=2)
                
            else:
                print("運行中のバスなし")
                
        except Exception as e:
            print(f"エラー: {e}")
        
        time.sleep(interval_seconds)

# 使用例（バックグラウンドで実行）
# monitor_bus_ids(30)
```

## 📊 現在運行中のバス詳細

| workNo | device_uid | 会社 | 路線名 | 位置 |
|--------|------------|------|--------|------|
| 291940 | jhb_5379914 | JR北海道 | 米里線[バ５] | 札幌市 |
| 292630 | jhb_5343966 | JR北海道 | 手稲線[５５] | 札幌市 |
| 292681 | jhb_5318919 | JR北海道 | もみじ台団地線[新１５] | 札幌市 |
| 292737 | jhb_5244906 | JR北海道 | 上野幌線[新１３] | 札幌市 |
| 293313 | jhb_5345980 | JR北海道 | 江別線[新２６] | 江別市 |
| 293720 | jhb_5346917 | JR北海道 | 江別線[新２６] | 札幌市 |
| 293778 | jhb_5379915 | JR北海道 | 新札幌線[１] | 札幌市 |
| 283223 | ksb_810 | 琴参バス | 丸亀坂出線 | 香川県 |
| 293054 | jtb_6077 | じょうてつ | 南５５ | 札幌市 |
| 300057 | 3eba6939c5e2c1e8 | 旭川電気軌道 | 3番 旭岡行 | 旭川市 |
| 300081 | bba53f2e1275d340 | 旭川電気軌道 | 105番 旭町・末広線 | 旭川市 |
| 300088 | 27cce26e9adfb1df | 旭川電気軌道 | 7４番 緑東大橋・南高線 | 旭川市 |
| 300070 | 38e202117fff2279 | 旭川電気軌道 | 176番 東神楽・東川線 | 旭川市 |
| 290798 | fcb_1962 | 富士急静岡 | 根方線 | 静岡県 |
| 283035 | fjb_1466 | 富士急バス | 富士山駅-甲府駅 | 山梨県 |
| 293705 | e20106e8a29e9cab | 北海道中央 | 札幌都心線 | 札幌市 |
| 300069 | 23b39058366d38bb | 北海道中央 | 札幌都心線 | 札幌市 |

## 🔧 実用的な活用方法

### 1. 特定路線のバス追跡
```python
def track_route_buses(route_name: str):
    """特定路線のバスを追跡"""
    api = BuskitaAPI()
    buses = api.get_all_active_buses()
    
    route_buses = [
        bus for bus in buses 
        if route_name in bus.get('routeNames', {}).get('1', '')
    ]
    
    for bus in route_buses:
        print(f"workNo: {bus['workNo']}, 遅延: {bus.get('delayMinutes', 0)}分")
    
    return route_buses

# 使用例
ebetsu_line_buses = track_route_buses("江別線")
```

### 2. 会社別バス監視
```python
def monitor_company_buses(company_code: str):
    """特定バス会社のバスを監視"""
    api = BuskitaAPI()
    buses = api.get_all_active_buses()
    
    company_buses = [
        bus for bus in buses 
        if bus.get('companyNo') == company_code
    ]
    
    return company_buses

# JR北海道バスを監視
jhb_buses = monitor_company_buses("jhb")
print(f"JR北海道バス: {len(jhb_buses)}台運行中")
```

### 3. 遅延情報の取得
```python
def get_delayed_buses():
    """遅延しているバスを取得"""
    api = BuskitaAPI()
    buses = api.get_all_active_buses()
    
    delayed_buses = [
        bus for bus in buses 
        if bus.get('delayMinutes', 0) > 0
    ]
    
    for bus in delayed_buses:
        print(f"workNo: {bus['workNo']}, 遅延: {bus['delayMinutes']}分, 路線: {bus.get('routeNames', {}).get('1', 'N/A')}")
    
    return delayed_buses
```

## ⚠️ 注意事項

1. **運行時間**: バスの運行時間外は0台となる場合があります
2. **データ更新**: リアルタイム更新ですが、30秒間隔での監視を推奨
3. **サイトID**: サイトID 17, 20-30は無効または利用不可
4. **workNo形式**: 数値型と文字列型が混在することがあります
5. **API制限**: 過度なリクエストは控えめに

## 📚 応用例

### バスダッシュボード作成
取得したバスIDを使用して、リアルタイムバス位置表示システムや遅延情報通知システムを構築できます。

### データ分析
バスIDと位置情報を継続的に収集することで、運行パターンや混雑状況の分析が可能です。

---

**最終更新: 2025年6月15日**  
**現在運行中バス数: 17台 (7社)**  
**主要ID: workNo, device_uid** 