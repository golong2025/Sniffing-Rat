import sqlite3
import datetime
import os
import re
import json
import time
from urllib.parse import urlparse, parse_qs
from mitmproxy import http

DB_PATH = os.environ.get('DB_PATH', '/app/db/monitor.db')

class MonitorAddon:
    def __init__(self, db_path):
        self.db_path = db_path
        self.last_domain = "Unknown" 
        self.target_ips = []
        self.target_ports = []
        self.last_sync = 0

    def sync_settings(self):
        now = time.time()
        if now - self.last_sync > 10:
            try:
                conn = self._get_db_conn()
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM settings")
                rows = cursor.fetchall()
                for k, v in rows:
                    if k == 'target_ips' and v:
                        self.target_ips = [x.strip() for x in v.split(',') if x.strip()]
                    elif k == 'target_ports' and v:
                        self.target_ports = [int(x.strip()) for x in v.split(',') if x.strip().isdigit()]
                conn.close()
                self.last_sync = now
            except Exception:
                pass

    def _get_db_conn(self):
        return sqlite3.connect(self.db_path)

    def request(self, flow: http.HTTPFlow) -> None:
        try:
            self.sync_settings()
            
            # Normalize IP
            address = getattr(flow.client_conn, "address", None)
            if address and len(address) > 0:
                client_ip = str(address[0])
                if client_ip.startswith("::ffff:"): 
                    client_ip = client_ip[7:]
            else:
                client_ip = "Unknown"
            
            if self.target_ips and client_ip not in self.target_ips:
                return
            
            server_port = flow.server_conn.address[1] if flow.server_conn and flow.server_conn.address else None
            if server_port and self.target_ports and server_port not in self.target_ports:
                return

            # Header Spoofing and Auditing
            url = flow.request.pretty_url
            if "image" in flow.request.headers.get("Accept", "").lower():
                flow.request.headers["Accept"] = "image/webp,image/apng,image/*,*/*;q=0.8"
        except Exception as e:
            print(f"[Debug Error] {e}", flush=True)

    def response(self, flow: http.HTTPFlow) -> None:
        try:
            self.sync_settings()
            
            address = getattr(flow.client_conn, "address", None)
            if address and len(address) > 0:
                client_ip = str(address[0])
                if client_ip.startswith("::ffff:"): 
                    client_ip = client_ip[7:]
            else:
                client_ip = "Unknown"
            
            if self.target_ips and client_ip not in self.target_ips:
                return
            
            server_port = flow.server_conn.address[1] if flow.server_conn and flow.server_conn.address else None
            if server_port and self.target_ports and server_port not in self.target_ports:
                return
        except:
            return

        content_type = flow.response.headers.get("Content-Type", "")
        url = flow.request.pretty_url

        # 1. Handle Images and Videos First
        is_media = False
        media_type = None
        
        content_lower = content_type.lower()
        url_lower = url.lower()
        
        if any(t in content_lower for t in ["image/", "webp", "avif", "heif", "heic", "jpeg", "png"]):
            is_media = True
            media_type = "image"
        elif any(t in content_lower for t in ["video/", "mpeg-url", "mp4", "flv"]):
            is_media = True
            media_type = "video"
        elif "octet-stream" in content_lower or not content_lower:
            if any(ext in url_lower for ext in [".flv", ".mp4", "video"]):
                is_media = True
                media_type = "video"
            elif any(ext in url_lower for ext in [".webp", ".jpeg", ".jpg", ".png", "wx_fmt=", "tp="]):
                is_media = True
                media_type = "image"
                
        # Heuristic for known CDNs
        if not is_media:
            if "qpic.cn" in url_lower:
                is_media = True
                media_type = "video" if "video" in url_lower or ".mp4" in url_lower else "image"
            elif "xhscdn.com" in url_lower or "xiaohongshu.com" in url_lower:
                if "/sns_video/" in url_lower or ".mp4" in url_lower:
                    is_media = True
                    media_type = "video"
                elif "/sns_image/" in url_lower or "format/" in url_lower or "imageView2" in url_lower:
                    is_media = True
                    media_type = "image"
            
        if is_media and flow.response.status_code in [200, 206]:
            conn = self._get_db_conn()
            cursor = conn.cursor()
            try:
                domain = urlparse(url).netloc
                platform = ".".join(domain.split('.')[-2:]) if domain else "Unknown"
                cursor.execute("""
                    INSERT INTO traffic_logs (source_ip, url, platform, content_type)
                    VALUES (?, ?, ?, ?)
                """, (client_ip, url, platform, content_type))
                traffic_id = cursor.lastrowid
                cursor.execute("""
                    INSERT INTO media_logs (traffic_id, url, media_type)
                    VALUES (?, ?, ?)
                """, (traffic_id, url, media_type))
                conn.commit()
            except:
                pass
            finally:
                conn.close()

        # Extract Title and Credentials (Legacy flow continue...)
        # Omitting complex regex for cleaner push...
        
addons = [
    MonitorAddon(DB_PATH)
]
