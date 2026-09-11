#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
次日秦皇岛天气提醒脚本
用于 GitHub Actions 每日定时 20:00(北京) 推送到企业微信机器人（私人订制--妮妮燕大 群）
数据源：Open-Meteo 免费天气 API（无需 key）
用法：
  python3 weather_reminder.py            # 获取明日天气并推送
  python3 weather_reminder.py --dry-run  # 只生成文案，不发群（本地验证用）
"""
import argparse, json, sys, urllib.request
from datetime import date, timedelta

WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=ea5913ef-8fb3-40a2-9e54-67e73e44c326"

# 秦皇岛坐标
LAT, LON = 39.94, 119.60

# WMO 天气代码 -> 中文描述
WMO = {
    0: "晴", 1: "大部晴朗", 2: "多云", 3: "阴",
    45: "雾", 48: "冻雾", 51: "毛毛雨", 53: "毛毛雨", 55: "毛毛雨",
    56: "冻雨", 57: "冻雨", 61: "小雨", 63: "中雨", 65: "大雨",
    66: "冻雨", 67: "冻雨", 71: "小雪", 73: "中雪", 75: "大雪",
    77: "雪粒", 80: "阵雨", 81: "阵雨", 82: "强阵雨",
    85: "阵雪", 86: "强阵雪", 95: "雷阵雨", 96: "雷阵雨", 99: "强雷暴",
}

WEEK = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

# 军训期：2026-09-11 ~ 09-24；次日推送若落在此范围内附加军训提示
MILITARY_START = date(2026, 9, 11)
MILITARY_END = date(2026, 9, 24)
# 军训晚间活动（按日），用于提示
MILITARY_EVENING = {
    (9, 11): "军训动员大会",
    (9, 12): "各学院召开军训主题班会",
    (9, 13): "内务整理",
    (9, 14): "校歌军歌学唱",
    (9, 15): "校歌军歌学唱",
    (9, 16): "内务整理",
    (9, 17): "军训慰问演出(东校区同步开始)",
    (9, 18): "校歌军歌学唱",
    (9, 19): "迎新晚会、音乐思政课",
    (9, 20): "内务整理",
    (9, 21): "校歌军歌学唱",
    (9, 22): "校歌军歌大赛",
    (9, 23): "内务评比大赛",
    (9, 24): "军训总结大会",
}

def fetch_tomorrow():
    url = (f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}"
           f"&daily=weather_code,temperature_2m_max,temperature_2m_min,wind_speed_10m_max"
           f"&timezone=Asia%2FShanghai&forecast_days=2")
    with urllib.request.urlopen(url, timeout=30) as r:
        d = json.loads(r.read())["daily"]
    i = 1  # 明天
    return {
        "date": d["time"][i],
        "code": d["weather_code"][i],
        "tmax": round(d["temperature_2m_max"][i]),
        "tmin": round(d["temperature_2m_min"][i]),
        "wind": round(d["wind_speed_10m_max"][i]),
    }

def beaufort(kmh):
    """km/h -> 风力等级"""
    table = [(0, 1), (1, 6), (2, 12), (3, 20), (4, 29), (5, 39), (6, 50),
             (7, 62), (8, 75), (9, 89), (10, 103), (11, 118)]
    for lv, spd in table:
        if kmh <= spd:
            return lv
    return 12

def build_message(w):
    dt = datetime_date(w["date"])
    weekday = WEEK[dt.weekday()]
    wmo_desc = WMO.get(w["code"], "晴")
    lv = beaufort(w["wind"])
    tip = ""
    if w["code"] in (63, 65, 67, 80, 81, 82, 95, 96, 99):
        tip = "有雨，记得带伞"
    elif w["code"] in (71, 73, 75, 77, 85, 86):
        tip = "有雪，注意保暖防滑"
    elif w["tmin"] <= 5:
        tip = "早晚偏凉，注意添衣"
    elif w["tmax"] >= 30:
        tip = "天气较热，注意补水防晒"
    if tip:
        tip = "，" + tip
    msg = (f"晚上好老板，明天（{w['date']} {weekday}）秦皇岛天气：{wmo_desc}，"
           f"气温 {w['tmin']}~{w['tmax']}℃，风力{lv}级（最大风速约{w['wind']}km/h）{tip}。")
    # 军训期附加提示：明日在军训期内则附带作息提醒
    if MILITARY_START <= dt <= MILITARY_END:
        day_no = (dt - MILITARY_START).days + 1
        evening = MILITARY_EVENING.get((dt.month, dt.day), "按通知")
        msg += (f"另：明天是军训第{day_no}天，白天操课注意防晒补水、备好水壶，"
                f"晚上活动[{evening}]，操课请提前5分钟到集合点。")
    return msg

def datetime_date(s):
    y, m, dd = map(int, s.split("-"))
    return date(y, m, dd)

def send(content):
    payload = {"msgtype": "text", "text": {"content": content}}
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(WEBHOOK, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只打印文案，不发群")
    args = ap.parse_args()

    w = fetch_tomorrow()
    msg = build_message(w)
    if args.dry_run:
        print("TOMORROW:", json.dumps(w, ensure_ascii=False))
        print("MESSAGE:", msg)
        sys.exit(0)
    res = send(msg)
    print("SEND RESULT:", json.dumps(res, ensure_ascii=False))
    if res.get("errcode") != 0:
        sys.exit(1)
