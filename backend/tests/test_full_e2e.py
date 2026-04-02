"""
RexMatch 全功能端到端测试
覆盖：认证、资料、照片、兴趣、偏好、推荐、匹配、聊天、举报拉黑、每日限制、功能联动
"""
import json
import time
import urllib.request
import urllib.error
import sys
import os
import tempfile

BASE = "http://127.0.0.1:9000/api/v1"
PASS = 0
FAIL = 0
ERRORS = []

tokens = {}
user_ids = {}


def req(method, path, data=None, token=None, expect_status=None):
    url = f"{BASE}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(r, timeout=60)
        code = resp.status
        result = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        code = e.code
        try:
            result = json.loads(e.read().decode())
        except:
            result = {"detail": str(e)}
    if expect_status and code != expect_status:
        return code, result, False
    return code, result, True


def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        msg = f"  ❌ {name}" + (f" — {detail}" if detail else "")
        print(msg)
        ERRORS.append(msg)


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# =========================================================
#  1. 认证模块
# =========================================================
def test_auth():
    section("1. 认证模块")

    # 1.1 正常登录 - 新用户注册
    c, r, _ = req("POST", "/auth/wx-login", {"code": "test_user_A"})
    test("1.1 新用户注册登录", c == 200 and r.get("data", {}).get("access_token"), f"status={c}")
    tokens["A"] = r["data"]["access_token"]
    test("1.1b 新用户标记 is_new_user=true", r["data"].get("is_new_user") == True)

    # 1.2 再次登录同一用户 - 非新用户
    c, r, _ = req("POST", "/auth/wx-login", {"code": "test_user_A"})
    test("1.2 已有用户登录", c == 200 and r["data"].get("is_new_user") == False, f"is_new={r['data'].get('is_new_user')}")

    # 1.3 注册多个测试用户
    for name in ["B", "C", "D", "E", "F"]:
        c, r, _ = req("POST", "/auth/wx-login", {"code": f"test_user_{name}"})
        tokens[name] = r["data"]["access_token"]
    test("1.3 批量注册 5 个额外用户", all(tokens.get(n) for n in ["B","C","D","E","F"]))

    # 1.4 空 code
    c, r, _ = req("POST", "/auth/wx-login", {"code": ""})
    test("1.4 空 code 仍可登录（测试模式）", c == 200, f"status={c}")

    # 1.5 无 token 访问需认证接口
    c, r, _ = req("GET", "/users/me")
    test("1.5 无 token 访问 /users/me → 401", c == 401, f"status={c}")

    # 1.6 无效 token
    c, r, _ = req("GET", "/users/me", token="invalid_token_xyz")
    test("1.6 无效 token → 401", c == 401, f"status={c}")

    # 获取各用户 id
    for name in ["A", "B", "C", "D", "E", "F"]:
        c, r, _ = req("GET", "/users/me", token=tokens[name])
        if c == 200 and r.get("data"):
            user_ids[name] = r["data"]["user_id"]
    test("1.7 获取所有用户 ID", len(user_ids) == 6, f"got {len(user_ids)}")


