#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""联想Y9000P售后/保障服务到期提醒（个人事务群）
设备：Legion Y9000P IAX10，主机编号 PF5Y7S5D
每个服务到期日 T：提前30天、提前15天、提前1天 各推一次。
"""
import argparse, json, sys, urllib.request
from datetime import date, datetime, timezone, timedelta

WEBHOOK = ("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?"
           "key=7debbcf9-f8d6-42ae-8928-ed15b167f5ac")
SIGN = "\n\n马维斯CELL推送"
CN = timezone(timedelta(hours=8))
DEVICE = "联想拯救者 Y9000P IAX10（主机编号 PF5Y7S5D）"

# (服务名, 到期日)
SERVICES = [
    ("消费笔记本6个月保障服务", "2027-02-10"),
    ("笔记本标准服务（整机1年保修）", "2027-08-10"),
    ("消费笔记本二年全面保修送修", "2028-08-10"),
    ("星月服务（7*24客服）", "2028-08-10"),
    ("消费笔记本拯救者特色服务", "2028-08-10"),
    ("主要服务上门期", "2030-10-26"),
    ("意外保保修", "2030-10-26"),
    ("Lenovo Care智臻5年-延长三年基础保修", "2030-10-26"),
    ("Lenovo Care智臻5年-5年上门", "2030-10-26"),
    ("Lenovo Care智臻5年-5年意外保", "2030-10-26"),
    ("Lenovo Care智臻5年-硬盘不回收", "2030-10-26"),
    ("Lenovo Care智臻5年-7*24技术支持", "2031-10-01"),
    ("Lenovo Care智臻5年-专属人工", "2031-10-01"),
    ("Lenovo Care智臻5年-一年一次到店体检", "2031-10-01"),
    ("Lenovo Care智臻5年-综合软件支持", "2031-10-01"),
    ("IT设备环保处置服务", "2046-08-10"),
]

LEADS = [(30, "提前1个月"), (15, "提前15天"), (1, "提前1天")]


def build(today):
    hits = []  # (lead_label, due, name)
    for name, due_s in SERVICES:
        due = date.fromisoformat(due_s)
        if today > due:
            continue
        for lead, label in LEADS:
            if today == due - timedelta(days=lead):
                hits.append((label, due_s, name))
                break
    if not hits:
        return None
    lines = [f"【联想售后服务到期提醒】{DEVICE}"]
    for label, due, name in sorted(hits, key=lambda x: x[1]):
        lines.append(f"- {name}｜{due}到期（{label}）")
    lines.append("请提前安排续保或确认保障状态。")
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
        print(f"今天（{today}）无到期提醒节点，跳过")
        return 0
    if a.dry_run:
        print(msg)
        return 0
    print(msg)
    print(send(msg))
    return 0


if __name__ == "__main__":
    sys.exit(main())
