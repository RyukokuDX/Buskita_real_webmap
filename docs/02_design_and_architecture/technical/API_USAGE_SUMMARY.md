# buskita.com API エンドポイント使用ガイド

PlaywrightによるWebスクレイピングで発見された**11個のAPIエンドポイント**の詳細な使用方法

## 📚 発見されたAPIエンドポイント一覧

| # | エンドポイント | 機能 | 必須パラメータ | データ件数 |
|---|---|---|---|---|
| 1 | `get-bus` | バス位置情報取得 | `language`, `workNo`, `siteId` | 0台（現在） |
| 2 | `get-companies-dictionary` | バス会社辞書 | `language` | 29社 |
| 3 | `get-landmarks-dictionary` | ランドマーク辞書 | `language`, `siteId` | 30件 |
| 4 | `get-dialog-informations` | 重要なお知らせ | `language`, `siteId` | 1件 |
| 5 | `get-holidays` | 祝日情報 | `language`, `siteId` | 8日 |
| 6 | `get-busstops-group` | バス停グループ | `language`, `siteId` | 2グループ |
| 7 | `get-busstops-grouping` | バス停グルーピング | `language`, `siteId` | 11件 |
| 8 | `get-maintenances` | メンテナンス情報 | `language`, `siteId` | 0件（現在） |
| 9 | `get-noriba-alias` | のりば別名 | `language`, `siteId` | 0件（現在） |
| 10 | `get-ui-dictionary-version` | UI辞書バージョン | `language`, `siteId` | ver.3 |
| 11 | `get-busstops-version` | バス停辞書バージョン | `language`, `siteId` | ver.3 |

## 🚀 基本的な使用方法

### 1. バス会社辞書の取得

```python
import requests

response = requests.post('https://api.buskita.com/get-companies-dictionary', 
                        json={'language': 1})
companies = response.json()['companiesDictionary']

for company in companies:
    print(f"{company['name']} ({company['shortName']})")
    print(f"  会社コード: {company['company_no']}")
    print(f"  カラー: 前景={company['fgcc']}, 背景={company['bgcc']}")
```

**結果例:**
- JR北海道バス (JHB) - 前景=#ffffff, 背景=#68bdeb
- 帝産湖南交通 (帝産湖南) - 前景=#000000, 背景=#f4a14e
- 富士急バス (富士急) - 前景=#ffffff, 背景=#e83416

### 2. ランドマーク情報の取得

```python
response = requests.post('https://api.buskita.com/get-landmarks-dictionary', 
                        json={'language': 1, 'siteId': 9})
landmarks = response.json()['landmarksDictionary']

for landmark in landmarks:
    lat = landmark['position']['latitude']
    lng = landmark['position']['longitude']
    print(f"{landmark['name']}: ({lat}, {lng})")
```

**結果例:**
- 龍谷大学: (34.964307, 135.939629)
- 立命館大学びわこ・くさつキャンパス: (34.9815964, 135.9622617)
- 滋賀医科大学病院: (34.973333, 135.951523)

### 3. 重要なお知らせの取得

```python
response = requests.post('https://api.buskita.com/get-dialog-informations', 
                        json={'language': 1, 'siteId': 9})
informations = response.json()['informations']

for info in informations:
    print(f"【{info['title']}】")
    print(f"公開日: {info['published']}")
    print(f"詳細URL: {info['targetUrl']}")
```

**現在のお知らせ:**
- 【４月１日から】大津市内(石山駅方面)の一部区間の運賃変更について
- 公開日: 2025-02-07T17:15:00+09:00

## 🔧 パラメータの詳細

### 共通パラメータ

| パラメータ | 型 | 必須 | 説明 | 例 |
|---|---|---|---|---|
| `language` | int | ✓ | 言語設定 | `1` (日本語), `2` (英語) |
| `siteId` | int | ✓ | サイトID | `9` (滋賀帝産), `1` (JR北海道) |

### エンドポイント固有パラメータ

#### `get-bus`
- `workNo` (str): 作業番号 - 例: `"48385"`

#### `get-holidays`
- 会社別の祝日情報を返す
- `tkt` (帝産湖南交通): 8日間の祝日

#### `get-busstops-group`
- `version` (int, optional): グループバージョン

## 📊 レスポンス構造

### バス会社辞書 (`get-companies-dictionary`)
```json
{
  "language": 1,
  "companiesDictionary": [
    {
      "company_no": "tkt",
      "name": "帝産湖南交通",
      "shortName": "帝産湖南",
      "fgcc": "#000000",
      "bgcc": "#f4a14e"
    }
  ]
}
```

### ランドマーク辞書 (`get-landmarks-dictionary`)
```json
{
  "landmarksDictionary": [
    {
      "id": 314,
      "name": "龍谷大学",
      "imageUrl": "",
      "informationUrl": "",
      "position": {
        "latitude": "34.964307",
        "longitude": "135.939629"
      },
      "category": {
        "category": null,
        "categoryName": null,
        "categoryMapUrl": null
      }
    }
  ],
  "language": 1
}
```

## 💡 実用的な活用例

### 1. 大学周辺のランドマーク検索
```python
def find_universities():
    response = requests.post('https://api.buskita.com/get-landmarks-dictionary', 
                            json={'language': 1, 'siteId': 9})
    landmarks = response.json()['landmarksDictionary']
    
    universities = [lm for lm in landmarks if '大学' in lm['name']]
    return universities
```

### 2. バス会社カラーマップ作成
```python
def create_company_colors():
    response = requests.post('https://api.buskita.com/get-companies-dictionary', 
                            json={'language': 1})
    companies = response.json()['companiesDictionary']
    
    color_map = {}
    for company in companies:
        color_map[company['company_no']] = {
            'name': company['name'],
            'foreground': company['fgcc'],
            'background': company['bgcc']
        }
    return color_map
```

### 3. お知らせ監視システム
```python
import time

def monitor_news():
    while True:
        response = requests.post('https://api.buskita.com/get-dialog-informations', 
                                json={'language': 1, 'siteId': 9})
        news = response.json()['informations']
        
        if news:
            latest = news[0]
            important_keywords = ['運賃', '運休', 'ダイヤ', '路線']
            if any(keyword in latest['title'] for keyword in important_keywords):
                print("🚨 重要なお知らせが更新されました！")
                print(f"タイトル: {latest['title']}")
                print(f"詳細: {latest['targetUrl']}")
        
        time.sleep(3600)  # 1時間ごとにチェック
```

## 🌟 サイトID一覧

| サイトID | 事業者 | 主な対象エリア |
|---|---|---|
| 1 | JR北海道バス | 北海道 |
| 9 | 滋賀帝産 | 滋賀県 |

## ⚠️ 注意事項

1. **必須パラメータ**: ほとんどのエンドポイントで `language` と `siteId` が必須
2. **エラーレスポンス**: パラメータ不足の場合は `HTTP 400` エラー
3. **データの更新**: バージョン管理されているため、定期的にバージョンを確認
4. **レート制限**: 過度なリクエストは避けること

## 📝 今回の発見の意義

1. **10個の新規エンドポイント発見**: 従来の `get-bus` に加えて多彩なAPI群を発見
2. **29社のバス会社情報**: 全国のバス事業者の詳細情報にアクセス可能
3. **30件のランドマーク情報**: GPS座標付きの施設情報で地図アプリ開発に活用
4. **リアルタイム情報**: 運賃変更等の重要なお知らせを自動取得可能

これらのAPIを組み合わせることで、包括的なバス情報システムの構築が可能になりました！ 