# AI エージェント向けタスク指示書：Buskita プロジェクトのリファクタリング

## **基本指令**

あなたは、これから与えられるタスクを、指定された順序で、一字一句違わずに実行しなければならない。各ステップの完了を確認した上で、次のステップに進むこと。自己判断による逸脱は許可しない。

---

### **フェーズ 1：ファイルとディレクトリの整理**

**タスク 1.1：旧ドキュメント用の`archive`ディレクトリを作成せよ。**

- **使用ツール:** `execute_command`
- **実行コマンド:**
  ```bash
  mkdir -p docs/archive
  ```

**タスク 1.2：開発ログ及び一時ファイルを`archive`ディレクトリに移動せよ。**

- **使用ツール:** `execute_command`
- **実行コマンド:**
  ```bash
  mv docs/03_planning_and_analysis/CURSOR_CLINE_GUIDE.md docs/03_planning_and_analysis/CURSOR_CLINE_WORKFLOW.md docs/04_logs_and_reports/ASSISTANT_SELF_ANALYSIS.md docs/04_logs_and_reports/DEVELOPMENT_LOG.md docs/archive/
  ```
- **注意:** 対象ファイルが存在しないことによるエラーは無視し、次のファイルの移動を続行せよ。

**タスク 1.3：設定ファイル内のバックアップファイルパスを修正せよ。**

- **使用ツール:** `replace_in_file`
- **対象ファイル:** `config.py`
- **変更内容:**
  ```diff
  ------- SEARCH
  # APIがダウンした際に使用するバックアップファイルのパス
  BACKUP_FILE = "buskita/archive/last_known_buses.json"
  =======
  # APIがダウンした際に使用するバックアップファイルのパス
  BACKUP_FILE = "buskita/data/last_known_buses.json"
  +++++++ REPLACE
  ```

**タスク 1.4：`.gitignore`を更新し、データファイルが Git の追跡対象となるようにせよ。**

- **使用ツール:** `replace_in_file`
- **対象ファイル:** `.gitignore`
- **変更内容:**
  ```diff
  ------- SEARCH
  # Project specific ignores
  # Ignore JSON files in the root, but not the timetable
  *.json
  !buskita/static/timetable.json
  =======
  # Project specific ignores
  # Ignore JSON files in the root, but not the timetable or data files
  *.json
  !buskita/static/timetable.json
  !buskita/data/*.json
  +++++++ REPLACE
  ```

---

### **フェーズ 2：依存関係の管理**

**タスク 2.1：開発専用の依存関係ファイル`requirements-dev.txt`を新規作成せよ。**

- **使用ツール:** `write_to_file`
- **対象ファイル:** `requirements-dev.txt`
- **書き込む内容:**
  ```
  # Development and testing libraries
  playwright>=1.40.0
  pandas>=2.0.0
  pytest>=7.0.0
  pytest-mock>=3.0.0
  ```

**タスク 2.2：本番用の`requirements.txt`から開発用ライブラリを削除せよ。**

- **使用ツール:** `write_to_file`
- **対象ファイル:** `requirements.txt`
- **書き込む内容（これによりファイルは上書きされる）:**
  ```
  # Production libraries
  requests>=2.31.0
  beautifulsoup4>=4.12.0
  json5>=0.9.0
  flask>=2.3.0
  gunicorn>=20.1.0
  python-dotenv>=1.0.0
  googlemaps>=4.10.0
  Flask-Caching>=2.0.0
  ```

---

### **フェーズ 3：コードの近代化とテストの追加**

**タスク 3.1：Flask アプリケーションの初期化処理を標準的な設定読み込み方法にリファクタリングせよ。**

- **使用ツール:** `replace_in_file`
- **対象ファイル:** `buskita/__init__.py`
- **変更内容:**

  - **注意:** 以下の`SEARCH`ブロックは一般的な Flask アプリケーションの構造に基づく予測である。実行前に`buskita/__init__.py`の実際の内容を読み取り、`SEARCH`ブロックをファイル内容と完全に一致するように調整してから`replace_in_file`を実行せよ。

  ```diff
  ------- SEARCH
  from flask import Flask
  from buskita.extensions import cache
  from buskita.main.routes import main_bp
  import logging
  from logging.handlers import RotatingFileHandler
  import os

  def create_app():
      app = Flask(__name__)
      app.config.from_object('config')  # Load config from config.py

      # Initialize extensions
      cache.init_app(app)

      # Register blueprints
      app.register_blueprint(main_bp)

      # Configure logging
      if not os.path.exists('logs'):
          os.mkdir('logs')
      file_handler = RotatingFileHandler('logs/buskita.log', maxBytes=10240, backupCount=10)
      file_handler.setFormatter(logging.Formatter(
          '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
      file_handler.setLevel(logging.INFO)
      app.logger.addHandler(file_handler)
      app.logger.setLevel(logging.INFO)
      app.logger.info('Buskita startup')

      return app
  =======
  from flask import Flask
  from buskita.extensions import cache
  from buskita.main.routes import main_bp
  import logging
  from logging.handlers import RotatingFileHandler
  import os

  def create_app():
      app = Flask(__name__)
      # Load config from config.py using the recommended method
      app.config.from_object('config')

      # Initialize extensions
      cache.init_app(app)

      # Register blueprints
      app.register_blueprint(main_bp)

      # Configure logging
      if not app.debug and not app.testing:
          if not os.path.exists('logs'):
              os.mkdir('logs')
          file_handler = RotatingFileHandler('logs/buskita.log', maxBytes=10240, backupCount=10)
          file_handler.setFormatter(logging.Formatter(
              '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
          file_handler.setLevel(logging.INFO)
          app.logger.addHandler(file_handler)
          app.logger.setLevel(logging.INFO)
          app.logger.info('Buskita startup')

      return app
  +++++++ REPLACE
  ```

**タスク 3.2：ルーティングの基本テストを行うためのテストファイル`tests/test_routes.py`を新規作成せよ。**

- **使用ツール:** `write_to_file`
- **対象ファイル:** `tests/test_routes.py`
- **書き込む内容:**

  ```python
  import pytest
  from buskita import create_app

  @pytest.fixture
  def app():
      app = create_app()
      app.config.update({
          "TESTING": True,
      })
      yield app

  @pytest.fixture
  def client(app):
      return app.test_client()

  def test_index_route(client):
      """Test that the index page loads correctly."""
      response = client.get('/')
      assert response.status_code == 200
      assert b"Ryukoku Bus Navi" in response.data
  ```

---

### **フェーズ 4：最終検証**

**タスク 4.1：Docker 環境を完全に再構築し、アプリケーションを起動せよ。**

- **使用ツール:** `execute_command`
- **実行コマンド:**
  ```bash
  docker-compose down -v && docker-compose up --build -d
  ```

**タスク 4.2：テストスイートを実行し、すべてのテストが成功することを確認せよ。**

- **使用ツール:** `execute_command`
- **実行コマンド:**
  ```bash
  pytest
  ```

**タスク 4.3：アプリケーションのヘルスチェックを行い、正常に応答することを確認せよ。**

- **使用ツール:** `execute_command`
- **実行コマンド:**
  ```bash
  curl --head http://127.0.0.1:5001
  ```
- **検証:** `HTTP/1.1 200 OK` が返却されることを確認せよ。

---

**以上で指示を終了する。**
