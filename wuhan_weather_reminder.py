#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""武汉天气速报·每日北京20:00推送（仔仔京汉群 f718c04a）
内容：明天武汉天气速报 + 穿衣/喝水/带伞生活提醒 + 后三天趋势
数据源：Open-Meteo（免key）
"""
import argparse, json, sys, urllib.request, urllib.parse
from datetime import date, datetime, timezone, timedelta

WEBHOOK = ("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?"
           "key=f718c04a-ccdb-4eb1-a85c-2a3b311110a7")
SIGN = "\n\n马维斯推送"
CN = timezone(timedelta(hours=8))
LAT, LON = 30.58, 114.27
WD = "一二三四五六日"

WMO = {0:"晴",1:"基本晴",2:"多云",3:"阴",45:"雾",48:"雾凇",51:"毛毛雨",53:"毛毛雨",55:"毛毛雨",
       56:"冻雨",57:"冻雨",61:"小雨",63:"中雨",65:"大雨",66:"冻雨",67:"冻雨",71:"小雪",73:"中雪",
       75:"大雪",77:"雪粒",80:"阵雨",81:"强阵雨",82:"暴阵雨",85:"阵雪",86:"强阵雪",95:"雷暴",
       96:"雷暴伴冰雹",99:"雷暴伴大冰雹"}
RAIN = {51,53,55,56,57,61,63,65,66,67,71,73,75,77,80,81,82,85,86,95,96,99}

def weather_cn(c): return WMO.get(c, "未知")

def dress(tmin, tmax):
    if tmin < 0: return "厚棉服+保暖内衣"
    if tmin < 8: return "厚外套/羽绒服"
    if tmax <= 15: return "毛衣+外套"
    if tmax <= 22: return "长袖+薄外套(早晚凉)"
    if tmax <= 27: return "短袖+薄外套(早晚)"
    if tmax <= 32: return "短袖"
    return "短袖+防晒"

def drink(tmax):
    if tmax >= 35: return "高温天,多补水(约2.5L)"
    if tmax >= 30: return "天气热,多喝水(约2L)"
    if tmax >= 26: return "适量饮水(约1.8L)"
    return "正常饮水(约1.5L)"

def umbrella(code, prob):
    if code in RAIN or prob >= 30: return f"建议带伞(降水概率{prob}%)"
    return "可不带伞"

def wind_cn(kmh):
    if kmh < 12: return "微风"
    if kmh < 20: return "轻风"
    if kmh < 29: return "和风"
    if kmh < 39: return "清劲风"
    if kmh < 50: return "强风"
    return "大风"

def fetch():
    q = {"latitude": LAT, "longitude": LON,
         "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_speed_10m_max",
         "timezone": "Asia/Shanghai", "forecast_days": 5}
    url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(q)
    with urllib.request.urlopen(url, timeout=20) as r:
        d = json.loads(r.read().decode())
    return d["daily"]

def build(dd):
    dates = dd["time"]
    tmax = int(dd["temperature_2m_max"][1]); tmin = int(dd["temperature_2m_min"][1])
    code = dd["weather_code"][1]; prob = int(dd["precipitation_probability_max"][1]); wind = dd["wind_speed_10m_max"][1]
    tm = date.fromisoformat(dates[1])
    lines = [f"【武汉天气速报·明日】{dates[1]} 周{WD[tm.weekday()]}",
             f"- 天气:{weather_cn(code)}(降水概率{prob}%)",
             f"- 气温:{tmin}~{tmax}℃",
             f"- 风力:{wind_cn(wind)}(约{int(wind)}km/h)",
             f"- 穿衣:{dress(tmin, tmax)}",
             f"- 喝水:{drink(tmax)}",
             f"- 带伞:{umbrella(code, prob)}",
             "- 后三天趋势:"]
    for i in range(2, 5):
        dt = date.fromisoformat(dates[i])
        lines.append(f"  {dates[i][5:]}周{WD[dt.weekday()]}:{weather_cn(dd['weather_code'][i])},{int(dd['temperature_2m_min'][i])}~{int(dd['temperature_2m_max'][i])}℃")
    return "\n".join(lines)

def send(text):
    text = f"{text}{SIGN}"
    body = json.dumps({"msgtype": "text", "text": {"content": text}},
                      ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(WEBHOOK, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只打印不发送")
    a = ap.parse_args()
    msg = build(fetch())
    if a.dry_run:
        print(msg)
        return 0
    print(send(msg))
    return 0

if __name__ == "__main__":
    sys.exit(main())