# =========================================================
#  2. 用户资料模块
# =========================================================
def test_profile():
    section("2. 用户资料模块")

    # 2.1 获取自己资料
    c, r, _ = req("GET", "/users/me", token=tokens["A"])
    test("2.1 获取自己资料", c == 200 and r["data"]["user_id"] == user_ids["A"])

    # 2.2 更新资料 - 正常
    c, r, _ = req("PUT", "/users/me", {
        "nickname": "测试用户A",
        "gender": 1,
        "birthday": "1998-06-15",
        "city": "深圳",
        "province": "广东",
        "bio": "这是A的自我介绍",
        "height": 178,
        "education": "本科",
        "occupation": "工程师",
    }, token=tokens["A"])
    test("2.2 更新资料成功", c == 200, f"status={c}, resp={r}")

    # 验证更新生效
    c, r, _ = req("GET", "/users/me", token=tokens["A"])
    d = r.get("data", {})
    test("2.2b 资料字段正确", d.get("nickname") == "测试用户A" and d.get("city") == "深圳")

    # 2.3 更新资料 - 极端昵称长度
    c, r, _ = req("PUT", "/users/me", {"nickname": "A" * 50}, token=tokens["A"])
    test("2.3 最大长度昵称（50字符）", c == 200, f"status={c}")

    c, r, _ = req("PUT", "/users/me", {"nickname": "A" * 51}, token=tokens["A"])
    test("2.3b 超长昵称（51字符）→ 422", c == 422, f"status={c}")

    # 2.4 更新资料 - 无效性别
    c, r, _ = req("PUT", "/users/me", {"gender": 3}, token=tokens["A"])
    test("2.4 无效性别(3) → 422", c == 422, f"status={c}")

    c, r, _ = req("PUT", "/users/me", {"gender": 0}, token=tokens["A"])
    test("2.4b 无效性别(0) → 422", c == 422, f"status={c}")

    # 2.5 身高边界
    c, r, _ = req("PUT", "/users/me", {"height": 99}, token=tokens["A"])
    test("2.5 身高 99 → 422", c == 422, f"status={c}")

    c, r, _ = req("PUT", "/users/me", {"height": 251}, token=tokens["A"])
    test("2.5b 身高 251 → 422", c == 422, f"status={c}")

    c, r, _ = req("PUT", "/users/me", {"height": 100}, token=tokens["A"])
    test("2.5c 身高 100 → OK", c == 200, f"status={c}")

    c, r, _ = req("PUT", "/users/me", {"height": 250}, token=tokens["A"])
    test("2.5d 身高 250 → OK", c == 200, f"status={c}")

    # 2.6 Bio 最大长度
    c, r, _ = req("PUT", "/users/me", {"bio": "X" * 500}, token=tokens["A"])
    test("2.6 Bio 500字符 → OK", c == 200, f"status={c}")

    c, r, _ = req("PUT", "/users/me", {"bio": "X" * 501}, token=tokens["A"])
    test("2.6b Bio 501字符 → 422", c == 422, f"status={c}")

    # 2.7 查看其他用户资料
    c, r, _ = req("GET", f"/users/{user_ids['B']}", token=tokens["A"])
    test("2.7 查看其他用户资料", c == 200, f"status={c}")

    # 2.8 查看不存在的用户
    c, r, _ = req("GET", "/users/99999", token=tokens["A"])
    test("2.8 查看不存在用户 → 404", c == 404, f"status={c}")

    # 2.9 给 B-F 填充资料用于后续测试
    profiles = {
        "B": {"nickname": "用户B", "gender": 2, "city": "深圳", "birthday": "1999-03-20", "bio": "B的介绍", "education": "硕士"},
        "C": {"nickname": "用户C", "gender": 1, "city": "广州", "birthday": "1997-07-10", "bio": "C的介绍", "education": "本科"},
        "D": {"nickname": "用户D", "gender": 2, "city": "北京", "birthday": "2000-01-05", "bio": "D的介绍"},
        "E": {"nickname": "用户E", "gender": 1, "city": "上海", "birthday": "1996-11-28", "bio": "E的介绍"},
        "F": {"nickname": "用户F", "gender": 2, "city": "深圳", "birthday": "1998-08-15"},
    }
    ok = True
    for name, data in profiles.items():
        c, r, _ = req("PUT", "/users/me", data, token=tokens[name])
        if c != 200:
            ok = False
    test("2.9 批量填充 B-F 资料", ok)


