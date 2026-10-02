#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""吉利车贷还款提醒（个人事务群 7debbcf9）
吉利12万车贷 3333.33元×36期，2026-04-07第一期 ~ 2029-03-07最后一期。
每月还款日 7 号；每月 4 号(提前3天)、6 号(提前1天)、7 号(当天) 各推一次。
"""
import argparse, json, sys, urllib.request
from datetime import date, datetime, timezone, timedelta

WEBHOOK = ("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?"
           "key=7debbcf9-f8d6-42ae-8928-ed15b167f5ac")
SIGN = "\n\n马维斯CELL推送"
CN = timezone(timedelta(hours=8))
CARD = "吉利车贷（12万，3333.33元×36期）"
DUE_DAY = 7
FIRST_YEAR, FIRST_MONTH = 2026, 4   # 第一期 2026-04-07
TOTAL = 36
BANK = "工商银行卡 尾号3454"

def build(today):
    day = today.day
    if day == DUE_DAY - 3:
        head = f"【车贷还款提醒·提前3天】{CARD}"
    elif day == DUE_DAY - 1:
        head = f"【车贷还款提醒·提前1天】{CARD}"
    elif day == DUE_DAY:
        head = f"【车贷还款提醒·今天到期】{CARD}"
    else:
        return None
    n = (today.year - FIRST_YEAR) * 12 + (today.month - FIRST_MONTH) + 1
    if 1 <= n <= TOTAL:
        period = f"本期为第 {n} 期（共{TOTAL}期）"
    else:
        period = f"共{TOTAL}期"
    lines = [
        head,
        f"本月（{today.year}年{today.month}月）还款日为 {today.month}月{DUE_DAY}日，应还 3333.33 元。{period}",
        f"还款渠道：吉致好车小程序；扣款银行：{BANK}。请确保账户余额充足。",
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
        print(f"今天（{today}）不是提醒日（4/6/7号），跳过")
        return 0
    if a.dry_run:
        print(msg)
        return 0
    print(msg)
    print(send(msg))
    return 0

if __name__ == "__main__":
    sys.exit(main())
