import os
import sqlite3
import urllib.request
import urllib.error
import io
from flask import Flask, render_template, jsonify, request, Response, send_from_directory
from urllib.parse import urlparse
from PIL import Image
import pillow_heif

pillow_heif.register_heif_opener()

app = Flask(__name__)
DB_PATH = os.environ.get('DB_PATH', '/app/db/monitor.db')

def get_db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index(): return render_template("index.html")

@app.route("/traffic")
def traffic_page(): return render_template("traffic.html")

@app.route("/media")
def media_page(): return render_template("media.html")

@app.route("/credentials")
def credentials_page(): return render_template("credentials.html")

@app.route("/api/traffic")
def get_traffic():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    offset = (page - 1) * per_page
    conn = get_db_conn()
    traffic = [dict(row) for row in conn.execute("SELECT * FROM traffic_logs ORDER BY visit_time DESC LIMIT ? OFFSET ?", (per_page, offset))]
    total_count = conn.execute("SELECT COUNT(*) FROM traffic_logs").fetchone()[0]
    conn.close()
    return jsonify({"traffic": traffic, "total_count": total_count, "page": page, "per_page": per_page})

@app.route("/api/media")
def get_media_api():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    offset = (page - 1) * per_page
    conn = get_db_conn()
    total_count = conn.execute("SELECT COUNT(*) FROM media_logs").fetchone()[0]
    media = [dict(row) for row in conn.execute("""
        SELECT ml.*, tl.platform FROM media_logs ml 
        JOIN traffic_logs tl ON ml.traffic_id = tl.id 
        ORDER BY ml.created_at DESC LIMIT ? OFFSET ?
    """, (per_page, offset))]
    conn.close()
    return jsonify({"media": media, "total_count": total_count, "page": page, "per_page": per_page})

@app.route("/proxy_image")
def proxy_image():
    url = request.args.get('url')
    if "qpic.cn" in url: url = url.replace("wx_fmt=wxgf", "wx_fmt=jpeg")
    elif "xhscdn.com" in url: url = url.replace("/format/heif/", "/format/webp/")
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    if "qpic.cn" in url: headers['Referer'] = 'https://mp.weixin.qq.com/'
    
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req)
    return Response(resp.read(), mimetype=resp.getheader('Content-Type'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