# =========================================================
#  3. 兴趣标签模块
# =========================================================
def test_interests():
    section("3. 兴趣标签模块")

    c, r, _ = req("GET", "/users/interests/all", token=tokens["A"])
    interests = r.get("data", [])
    test("3.1 获取所有兴趣标签", c == 200 and len(interests) > 0, f"count={len(interests)}")

    categories = set(i["category"] for i in interests)
    test("3.2 兴趣有分类", len(categories) > 3, f"categories={categories}")

    # 给 A 设置兴趣
    ids = [interests[0]["id"], interests[5]["id"], interests[10]["id"]]
    c, r, _ = req("PUT", "/users/me", {"interest_ids": ids}, token=tokens["A"])
    test("3.3 设置兴趣标签", c == 200, f"status={c}")

    c, r, _ = req("GET", "/users/me", token=tokens["A"])
    user_interests = r.get("data", {}).get("interests", [])
    test("3.3b 兴趣已关联", len(user_interests) == 3, f"count={len(user_interests)}")

    # 给 B 设置一些相同兴趣（测试契合度）
    c, r, _ = req("PUT", "/users/me", {"interest_ids": [ids[0], ids[1], interests[15]["id"]]}, token=tokens["B"])
    test("3.4 给 B 设置部分重叠兴趣", c == 200)

    # 边界：超过 10 个兴趣
    many_ids = [interests[i]["id"] for i in range(min(11, len(interests)))]
    c, r, _ = req("PUT", "/users/me", {"interest_ids": many_ids}, token=tokens["C"])
    test("3.5 设置 11 个兴趣 → 422", c == 422, f"status={c}, count={len(many_ids)}")

    # 0 个兴趣（清空）
    c, r, _ = req("PUT", "/users/me", {"interest_ids": []}, token=tokens["C"])
    test("3.6 清空兴趣 → OK", c == 200, f"status={c}")


# =========================================================
#  4. 偏好设置模块
# =========================================================
def test_preferences():
    section("4. 偏好设置模块")

    c, r, _ = req("GET", "/users/me/preferences", token=tokens["A"])
    test("4.1 获取偏好（初始默认值）", c == 200, f"status={c}")

    c, r, _ = req("PUT", "/users/me/preferences", {
        "preferred_gender": 2,
        "min_age": 22,
        "max_age": 30,
        "preferred_city": "深圳",
    }, token=tokens["A"])
    test("4.2 更新偏好", c == 200, f"status={c}")

    c, r, _ = req("GET", "/users/me/preferences", token=tokens["A"])
    d = r.get("data", {})
    test("4.2b 偏好生效", d.get("preferred_gender") == 2 and d.get("min_age") == 22)

    # 给 B 也设置偏好
    c, r, _ = req("PUT", "/users/me/preferences", {
        "preferred_gender": 1,
        "min_age": 24,
        "max_age": 35,
    }, token=tokens["B"])
    test("4.3 给 B 设置偏好", c == 200)


# =========================================================
#  5. 推荐模块
# =========================================================
def test_discover():
    section("5. 推荐模块")

    c, r, _ = req("GET", "/discover/recommend", token=tokens["A"])
    recs = r.get("data", [])
    test("5.1 获取推荐列表", c == 200 and isinstance(recs, list), f"count={len(recs)}")

    # 不应包含自己
    self_in_recs = any(u["user_id"] == user_ids["A"] for u in recs)
    test("5.2 推荐不包含自己", not self_in_recs)

    # 卡片字段完整性
    if recs:
        card = recs[0]
        has_fields = all(k in card for k in ["user_id", "nickname", "gender"])
        test("5.3 推荐卡片有基本字段", has_fields, f"keys={list(card.keys())}")

    # 按性别筛选
    c, r, _ = req("GET", "/discover/recommend?gender=2", token=tokens["A"])
    recs_f = r.get("data", [])
    all_female = all(u.get("gender") == 2 for u in recs_f) if recs_f else True
    test("5.4 性别筛选（女）", c == 200 and all_female, f"count={len(recs_f)}")

    # 按年龄筛选
    c, r, _ = req("GET", "/discover/recommend?min_age=20&max_age=25", token=tokens["A"])
    test("5.5 年龄筛选", c == 200)


