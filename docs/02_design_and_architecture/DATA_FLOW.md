# アプリケーション データフロー

このドキュメントは、「Ryukoku Bus Navi」の主要なデータの流れを図示したものです。

## データフロー図

```mermaid
graph TD
    subgraph "データ層"
        A["buskita/static/timetable.json"]
        B["帝産バスAPI<br/>(リアルタイムバス位置)"]
    end

    subgraph "サーバー処理 (buskita/)"
        C["routes.py<br/>(URLルーティング)"]
        D["services/__init__.py<br/>(ビジネスロジック)"]
    end
    
    subgraph "ブラウザ表示 (templates/)"
        E["Dashboard<br/>(次のバスまでのカウントダウン)"]
        F["Leaflet Map<br/>(バスアイコンのリアルタイム表示)"]
    end

    A --> C
    B --> D
    D --> C

    C --> E
    C --> F
    D --> E
    D --> F

    style A fill:#e6f3ff,stroke:#367d91
    style B fill:#e6f3ff,stroke:#367d91
    style C fill:#f0f0f0,stroke:#333
    style D fill:#f0f0f0,stroke:#333
    style E fill:#fff5e6,stroke:#d46f00
    style F fill:#fff5e6,stroke:#d46f00
``` 