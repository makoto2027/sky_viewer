## Sky Viewer

天気検索・地図表示の Flask アプリです。

### 必要要件
- Python 3.10+
- OpenWeatherMap API キー

### セットアップ
```bash
cd "/this/repository/path"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 環境変数の設定
プロジェクトルート、または `sky_viewer/` に `.env` を作成:
```bash
OPENWEATHERMAP_API_KEY=あなたのAPIキー
FLASK_SECRET_KEY=ランダムな長い文字列
```

### 起動方法
- ルートからモジュール指定:
```bash
cd "/this/repository/path"
source .venv/bin/activate
flask --app sky_viewer.app --debug run
```

- または `sky_viewer` ディレクトリで起動:
```bash
cd "/this/repository/path/sky_viewer"
source ../.venv/bin/activate
export FLASK_APP=app:app
export FLASK_DEBUG=1
flask run
```

### 主なエンドポイント
- `GET /` トップ（都市名検索）
- `GET /map` マップ表示（現在地/クリック位置の天気）
- `GET /history` 検索履歴（お気に入りフィルタ、期間指定）
- `GET /api/weather?city=Tokyo` 都市名で天気取得
- `GET /api/weather?lat=..&lon=..` 緯度経度で天気取得

### データベース
SQLite を使用。履歴DBは `sky_viewer/database/history.db`。

### トラブルシュート
- Error: Could not locate a Flask application
  - 実行場所を `sky_viewer/` にするか、`--app sky_viewer.app` を付けて実行してください。
- API キー未設定
  - `.env` の `OPENWEATHERMAP_API_KEY` を設定。

### 開発メモ
- 静的ファイル: `sky_viewer/static/`
- テンプレート: `sky_viewer/templates/`
- アプリ本体: `sky_viewer/app.py`

### ライセンス
教育目的のサンプル。必要に応じて追記してください。