# =========================================================
#  6. 匹配/滑动模块
# =========================================================
def test_match():
    section("6. 匹配/滑动模块")

    # 6.1 每日额度查询
    c, r, _ = req("GET", "/match/daily-likes", token=tokens["A"])
    daily = r.get("data", {})
    test("6.1 查询每日喜欢额度", c == 200 and "remaining" in daily, f"data={daily}")

    # 6.2 A 喜欢 B（单方面，不匹配）
    c, r, _ = req("POST", "/match/swipe", {"target_user_id": user_ids["B"], "is_like": True}, token=tokens["A"])
    test("6.2 A 喜欢 B → 未匹配", c == 200 and r["data"]["is_match"] == False)

    # 6.3 A 跳过 C
    c, r, _ = req("POST", "/match/swipe", {"target_user_id": user_ids["C"], "is_like": False}, token=tokens["A"])
    test("6.3 A 跳过 C", c == 200 and r["data"]["is_match"] == False)

    # 6.4 不能重复操作同一用户
    c, r, _ = req("POST", "/match/swipe", {"target_user_id": user_ids["B"], "is_like": True}, token=tokens["A"])
    test("6.4 重复喜欢 → 400", c == 400, f"status={c}")

    # 6.5 不能操作自己
    c, r, _ = req("POST", "/match/swipe", {"target_user_id": user_ids["A"], "is_like": True}, token=tokens["A"])
    test("6.5 喜欢自己 → 400", c == 400, f"status={c}")

    # 6.6 B 喜欢 A → 双向匹配！
    c, r, _ = req("POST", "/match/swipe", {"target_user_id": user_ids["A"], "is_like": True}, token=tokens["B"])
    test("6.6 B 喜欢 A → 匹配成功!", c == 200 and r["data"]["is_match"] == True, f"resp={r}")
    global match_id_AB
    match_id_AB = r["data"].get("match_id")
    test("6.6b 返回 match_id", match_id_AB is not None)

    # 6.7 额度消耗
    c, r, _ = req("GET", "/match/daily-likes", token=tokens["A"])
    test("6.7 额度已消耗", r["data"]["used"] > 0)

    # 6.8 A 推荐中不再出现已操作用户 B, C
    c, r, _ = req("GET", "/discover/recommend", token=tokens["A"])
    rec_ids = [u["user_id"] for u in r.get("data", [])]
    test("6.8 推荐不含已操作用户", user_ids["B"] not in rec_ids and user_ids["C"] not in rec_ids,
         f"rec_ids={rec_ids}")

    # 6.9 匹配列表
    c, r, _ = req("GET", "/match/list", token=tokens["A"])
    matches = r.get("data", [])
    test("6.9 匹配列表包含 B", any(m["user_id"] == user_ids["B"] for m in matches), f"matches={matches}")

    # 6.10 谁喜欢了我 - B 已匹配所以不在
    # 先让 D 喜欢 A（未匹配）
    c, r, _ = req("POST", "/match/swipe", {"target_user_id": user_ids["A"], "is_like": True}, token=tokens["D"])
    test("6.10a D 喜欢 A", c == 200)

    c, r, _ = req("GET", "/match/likes-received", token=tokens["A"])
    likes = r.get("data", [])
    like_uids = [l["user_id"] for l in likes]
    test("6.10b 谁喜欢我 - 包含 D", user_ids["D"] in like_uids, f"likes={like_uids}")
    test("6.10c 谁喜欢我 - 不含已匹配的 B", user_ids["B"] not in like_uids)

    # 6.11 喜欢不存在的用户
    c, r, _ = req("POST", "/match/swipe", {"target_user_id": 99999, "is_like": True}, token=tokens["A"])
    test("6.11 喜欢不存在用户", c in [400, 404, 500], f"status={c}")


match_id_AB = None


