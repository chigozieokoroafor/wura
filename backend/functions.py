import requests
import jwt
import datetime
from backend.config import secret_key
import string, random
from email.message import EmailMessage
from email.mime.text import MIMEText
from mimetypes import MimeTypes
import smtplib, ssl
from email import contentmanager
from flask import request, jsonify
from functools import wraps
from jwt.exceptions import ExpiredSignatureError, DecodeError


class Authentication:
    def generate_access_token(data, minutes=60):
        exp = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
        #data["start"] = datetime.datetime.timestamp(datetime.datetime.now())
        data["exp"] = datetime.datetime.timestamp(exp)
        token = jwt.encode(data, secret_key,algorithm="HS256")
        return token
    
    def generate_otp():
        otpcode = "".join(random.choices(string.digits, k=4))
        expiry = datetime.timedelta(minutes=5.0)
        start_time = datetime.datetime.timestamp(datetime.datetime.now()) 
        stop_time = datetime.datetime.timestamp(datetime.datetime.now() + expiry)
        return {"otp":otpcode, "stoptime":stop_time, "starttime":start_time}
    
    def sendMail(email, otp_code):
        try:
            email_sender = "okoroaforc14@gmail.com"
            email_password = "fskhwjqqbktuqkzg"

            email_reciever = email
            #subject = "test"
            file = open("backend/verification.html")
            subject = file.read().format(code=otp_code, support_mail="okoroaforc14@gmail.com")
            
            em = MIMEText(subject,"html")
            em["From"] = email_sender
            em["To"] = email_reciever
            em["subject"] = "Test Mail"
            

            context = ssl.create_default_context()

            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_reciever, em.as_string())
            return {"detail":"verification mail sent", "status":"success"}
        except smtplib.SMTPAuthenticationError as e:
            return {"detail":"error sending verification mail", "status":"fail"}

    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            bearer_token = request.headers.get("Authorization")
            
            if not bearer_token:
                return jsonify({"detail": "Token is missing","status":"error"}), 403
            try:          
                data = jwt.decode(bearer_token, secret_key,algorithms=["HS256"])
            except ExpiredSignatureError as e:
                return jsonify({"detail":"Token Expired", "status":"fail"}), 400
            except DecodeError as d:
                return jsonify({"detail":"Incorrect Token", "status":"fail"}), 400
            return f(*args, **kwargs)
        return decorated

    def generate_refresh_token(token):
        decoded = jwt.decode(token,secret_key,["HS256"])
        now = datetime.datetime.time(datetime.datetime.now())
        exp = decoded["exp"]

        difference = exp - now
        check = 0<difference<60.0

        if check is True:
            decoded.pop("exp")
            t = Authentication.generate_access_token(decoded)
            return t
        return ""


def filter_cursor(cursor):
    main_list = []
    for i in cursor:
        i.pop("_id")
        try:
            i.pop("timestamp")
        except KeyError as e :
            pass
        main_list.append(i)
    return main_list

