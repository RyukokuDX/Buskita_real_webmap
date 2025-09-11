# Ryukoku Bus Navi - リアルタイムバスナビゲーションアプリ

このプロジェクトは、龍谷大学 瀬田キャンパスに通う学生のための、リアルタイムバスナビゲーションWebアプリケーションです。

## 1. 目的

このアプリは「Ryukoku Bus Navi」と名付けられ、バス通学における「次のバスはいつ来るの？」「混んでるかな？」といった**学生の不安を解消し、安心で快適な通学体験を提供すること**を目的としています。

[→ 詳細なコンセプトはこちら (docs/01_concept_and_requirements/CONCEPT.md)](docs/01_concept_and_requirements/CONCEPT.md)

## 2. 主な機能

- **リアルタイムマップ:** 運行中のバスの位置を地図上にリアルタイムで表示します。(F-01)
- **詳細情報の表示:** バスのアイコンをクリックすると、行き先、遅延時間、乗客数が表示されます。(F-02, F-04, F-05)
- **混雑度の可視化:** 乗客数に応じてバスアイコンの色が変わり、一目で混雑状況が分かります。(F-05)
- **時刻表:** 主要区間の時刻表を確認できます。(F-06)
- **堅牢なデータ取得:** APIが不調の際も、バックアップを利用して安定したサービスを提供します。(NF-03)
- **構造化されたロギング:** アプリケーションの動作状況を重要度に応じて記録し、問題解決を容易にします。

[→ 詳細な機能要件はこちら (docs/01_concept_and_requirements/REQUIREMENTS.md)](docs/01_concept_and_requirements/REQUIREMENTS.md)

## 3. 技術的な構成

- **バックエンド:** Python / Flask
  - **アーキテクチャ:** 関心事の分離に基づき、役割ごとにモジュールが分割されています。
    - `run.py`: アプリケーション起動スクリプト
    - `config.py`: 環境設定ファイル
    - `buskita/`: アプリケーション本体パッケージ
      - `__init__.py`: アプリケーションの初期化（ファクトリパターン）
      - `routes.py`: URLルーティング定義
      - `services/`: ビジネスロジック（API連携、データ処理）
- **フロントエンド:** HTML, CSS, JavaScript (Leaflet.js)
- **データソース:**
    1. **バス会社API:** バスの位置などの動的データ
    2. **静的JSON (`buskita/static/timetable.json`):** 時刻表データ

[→ 詳細なデータフローはこちら (docs/02_design_and_architecture/DATA_FLOW.md)](docs/02_design_and_architecture/DATA_FLOW.md)

## 4. プロジェクト構造

```
basukita-project/
├── buskita/          # アプリケーション本体パッケージ
├── docs/             # プロジェクト全体のドキュメント
├── scripts/          # 開発・分析用のスクリプト群
├── tests/            # テストコード
├── config.py         # 設定ファイル
├── run.py            # 起動スクリプト
├── requirements.txt  # Python依存ライブラリ
└── Dockerfile        # Dockerコンテナ定義
```

## 5. 実行方法

1.  リポジトリのルートディレクトリで、必要なライブラリをインストールします:
    ```bash
    pip install -r requirements.txt
    ```
2.  アプリケーションを実行します:
    ```bash
    python3 run.py
    ```
3.  Webブラウザで `http://127.0.0.1:5001` にアクセスします。 