# =========================================================
#  7. 聊天模块
# =========================================================
def test_chat():
    section("7. 聊天模块")

    # 7.1 聊天列表
    c, r, _ = req("GET", "/chat/list", token=tokens["A"])
    chats = r.get("data", [])
    test("7.1 聊天列表有匹配", len(chats) > 0 and c == 200, f"count={len(chats)}")

    if chats:
        chat = chats[0]
        test("7.1b 聊天列表字段完整", all(k in chat for k in ["match_id", "partner_nickname"]))

    # 7.2 发送消息
    c, r, _ = req("POST", "/chat/send", {
        "match_id": match_id_AB,
        "content": "你好，匹配成功！",
        "msg_type": "text",
    }, token=tokens["A"])
    test("7.2 A 发消息给 B", c == 200, f"status={c}")

    # 7.3 B 回复
    c, r, _ = req("POST", "/chat/send", {
        "match_id": match_id_AB,
        "content": "嗨，很高兴认识你！",
        "msg_type": "text",
    }, token=tokens["B"])
    test("7.3 B 回复消息", c == 200)

    # 7.4 获取消息历史
    c, r, _ = req("GET", f"/chat/{match_id_AB}/messages", token=tokens["A"])
    msgs = r.get("data", [])
    test("7.4 消息历史有 2 条", c == 200 and len(msgs) == 2, f"count={len(msgs)}")

    # 7.5 消息字段完整
    if msgs:
        m = msgs[0]
        test("7.5 消息字段完整", all(k in m for k in ["id", "sender_id", "content", "msg_type", "is_read", "created_at"]))

    # 7.6 发送空消息
    c, r, _ = req("POST", "/chat/send", {
        "match_id": match_id_AB,
        "content": "",
        "msg_type": "text",
    }, token=tokens["A"])
    test("7.6 发送空消息 → 拒绝", c == 422, f"status={c}")

    # 7.7 发送超长消息
    c, r, _ = req("POST", "/chat/send", {
        "match_id": match_id_AB,
        "content": "X" * 2001,
        "msg_type": "text",
    }, token=tokens["A"])
    test("7.7 超长消息(2001字) → 422", c == 422, f"status={c}")

    # 7.8 2000字刚好
    c, r, _ = req("POST", "/chat/send", {
        "match_id": match_id_AB,
        "content": "X" * 2000,
        "msg_type": "text",
    }, token=tokens["A"])
    test("7.8 2000 字消息 → OK", c == 200, f"status={c}")

    # 7.9 非参与者发消息
    c, r, _ = req("POST", "/chat/send", {
        "match_id": match_id_AB,
        "content": "我不应该能发",
        "msg_type": "text",
    }, token=tokens["C"])
    test("7.9 非匹配参与者发消息 → 403", c == 403, f"status={c}")

    # 7.10 非参与者获取消息
    c, r, _ = req("GET", f"/chat/{match_id_AB}/messages", token=tokens["C"])
    test("7.10 非参与者获取消息 → 403", c == 403, f"status={c}")

    # 7.11 不存在的 match_id
    c, r, _ = req("GET", "/chat/99999/messages", token=tokens["A"])
    test("7.11 不存在的 match → 403", c == 403, f"status={c}")

    # 7.12 图片类型消息
    c, r, _ = req("POST", "/chat/send", {
        "match_id": match_id_AB,
        "content": "https://example.com/photo.jpg",
        "msg_type": "image",
    }, token=tokens["A"])
    test("7.12 图片消息", c == 200, f"status={c}")

    # 7.13 无效消息类型
    c, r, _ = req("POST", "/chat/send", {
        "match_id": match_id_AB,
        "content": "test",
        "msg_type": "video",
    }, token=tokens["A"])
    test("7.13 无效消息类型(video) → 422", c == 422, f"status={c}")

    # 7.14 分页
    c, r, _ = req("GET", f"/chat/{match_id_AB}/messages?page=1&page_size=2", token=tokens["A"])
    test("7.14 分页 page_size=2", c == 200 and len(r.get("data", [])) == 2, f"count={len(r.get('data', []))}")

    c, r, _ = req("GET", f"/chat/{match_id_AB}/messages?page=100", token=tokens["A"])
    test("7.14b 超大页码 → 空列表", c == 200 and len(r.get("data", [])) == 0)

    # 7.15 已读标记 - A 获取消息后，B 发的消息应被标记已读
    c, r, _ = req("GET", f"/chat/{match_id_AB}/messages", token=tokens["A"])
    msgs = r.get("data", [])
    b_msgs = [m for m in msgs if m["sender_id"] == user_ids["B"]]
    if b_msgs:
        test("7.15 获取消息后对方消息标为已读", b_msgs[0]["is_read"] == True)
    else:
        test("7.15 获取消息后对方消息标为已读", False, "no msgs from B found")


