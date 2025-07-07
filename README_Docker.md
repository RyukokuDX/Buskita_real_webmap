# バスキタWebアプリ Docker化

このプロジェクトは、龍谷大学のバス運行情報を表示するFlask WebアプリケーションをDocker化したものです。

## 前提条件

- Docker
- Docker Compose

## 使用方法

### 1. アプリケーションの起動

```bash
# Docker Composeでアプリケーションを起動
docker-compose up -d

# ログを確認
docker-compose logs -f
```

### 2. アプリケーションへのアクセス

アプリケーションは以下のURLでアクセスできます：
- メインページ: http://localhost:5001
- 時刻表ページ: http://localhost:5001/timetable

### 3. アプリケーションの停止

```bash
# アプリケーションを停止
docker-compose down

# コンテナとイメージを削除
docker-compose down --rmi all
```

## 開発モード

開発時にコードの変更を反映させるには、ボリュームマウントが設定されています：

```bash
# 開発モードで起動（コードの変更が即座に反映）
docker-compose up -d

# コードを変更後、コンテナを再起動
docker-compose restart
```

## ファイル構成

```
.
├── Dockerfile              # Dockerイメージの定義
├── docker-compose.yml      # Docker Compose設定
├── .dockerignore          # Dockerビルド時の除外ファイル
├── buskita/               # アプリケーションコード
│   ├── web_map_app.py    # メインアプリケーション
│   ├── requirements.txt   # Python依存関係
│   ├── templates/         # HTMLテンプレート
│   └── static/           # 静的ファイル
└── archive/              # バックアップファイル（ボリュームマウント）
```

## 環境変数

以下の環境変数が設定されています：

- `FLASK_ENV=production`: 本番環境モード
- `PYTHONUNBUFFERED=1`: Pythonの出力バッファリングを無効化

## ヘルスチェック

アプリケーションにはヘルスチェックが設定されており、30秒ごとにアプリケーションの状態を確認します。

## トラブルシューティング

### ポートが既に使用されている場合

```bash
# 使用中のポートを確認
netstat -tulpn | grep 5001

# 別のポートで起動する場合
docker-compose up -d -p 5002:5001
```

### ログの確認

```bash
# リアルタイムでログを確認
docker-compose logs -f buskita-webapp

# 特定のコンテナのログを確認
docker logs <container_id>
```

### コンテナ内でのデバッグ

```bash
# コンテナ内に入る
docker-compose exec buskita-webapp bash

# アプリケーションを手動で起動
python web_map_app.py
```

## 本番環境での使用

本番環境では、以下の点を考慮してください：

1. **セキュリティ**: 適切なファイアウォール設定
2. **ログ管理**: ログローテーションの設定
3. **バックアップ**: データの定期的なバックアップ
4. **監視**: アプリケーションの監視設定

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。 