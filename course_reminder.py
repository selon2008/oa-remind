#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
课程提醒脚本 - 燕山大学 设计学类26-2 (2026-2027 秋季学期)
用于 GitHub Actions 每日定时：推送给企业微信机器人(私人定制群)
  - 早上 07:00 推送当天课程
  - 晚上 19:00 推送第二天课程
数据源：排课表_Marvis.md（权威电子版）
用法：python3 course_reminder.py --mode today|tomorrow
"""
import argparse, json, sys, urllib.request
from datetime import date, timedelta

# ----------------------- 教学周定义 -----------------------
# 第1周：2026-08-31 ~ 09-06；每周一为起点
SEMESTER_START = date(2026, 8, 31)
def week_start(w):
    return SEMESTER_START + timedelta(weeks=w - 1)

TOTAL_WEEKS = 25
# 无课周（第20周起）与考试周
NO_CLASS_WEEKS = set(range(20, 26))
MID_EXAM_WEEK = 9     # 第9周 期中
FINAL_EXAM_WEEK = 19  # 第19周 期末

# ----------------------- 节次时间表 -----------------------
PERIODS = {
    1:  "8:00-8:45",   2:  "8:50-9:35",   3:  "10:05-10:50", 4:  "10:55-11:40",
    5:  "13:30-14:15", 6:  "14:20-15:05", 7:  "15:35-16:20", 8:  "16:25-17:10",
    9:  "18:10-18:55", 10: "19:00-19:45", 11: "20:05-20:50", 12: "20:55-21:40",
}

# ----------------------- 课程信息（代号 -> 全称/教师/教室按星期） -----------------------
# room: {星期0..6: 教室}; teacher: 教师
COURSES = {
    "思":  {"name": "思想道德与法治",              "teacher": "张丽娜",
            "room": {0: "西(五)C3010", 2: "西(五)C309 多媒体"}},
    "外":  {"name": "外语BⅠ",                      "teacher": "朱敏",
            "room": {1: "西(五)C201 多媒体", 3: "西(五)C201 多媒体"}},
    "造":  {"name": "造型基础",                    "teacher": "谷庆巍",
            "room": {0: "美术馆B201", 2: "美术馆B201", 4: "美术馆B201"}},
    "设":  {"name": "设计构成",                    "teacher": "王泽烨",
            "room": {0: "美术馆B201", 2: "美术馆B201", 4: "美术馆B201"}},
    "设1": {"name": "设计美学",                    "teacher": "蒋玉",
            "room": {0: "美术馆B201", 2: "美术馆B201", 4: "美术馆B201"}},
    "设2": {"name": "设计概论",                    "teacher": "刘念念",
            "room": {0: "美术馆B201", 1: "美术馆B201", 2: "美术馆B201", 4: "美术馆B201"}},
    "职":  {"name": "职业生涯规划与就业指导Ⅰ",    "teacher": "刘维尚",
            "room": {0: "音乐厅A101", 2: "音乐厅A101", 4: "音乐厅A101"}},
    "中":  {"name": "中华民族共同体概论",          "teacher": "雷霆",
            "room": {2: "西(五)B102 多媒体"}},
    "国":  {"name": "国家安全教育",                "teacher": "雷霆",
            "room": {2: "西(五)B102 多媒体"}},
    "形":  {"name": "形势与政策Ⅰ",                "teacher": "常玉洁",
            "room": {2: "西(五)C208 多媒体", 4: "西(五)C208 多媒体"}},
    "大":  {"name": "大学生心理健康教育Ⅰ",        "teacher": "杨丽欣",
            "room": {1: "西校区(五)C309 多媒体"}},
    "体":  {"name": "体育Ⅰ(合班)",                "teacher": "井兰香",
            "room": {4: "场地按分班安排"}},
}

# ----------------------- 每周课表 -----------------------
# SCHEDULE[星期] = [ [start, end, [(代号, 适用周字符串), ...]], ... ]
SCHEDULE = {
    0: [  # 星期一
        [3, 4, [("思", "1,5,6,7,8,10,11,12,13,14,15,16,17,18")]],
        [5, 6, [("造", "5-8"), ("设", "10-12"), ("设1", "13-15"), ("设2", "16-18")]],
        [7, 8, [("造", "5-8"), ("设", "10-12"), ("设1", "13-15"), ("设2", "16-18")]],
        [9, 10, [("职", "2")]],
        [11, 12, [("职", "2")]],
    ],
    1: [  # 星期二
        [3, 4, [("外", "1,2,5,6,7,8,10,11,12,13,14,15")]],
        [5, 6, [("大", "5-8,10-12"), ("设2", "16-18")]],
        [7, 8, [("设2", "16-18")]],
    ],
    2: [  # 星期三
        [1, 2, [("造", "5-8"), ("设", "10-12"), ("设1", "13-15")]],
        [3, 4, [("造", "5-8"), ("设", "10-12"), ("设1", "13-15")]],
        [5, 6, [("形", "10-11")]],
        [7, 8, [("中", "1,2,5,6,7,8,10,11"), ("国", "12"), ("思", "13-17")]],
        [9, 10, [("职", "2")]],
        [11, 12, [("职", "2")]],
    ],
    3: [  # 星期四
        [3, 4, [("外", "1,2,5,6,7,8,10,11,12,13,14,15")]],
    ],
    4: [  # 星期五
        [1, 2, [("造", "5-8"), ("设", "10-12"), ("设1", "13-15")]],
        [3, 4, [("造", "5-8"), ("设", "10-12"), ("设1", "13-15")]],
        [5, 6, [("形", "10-11"), ("设2", "16-17")]],
        [7, 8, [("体", "1-8,10-15"), ("设2", "16-17")]],
        [9, 10, [("职", "2")]],
        [11, 12, [("职", "2")]],
    ],
}

# ----------------------- 军训安排 (2026-09-11 ~ 09-24) -----------------------
MILITARY_START = date(2026, 9, 11)
MILITARY_END = date(2026, 9, 24)

# 固定每日作息（第一张图）
MILITARY_RHYTHM = [
    "6:30 起床",
    "6:30-7:00 洗漱、整理内务、打扫卫生",
    "7:00-8:00 早饭",
    "8:00-11:40 操课",
    "11:40-13:30 午饭、午休",
    "14:00-18:00 操课",
    "18:00-19:00 晚饭",
    "19:00-21:00 操课",
    "22:00 就寝",
]

# 每日活动（第二张图）：key=(月,日) -> (上午, 下午, 晚上)
MILITARY_DAILY = {
    (9, 11): ("操课", "操课", "军训动员大会"),
    (9, 12): ("操课", "操课", "各学院召开军训主题班会"),
    (9, 13): ("操课", "操课", "内务整理"),
    (9, 14): ("操课", "操课", "校歌军歌学唱"),
    (9, 15): ("操课", "操课", "校歌军歌学唱"),
    (9, 16): ("海港区分送兵大会(暂定)", "操课", "内务整理"),
    (9, 17): ("操课", "操课", "军训慰问演出(东校区同步开始)"),
    (9, 18): ("操课", "操课", "校歌军歌学唱"),
    (9, 19): ("长征胜利90周年主题讲座", "行军拉练(东校区)", "迎新晚会、音乐思政课"),
    (9, 20): ("操课", "行军拉练(西校区)", "内务整理"),
    (9, 21): ("操课", "操课", "校歌军歌学唱"),
    (9, 22): ("安全教育", "操课", "校歌军歌大赛"),
    (9, 23): ("操课", "操课", "内务评比大赛"),
    (9, 24): ("操课", "无", "军训总结大会"),
}

def build_military_message(target, amt):
    """军训期推送：固定作息 + 当日活动"""
    tw = target.weekday()
    day_no = (target - MILITARY_START).days + 1
    header = f"老板,{amt} {target.month}月{target.day}日(星期{weekday_cn(tw)})军训第{day_no}天"
    lines = [f"{header}作息安排如下:"]
    for item in MILITARY_RHYTHM:
        lines.append(f"- {item}")
    m, d = target.month, target.day
    a, p, e = MILITARY_DAILY.get((m, d), ("操课", "操课", "按通知"))
    lines.append(f"当日活动:上午[{a}],下午[{p}],晚上[{e}]")
    lines.append("提醒:操课提前5分钟在指定地点集合。")
    return "\n".join(lines)

# ----------------------- 辅助函数 -----------------------
def parse_weeks(s):
    """'1,5-8,10' -> set{1,5,6,7,8,10}"""
    out = set()
    for part in s.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            out.update(range(int(a), int(b) + 1))
        else:
            out.add(int(part))
    return out

def get_week(day):
    """返回日期对应教学周；不在学期内返回 None"""
    for w in range(1, TOTAL_WEEKS + 1):
        ws = week_start(w)
        if ws <= day <= ws + timedelta(days=6):
            return w
    return None

def weekday_cn(w):
    return "一二三四五六日"[w] + ""

def build_message(mode):
    today = date.today()
    target = today if mode == "today" else today + timedelta(days=1)
    tw = target.weekday()
    week = get_week(target)
    amt = "今天" if mode == "today" else "明天"

    # 军训期：优先推送军训作息安排
    if MILITARY_START <= target <= MILITARY_END:
        return build_military_message(target, amt)

    header = f"老板,{amt} {target.month}月{target.day}日(星期{weekday_cn(tw)})"

    # 周末或不在学期内 -> 全天无课
    if tw >= 5 or week is None:
        return f"{header}全天无课,好好休息。"
    if week in NO_CLASS_WEEKS:
        return f"{header}属第{week}周无课周,全天无课。"
    if week == FINAL_EXAM_WEEK:
        header = f"{header}为期末考试周"
    if week == MID_EXAM_WEEK:
        header = f"{header}为期中考试周"

    lines = [f"{header}课程安排如下:"]
    used = []   # 有课的节次号
    for start, end, items in SCHEDULE[tw]:
        chosen = None
        for code, wstr in items:
            if week in parse_weeks(wstr):
                chosen = code
                break
        if chosen is None:
            continue
        c = COURSES[chosen]
        room = c["room"].get(tw, "教室见通知")
        for n in range(start, end + 1):
            lines.append(f"- 第{n}节({PERIODS[n]}) {c['name']},教室{room},授课教师{c['teacher']}")
            used.append(n)

    if not used:
        return f"{header}全天无课。"

    first, last = min(used), max(used)
    tail = []
    if first > 1:
        tail.append(f"上午1-{first - 1}节无课")
    tail.append(f"第{first}节起上课,最晚到第{last}节({PERIODS[last]})结束")
    lines.append(",".join(tail))
    return "\n".join(lines)

# ----------------------- 发送企业微信 -----------------------
WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=ea5913ef-8fb3-40a2-9e54-67e73e44c326"

def send(text):
    text = f"{text}\n\n马维斯推送"
    body = json.dumps({"msgtype": "text", "text": {"content": text}}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(WEBHOOK, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["today", "tomorrow"], default="today")
    args = ap.parse_args()
    msg = build_message(args.mode)
    print("=== 推送内容 ===")
    print(msg)
    print("=== 发送结果 ===")
    print(send(msg))
