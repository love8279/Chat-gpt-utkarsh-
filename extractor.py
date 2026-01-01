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
    
    # --- APNA LOGIN YAHA DALEIN ---
    email = "YOUR_MOBILE_HERE" 
    password = "YOUR_PASSWORD_HERE"

    try:
        r1 = session.get('https://online.utkarsh.com/')
        csrf = r1.cookies.get('csrf_name')
        l_res = session.post('https://online.utkarsh.com/web/Auth/login', data={'csrf_name': csrf, 'mobile': email, 'password': password, 'submit': 'LogIn'}).json()
        
        dec_login = decrypt_stream(l_res.get("response"))
        if not dec_login: return "Error: Login Response Decrypt Nahi Hua"
        dr1 = json.loads(dec_login)
        
        # User details extraction with safety
        u_data = dr1.get("data", {})
        jwt = u_data.get("jwt") if isinstance(u_data, dict) else None
        token = dr1.get("token")
        uid = str(u_data.get("id")) if isinstance(u_data, dict) else "0"
        
        if not jwt: return "Error: Login Fail (JWT missing). Email/Pass check karein."

        h = {'token': token, 'jwt': jwt, 'User-Agent': 'Mozilla/5.0'}
        ukey = "".join(key_chars[int(i)] for i in (uid + "1524567456436545")[:16]).encode()
        uiv = "".join(iv_chars[int(i)] for i in (uid + "1524567456436545")[:16]).encode()

        with open(filename, "w", encoding="utf-8") as f:
            d3 = {"course_id": ci, "revert_api": "1#0#0#1", "parent_id": 0, "tile_id": "15330", "layer": 1, "type": "course_combo"}
            r4 = session.post('https://online.utkarsh.com/web/Course/tiles_data', headers=h, data={'tile_input': encrypt_stream(json.dumps(d3)), 'csrf_name': csrf}).json()
            
            dr3_raw = decrypt_stream(r4.get("response"))
            if not dr3_raw: return "Error: Course Data Decrypt Nahi Hua"
            dr3 = json.loads(dr3_raw)
            
            # --- MAIN FIX: LIST vs DICT CHECK ---
            raw_data_field = dr3.get("data", [])
            if isinstance(raw_data_field, dict):
                items = raw_data_field.get("list", [])
            else:
                items = raw_data_field # Agar data khud hi ek list hai

            if not isinstance(items, list): items = []

            for item in items:
                if not isinstance(item, dict): continue
                fi = item.get("id")
                f.write(f"\n--- SECTION: {item.get('title')} ---\n")
                
                # Layer 2 (Subjects)
                d5 = {"course_id": fi, "layer": 1, "page": 1, "parent_id": fi, "revert_api": "1#1#0#1", "tile_id": "0", "type": "content"}
                r5 = session.post('https://online.utkarsh.com/web/Course/tiles_data', headers=h, data={'tile_input': encrypt_stream(json.dumps(d5)), 'csrf_name': csrf}).json()
                
                dr4_raw = decrypt_stream(r5.get("response"))
                if not dr4_raw: continue
                dr4 = json.loads(dr4_raw)
                
                l2_data = dr4.get("data", {})
                sub_list = l2_data.get("list", []) if isinstance(l2_data, dict) else []

                for sub in sub_list:
                    if not isinstance(sub, dict): continue
                    sfi = sub.get("id")
                    d7 = {"course_id": fi, "parent_id": fi, "layer": 2, "page": 1, "subject_id": sfi, "topic_id": sfi, "type": "content"}
                    r6 = session.post('https://online.utkarsh.com/web/Course/get_layer_two_data', headers=h, data={'layer_two_input_data': base64.b64encode(json.dumps(d7).encode()).decode(), 'csrf_name': csrf}).json()
                    
                    dr5_raw = decrypt_stream(r6.get("response"))
                    if not dr5_raw: continue
                    dr5 = json.loads(dr5_raw)
                    l3_data = dr5.get("data", {})
                    top_list = l3_data.get("list", []) if isinstance(l3_data, dict) else []

                    for top in top_list:
                        if not isinstance(top, dict): continue
                        ti = top.get("id")
                        d9 = {"course_id": fi, "parent_id": fi, "layer": 3, "page": 1, "subject_id": sfi, "topic_id": ti, "type": "content"}
                        r7 = session.post('https://online.utkarsh.com/web/Course/get_layer_two_data', headers=h, data={'layer_two_input_data': base64.b64encode(json.dumps(d9).encode()).decode(), 'csrf_name': csrf}).json()
                        
                        dr6_raw = decrypt_stream(r7.get("response"))
                        if not dr6_raw: continue
                        dr6 = json.loads(dr6_raw)
                        l4_data = dr6.get("data", {})
                        vids = l4_data.get("list", []) if isinstance(l4_data, dict) else []

                        for v in vids:
                            if not isinstance(v, dict): continue
                            payload = v.get("payload", {})
                            jti = payload.get("tile_id") if isinstance(payload, dict) else None
                            if jti:
                                try:
                                    j5 = post_request("/meta_distributer/on_request_meta_source", {"course_id": fi, "tile_id": jti, "type": "video", "userid": uid}, ukey, uiv)
                                    v_meta = j5.get("data", {})
                                    if isinstance(v_meta, dict):
                                        v_url = v_meta.get("link") or (v_meta.get("bitrate_urls", [{}])[0].get("url") if v_meta.get("bitrate_urls") else None)
                                        if v_url: f.write(f"{v.get('title')}: {v_url.split('?Expires=')[0]}\n")
                                except: continue
        return filename
    except Exception as e: return f"Error Logic Me: {str(e)}"
    