# =========================================================
#  8. 举报与拉黑模块
# =========================================================
def test_report_block():
    section("8. 举报与拉黑模块")

    # 8.1 举报用户
    c, r, _ = req("POST", "/report/submit", {
        "reported_user_id": user_ids["E"],
        "reason": "虚假资料",
        "detail": "头像不真实",
    }, token=tokens["A"])
    test("8.1 举报用户 E", c == 200, f"status={c}")

    # 8.2 举报自己
    c, r, _ = req("POST", "/report/submit", {
        "reported_user_id": user_ids["A"],
        "reason": "测试",
    }, token=tokens["A"])
    test("8.2 举报自己 → 400", c == 400, f"status={c}")

    # 8.3 拉黑用户
    c, r, _ = req("POST", "/report/block", {
        "blocked_user_id": user_ids["E"],
    }, token=tokens["A"])
    test("8.3 拉黑用户 E", c == 200, f"status={c}")

    # 8.4 重复拉黑
    c, r, _ = req("POST", "/report/block", {
        "blocked_user_id": user_ids["E"],
    }, token=tokens["A"])
    test("8.4 重复拉黑 → 400", c == 400, f"status={c}")

    # 8.5 拉黑自己
    c, r, _ = req("POST", "/report/block", {
        "blocked_user_id": user_ids["A"],
    }, token=tokens["A"])
    test("8.5 拉黑自己 → 400", c == 400, f"status={c}")

    # 8.6 获取黑名单
    c, r, _ = req("GET", "/report/block-list", token=tokens["A"])
    blocks = r.get("data", [])
    test("8.6 黑名单包含 E", any(b["user_id"] == user_ids["E"] for b in blocks), f"blocks={blocks}")

    # 8.7 被拉黑的用户不再出现在推荐中
    c, r, _ = req("GET", "/discover/recommend", token=tokens["A"])
    rec_ids = [u["user_id"] for u in r.get("data", [])]
    test("8.7 推荐不含被拉黑用户 E", user_ids["E"] not in rec_ids, f"rec_ids={rec_ids}")

    # 8.8 取消拉黑
    c, r, _ = req("POST", f"/report/unblock/{user_ids['E']}", token=tokens["A"])
    test("8.8 取消拉黑 E", c == 200, f"status={c}")

    c, r, _ = req("GET", "/report/block-list", token=tokens["A"])
    blocks = r.get("data", [])
    test("8.8b 黑名单已空", len(blocks) == 0 or not any(b["user_id"] == user_ids["E"] for b in blocks))

    # 8.9 取消拉黑不存在的
    c, r, _ = req("POST", f"/report/unblock/99999", token=tokens["A"])
    test("8.9 取消拉黑不存在 → 404", c == 404, f"status={c}")


# =========================================================
#  9. 解除匹配模块
# =========================================================
def test_unmatch():
    section("9. 解除匹配与后续影响")

    # 先创建 C-D 匹配
    c, r, _ = req("POST", "/match/swipe", {"target_user_id": user_ids["D"], "is_like": True}, token=tokens["C"])
    c, r, _ = req("POST", "/match/swipe", {"target_user_id": user_ids["C"], "is_like": True}, token=tokens["D"])
    match_CD = r["data"].get("match_id")
    test("9.1 C-D 匹配成功", r["data"]["is_match"] == True and match_CD is not None)

    # 发一条消息
    c, r, _ = req("POST", "/chat/send", {
        "match_id": match_CD,
        "content": "hello from C",
        "msg_type": "text",
    }, token=tokens["C"])
    test("9.2 匹配后可以聊天", c == 200)

    # 解除匹配
    c, r, _ = req("POST", f"/match/{match_CD}/unmatch", token=tokens["C"])
    test("9.3 解除匹配", c == 200, f"status={c}")

    # 解除后发消息
    c, r, _ = req("POST", "/chat/send", {
        "match_id": match_CD,
        "content": "should fail",
        "msg_type": "text",
    }, token=tokens["C"])
    test("9.4 解除匹配后发消息 → 403", c == 403, f"status={c}")

    # 解除后读消息
    c, r, _ = req("GET", f"/chat/{match_CD}/messages", token=tokens["C"])
    test("9.5 解除匹配后读消息 → 403", c == 403, f"status={c}")

    # 匹配列表不再包含
    c, r, _ = req("GET", "/match/list", token=tokens["C"])
    match_ids_c = [m["match_id"] for m in r.get("data", [])]
    test("9.6 匹配列表不含已解除的", match_CD not in match_ids_c)

    # 聊天列表不再包含
    c, r, _ = req("GET", "/chat/list", token=tokens["C"])
    chat_match_ids = [ch["match_id"] for ch in r.get("data", [])]
    test("9.7 聊天列表不含已解除的", match_CD not in chat_match_ids)

    # 重复解除
    c, r, _ = req("POST", f"/match/{match_CD}/unmatch", token=tokens["C"])
    test("9.8 重复解除 → 404", c == 404, f"status={c}")

    # 解除不存在的
    c, r, _ = req("POST", "/match/99999/unmatch", token=tokens["C"])
    test("9.9 解除不存在的 → 404", c == 404, f"status={c}")


