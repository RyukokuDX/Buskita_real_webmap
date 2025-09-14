# Ryukoku Bus Navi - リアルタイムバスナビゲーション

## 1. 概要

**Ryukoku Bus Navi** は、龍谷大学 瀬田キャンパスに通う学生・教職員のためのリアルタイムバスナビゲーション・ウェブアプリケーションです。

バス通学における「次のバスはいつ来るの？」「混んでるかな？」といった**学生の日常的な不安を解消し、安心で快適な通学体験を提供すること**を目的としています。

このアプリは、単なる移動を支援するツールではなく、日々の学生生活に「確かな安心」と「小さな幸せ」を届けるパートナーとなることを目指しています。

- **コンセプト詳細:** [docs/01_concept_and_requirements/CONCEPT.md](docs/01_concept_and_requirements/CONCEPT.md)
- **要件定義:** [docs/01_concept_and_requirements/REQUIREMENTS.md](docs/01_concept_and_requirements/REQUIREMENTS.md)

## 2. 主な機能

- **リアルタイムマップ:** 運行中のバスの位置、行き先、遅延時間を地図上にリアルタイムで表示します。
- **混雑度の可視化:** 乗客数に応じてバスのアイコンが色分けされ、一目で混雑状況を把握できます。
- **時刻表 & カウントダウン:** 主要区間の時刻表と、次のバスまでの時間を表示します。
- **堅牢なデータ取得:** API の不調時もバックアップを利用し、安定したサービスを提供します。
- **構造化ロギング:** アプリケーションの動作状況を記録し、迅速な問題解決を支援します。

## 3. 技術スタック

- **バックエンド:** Python, Flask
- **フロントエンド:** HTML, CSS, JavaScript (Leaflet.js)
- **データソース:** バス会社 API, 静的 JSON
- **インフラ:** Docker

- **アーキテクチャ設計:** [docs/02_design_and_architecture/DATA_FLOW.md](docs/02_design_and_architecture/DATA_FLOW.md)

## 4. プロジェクト構造

```
basukita-project/
├── buskita/          # アプリケーション本体 (Flask)
├── docs/             # プロジェクトドキュメント
├── tests/            # テストコード
├── config.py         # 設定ファイル
├── run.py            # 起動スクリプト
├── requirements.txt  # Python依存ライブラリ
├── Dockerfile        # Dockerコンテナ定義
└── docker-compose.yml # Docker Compose定義
```

## 5. 実行方法

### 5.1. ローカル環境での実行

1.  **依存ライブラリのインストール:**

    ```bash
    # 本番環境向け
    pip install -r requirements.txt

    # テストなど開発に必要なライブラリを含む場合
    pip install -r requirements-dev.txt
    ```

2.  **アプリケーションの実行:**
    ```bash
    python3 run.py
    ```
3.  **アクセス:**
    Web ブラウザで `http://127.0.0.1:5001` にアクセスします。

### 5.2. Docker を使用した実行

1.  **Docker コンテナのビルドと起動:**
    ```bash
    docker-compose up --build
    ```
2.  **アクセス:**
    Web ブラウザで `http://127.0.0.1:5001` にアクセスします。
