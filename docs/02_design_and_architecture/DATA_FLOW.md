# アプリケーション データフロー

このドキュメントは、「Ryukoku Bus Navi」の主要なデータの流れを図示したものです。

## データフロー図

```mermaid
graph TD
    subgraph "データ層"
        A["timetable.json<br/>(静的時刻表)"]
        B["帝産バスAPI<br/>(get-buses, get-bus)"]
        C["バックアップファイル<br/>(last_known_buses.json)"]
    end

    subgraph "サーバー処理層"
        D["バックグラウンドスレッド<br/>(10秒間隔データ取得)"]
        E["Flask-Cache<br/>(メモリキャッシュ)"]
        F["routes.py<br/>(URLルーティング)"]
        G["services/__init__.py<br/>(並列API処理)"]
    end

    subgraph "フロントエンド"
        H["リアルタイムマップ<br/>(3秒間隔更新)"]
        I["ダッシュボード<br/>(カウントダウン)"]
        J["時刻表ページ<br/>(静的表示)"]
    end

    B --> D
    D --> E
    E --> F
    A --> F
    C --> F
    F --> G
    G --> H
    G --> I
    F --> J
```
