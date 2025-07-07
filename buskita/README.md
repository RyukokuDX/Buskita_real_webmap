# Buskita API 研究プロジェクト

バスキタ（buskita.com）APIの包括的な調査・分析プロジェクトです。

## プロジェクト概要

このプロジェクトでは、バスキタAPIの機能を詳細に調査し、バス位置情報の取得方法やAPIエンドポイントの発見、技術仕様の分析を行いました。

### 主な成果

- **APIエンドポイント発見**: 1個から11個のエンドポイントを発見
- **バスID取得システム**: 全国17台のバスの実時間追跡システムを構築
- **技術分析**: アプリのアーキテクチャと技術スタックを解明
- **包括的ドキュメント**: 使用方法とAPIガイドを完備

## ディレクトリ構造

```
buskita/
├── README.md                    # このファイル
├── docs/                        # ドキュメント類
│   ├── バスキタアプリ技術分析レポート.md
│   ├── バスID取得完全ガイド.md
│   ├── API_USAGE_SUMMARY.md
│   └── bus_id_guide_20250615_225957.md
├── scripts/                     # Pythonスクリプト
│   ├── bus_location_tracker.py          # 基本バス位置追跡
│   ├── ohmi_bus_location_tracker.py     # 近江バス専用追跡
│   ├── bus_id_explorer.py               # バスID探索ツール
│   ├── bus_id_analyzer.py               # バスID分析ツール
│   ├── bus_data_structure_analyzer.py   # データ構造分析
│   ├── bus_monitor.py                   # バス監視ツール
│   └── buskita_api_usage_guide.py       # API使用ガイド
├── data/                        # データファイル
│   ├── api_responses/           # APIレスポンスデータ
│   ├── raw_data/               # 生データ（バス位置情報等）
│   └── screenshots/            # スクリーンショット
├── analysis/                   # 分析データ
├── temp/                      # 一時ファイル
└── web_assets/               # Webアセット（HTML/CSS/JS）
```

## 主要機能

### 1. バス位置追跡
- リアルタイムでバスの位置情報を取得
- 30秒間隔での自動更新
- JSONファイルでの位置履歴保存

### 2. APIエンドポイント探索
- 11個のAPIエンドポイントを発見・分析
- 各エンドポイントの詳細な使用方法を文書化
- バス会社情報、停留所情報、メンテナンス情報等を取得

### 3. バスID管理システム
- 全国17台のアクティブなバスを特定
- workNoとdevice_uidの2つの識別システム
- 7つのサイト（バス会社）にわたる運行状況監視

### 4. 技術分析
- ネイティブアプリとWebアプリの両方をサポート
- MediaMagic Co.,Ltd.による開発
- マルチテナント・アーキテクチャ

## 使用方法

### 環境セットアップ
```bash
# 必要なパッケージのインストール
pip install -r requirements.txt
```

### 基本的なバス位置追跡
```bash
cd scripts
python bus_location_tracker.py
```

### バスID探索
```bash
cd scripts
python bus_id_explorer.py
```

### API使用例
```bash
cd scripts
python buskita_api_usage_guide.py
```

## 発見されたAPIエンドポイント

1. `get-bus` - バス位置情報取得
2. `get-buses` - 全アクティブバス一覧
3. `get-maintenances` - メンテナンス情報
4. `get-companies-dictionary` - バス会社情報
5. `get-holidays` - 休日情報
6. `get-noriba-alias` - 停留所別名
7. `get-ui-dictionary-version` - UI辞書バージョン
8. `get-busstops-version` - 停留所辞書バージョン
9. `get-landmarks-dictionary` - ランドマーク情報
10. `get-busstops-group` - 停留所グループ
11. `get-dialog-informations` - 重要なお知らせ
12. `get-busstops-grouping` - 停留所関係性

## 対象バス会社

現在追跡可能な7つのバス会社：
- JR北海道バス (jhb) - 7台
- 琴参バス (ksb) - 1台  
- じょうてつ (jtb) - 1台
- 旭川電気軌道 (adk) - 4台
- 富士急静岡バス (fcb) - 1台
- 富士急バス (fjb) - 1台
- 北海道中央バス (hkt) - 2台

## ライセンス

このプロジェクトは研究・教育目的で作成されています。
バスキタAPIの利用は各バス会社の利用規約に従ってください。

## 貢献

バグ報告や機能改善の提案は歓迎します。 