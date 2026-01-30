import requests
import json
import sys

# 设置输出编码
if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "AIzaSyDIcOvvB5hM7DxgjuIb7jBEzIxESR6AR9g"

print("=" * 60)
print("🔍 测试 Gemini API（HTTP直接调用）")
print("=" * 60)

# 测试1: 基本API调用
print("\n【测试1】基本API连接测试...")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

payload = {
    "contents": [{
        "parts": [{
            "text": "你好，请用中文回复：今天是几号？"
        }]
    }]
}

try:
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text']
        print("✅ API连接成功！")
        print(f"回复: {text}")
    else:
        print(f"❌ API调用失败")
        print(f"状态码: {response.status_code}")
        print(f"错误: {response.text}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ 请求失败: {e}")
    sys.exit(1)

# 测试2: 测试搜索功能
print("\n" + "=" * 60)
print("【测试2】测试Google搜索功能")
print("=" * 60)

payload_with_search = {
    "contents": [{
        "parts": [{
            "text": "请搜索：2026年1月30日有哪些重要的足球比赛？请列出至少3场比赛的详细信息。"
        }]
    }],
    "tools": [{
        "googleSearchRetrieval": {}
    }]
}

try:
    print("📤 发送搜索请求...")
    response = requests.post(url, json=payload_with_search)
    
    if response.status_code == 200:
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text']
        print("\n✅ 搜索功能测试成功！")
        print("=" * 60)
        print("📥 返回内容:")
        print("=" * 60)
        print(text)
        print(f"\n📊 内容长度: {len(text)} 字符")
    else:
        print(f"❌ 搜索功能不可用")
        print(f"状态码: {response.status_code}")
        print(f"错误: {response.text}")
        
except Exception as e:
    print(f"❌ 搜索请求失败: {e}")

# 测试3: 足球预测测试
print("\n" + "=" * 60)
print("【测试3】足球比赛预测数据搜集测试")
print("=" * 60)

payload_football = {
    "contents": [{
        "parts": [{
            "text": """
请搜集以下足球比赛的最新预测数据：

比赛：阿森纳 vs 卡拉特  
时间：2026年1月30日
联赛：欧冠

请搜索并提供：
1. 双方最新伤病情况
2. 最新赔率数据
3. 近期战绩
4. 比分预测及理由

请用中文详细回答。
"""
        }]
    }],
    "tools": [{
        "googleSearchRetrieval": {}
    }]
}

try:
    print("📤 发送足球预测查询...")
    response = requests.post(url, json=payload_football)
    
    if response.status_code == 200:
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text']
        print("\n✅ 足球预测测试成功！")
        print("=" * 60)
        print("📥 预测数据:")
        print("=" * 60)
        print(text)
        print(f"\n📊 内容长度: {len(text)} 字符")
        
        # 保存结果
        with open("gemini_test_result.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print("\n💾 结果已保存至: gemini_test_result.txt")
    else:
        print(f"❌ 足球预测测试失败")
        print(f"状态码: {response.status_code}")
        print(f"错误: {response.text}")
        
except Exception as e:
    print(f"❌ 请求失败: {e}")

print("\n" + "=" * 60)
print("🎉 测试完成！")
print("=" * 60)
