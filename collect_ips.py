import requests
from bs4 import BeautifulSoup
import re
import os
import time

# 目标URL列表
urls = ['https://api.uouin.com/cloudflare.html', 
        'https://ip.164746.xyz'
        ]

# 正则表达式用于匹配IP地址
ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

# IP地理位置API
GEO_API_URL = "http://ip-api.com/json/"

def get_country_flag(country_code):
    """根据国家代码返回国旗emoji"""
    if not country_code:
        return "🏴"
    
    # 将国家代码转换为国旗emoji
    flag_emoji = ""
    for char in country_code.upper():
        flag_emoji += chr(ord(char) + 127397)
    
    return flag_emoji

def get_ip_country(ip):
    """获取IP的国家信息（中文）"""
    try:
        # 添加lang=zh-CN参数获取中文结果
        response = requests.get(f"{GEO_API_URL}{ip}?lang=zh-CN", timeout=5)
        data = response.json()
        
        if data['status'] == 'success':
            country = data.get('country', '未知')
            country_code = data.get('countryCode', '')
            flag = get_country_flag(country_code)
            return f"{flag} {country}"
    except:
        pass
    
    return "🏴 未知"

def main():
    all_ips = set()
    
    print("开始抓取IP地址...")
    
    # 首先收集所有IP
    for url in urls:
        try:
            print(f"正在从 {url} 抓取IP...")
            
            # 发送HTTP请求获取网页内容
            response = requests.get(url)
            
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 根据网站的不同结构找到包含IP地址的元素
            if url == 'https://api.uouin.com/cloudflare.html':
                elements = soup.find_all('tr')
            elif url == 'https://ip.164746.xyz':
                elements = soup.find_all('tr')
            else:
                elements = soup.find_all('li')
            
            # 遍历所有元素,查找IP地址
            for element in elements:
                element_text = element.get_text()
                ip_matches = re.findall(ip_pattern, element_text)
                
                # 如果找到IP地址,添加到集合中
                for ip in ip_matches:
                    all_ips.add(ip)
            
            print(f"从 {url} 找到 {len(ip_matches)} 个IP")
            
        except Exception as e:
            print(f"从 {url} 抓取失败: {e}")
            continue
    
    print(f"总共收集到 {len(all_ips)} 个唯一IP地址")
    print("开始获取IP国家信息...")
    
    # 获取每个IP的国家信息
    ip_data = []
    for ip in all_ips:
        country_info = get_ip_country(ip)
        # 提取国家名称用于排序（去掉国旗emoji）
        country_name = country_info.split(' ', 1)[1] if ' ' in country_info else '未知'
        ip_data.append({
            'ip': ip,
            'country_info': country_info,
            'country': country_name
        })
        # 避免API请求过快
        time.sleep(0.1)
    
    # 按照国家分组，每个国家内的IP按数字排序
    country_groups = {}
    for info in ip_data:
        country = info['country']
        if country not in country_groups:
            country_groups[country] = []
        country_groups[country].append(info)
    
    # 检查ip.txt文件是否存在,如果存在则删除它
    if os.path.exists('ip.txt'):
        os.remove('ip.txt')
    
    # 创建一个文件来存储IP地址
    with open('ip.txt', 'w', encoding='utf-8') as file:
        # 按国家名称排序
        sorted_countries = sorted(country_groups.keys())
        
        for country in sorted_countries:
            country_ips = country_groups[country]
            
            # 同一个国家的IP用数字1、2、3排序
            for i, info in enumerate(country_ips, 1):
                file.write(f"{info['ip']}#{info['country_info']}{i}\n")
    
    print('IP地址已保存到ip.txt文件中。')

if __name__ == "__main__":
    main()