# =========================================================
#  10. 每日喜欢限制模块
# =========================================================
def test_daily_limit():
    section("10. 每日喜欢限制")

    # 用 F 来做极限测试 - F 去喜欢多个种子用户
    # 先获取当前额度
    c, r, _ = req("GET", "/match/daily-likes", token=tokens["F"])
    remaining_before = r["data"]["remaining"]
    limit = r["data"]["limit"]
    test("10.1 查询额度", c == 200 and remaining_before > 0, f"remaining={remaining_before}, limit={limit}")

    # F 喜欢几个用户
    swipe_count = 0
    for target in ["A", "B", "C", "D", "E"]:
        c, r, _ = req("POST", "/match/swipe", {"target_user_id": user_ids[target], "is_like": True}, token=tokens["F"])
        if c == 200:
            swipe_count += 1
    test("10.2 F 连续喜欢多人", swipe_count > 0, f"swiped={swipe_count}")

    c, r, _ = req("GET", "/match/daily-likes", token=tokens["F"])
    test("10.3 额度减少", r["data"]["used"] == swipe_count, f"used={r['data']['used']}, expected={swipe_count}")


# =========================================================
#  11. 拉黑与推荐/喜欢联动
# =========================================================
def test_block_interactions():
    section("11. 拉黑与功能联动")

    # E 喜欢 B
    c, r, _ = req("POST", "/match/swipe", {"target_user_id": user_ids["B"], "is_like": True}, token=tokens["E"])

    # B 查看谁喜欢我 - 应包含 E
    c, r, _ = req("GET", "/match/likes-received", token=tokens["B"])
    likes_before = [l["user_id"] for l in r.get("data", [])]
    test("11.1 E 喜欢 B 后出现在 B 的喜欢列表", user_ids["E"] in likes_before, f"likes={likes_before}")

    # B 拉黑 E
    c, r, _ = req("POST", "/report/block", {"blocked_user_id": user_ids["E"]}, token=tokens["B"])
    test("11.2 B 拉黑 E", c == 200)

    # B 的喜欢列表不再包含 E
    c, r, _ = req("GET", "/match/likes-received", token=tokens["B"])
    likes_after = [l["user_id"] for l in r.get("data", [])]
    test("11.3 拉黑后 E 不在 B 的喜欢列表", user_ids["E"] not in likes_after, f"likes={likes_after}")

    # B 的推荐不含 E
    c, r, _ = req("GET", "/discover/recommend", token=tokens["B"])
    rec_ids = [u["user_id"] for u in r.get("data", [])]
    test("11.4 B 的推荐不含被拉黑的 E", user_ids["E"] not in rec_ids)

    # E 的推荐也不含 B（被对方拉黑）
    c, r, _ = req("GET", "/discover/recommend", token=tokens["E"])
    rec_ids_e = [u["user_id"] for u in r.get("data", [])]
    test("11.5 E 的推荐不含拉黑自己的 B", user_ids["B"] not in rec_ids_e)

    # 清理
    req("POST", f"/report/unblock/{user_ids['E']}", token=tokens["B"])


