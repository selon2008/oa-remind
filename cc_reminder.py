#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""广发车主金卡还款提醒（个人事务群 f718c04a）
每月还款日 4 号；每月 1 号(提前3天)、3 号(提前1天)、4 号(当天) 各推一次。
"""
import argparse, json, sys, urllib.request
from datetime import date, datetime, timezone, timedelta

WEBHOOK = ("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?"
           "key=f718c04a-ccdb-4eb1-a85c-2a3b311110a7")
SIGN = "\n\n马维斯推送"
CN = timezone(timedelta(hours=8))
CARD = "广发车主金卡（广发银行信用卡ETC）尾号7792"
DUE_DAY = 4

def build(today):
    day = today.day
    if day == DUE_DAY - 3:
        head = f"【信用卡还款提醒·提前3天】{CARD}"
    elif day == DUE_DAY - 1:
        head = f"【信用卡还款提醒·提前1天】{CARD}"
    elif day == DUE_DAY:
        head = f"【信用卡还款提醒·今天到期】{CARD}"
    else:
        return None
    lines = [
        head,
        f"本月（{today.year}年{today.month}月）还款日为 {today.month}月{DUE_DAY}日，请记得按时还款，避免逾期影响征信。",
        "还款渠道：广发银行App、云闪付、绑定储蓄卡自动还款等均可。",
    ]
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
    ap.add_argument("--date", default="", help="模拟日期 YYYY-MM-DD（留空=今天）")
    ap.add_argument("--dry-run", action="store_true", help="只打印不发送")
    a = ap.parse_args()
    today = date.fromisoformat(a.date) if a.date else datetime.now(CN).date()
    msg = build(today)
    if msg is None:
        print(f"今天（{today}）不是提醒日（1/3/4号），跳过")
        return 0
    if a.dry_run:
        print(msg)
        return 0
    print(msg)
    print(send(msg))
    return 0

if __name__ == "__main__":
    sys.exit(main())
