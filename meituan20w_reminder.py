#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""美团还款 20 万提醒（个人事务群 7debbcf9）
2026年11月3号、11月4号 各推一次，提醒在美团还 20 万。
"""
import argparse, json, sys, urllib.request
from datetime import date, datetime, timezone, timedelta

WEBHOOK = ("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?"
           "key=7debbcf9-f8d6-42ae-8928-ed15b167f5ac")
SIGN = "\n\n马维斯CELL推送"
CN = timezone(timedelta(hours=8))
TARGETS = {(11, 3), (11, 4)}  # (月, 日)

def build(today):
    if (today.month, today.day) not in TARGETS:
        return None
    tag = "今天" if today.day == 3 else "明天"
    lines = [
        f"【美团还款 20 万提醒·{tag}】",
        "请于 11 月 4 日前在美团平台完成 20 万元还款，避免逾期。",
        "还款渠道：美团App → 我的 → 月付/钱包 → 待还账单。",
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
        print(f"今天（{today}）不是提醒日（11月3/4号），跳过")
        return 0
    if a.dry_run:
        print(msg)
        return 0
    print(msg)
    print(send(msg))
    return 0

if __name__ == "__main__":
    sys.exit(main())