def compile_currencies():
    country_list = [("Afghanistan", "AFN", "AF"),
    ("Albania","ALL", "AL"),
    ["Aland Island", "EUR", "AX"],
    ("Algeria","DZD", "DZ"),
    ("American-Samoa","USD", "AS"),
    ("Andorra","EUR", "AD"),
    ("Angola","AOA", "AO"),
    ("Anguilla","XCD", "AI"),
    ("Antigua-Barbuda","XCD", "AG"),
    ("Argentina","ARS", "AR"),
    ("Armenia","AMD", "AM"),
    ("Aruba","AWG", "AW"),
    ["Ascension Island", "SHP", "AC"],
    ("Australia","AUD", "AU"),
    ("Austria","EUR", "AT"),
    ("Azerbaijan","AZN", "AZ"),
    ("Bahamas","BSD", "BS"),
    ("Bahrain","BHD", "BH"),
    ("Bangladesh","BDT", "BD"),
    ("Barbados","BBD", "BB"),
    ("Belarus","BYR", "BY"),
    ("Belgium","EUR", "BE"),
    ("Belize","BZD", "BZ"),
    ("Benin","XOF", "BJ"),
    ("Bermuda","BMD", "BM"),
    ("Bhutan","BTN", "BT"),
    ("Bolivia","BOB", "BO"),
    ("Bosnia-Herzegovina","BAM", "BA"),
    ("Botswana","BWP", "BW"),
    ("Brazil","BRL", "BR"),
    ("British Indian Ocean Territory","USD", "IO"),
    ("Brunei Darussalam","BND", "BN"),
    ("Bulgaria","BGN", "BG"),
    ("Burkina Faso","XOF", "BF"),
    ("Burundi","BIF", "BI"),
    ("Cape Verde","CVE", "CV"),
    ("Cambodia","KHR", "KH"),
    ("Cameroon","XAF", "CM"),
    ("Canada","CAD", "CA"),
    ("Cayman Islands","KYD", "KY"),
    ("Central African Republic","XAF", "CF"),
    ["Carribean Neatherlands", "ANG", "BO"],
    ("Chad","XAF", "TD"),
    ("Chile","CLP", "CL"),
    ("China","CNY", "CN"),
    ("Christmas Island","AUD", "CX"),
    ("Cocos (Keeling) Islands","AUD", "CC"),
    ("Colombia","COP", "CO"),
    ("Comoros","KMF", "KM"),
    ("Congo","XAF", "CG"),
    ("Congo, Dem. Republic","CDF", "CD"),
    ("Cook Islands","NZD", "CK"),
    ("Costa Rica","CRC", "CR"),
    ("Croatia","HRK", "HR"),
    ("Cuba","CUP", "CU"),
    ("Curaçao","ANG", "CW"),
    ("Cyprus","EUR", "CY"),
    ("Czechia","CZK", "CZ"),
    ("Côte d'Ivoire","XOF", "CI"),
    ("Denmark","DKK", "DK"),
    ("Djibouti","DJF", "DJ"),
    ("Dominica","XCD", "DM"),
    ("Dominican Republic","DOP", "DO"),
    ("Ecuador","ECS", "EC"),
    ["East Timor", "USD", "TL"],
    ("Egypt","EGP", "EG"),
    ("El Salvador","SVC", "SV"),
    ("Equatorial Guinea","XAF", "GO"),
    ("Eritrea","ERN", "ER"),
    ("Estonia","EUR", "EE"),
    ("Ethiopia","ETB", "ET"),
    ("Falkland Islands (Malvinas)","FKP", "FK"),
    ("Faroe Islands","DKK", "FO"),
    ("Fiji","FJD", "FJ"),
    ("Finland","EUR", "FI"),
    ("France","EUR", "FR"),
    ("French Guiana","EUR", "GF"),
    ("French Polynesia","XPF", "PF"),
    ("Gabon","XAF", "GA"),
    ("Gambia","GMD", "GM"),
    ("Georgia","GEL", "GE"),
    ("Germany","EUR", "DE"),
    ("Ghana","GHS", "GH"),
    ("Gibraltar","GIP", "GI"),
    ("Greece","EUR", "GR"),
    ("Greenland","DKK", "GL"),
    ("Grenada","XCD", "GD"),
    ("Guadeloupe (French)","EUR", "GP"),
    ("Guam (USA)","USD", "GU"),
    ("Guatemala","QTQ", "GT"),
    ("Guernsey","GGP", "GG"),
    ("Guinea","GNF", "GN"),
    ("Guinea Bissau","GWP", "GW"),
    ("Guyana","GYD", "GY"),
    ("Haiti","HTG", "HT"),
    ("Heard Island and McDonald Islands","AUD", "HM"),
    ("Honduras","HNL", "HN"),
    ("Hong Kong","HKD", "HK"),
    ("Hungary","HUF", "HU"),
    ("Iceland","ISK", "IS"),
    ("India","INR", "IN"),
    ("Indonesia","IDR", "ID"),
    ("Iran","IRR", "IR"),
    ("Iraq","IQD", "IQ"),
    ("Ireland","EUR", "IE"),
    ("Isle of Man","GBP", "IM"),
    ("Israel","ILS", "IL"),
    ("Italy","EUR", "IT"),
    ("Jamaica","JMD", "JM"),
    ("Japan","JPY", "JP"),
    ("Jersey","GBP", "JE"),
    ("Jordan","JOD", "JO"),
    ("Kazakhstan","KZT", "KZ"),
    ("Kenya","KES", "KE"),
    ("Kiribati","AUD", "KI"),
    ("Korea-North","KPW", "KP"),
    ("Korea-South","KRW", "KR"),
    ("Kuwait","KWD", "KW"),
    ["Kosovo", "EUR", "XK"],
    ("Kyrgyzstan","KGS", "KG"),
    ("Laos","LAK", "LA"),
    ("Latvia","LVL", "LV"),
    ("Lebanon","LBP", "LB"),
    ("Lesotho","LSL", "LS"),
    ("Liberia","LRD", "LR"),
    ("Libya","LYD", "LY"),
    ("Liechtenstein","CHF", "LI"),
    ("Lithuania","LTL", "LT"),
    ("Luxembourg","EUR", "LU"),
    ("Macao","MOP", "MO"),
    ("Madagascar","MGF", "MG"),
    ["Macedonia", "MKD", "MK"],
    ("Malawi","MWK", "MW"),
    ("Malaysia","MYR", "MY"),
    ("Maldives","MVR", "MV"),
    ("Mali","XOF", "ML"),
    ("Malta","EUR", "MT"),
    ("Marshall Islands","USD", "MH"),
    ("Martinique (French)","EUR", "MQ"),
    ("Mauritania","MRO", "MR"),
    ("Mauritius","MUR", "MU"),
    ("Mayotte","EUR", "YT"),
    ("Mexico","MXN", "MX"),
    ("Micronesia","USD", "FM"),
    ("Moldova","MDL", "MD"),
    ("Monaco","EUR", "MC"),
    ("Mongolia","MNT", "MN"),
    ("Montenegro","EUR", "ME"),
    ("Montserrat","XCD", "MS"),
    ("Morocco","MAD", "MA"),
    ("Mozambique","MZN", "MZ"),
    ("Myanmar","MMK", "MM"),
    ("Namibia","NAD", "NA"),
    ("Nauru","AUD", "NR"),
    ("Nepal","NPR", "NP"),
    ("Netherlands","EUR", "NL"),
    ("New Caledonia (French)","XPF", "NC"),
    ("New Zealand","NZD", "NZ"),
    ("Nicaragua","NIO", "NI"),
    ("Niger","XOF", "NE"),
    ("Nigeria","NGN", "NG"),
    ("Niue","NZD", "NU"),
    ("Norfolk Island","AUD", "NF"),
    ("Northern Mariana Islands","USD", "MP"),
    ("Norway","NOK", "NO"),
    ("Oman","OMR", "OM"),
    ["Pakistan","PKR", "PK"],
    ["Palau","USD", "PW"],
    ["Panama","PAB", "PA"],
    ["Palestinian Territories", "ILS", "PS"],
    ["Papua New Guinea","PGK", "PG"],
    ["Paraguay","PYG", "PY"],
    ["Peru","PEN", "PE"],
    ["Philippines","PHP", "PH"],
    ["Poland","PLN", "PL"],
    ["Portugal","EUR", "PT"],
    ["Puerto Rico","USD", "PR"],
    ["Qatar","QAR", "QA"],
    ["Reunion (French)","EUR", "RE"],
    ["Romania","RON", "RO"],
    ["Russia","RUB", "RU"],
    ["Rwanda","RWF", "RW"],
    ["Saint Helena","SHP", "SH"],
    ["Saint Kitts & Nevis Anguilla","XCD", "KN"],
    ["Saint Lucia","XCD", "LC"],
    ["Saint Pierre and Miquelon","EUR", "PM"],
    ["Saint Vincent & Grenadines","XCD", "VC"],
    ["Saint Martin", "XCD", "MF"],
    ["Saint Barthélemy", "XCD", "BL"],
    ["Samoa","WST", "WS"],
    ["San Marino","EUR", "SM"],
    ["Sao Tome and Principe","STD", "ST"],
    ["Saudi Arabia","SAR", "SA"],
    ["Senegal",	"XOF", "SN"],
    ["Serbia","RSD", "RS"],
    ["Seychelles","SCR", "SC"],
    ["Sierra Leone","SLL", "SL"],
    ["Singapore","SGD", "SG"],
    ["Slovakia","EUR", "SK"],
    ["Slovenia","EUR", "SI"],
    ["Solomon Islands","SBD", "SB"],
    ["Somalia","SOS", "SO"],
    ["Sint Maarten", "XCD", "SX"],
    ["South Africa","ZAR", "ZA"],
    ["South Georgia & South Sandwich Islands","GBP", "GS"],
    ["South Sudan","SSP", "SS"],
    ["Spain","EUR", "ES"],
    ["Sri Lanka", "LKR", "LK"],
    ["Sudan","SDG", "SD"],
    ["Suriname","SRD", "SR"],
    ["Svalbard and Jan Mayen Islands","NOK", "SJ"],
    ["Eswatini", "SZL", "SZ"],
    ["Sweden","SEK", "SEK"],
    ["Switzerland","CHF", "CH"],
    ["Syria","SYP", "SY"],
    ["Taiwan", "TWD", "TW"],
    ["Tajikistan","TJS", "TJ"],
    ["Tanzania","TZS", "TZ"],
    ["Thailand","THB", "TH"],
    ["Togo","XOF", "TOGO"],
    ["Tokelau",	"NZD", "TK"],
    ["Tonga","TOP", "TO"],
    ["Trinidad and Tobago","TTD", "TT"],
    ["Tunisia","TND", "TN"],
    ["Turkey","TRY", "TR"],
    ["Turkmenistan","TMT", "TM"],
    ["Turks and Caicos Islands","USD", "TC"],
    ["Tuvalu",	"AUD", "TV"],
    ["USA","USD", "US"],
    ["Uganda","UGX", "UG"],
    ["Ukraine","UAH", "UA"],
    ["United Arab Emirates","AED", "AE"],
    ["United Kingdom", "GBP", "GB"],
    ["Uruguay","UYU", "UY"],
    ["Uzbekistan",	"UZS", "UZ"],
    ["Vanuatu","VUV", "VU"],
    ["Vatican City", "VAL", "VA"],
    ["Venezuela", "VEF", "VE"],
    ["Vietnam","VND", "VN"],
    ["Virgin Islands (British)","USD", "VG"],
    ["Virgin Islands (USA)","USD", "VI"],
    ["Wallis and Futuna Islands", "XPF", "WF"],
    ["Western Sahara", "MAD", "EH"],
    ["Yemen", "YER", "YE"],
    ["Zambia","ZMW", "ZM"],
    ["Zimbabwe","ZWD", "ZW"]]
    count_ = []
    currencies = []
    for i in country_list:
        country_dict = {}
        country_dict["country"] = i[0]
        country_dict["currency"] = i[1]
        country_dict["symbol"] = i[2]
        count_.append(country_dict)
        if i[1] in currencies:
            pass
        else:
            currencies.append(i[1])
    #currencies = []
    joined_c = ",".join(currencies)
    return {"currencies":joined_c, "country_list":count_}


def currency_update():
    country_data = compile_currencies()
    curr = country_data["currencies"]
    
    url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={curr}&base=NGN"

    payload = {}
    headers= {
    "apikey": "5Zg6VsEVrBDjAdiYupAhUb6sMyaFMytz"
    }

    response = requests.request("GET", url, headers=headers, data = payload)

    if response.ok:
        result = response.json()

