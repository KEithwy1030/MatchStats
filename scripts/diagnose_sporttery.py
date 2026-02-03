"""
竞彩 API 诊断工具
测试竞彩官网 API 是否可访问，并打印详细响应信息
"""
import asyncio
import aiohttp
import json

API_URL = "https://webapi.sporttery.cn/gateway/uniform/football/getMatchListV1.qry?clientCode=3001"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.sporttery.cn/',
    'Origin': 'https://www.sporttery.cn'
}

async def test_sporttery_api():
    print("=" * 70)
    print("竞彩官网 API 诊断工具")
    print("=" * 70)

    print(f"\n[1] 请求 URL: {API_URL}")

    try:
        print("\n[2] 发送 HTTP 请求...")
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=15)) as response:
                print(f"     状态码: {response.status}")
                print(f"     Content-Type: {response.headers.get('Content-Type')}")

                if response.status != 200:
                    print(f"\n[ERROR] HTTP 状态码异常: {response.status}")
                    text = await response.text()
                    print(f"     响应内容: {text[:200]}")
                    return

                print("\n[3] 解析 JSON 响应...")
                try:
                    data = await response.json()
                except:
                    text = await response.text()
                    print(f"\n[ERROR] 响应不是有效的 JSON")
                    print(f"     响应内容: {text[:500]}")
                    return

                print("\n[4] 分析响应结构...")
                print(f"     success 字段: {data.get('success')}")
                print(f"     errorCode 字段: {data.get('errorCode')}")

                if not data.get('success') and data.get('errorCode') != '0':
                    print(f"\n[ERROR] API 返回失败")
                    print(f"     完整响应: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
                    return

                value = data.get('value', {})
                match_info_list = value.get('matchInfoList', [])

                print(f"\n[5] 数据解析成功")
                print(f"     matchInfoList 长度: {len(match_info_list)}")

                if len(match_info_list) == 0:
                    print(f"\n[WARN] 当前没有竞彩比赛数据")
                    return

                total_matches = 0
                for i, group in enumerate(match_info_list[:3], 1):
                    business_date = group.get('businessDate')
                    sub_matches = group.get('subMatchList', [])
                    print(f"\n     分组 {i}:")
                    print(f"       日期: {business_date}")
                    print(f"       场次: {len(sub_matches)}")
                    total_matches += len(sub_matches)

                    if len(sub_matches) > 0:
                        first_match = sub_matches[0]
                        print(f"       示例: {first_match.get('homeTeamAbbName')} vs {first_match.get('awayTeamAbbName')}")

                print(f"\n[6] 总结")
                print(f"     总场次: {total_matches}")
                print(f"     ✓ API 可访问")
                print(f"     ✓ 数据格式正确")

    except asyncio.TimeoutError:
        print("\n[ERROR] 请求超时（15秒）")
        print("     可能原因:")
        print("     1. 网络连接问题")
        print("     2. 竞彩官网只允许中国大陆 IP 访问")
        print("     3. 防火墙阻止")

    except aiohttp.ClientConnectorError as e:
        print(f"\n[ERROR] 连接失败: {e}")
        print("     可能原因:")
        print("     1. 网站不可访问")
        print("     2. DNS 解析失败")
        print("     3. 需要代理/VPN")

    except Exception as e:
        print(f"\n[ERROR] 未知错误: {e}")
        print(f"     错误类型: {type(e).__name__}")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(test_sporttery_api())
