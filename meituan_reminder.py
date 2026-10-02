#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""美团月付还款提醒（个人事务群 7debbcf9）
每月还款日 8 号；每月 5 号(提前3天)、7 号(提前1天)、8 号(当天) 各推一次。
"""
import argparse, json, sys, urllib.request
from datetime import date, datetime, timezone, timedelta

WEBHOOK = ("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?"
           "key=7debbcf9-f8d6-42ae-8928-ed15b167f5ac")
SIGN = "\n\n马维斯CELL推送"
CN = timezone(timedelta(hours=8))
CARD = "美团月付"
DUE_DAY = 8

def build(today):
    day = today.day
    if day == DUE_DAY - 3:
        head = f"【美团月付还款提醒·提前3天】{CARD}"
    elif day == DUE_DAY - 1:
        head = f"【美团月付还款提醒·提前1天】{CARD}"
    elif day == DUE_DAY:
        head = f"【美团月付还款提醒·今天到期】{CARD}"
    else:
        return None
    lines = [
        head,
        f"本月（{today.year}年{today.month}月）还款日为 {today.month}月{DUE_DAY}日，请记得按时还款。",
        "还款渠道：美团App → 我的 → 月付 → 待还账单，可手动还款或开通自动还款。",
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
        print(f"今天（{today}）不是提醒日（5/7/8号），跳过")
        return 0
    if a.dry_run:
        print(msg)
        return 0
    print(msg)
    print(send(msg))
    return 0

if __name__ == "__main__":
    sys.exit(main())
