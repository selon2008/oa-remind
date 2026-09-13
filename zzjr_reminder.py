#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仔仔(李思远)周日捷豹秋季课 + 武汉天气 提醒脚本
推送到企业微信群：私人订制消息--仔仔京汉
定时触发方案：
  - 周六 20:30  推送第二天(周日)课程 + 周日武汉天气
  - 周日 08:30  推送当天(周日)课程 + 当天武汉天气
  - 周日 12:00  推送午饭提醒（12:30 去南国西汇带仔仔吃午饭）
  - 周日 13:15  推送下午上课提醒（13:30 数学·史老师班）
  - 周日 16:30  推送当天(周日)课程 + 当天武汉天气 + 接送提醒
用法：
  python3 zzjr_reminder.py --mode saturday|sunday_morning|sunday_lunch|sunday_class_start|sunday_afternoon
  python3 zzjr_reminder.py --mode saturday --dry-run   # 只打印不发群
"""
import argparse, json, sys, urllib.request
from datetime import date, timedelta

WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f718c04a-ccdb-4eb1-a85c-2a3b311110a7"

# 武汉市区坐标
LAT, LON = 30.58, 114.27

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

# ----------------------- 周日固定课程 -----------------------
# (开始, 结束, 科目, 老师)
SUNDAY_CLASSES = [
    ("10:30", "12:30", "英语", "朱老师班"),
    ("13:30", "15:30", "数学", "史老师班"),
    ("15:40", "17:40", "化学", "焦老师班"),
]

def fetch_weather(d):
    """d=0 今天, d=1 明天；返回结构化天气"""
    url = (f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}"
           f"&daily=weather_code,temperature_2m_max,temperature_2m_min,wind_speed_10m_max"
           f"&timezone=Asia%2FShanghai&forecast_days=2")
    with urllib.request.urlopen(url, timeout=30) as r:
        dd = json.loads(r.read())["daily"]
    return {
        "date": dd["time"][d],
        "code": dd["weather_code"][d],
        "tmax": round(dd["temperature_2m_max"][d]),
        "tmin": round(dd["temperature_2m_min"][d]),
        "wind": round(dd["wind_speed_10m_max"][d]),
    }

def beaufort(kmh):
    table = [(0, 1), (1, 6), (2, 12), (3, 20), (4, 29), (5, 39), (6, 50),
             (7, 62), (8, 75), (9, 89), (10, 103), (11, 118)]
    for lv, spd in table:
        if kmh <= spd:
            return lv
    return 12

def weather_line(w):
    dt = date(*map(int, w["date"].split("-")))
    weekday = WEEK[dt.weekday()]
    desc = WMO.get(w["code"], "晴")
    lv = beaufort(w["wind"])
    tip = ""
    if w["code"] in (63, 65, 67, 80, 81, 82, 95, 96, 99):
        tip = "，有雨记得带伞"
    elif w["code"] in (71, 73, 75, 77, 85, 86):
        tip = "，有雪注意保暖防滑"
    elif w["tmin"] <= 5:
        tip = "，早晚偏凉注意添衣"
    elif w["tmax"] >= 30:
        tip = "，天气较热注意补水防晒"
    return f"{w['date']}({weekday})武汉天气：{desc}，气温 {w['tmin']}~{w['tmax']}℃，风力{lv}级{tip}。"

def class_lines():
    lines = []
    for s, e, subj, teacher in SUNDAY_CLASSES:
        lines.append(f"- {s}-{e} {subj}（{teacher}）")
    return "\n".join(lines)

def build_message(mode, w):
    if mode == "saturday":
        return (f"老板，明天（{w['date']}）仔仔捷豹秋季课安排：\n{class_lines()}\n"
                f"【天气】{weather_line(w)}\n"
                f"接送提醒：10:30 前送仔仔到校，12:30 下课接回；13:30 前再送，17:40 课后接回。")
    if mode == "sunday_morning":
        return (f"早上好老板，今天（{w['date']}）仔仔捷豹秋季课：\n{class_lines()}\n"
                f"【天气】{weather_line(w)}\n"
                f"接送提醒：10:30 前送仔仔到校，12:30 下课接回；13:30 前再送，17:40 课后接回。")
    if mode == "sunday_afternoon":
        return (f"下午好老板，今天是仔仔上课日（{w['date']}）：\n"
                f"当前课程：15:40-17:40 化学（焦老师班）进行中，17:40 下课请到点接回仔仔。\n"
                f"全天课程回顾：\n{class_lines()}\n"
                f"【天气】{weather_line(w)}")
    if mode == "sunday_lunch":
        return (f"老板，英语课 12:30 下课了。12:30 去南国西汇带仔仔吃午饭。")
    if mode == "sunday_class_start":
        return (f"老板，13:30 下午上课了（数学·史老师班），请提前送仔仔到校。")
    raise ValueError(mode)

def send(content):
    payload = {"msgtype": "text", "text": {"content": content}}
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(WEBHOOK, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["saturday", "sunday_morning", "sunday_lunch", "sunday_class_start", "sunday_afternoon"], required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    today = date.today()
    if args.mode == "saturday":
        d = 1  # 明天(周日)天气
    else:
        d = 0  # 今天(周日)天气
    w = fetch_weather(d)
    msg = build_message(args.mode, w)
    if args.dry_run:
        print("MODE:", args.mode)
        print("WEATHER:", json.dumps(w, ensure_ascii=False))
        print("MESSAGE:\n" + msg)
        sys.exit(0)
    res = send(msg)
    print("SEND RESULT:", json.dumps(res, ensure_ascii=False))
    if res.get("errcode") != 0:
        sys.exit(1)