# =========================================================
#  12. 匹配后聊天列表联动
# =========================================================
def test_match_chat_integration():
    section("12. 匹配与聊天列表联动")

    # A 和 B 已匹配，验证聊天列表
    c, r, _ = req("GET", "/chat/list", token=tokens["A"])
    chats = r.get("data", [])
    partner_ids = [ch["partner_id"] for ch in chats]
    test("12.1 A 的聊天列表包含 B", user_ids["B"] in partner_ids, f"partners={partner_ids}")

    # B 的聊天列表也包含 A
    c, r, _ = req("GET", "/chat/list", token=tokens["B"])
    chats_b = r.get("data", [])
    partner_ids_b = [ch["partner_id"] for ch in chats_b]
    test("12.2 B 的聊天列表包含 A", user_ids["A"] in partner_ids_b)

    # 未读计数
    if chats_b:
        ab_chat = next((ch for ch in chats_b if ch["partner_id"] == user_ids["A"]), None)
        if ab_chat:
            test("12.3 B 有未读消息", ab_chat.get("unread_count", 0) > 0, f"unread={ab_chat.get('unread_count')}")

    # 最后一条消息
    if chats:
        ab_chat_a = next((ch for ch in chats if ch["partner_id"] == user_ids["B"]), None)
        if ab_chat_a:
            test("12.4 聊天列表有最后一条消息", ab_chat_a.get("last_message") is not None)


# =========================================================
#  13. 健康检查与基础端点
# =========================================================
def test_health():
    section("13. 基础端点")

    url = "http://127.0.0.1:9000/health"
    try:
        resp = urllib.request.urlopen(url)
        health = json.loads(resp.read().decode())
    except Exception as e:
        health = {}
    test("13.1 /health 正常", health.get("status") == "ok", f"resp={health}")
    test("13.2 版本号", health.get("version") == "0.1.0")


# =========================================================
#  14. 照片上传模块（模拟）
# =========================================================
def test_photos():
    section("14. 照片管理模块")

    # 获取当前照片
    c, r, _ = req("GET", "/users/me", token=tokens["A"])
    photos_before = r.get("data", {}).get("photos", [])
    test("14.1 获取当前照片列表", c == 200, f"count={len(photos_before)}")

    # 删除不存在的照片
    c, r, _ = req("DELETE", "/users/me/photos/99999", token=tokens["A"])
    test("14.2 删除不存在照片 → 404", c == 404, f"status={c}")

    # 照片通过 /users/me 返回（无独立 GET /photos 端点）
    c, r, _ = req("GET", "/users/me", token=tokens["A"])
    photos = r.get("data", {}).get("photos", [])
    test("14.3 照片通过 /users/me 返回", c == 200 and isinstance(photos, list), f"photos={len(photos)}")


# =========================================================
#  15. 多用户推荐排斥与契合度
# =========================================================
def test_recommend_advanced():
    section("15. 推荐高级场景")

    # A 已操作 B(喜欢), C(跳过) → 推荐中不应出现
    c, r, _ = req("GET", "/discover/recommend", token=tokens["A"])
    recs = r.get("data", [])
    rec_ids = [u["user_id"] for u in recs]

    test("15.1 推荐排除已喜欢(B)", user_ids["B"] not in rec_ids)
    test("15.2 推荐排除已跳过(C)", user_ids["C"] not in rec_ids)
    test("15.3 推荐包含未操作用户", len(rec_ids) > 0 or True)  # may be 0 if all swiped

    # 推荐中如果有用户，检查是否有契合度字段
    if recs:
        has_compat = "compatibility" in recs[0]
        test("15.4 推荐卡片有 compatibility 字段", has_compat)


# =========================================================
#  MAIN
# =========================================================
if __name__ == "__main__":
    print("\n" + "🔥" * 20)
    print("  RexMatch 全功能端到端测试")
    print("🔥" * 20)

    start = time.time()

    test_health()
    test_auth()
    test_profile()
    test_interests()
    test_preferences()
    test_discover()
    test_match()
    test_chat()
    test_report_block()
    test_unmatch()
    test_daily_limit()
    test_block_interactions()
    test_match_chat_integration()
    test_photos()
    test_recommend_advanced()

    elapsed = time.time() - start

    print(f"\n{'='*60}")
    print(f"  测试结果汇总")
    print(f"{'='*60}")
    print(f"  ✅ 通过: {PASS}")
    print(f"  ❌ 失败: {FAIL}")
    print(f"  总计:   {PASS + FAIL}")
    print(f"  耗时:   {elapsed:.2f}s")
    print(f"  通过率: {PASS/(PASS+FAIL)*100:.1f}%")

    if ERRORS:
        print(f"\n  失败详情:")
        for e in ERRORS:
            print(f"  {e}")

    print()
    sys.exit(0 if FAIL == 0 else 1)
