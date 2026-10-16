#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
麦当劳 MCP 省钱点餐助手 (main.py)
==================================
通过麦当劳 MCP (mcd-mcp) 远程服务，自动查询门店 / 菜单 / 优惠券 / 价格，
为给定约束（预算、不吃辣、一人、主食+饮料）推荐【最省钱的唯一组合】。

所有鉴权信息均从环境变量读取，绝不硬编码 Token。

依赖安装：
    pip install "mcp>=2.0" httpx

环境变量（必填 / 可选）：
    MCD_MCP_TOKEN   麦当劳 MCP Bearer Token（必填）
    MCD_MCP_URL     服务地址，默认 https://mcp.mcd.cn
    MCD_CITY        城市，默认 广州
    MCD_DISTRICT    区域，默认 天河区
    MCD_STORE_CODE  直接指定门店 storeCode（设置后跳过附近门店查询）
    MCD_BUDGET      预算（元），默认 20
    MCD_NO_SPICY    1=不吃辣（默认 1）
    MCD_PERSONS     人数，默认 1
    MCD_WANT_STAPLE 1=需要主食（默认 1）
    MCD_WANT_DRINK  1=需要饮料（默认 1）
    MCD_DEBUG       1=把每个工具原始返回写入 *_raw.json 便于排查

运行：
    export MCD_MCP_TOKEN=你的token
    python main.py
