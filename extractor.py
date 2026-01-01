import os
import requests
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from base64 import b64decode, b64encode

# Configuration
API_URL = "https://application.utkarshapp.com/index.php/data_model"
COMMON_KEY = b"%!^F&^$)&^$&*$^&"
COMMON_IV = b"#*v$JvywJvyJDyvJ"
key_chars = "%!F*&^$)_*%3f&B+"
iv_chars = "#*$DJvyw2w%!_-$@"

def decrypt_stream(enc):
    try:
        enc = b64decode(enc)
        key = '%!$!%_$&!%F)&^!^'.encode('utf-8')
        iv = '#*y*#2yJ*#$wJv*v'.encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_bytes = cipher.decrypt(enc)
        try:
            plaintext = unpad(decrypted_bytes, AES.block_size).decode('utf-8')
        except:
            plaintext = decrypted_bytes.decode('utf-8', errors='ignore')
        
        start = plaintext.find('{')
        end = plaintext.rfind('}')
        if start != -1 and end != -1:
            return plaintext[start:end+1]
        return None
    except:
        return None

def encrypt_stream(plain_text):
    key = '%!$!%_$&!%F)&^!^'.encode('utf-8')
    iv = '#*y*#2yJ*#$wJv*v'.encode('utf-8')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_text = pad(plain_text.encode('utf-8'), AES.block_size)
    return b64encode(cipher.encrypt(padded_text)).decode('utf-8')

def post_request(path, data, key, iv):
    # Encryption and API call logic from your source
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(json.dumps(data, separators=(",", ":")).encode(), AES.block_size)
    encrypted = b64encode(cipher.encrypt(padded_data)).decode() + ":"
    
    headers = {
        "Authorization": "Bearer 152#svf346t45ybrer34yredk76t",
        "Content-Type": "text/plain; charset=UTF-8",
        "devicetype": "1",
        "userid": str(data.get("userid", "0")),
        "version": "152"
    }
    
    res = requests.post(f"{API_URL}{path}", headers=headers, data=encrypted)
    
    # Decryption
    cipher_dec = AES.new(key, AES.MODE_CBC, iv)
    enc_data = b64decode(res.text.split(":")[0])
    decrypted = unpad(cipher_dec.decrypt(enc_data), AES.block_size).decode()
    return json.loads(decrypted)

def extract_course_to_file(ci):
    session = requests.Session()
    filename = f"course_{ci}.txt"
    
    # 1. Login Details (Yahan apni sahi details dalein)
    email = "APNA_MOBILE_YA_EMAIL" 
    password = "APNA_PASSWORD"
    
    # Login Flow
    r1 = session.get('https://online.utkarsh.com/')
    csrf = r1.cookies.get('csrf_name')
    
    l_data = {'csrf_name': csrf, 'mobile': email, 'password': password, 'submit': 'LogIn'}
    l_headers = {'User-Agent': 'Mozilla/5.0'}
    u2 = session.post('https://online.utkarsh.com/web/Auth/login', data=l_data, headers=l_headers).json()
    
    dr1 = json.loads(decrypt_stream(u2.get("response")))
    jwt = dr1.get("data", {}).get("jwt")
    token = dr1.get("token")
    user_id = str(dr1.get("data", {}).get("id"))
    
    h = {'token': token, 'jwt': jwt, 'User-Agent': 'Mozilla/5.0'}
    
    # Keys setup for Meta Source
    key = "".join(key_chars[int(i)] for i in (user_id + "1524567456436545")[:16]).encode()
    iv = "".join(iv_chars[int(i)] for i in (user_id + "1524567456436545")[:16]).encode()

    with open(filename, "w", encoding="utf-8") as f:
        # Layer 1
        d3 = {"course_id": ci, "revert_api": "1#0#0#1", "parent_id": 0, "tile_id": "15330", "layer": 1, "type": "course_combo"}
        r4 = session.post('https://online.utkarsh.com/web/Course/tiles_data', headers=h, data={'tile_input': encrypt_stream(json.dumps(d3)), 'csrf_name': csrf}).json()
        dr3 = json.loads(decrypt_stream(r4.get("response")))

        for item in dr3.get("data", []):
            fi = item.get("id")
            f.write(f"\n--- {item.get('title')} ---\n")
            
            # Layer 2 (Subjects)
            d5 = {"course_id": fi, "layer": 1, "page": 1, "parent_id": fi, "revert_api": "1#1#0#1", "tile_id": "0", "type": "content"}
            r5 = session.post('https://online.utkarsh.com/web/Course/tiles_data', headers=h, data={'tile_input': encrypt_stream(json.dumps(d5)), 'csrf_name': csrf}).json()
            dr4 = json.loads(decrypt_stream(r5.get("response")))

            for sub in dr4.get("data", {}).get("list", []):
                sfi = sub.get("id")
                d7 = {"course_id": fi, "parent_id": fi, "layer": 2, "page": 1, "subject_id": sfi, "topic_id": sfi, "type": "content"}
                de3 = base64.b64encode(json.dumps(d7).encode()).decode()
                r6 = session.post('https://online.utkarsh.com/web/Course/get_layer_two_data', headers=h, data={'layer_two_input_data': de3, 'csrf_name': csrf}).json()
                dr5 = json.loads(decrypt_stream(r6["response"]))

                for topic in dr5.get("data", {}).get("list", []):
                    ti = topic.get("id")
                    d9 = {"course_id": fi, "parent_id": fi, "layer": 3, "page": 1, "subject_id": sfi, "topic_id": ti, "type": "content"}
                    de4 = base64.b64encode(json.dumps(d9).encode()).decode()
                    r7 = session.post('https://online.utkarsh.com/web/Course/get_layer_two_data', headers=h, data={'layer_two_input_data': de4, 'csrf_name': csrf}).json()
                    dr6 = json.loads(decrypt_stream(r7["response"]))

                    # Final Videos Extraction
                    if "data" in dr6 and "list" in dr6["data"]:
                        for vid in dr6["data"]["list"]:
                            jti = vid["payload"]["tile_id"]
                            j4 = {"course_id": fi, "tile_id": jti, "type": "video", "userid": user_id}
                            # Meta Distributer call
                            j5 = post_request("/meta_distributer/on_request_meta_source", j4, key, iv)
                            
                            cj = j5.get("data", {})
                            url = cj.get("link", "")
                            if not url and cj.get("bitrate_urls"):
                                url = cj["bitrate_urls"][0].get("url", "")
                            
                            if url:
                                clean_url = url.split("?Expires=")[0]
                                f.write(f"{vid.get('title')}: {clean_url}\n")
    
    return filename
    
