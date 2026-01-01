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

def decrypt_stream(enc):
    try:
        if not enc: return None
        enc = b64decode(enc)
        k, v = '%!$!%_$&!%F)&^!^'.encode(), '#*y*#2yJ*#$wJv*v'.encode()
        cipher = AES.new(k, AES.MODE_CBC, v)
        dec = cipher.decrypt(enc)
        try: text = unpad(dec, 16).decode('utf-8')
        except: text = dec.decode('utf-8', errors='ignore')
        s, e = text.find('{'), text.rfind('}')
        return text[s:e+1] if s != -1 else None
    except: return None

def encrypt_stream(text):
    k, v = '%!$!%_$&!%F)&^!^'.encode(), '#*y*#2yJ*#$wJv*v'.encode()
    cipher = AES.new(k, AES.MODE_CBC, v)
    return b64encode(cipher.encrypt(pad(text.encode(), 16))).decode()

def post_request(path, data, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    enc = b64encode(cipher.encrypt(pad(json.dumps(data).encode(), 16))).decode() + ":"
    h = {"Authorization": "Bearer 152#svf346t45ybrer34yredk76t", "userid": str(data.get("userid", "0")), "version": "152"}
    r = requests.post(f"{API_URL}{path}", headers=h, data=enc)
    c_dec = AES.new(key, AES.MODE_CBC, iv)
    return json.loads(unpad(c_dec.decrypt(b64decode(r.text.split(":")[0])), 16).decode())

def extract_course_to_file(ci):
    session = requests.Session()
    filename = f"course_{ci}.txt"
    
    # --- YAHAN APNI DETAILS ZAROOR DALEIN ---
    email = "REPLACE_WITH_MOBILE" 
    password = "REPLACE_WITH_PASSWORD"

    try:
        r1 = session.get('https://online.utkarsh.com/')
        csrf = r1.cookies.get('csrf_name')
        l_res = session.post('https://online.utkarsh.com/web/Auth/login', data={'csrf_name': csrf, 'mobile': email, 'password': password, 'submit': 'LogIn'}).json()
        
        dr1 = json.loads(decrypt_stream(l_res.get("response")))
        jwt, token, uid = dr1["data"]["jwt"], dr1["token"], str(dr1["data"]["id"])
        h = {'token': token, 'jwt': jwt, 'User-Agent': 'Mozilla/5.0'}
        ukey = "".join(key_chars[int(i)] for i in (uid + "1524567456436545")[:16]).encode()
        uiv = "".join(iv_chars[int(i)] for i in (uid + "1524567456436545")[:16]).encode()

        with open(filename, "w", encoding="utf-8") as f:
            d3 = {"course_id": ci, "revert_api": "1#0#0#1", "parent_id": 0, "tile_id": "15330", "layer": 1, "type": "course_combo"}
            r4 = session.post('https://online.utkarsh.com/web/Course/tiles_data', headers=h, data={'tile_input': encrypt_stream(json.dumps(d3)), 'csrf_name': csrf}).json()
            dr3 = json.loads(decrypt_stream(r4.get("response")))
            
            # FIXED: Handling 'list' vs 'dict' error
            l1_data = dr3.get("data", [])
            items = l1_data.get("list", []) if isinstance(l1_data, dict) else l1_data

            for item in items:
                fi = item.get("id")
                f.write(f"\n--- {item.get('title')} ---\n")
                
                # Layer 2
                d5 = {"course_id": fi, "layer": 1, "page": 1, "parent_id": fi, "revert_api": "1#1#0#1", "tile_id": "0", "type": "content"}
                r5 = session.post('https://online.utkarsh.com/web/Course/tiles_data', headers=h, data={'tile_input': encrypt_stream(json.dumps(d5)), 'csrf_name': csrf}).json()
                dr4 = json.loads(decrypt_stream(r5.get("response")))
                sub_list = dr4.get("data", {}).get("list", []) if isinstance(dr4.get("data"), dict) else []

                for sub in sub_list:
                    sfi = sub.get("id")
                    d7 = {"course_id": fi, "parent_id": fi, "layer": 2, "page": 1, "subject_id": sfi, "topic_id": sfi, "type": "content"}
                    r6 = session.post('https://online.utkarsh.com/web/Course/get_layer_two_data', headers=h, data={'layer_two_input_data': base64.b64encode(json.dumps(d7).encode()).decode(), 'csrf_name': csrf}).json()
                    dr5 = json.loads(decrypt_stream(r6.get("response")))
                    top_list = dr5.get("data", {}).get("list", []) if isinstance(dr5.get("data"), dict) else []

                    for top in top_list:
                        ti = top.get("id")
                        d9 = {"course_id": fi, "parent_id": fi, "layer": 3, "page": 1, "subject_id": sfi, "topic_id": ti, "type": "content"}
                        r7 = session.post('https://online.utkarsh.com/web/Course/get_layer_two_data', headers=h, data={'layer_two_input_data': base64.b64encode(json.dumps(d9).encode()).decode(), 'csrf_name': csrf}).json()
                        dr6 = json.loads(decrypt_stream(r7.get("response")))
                        vids = dr6.get("data", {}).get("list", []) if isinstance(dr6.get("data"), dict) else []

                        for v in vids:
                            jti = v.get("payload", {}).get("tile_id")
                            if jti:
                                try:
                                    j5 = post_request("/meta_distributer/on_request_meta_source", {"course_id": fi, "tile_id": jti, "type": "video", "userid": uid}, ukey, uiv)
                                    url = j5.get("data", {}).get("link", "") or j5.get("data", {}).get("bitrate_urls", [{}])[0].get("url", "")
                                    if url: f.write(f"{v.get('title')}: {url.split('?Expires=')[0]}\n")
                                except: continue
        return filename
    except Exception as e: return f"Error: {str(e)}"
        
