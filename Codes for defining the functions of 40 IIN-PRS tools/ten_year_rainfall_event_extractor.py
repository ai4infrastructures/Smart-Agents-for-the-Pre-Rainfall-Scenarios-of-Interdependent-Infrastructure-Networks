import json


def ten_year_rainfall_event_extractor(global_json_path):
    # 定义输出文件名称
    output_path = "ten_year_rainfall_event.json"

    # 这里可选：如果需要处理该文件的数据，可以先读取或更新该文件
    try:
        with open(output_path, 'r', encoding='utf-8') as event_file:
            event_data = json.load(event_file)
    except FileNotFoundError:
        print(f"文件 {output_path} 未找到，创建一个新的空数据文件。")
        event_data = {}
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(event_data, f, indent=4, ensure_ascii=False)

    # 读取全局数据文件 Global_Data.json
    try:
        with open(global_json_path, 'r', encoding='utf-8') as global_file:
            global_data = json.load(global_file)
    except FileNotFoundError:
        global_data = {}

    # 更新全局数据，将 output_path 作为值，键为 "one-in-fifty-year rainfall event.json"
    global_data["ten_year_rainfall_event"] = output_path

    # 写回更新后的全局数据文件
    with open(global_json_path, 'w', encoding='utf-8') as global_file:
        json.dump(global_data, global_file, indent=4, ensure_ascii=False)

    print(f"全局数据文件已更新：{global_json_path}")


# 示例用法
global_json_path = "Global_Data.json"
ten_year_rainfall_event_extractor(global_json_path)
