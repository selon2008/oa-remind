#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""巨人培优·国庆上课安排 到点提醒
- 北京 20:00：10/6 提醒明天上周日班课；10/9 提醒后天上周日班课
- 北京 06:20：10/10 提醒今天公立学校补课
目标群：私人订制消息--仔仔京汉（f718c04a）
"""
import argparse, json, sys, urllib.request
from datetime import date, datetime, timezone, timedelta

WEBHOOK = ("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?"
           "key=f718c04a-ccdb-4eb1-a85c-2a3b311110a7")
SIGN = "\n\n马维斯CELL推送"
CN = timezone(timedelta(hours=8))

EVENING = {
    (10, 6): "【巨人培优·提醒】明天(10月7日)巨人培优上周日班课程，请提前做好接送安排。",
    (10, 9): "【巨人培优·提醒】后天(10月11日 周日)巨人培优上周日班课程，请提前做好接送安排。",
}
MORNING = {
    (10, 10): "【巨人培优·提醒】今天(10月10日 周六)公立学校补课，请按时到校。",
}

def build_message(target, mode):
    key = (target.month, target.day)
    return (EVENING if mode == "evening" else MORNING).get(key)

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
    ap.add_argument("--mode", choices=["evening", "morning"], required=True)
    ap.add_argument("--date", help="模拟日期 YYYY-MM-DD(默认北京今天)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    d = date.fromisoformat(a.date) if a.date else datetime.now(CN).date()
    msg = build_message(d, a.mode)
    if msg is None:
        print("未命中提醒节点，静默")
        return 0
    if a.dry_run:
        print(msg)
        return 0
    print(send(msg))
    return 0

if __name__ == "__main__":
    sys.exit(main())
