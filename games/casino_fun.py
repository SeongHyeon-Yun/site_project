import hashlib
import json
import base64
import requests
import time
import random


secret_key = "319a6412ffdfa757efec34f5cc9242b0"
url = "https://gate.nxzone.net"


# 해쉬값 만들기
def make_hash(*parts):
    try:
        normalized = []
        for p in parts:
            if isinstance(p, (dict, list)):
                # 공백 없이 안정적인 직렬화 (벤더가 필드 순서 요구하면 sort_keys=True 고려)
                normalized.append(
                    json.dumps(p, separators=(",", ":"), ensure_ascii=False)
                )
            elif isinstance(p, bytes):
                normalized.append(p.decode("utf-8"))
            else:
                normalized.append(str(p))

        data_to_hash = "".join(normalized)
        digest = hashlib.sha256(data_to_hash.encode("utf-8")).digest()
        return base64.b64encode(digest).decode("utf-8")
    except Exception as e:
        print("fail to make hash", e)
        return ""


# 중복 호출 방지 키
def make_request_key():
    # 현재 시간 (밀리초)
    timestamp = int(time.time() * 1000)
    # 100~999 사이의 난수
    rand_num = random.randint(100, 999)
    return f"{timestamp}{rand_num}"


# 카지노 게임 가져오기
def get_casino_list(secret_key, url):
    try:
        url = f"{url}/vendors"
        hash = make_hash(secret_key)

        headers = {
            "agent": "onePiece",
            "secretKey": secret_key,
            "User-agent": "Mozilla",
            "hash": hash,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = requests.post(url, headers=headers, data="", timeout=10)

        data = response.json()

        vendors = data["vendors"]

        result = []
        ven_list = [
            "아시안게이밍 카지노",
            "오리엔탈 게이밍",
            "이주기",
            "taishan 카지노",
        ]

        for i in vendors:
            category = i["category"]
            name = i["name"]
            key = i["key"]
            skins = i["skins"]
            if category == "casino" and name not in ven_list:
                result.append({"vendor": name, "key": key, "skin": skins[0]["skin"]})

        return result
    except requests.RequestException as e:
        print("💥 API 요청 실패:", e)
        return None


# 슬롯 게임 리스트 가져오기
def get_slot_list(secret_key, url):
    try:
        url = f"{url}/vendors"
        hash = make_hash(secret_key)

        headers = {
            "agent": "onePiece",
            "secretKey": secret_key,
            "User-agent": "Mozilla",
            "hash": hash,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(url, headers=headers, data="", timeout=10)

        data = response.json()

        vendors = data["vendors"]
        count = 0

        result = []
        get_list = [
            "마이크로게이밍 그랜드 슬롯",
            "프라그마틱 슬롯",
            "하바네로",
            "블루프린트 슬롯",
            "CQ9 슬롯",
            "레드타이거",
            "부운고",
            "넷엔트",
            "PG소프트",
            "스카이윈드 슬롯",
            "플레이스타 슬롯",
            "플레이앤고",
            "에보플레이 슬롯",
            "아바타UX 슬롯",
            "노리밋시티 슬롯",
            "핵쏘우게이밍 슬롯",
            "드래곤소프트",
            "와즈단",
        ]

        for i in vendors:
            category = i["category"]
            key = i["key"]
            name = i["name"]
            if category == "slot" and name in get_list:
                count += 1
                result.append({"vendor": name, "key": key})

    except Exception as e:
        return e

    return result


def get_slot_page(secret_key, url, vendorKey):
    url = f"{url}/games"

    body = {"vendorKey": vendorKey, "skin": "SLOT", "type": "Slot"}

    hash = make_hash(body, secret_key)

    headers = {
        "agent": "onePiece",
        "secretKey": secret_key,
        "User-agent": "Mozilla",
        "hash": hash,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    
    try:
        resp = requests.post(url, headers=headers, data=body, timeout=10)
        resp.raise_for_status()
        resp_data = resp.json()
    except Exception as e:
        return e

    return resp_data


def casino_run(key, skin, ip, username, secret_key, url):
    url = f"{url}/play"
    requestKey = make_request_key()

    body = {
        "vendorKey": key,
        "gameKey": skin,
        "siteUsername": username,
        "nickname": "",
        "ip": ip,
        "requestKey": requestKey,
    }

    hash = make_hash(body, secret_key)

    headers = {
        "agent": "onePiece",
        "secretKey": secret_key,
        "User-agent": "Mozilla",
        "hash": hash,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        resp = requests.post(url, data=body, headers=headers, timeout=10)
        resp.raise_for_status()
        resp_data = resp.json()  # json.loads(resp.text)와 동일
        game_url = resp_data.get("url")  # "url" 키 값 꺼내기
    except requests.exceptions.RequestException as e:
        print("request error:", e)

    return {"url": game_url}
