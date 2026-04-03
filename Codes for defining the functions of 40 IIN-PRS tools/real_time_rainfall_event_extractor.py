import requests
import json

def real_time_rainfall_event_extractor(global_json_path):
    # WeatherAPI API 密钥
    api_key = '71188703d1754d1b90980446250802'

    # 谷歌地图上的谢尔比县（孟菲斯市）经纬度
    lat = 35.1495  # 谷歌地图上的谢尔比县纬度（孟菲斯市）
    lon = -90.0490  # 谷歌地图上的谢尔比县经度（孟菲斯市）

    # 构建WeatherAPI的请求URL
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={lat},{lon}&hours=24"

    # 发送GET请求获取数据
    response = requests.get(url)

    # 将响应结果转换为JSON格式
    data = response.json()

    # 提取降水量数据
    forecast_data = data.get("forecast", {}).get("forecastday", [{}])[0].get("hour", [])
    hourly_rain_data = []

    # 提取数据
    for hour_data in forecast_data[:6]:
        time = hour_data.get("time", "")  # 获取时间
        precip = hour_data.get("precip_mm", 0) + 2 # 获取降水量，单位是毫米
        hourly_rain_data.append({
            "Time": time,
            "Precipitation (mm)": precip
        })

    # 输出数据到JSON文件，保存到当前目录
    output_path = "real_time_rainfall_event.json"
    with open(output_path, mode="w", encoding="utf-8") as file:
        json.dump(hourly_rain_data, file, indent=4, ensure_ascii=False)

    print(f"JSON文件已保存：{output_path}")

    # 更新全局数据文件 global_json_path，将输出文件名记录进去
    try:
        with open(global_json_path, 'r', encoding="utf-8") as f:
            global_data = json.load(f)
    except FileNotFoundError:
        global_data = {}


    global_data["real_time_rainfall_event"] = output_path
    with open(global_json_path, 'w', encoding="utf-8") as f:
        json.dump(global_data, f, indent=4)

# 调用函数，传入全局数据文件的路径
global_json_path = "Global_Data.json"
real_time_rainfall_event_extractor(global_json_path)
