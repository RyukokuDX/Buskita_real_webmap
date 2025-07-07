# Python 3.11ベースイメージを使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージを更新し、必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係をコピーしてインストール
COPY buskita/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY buskita/ .

# ポート5001を公開
EXPOSE 5001

# 環境変数を設定
ENV FLASK_APP=web_map_app.py
ENV FLASK_ENV=production

# 必要なディレクトリを作成
RUN mkdir -p archive

# Gunicornでアプリケーションを起動
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--timeout", "120", "web_map_app:app"] 