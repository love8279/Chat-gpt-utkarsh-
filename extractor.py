import os
import requests
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from base64 import b64decode, b64encode

# Config
API_URL = "https://application.utkarshapp.com/index.php/data_model"
key_chars = "%!F*&^$)_*%3f&B+"
iv_chars = "#*$DJvyw2w%!_-$@"

# --- AAPKA UPDATED TOKEN AUR ID ---
MY_JWT = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjEwNDc4NjY3IiwiZGV2aWNlX3R5cGUiOiIxIiwidmVyc2lvbl9jb2RlIjoiMTgwIiwiaWNyIjoiMiIsImlhdCI6MTc2NzI3MjcyOSwiZXhwIjoxNzY5NDMyNzI5fQ.T-fr6kOWXO4Aycki9Yw-zcEXdQoZS_2jMWSGEw2tWb0"
MY_UID = "10478667"
# ---------------------------------

def decrypt_stream(enc):
    try:
        if not enc: return None
        enc = b64decode(enc)
        # Standard Static Keys for Utkarsh
        k, v = '%!$!%_$&!%F)&^!^'.encode(), '#*y*#2yJ*#$wJv*v'.encode()
        cipher = AES.new(k, AES.MODE_CBC, v)
        dec = cipher.decrypt(enc)
        try: 
            text = unpad(dec, 16).decode('utf-8')
        except: 
            text = dec.decode('utf-8', errors='ignore')
        
        s, e = text.find('{'), text.rfind('}')
        if s != -1:
            return text[s:e+1]
        return None
    except Exception:
        return None

def encrypt_stream(text):
    k, v = '%!$!%_$&!%F)&^!^'.encode(), '#*y*#2yJ*#$wJv*v'.encode()
    cipher = AES.new(k, AES.MODE_CBC, v)
    return b64encode(cipher.encrypt(pad(text.encode(), 16))).decode()

def post_request(path, data, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    payload_data = json.dumps(data).encode()
    enc = b64encode(cipher.encrypt(pad(payload_data, 16))).decode() + ":"
    h = {
        "Authorization": "Bearer 152#svf346t45ybrer34yredk76t", 
        "userid": MY_UID, 
        "version": "152",
        "User-Agent": "okhttp/4.9.1",
        "X-Requested-With": "com.utkarshnew.android"
    }
    try:
        r = requests.post(f"{API_URL}{path}", headers=h, data=enc, timeout=15)
        if r.status_code == 200:
            c_dec = AES.new(key, AES.MODE_CBC, iv)
            decrypted = unpad(c_dec.decrypt(b64decode(r.text.split(":")[0])), 16).decode()
            return json.loads(decrypted)
    except:
        pass
    return {}

def extract_course_to_file(ci):
    session = requests.Session()
    filename = f"course_{ci}.txt"
    
    h = {
        'jwt': MY_JWT,
        'User-Agent': 'okhttp/4.9.1',
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'com.utkarshnew.android',
        'version_code': '180',
        'device_type': '1'
    }
    
    ukey = "".join(key_chars[int(i)] for i in (MY_UID + "1524567456436545")[:16]).encode()
    uiv = "".join(iv_chars[int(i)] for i in (MY_UID + "1524567456436545")[:16]).encode()

    try:
        with open(filename, "w", encoding="utf-8") as f:
            # Layer 1: Main Data
            d3 = {"course_id": ci, "revert_api": "1#0#0#1", "parent_id": 0, "tile_id": "15330", "layer": 1, "type": "course_combo"}
            r4_resp = session.post('https://online.utkarsh.com/web/Course/tiles_data', headers=h, data={'tile_input': encrypt_stream(json.dumps(d3))})
            
            if r4_resp.status_code != 200:
                return f"Error: Server Status {r4_resp.status_code}. (Token Expired?)"

            dr3_raw = decrypt_stream(r4_resp.json().get("response"))
            if not dr3_raw: return "Error: Data Decryption Failed. Check your Token."
            
            dr3 = json.loads(dr3_raw)
            l1_data = dr3.get("data", [])
            items = l1_data.get("list", []) if isinstance(l1_data, dict) else l1_data

            if not items: return "Error: No items found in this Batch."

            for item in items:
                if not isinstance(item, dict): continue
                fi = item.get("id")
                f.write(f"\n\n--- SECTION: {item.get('title')} ---\n")
                
                # Layer 2: Subjects
                d5 = {"course_id": fi, "layer": 1, "page": 1, "parent_id": fi, "revert_api": "1#1#0#1", "tile_id": "0", "type": "content"}
                r5_resp = session.post('https://online.utkarsh.com/web/Course/tiles_data', headers=h, data={'tile_input': encrypt_stream(json.dumps(d5))})
                dr4_raw = decrypt_stream(r5_resp.json().get("response"))
                if not dr4_raw: continue
                
                dr4 = json.loads(dr4_raw)
                sub_list = dr4.get("data", {}).get("list", []) if isinstance(dr4.get("data"), dict) else []

                for sub in sub_list:
                    if not isinstance(sub, dict): continue
                    sfi = sub.get("id")
                    
                    # Layer 3: Topics
                    d7 = {"course_id": fi, "parent_id": fi, "layer": 2, "page": 1, "subject_id": sfi, "topic_id": sfi, "type": "content"}
                    r6_resp = session.post('https://online.utkarsh.com/web/Course/get_layer_two_data', headers=h, data={'layer_two_input_data': b64encode(json.dumps(d7).encode()).decode()})
                    dr5_raw = decrypt_stream(r6_resp.json().get("response"))
                    if not dr5_raw: continue
                    
                    dr5 = json.loads(dr5_raw)
                    top_list = dr5.get("data", {}).get("list", []) if isinstance(dr5.get("data"), dict) else []

                    for top in top_list:
                        if not isinstance(top, dict): continue
                        ti = top.get("id")
                        
                        # Layer 4: Final Videos/Links
                        d9 = {"course_id": fi, "parent_id": fi, "layer": 3, "page": 1, "subject_id": sfi, "topic_id": ti, "type": "content"}
                        r7_resp = session.post('https://online.utkarsh.com/web/Course/get_layer_two_data', headers=h, data={'layer_two_input_data': b64encode(json.dumps(d9).encode()).decode()})
                        dr6_raw = decrypt_stream(r7_resp.json().get("response"))
                        if not dr6_raw: continue
                        
                        dr6 = json.loads(dr6_raw)
                        vids = dr6.get("data", {}).get("list", []) if isinstance(dr6.get("data"), dict) else []

                        for v in vids:
                            if not isinstance(v, dict): continue
                            title = v.get('title', 'No Title')
                            jti = v.get("payload", {}).get("tile_id") if isinstance(v.get("payload"), dict) else None
                            
                            if jti:
                                try:
                                    j5 = post_request("/meta_distributer/on_request_meta_source", {"course_id": fi, "tile_id": jti, "type": "video", "userid": MY_UID}, ukey, uiv)
                                    v_data = j5.get("data", {})
                                    url = v_data.get("link") or (v_data.get("bitrate_urls", [{}])[0].get("url") if v_data.get("bitrate_urls") else None)
                                    if url: 
                                        f.write(f"{title}: {url.split('?Expires=')[0]}\n")
                                except:
                                    continue
        return filename
    except Exception as e:
        return f"Error: {str(e)}"
        
