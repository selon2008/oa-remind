#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""京汉九年级4班 每日课程与作息提醒（武汉市十一初级中学）

- 北京 06:20 推送【当天】课程与时间安排
- 北京 20:00 推送【次日】课程与时间安排
- 发往企业微信群：私人订制消息--仔仔京汉（f718c04a）
数据来源：家长提供的《京汉九年级4班课程表》《作息时间表》照片
"""
import argparse
import json
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone

WEBHOOK = ("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?"
           "key=f718c04a-ccdb-4eb1-a85c-2a3b311110a7")
SIGN = "\n\n马维斯推送"
CN = timezone(timedelta(hours=8))
WD_CN = "一二三四五六日"

# ---- 作息时间（源自作息时间表）----
T_LINEUP = "7:40-7:55"      # 自习(升旗)，仅周一
T_AM1 = "8:05-8:50"
T_AM2 = "9:00-9:45"
T_BIG = "9:45-10:30"        # 体育活动/大课间
T_AM3 = "10:30-11:15"
T_AM4 = "11:25-12:10"
T_LUNCH = "12:10-12:40"
T_NAP = "13:00-13:50"
T_XIHUI = "13:50-14:00"
T_PM1 = "14:00-14:45"       # 第五节
T_PMBRK = "14:45-15:00"     # 大课间(眼保健操)
T_PM2 = "15:00-15:45"       # 第六节
T_PM3 = "15:55-16:40"       # 第七节
T_DELAY = "16:50-18:20"     # 课后延时服务

# ---- 课程表（周一~周五顺序；自习/班会无教师）----
AM1 = [("物理", "丁凯"), ("化学", "张丽娜"), ("化学", "张丽娜"), ("历史", "陈瑜"), ("英语", "邵洪慧")]
AM2 = [("语文", "吴婷"), ("数学", "张凡"), ("数学", "张凡"), ("道法", "孔德霖"), ("数学", "张凡")]
BIG = [("道法", "孔德霖"), ("历史", "陈瑜"), ("道法", "孔德霖"), ("", ""), ("", "")]
AM3 = [("化学", "张丽娜"), ("语文", "吴婷"), ("英语", "邵洪慧"), ("英语", "邵洪慧"), ("数学", "张凡")]
AM4 = [("数学", "张凡"), ("语文", "吴婷"), ("英语", "邵洪慧"), ("语文", "吴婷"), ("物理", "丁凯")]
PM1 = [("英语", "邵洪慧"), ("英语", "邵洪慧"), ("物理", "丁凯"), ("物理", "丁凯"), ("化学", "张丽娜")]
PM2 = [("历史", "陈瑜"), ("物理", "丁凯"), ("语文", "吴婷"), ("数学", "张凡"), ("语文", "吴婷")]
PM3 = [("体育", "胡霞飞"), ("体育", "胡霞飞"), ("道法", "孔德霖"), ("自习", ""), ("班会", "")]


def _line(label, span, subject, teacher):
    if not subject:
        return f"- {label}({span}) 休息/体育活动"
    if not teacher:
        return f"- {label}({span}) {subject}"
    return f"- {label}({span}) {subject},教师{teacher}"


def build_message(target, mode):
    """mode: today / next"""
    wd = target.weekday()
    tag = "今日" if mode == "today" else "明日"
    head = f"【京汉九年级4班·{tag}课程】{target.strftime('%Y-%m-%d')} 周{WD_CN[wd]}"
    if wd >= 5:
        nxt = target + timedelta(days=(7 - wd))
        return (f"{head}\n"
                f"- {'今天' if mode == 'today' else '明天'}是周{'六日'[wd - 5]},没有课,休息\n"
                f"- 下一次上课:{nxt.strftime('%Y-%m-%d')} 周一")

    lines = [head]
    if wd == 0:
        lines.append(f"- 升旗仪式({T_LINEUP})")
    lines.append(_line("第1节", T_AM1, *AM1[wd]))
    lines.append(_line("第2节", T_AM2, *AM2[wd]))
    lines.append(_line("大课间", T_BIG, *BIG[wd]))
    lines.append(_line("第3节", T_AM3, *AM3[wd]))
    lines.append(_line("第4节", T_AM4, *AM4[wd]))
    lines.append(f"- 午餐({T_LUNCH}) 午休({T_NAP}) 夕会({T_XIHUI})")
    lines.append(_line("第5节", T_PM1, *PM1[wd]))
    lines.append(_line("第6节", T_PM2, *PM2[wd]))
    lines.append(_line("第7节", T_PM3, *PM3[wd]))
    lines.append(f"- 课后延时服务({T_DELAY})")
    lines.append("小结:上午4节+大课间,下午3节,共7节;含课间操与课后延时服务。")
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
    ap.add_argument("--mode", choices=["today", "next"], required=True)
    ap.add_argument("--date", help="模拟基准日期 YYYY-MM-DD(默认北京今天)")
    ap.add_argument("--dry-run", action="store_true", help="只打印不发送")
    a = ap.parse_args()
    base = date.fromisoformat(a.date) if a.date else datetime.now(CN).date()
    target = base if a.mode == "today" else base + timedelta(days=1)
    msg = build_message(target, a.mode)
    if a.dry_run:
        print(msg)
        return 0
    print(send(msg))
    return 0


if __name__ == "__main__":
    sys.exit(main())
