#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
李思远(仔仔) 学平险续保提醒脚本
保单期间：2026-09-17 ~ 2027-09-17
提醒节点（到期前）：2027-08-17 提前1个月 / 2027-09-02 提前半个月 / 2027-09-07 提前10天 / 2027-09-12 提前5天
推送对象：企业微信群（私人订制消息--仔仔京汉）
用法：
  python3 insurance_reminder.py                      # 按当天日期判断，命中节点才推送
  python3 insurance_reminder.py --date 2027-09-07    # 模拟指定日期（用于验证）
  python3 insurance_reminder.py --dry-run --date 2027-09-07   # 只打印不发群
"""
import argparse, json, sys, urllib.request
from datetime import date, datetime

WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f718c04a-ccdb-4eb1-a85c-2a3b311110a7"

INSURED = "李思远（仔仔）"
POLICY_START = date(2026, 9, 17)
POLICY_END = date(2027, 9, 17)

# 提醒节点：日期 -> 标签
TARGETS = [
    ("2027-08-17", "提前1个月"),
    ("2027-09-02", "提前半个月"),
    ("2027-09-07", "提前10天"),
    ("2027-09-12", "提前5天"),
]


def build_message(today):
    """命中提醒节点则返回文案，否则返回 None。"""
    for d, label in TARGETS:
        if today.isoformat() == d:
            left = (POLICY_END - today).days
            return (
                f"学平险续保提醒（{label}）：{INSURED}的学平险"
                f"（{POLICY_START:%Y-%m-%d} 至 {POLICY_END:%Y-%m-%d}）"
                f"将于 {left} 天后到期，请及时联系保险顾问办理续保。"
            )
    return None


def send(text):
    text = f"{text}\n\n马维斯推送"
    body = json.dumps({"msgtype": "text", "text": {"content": text}},
                      ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(WEBHOOK, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="", help="模拟日期 YYYY-MM-DD，留空用今天")
    ap.add_argument("--dry-run", action="store_true", help="只打印不发送")
    args = ap.parse_args()

    today = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()
    msg = build_message(today)

    if msg is None:
        print(f"{today} 非提醒节点，不发送。节点：{[d for d, _ in TARGETS]}")
        return 0
    print(msg)
    if args.dry_run:
        print("[dry-run] 未发送")
        return 0
    print(send(msg))
    return 0


if __name__ == "__main__":
    sys.exit(main())