"""

import os
import re
import sys
import json
import asyncio

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


# ---------------------------------------------------------------------------
# 配置（全部来自环境变量，禁止硬编码 Token）
# ---------------------------------------------------------------------------
TOKEN = None  # 仅在 main() 中从环境变量 MCD_MCP_TOKEN 读取，绝不硬编码
URL = os.environ.get("MCD_MCP_URL", "https://mcp.mcd.cn")
CITY = os.environ.get("MCD_CITY", "广州")
DISTRICT = os.environ.get("MCD_DISTRICT", "天河区")
STORE_CODE = os.environ.get("MCD_STORE_CODE")  # 可选覆盖
BUDGET = float(os.environ.get("MCD_BUDGET", "20"))
NO_SPICY = os.environ.get("MCD_NO_SPICY", "1") == "1"
PERSONS = int(os.environ.get("MCD_PERSONS", "1"))
WANT_STAPLE = os.environ.get("MCD_WANT_STAPLE", "1") == "1"
WANT_DRINK = os.environ.get("MCD_WANT_DRINK", "1") == "1"
DEBUG = os.environ.get("MCD_DEBUG", "0") == "1"


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------
def is_spicy(name: str) -> bool:
    """根据名称判断是否为辣味（用户说“不想吃太辣的”）。"""
    spicy_kw = ["辣", "麻辣", "香辣", "酸辣", "辣翅", "龙焰", "火辣", "爆辣", "椒麻"]
    return any(k in name for k in spicy_kw)


def extract_json(text: str):
    """
    工具返回体通常是“字段说明(markdown) + 真实JSON”。
    在文本里尝试所有可能的 '{' 起点，取能解析且最长的一段作为 JSON。
    """
    best = None
    last = text.rfind("}")
    for i, ch in enumerate(text):
        if ch != "{":
            continue
        sub = text[i:last + 1]
        try:
            obj = json.loads(sub)
        except Exception:
            continue
        if best is None or len(sub) > len(best[1]):
            best = (sub, obj)
    return best[1] if best else None


def parse_coupons(text: str):
    """available-coupons 返回 markdown 列表，解析出 (标题, 状态)。"""
    out = []
    for seg in text.split("优惠券标题："):
        if "状态：" not in seg:
            continue
        title = seg.split("状态：")[0].replace("\\", "").strip()
        status = seg.split("状态：")[1].split("\n")[0].replace("\\", "").strip()
        if title:
            out.append((title, status))
    return out


def price_cents(obj) -> int:
    """从 calculate-price 的返回里取总价（单位：分）。"""
    d = (obj or {}).get("data", {}) or {}
    if "price" in d and d["price"] is not None:
        return int(d["price"])
    return sum(int(p.get("subtotal", 0) or 0) for p in d.get("productList", []))


def yuan(cents: int) -> str:
    return f"¥{cents / 100:.2f}"


# ---------------------------------------------------------------------------
# MCP 连接与调用
# ---------------------------------------------------------------------------
async def call_tool(session: ClientSession, name: str, args: dict):
    res = await session.call_tool(name, args)
    if getattr(res, "is_error", False):
        raise RuntimeError(f"工具 {name} 调用失败：{res}")
    text = "".join(getattr(b, "text", "") for b in res.content
                   if getattr(b, "type", None) == "text")
    if DEBUG:
        with open(f"{name}_raw.json", "w", encoding="utf-8") as f:
            f.write(text)
    return extract_json(text), text  # 返回 (解析后的dict或None, 原始文本)


async def get_session():
    """返回一个异步上下文管理器：(read_stream, write_stream)。"""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    http_client = httpx.AsyncClient(headers=headers, timeout=30)
    return streamable_http_client(URL, http_client=http_client), http_client


# ---------------------------------------------------------------------------
# 核心推荐逻辑
# ---------------------------------------------------------------------------
async def pick_combo(session, menu, budget, no_spicy):
    """
    在菜单里找“随心配 1+1”类组合，价格 <= 预算。
    对每个候选（从便宜到贵）查详情，挑出 不辣主食 + 饮料 的选法。
    返回 (combo_code, combo_name, combo_yuan, selection) 或 None。
    """
    data = menu.get("data", {})
    meals_map = data.get("meals", {})
    candidates = []
    for cat in data.get("categories", []):
        if "随心配" not in cat.get("name", ""):
            continue
        for ref in cat.get("meals", []):
            code = ref.get("code")
            detail = meals_map.get(code, {})
            try:
                price = float(detail.get("currentPrice", "0"))
            except (TypeError, ValueError):
                continue
            if budget >= price >= 0:
                candidates.append((price, code, detail.get("name", "")))
    candidates.sort(key=lambda x: x[0])  # 便宜优先

    for price, code, name in candidates:
        detail_obj, _ = await call_tool(session, "query-meal-detail",
            {"storeCode": STORE_CODE, "orderType": 1, "beType": 1, "code": code})
        rounds = (detail_obj or {}).get("data", {}).get("rounds", [])
        if not rounds:
            continue
        staple_round = rounds[0]
        drink_round = rounds[-1]
        staple = next((c for c in staple_round.get("choices", [])
                       if not (no_spicy and is_spicy(c.get("name", "")))), None)
        drink = next((c for c in drink_round.get("choices", [])), None)
        if not staple or not drink:
            continue
        return {
            "code": code, "name": name, "price": price,
            "staple_code": staple["code"], "staple_name": staple["name"],
            "drink_code": drink["code"], "drink_name": drink["name"],
        }
    return None


async def main():
    global TOKEN, STORE_CODE
    TOKEN = os.environ.get("MCD_MCP_TOKEN")
    if not TOKEN:
        sys.exit("❌ 请先设置环境变量 MCD_MCP_TOKEN（麦当劳 MCP Bearer Token）")

    # 1) 连接 MCP
    transport_cm, http_client = await get_session()
    async with transport_cm as (r, w):
        try:
            async with ClientSession(r, w) as session:
                await session.initialize()

                # 2) 确定门店
                if STORE_CODE:
                    store_name = f"指定门店({STORE_CODE})"
                else:
                    stores_obj, _ = await call_tool(session, "query-nearby-stores",
                        {"beType": 1, "searchType": 2, "city": CITY, "keyword": DISTRICT})
                    stores = (stores_obj or {}).get("data", [])
                    if not stores:
                        sys.exit(f"❌ 在 {CITY}{DISTRICT} 附近没有查到门店")
                    STORE_CODE = stores[0]["storeCode"]
                    store_name = stores[0].get("storeName", STORE_CODE)
                print(f"🏪 门店：{store_name}  (storeCode={STORE_CODE})\n")

                # 3) 菜单
                menu_obj, _ = await call_tool(session, "query-meals",
                    {"storeCode": STORE_CODE, "orderType": 1, "beType": 1})

                # 4) 优惠券
                _, coupon_text = await call_tool(session, "available-coupons", {})
                coupons = parse_coupons(coupon_text)

                # 5) 选最省组合
                combo = await pick_combo(session, menu_obj, BUDGET, NO_SPICY)
                if not combo:
                    sys.exit("❌ 当前菜单里没有满足条件的“随心配”组合，无法给出推荐")

                # 6) 用 calculate-price 取权威价格（单位：分）
                combo_obj, _ = await call_tool(session, "calculate-price",
                    {"storeCode": STORE_CODE, "orderType": 1, "beType": 1,
                     "items": [{"productCode": combo["code"], "quantity": 1}]})
                combo_cents = price_cents(combo_obj)

                single_obj, _ = await call_tool(session, "calculate-price",
                    {"storeCode": STORE_CODE, "orderType": 1, "beType": 1,
                     "items": [{"productCode": combo["staple_code"], "quantity": 1},
                               {"productCode": combo["drink_code"], "quantity": 1}]})
                single_cents = price_cents(single_obj)

                saved = single_cents - combo_cents
                saved_pct = (saved / single_cents * 100) if single_cents else 0

                # 7) 优惠券是否适用
                applicable = [c for c in coupons
                              if any(k in c[0] for k in
                                     [combo["staple_name"], combo["drink_name"], combo["name"]])]
                coupon_note = ("（其中可用券：" + "、".join(f"{t}({s})" for t, s in applicable) + "）") \
                    if applicable else "（当前券均不适用于此组合，随心配已是最低价）"

                # 8) 输出
                print("🎯 推荐组合（最省钱）：%s  %s" % (combo["name"], yuan(combo_cents)))
                print("   🍔 主食：%s%s" % (combo["staple_name"],
                                           "（不辣）" if NO_SPICY else ""))
                print("   🥤 饮料：%s%s" % (combo["drink_name"],
                                           "（不辣）" if NO_SPICY else ""))
                print()
                print("   ✅ 预算 %s 元：%s" % (f"{BUDGET:.0f}",
                                                "满足" if combo_cents <= BUDGET * 100 else "超支"))
                print("   ✅ 不吃辣：%s" % ("满足" if not (NO_SPICY and is_spicy(combo["staple_name"])) else "不满足"))
                print("   ✅ 一人吃：%s" % ("满足" if PERSONS == 1 else f"按{PERSONS}人计"))
                print("   ✅ 主食+饮料：满足")
                print()
                print("   💡 省钱对比：单点「%s + %s」要 %s，" %
                      (combo["staple_name"], combo["drink_name"], yuan(single_cents)))
                print("      用「%s」只花 %s，" % (combo["name"], yuan(combo_cents)))
                print("      省了 %s（约 %.0f%% off）" % (yuan(saved), saved_pct))
                print("   🎫 优惠券：%s" % coupon_note)
                print()
                print("   到点单时直接点「%s」，选 %s + %s 即可。" %
                      (combo["name"], combo["staple_name"], combo["drink_name"]))
        finally:
            await http_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
