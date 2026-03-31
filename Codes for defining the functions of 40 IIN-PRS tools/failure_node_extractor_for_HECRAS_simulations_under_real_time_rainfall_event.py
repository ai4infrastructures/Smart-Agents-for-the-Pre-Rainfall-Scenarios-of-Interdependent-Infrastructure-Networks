import os
import win32com.client
import pandas as pd
import json

def failure_node_extractor_for_HECRAS_simulations(global_json_path):
    with open(global_json_path, 'r', encoding='utf-8') as f:
        file_paths = json.load(f)
    rainfall_json_path = file_paths['real_time_rainfall_event']

    def ChangeSimTime():
        ad_ts = pd.read_json(rainfall_json_path)#新边界条件
        ad_ts['Time'] = pd.to_datetime(ad_ts['Time'])
        simStartTime = ad_ts['Time'].min().strftime("%d%b%Y,%H%M").upper()
        simEndTime = ad_ts['Time'].max().strftime("%d%b%Y,%H%M").upper()
        n = 0
        with open(r"C:\Users\26389\Desktop\shelby\shelby.p01", 'r') as ufile:
            lines = ufile.readlines()  # 读取所有行到列表中

        # 遍历 lines 列表，修改符合条件的行
        for i, line in enumerate(lines):
            if 'Simulation Date' in line:
                lines[i] = 'Simulation Date=' + simStartTime + ',' + simEndTime + '\n'  # 修改列表中的行

        # 将修改后的内容写回文件
        with open(r"C:\Users\26389\Desktop\shelby\shelby.p01", 'w') as ufile:
            ufile.writelines(lines)  # 将修改后的列表写回文件

    def ChangeBC():
        ad_ts = pd.read_json(rainfall_json_path) #新边界条件

        n = 0
        with open(r"C:\Users\26389\Desktop\shelby\shelby.u01") as ufile:
            lines = ufile.readlines()
            for line in lines:
                n+=1
                if 'Precipitation Hydrograph=' in line:
                    upBCStartIndex = n+1
            del lines[upBCStartIndex-2:]

        f = open(r"C:\Users\26389\Desktop\shelby\shelby.u01",'w')
        for line in lines[0:upBCStartIndex-1]:
            f.write(line)

        flowts = ad_ts['Precipitation (mm)'].to_numpy()
        l_n = len(flowts)
        flow = [flowts[i:i+10] for i in range(0, len(flowts), 10)]
        f.write(f'Precipitation Hydrograph= {l_n} ' )
        f.write('\n')
        for k in flow:
            l_ce = 8  # 每个数字最长8个空格长度
            s_space = ' '  # 单个空格
            for j in k:
                j = round(j, 3)
                l_t = l_ce - len(str(j))  # 计算空格数量
                s_l = s_space * l_t
                f.write(s_l)
                f.write(str(j))
            f.write('\n')
        f.write('''DSS Path=
Use DSS=False
Use Fixed Start Time=False
Fixed Start Date/Time=24JAN2025,1200
Is Critical Boundary=False
Critical Boundary Flow=
Met Point Raster Parameters=,,,,
Precipitation Mode=Disable
Wind Mode=No Wind Forces
Air Density Mode=
Wave Mode=No Wave Forcing
Met BC=Precipitation|Expanded View=0
Met BC=Precipitation|Point Interpolation=Nearest
Met BC=Precipitation|Gridded Source=DSS
Met BC=Precipitation|Gridded Interpolation=
Met BC=Evapotranspiration|Expanded View=0
Met BC=Evapotranspiration|Point Interpolation=Nearest
Met BC=Evapotranspiration|Gridded Source=DSS
Met BC=Evapotranspiration|Gridded Interpolation=
Met BC=Wind Speed|Expanded View=0
Met BC=Wind Speed|Point Interpolation=Nearest
Met BC=Wind Speed|Gridded Source=DSS
Met BC=Wind Speed|Gridded Interpolation=
Met BC=Wind Direction|Expanded View=0
Met BC=Wind Direction|Point Interpolation=Nearest
Met BC=Wind Direction|Gridded Source=DSS
Met BC=Wind Direction|Gridded Interpolation=
Met BC=Wind Velocity X|Expanded View=0
Met BC=Wind Velocity X|Point Interpolation=Nearest
Met BC=Wind Velocity X|Gridded Source=DSS
Met BC=Wind Velocity X|Gridded Interpolation=
Met BC=Wind Velocity Y|Expanded View=0
Met BC=Wind Velocity Y|Point Interpolation=Nearest
Met BC=Wind Velocity Y|Gridded Source=DSS
Met BC=Wind Velocity Y|Gridded Interpolation=
Met BC=Wave Forcing X|Expanded View=0
Met BC=Wave Forcing X|Point Interpolation=Nearest
Met BC=Wave Forcing X|Gridded Source=DSS
Met BC=Wave Forcing X|Gridded Interpolation=
Met BC=Wave Forcing Y|Expanded View=0
Met BC=Wave Forcing Y|Point Interpolation=Nearest
Met BC=Wave Forcing Y|Gridded Source=DSS
Met BC=Wave Forcing Y|Gridded Interpolation=
Met BC=Air Density|Mode=Constant
Met BC=Air Density|Expanded View=0
Met BC=Air Density|Constant Value=1.225
Met BC=Air Density|Constant Units=kg/m3
Met BC=Air Density|Point Interpolation=Nearest
Met BC=Air Density|Gridded Source=DSS
Met BC=Air Density|Gridded Interpolation=
Met BC=Air Temperature|Expanded View=0
Met BC=Air Temperature|Point Interpolation=Nearest
Met BC=Air Temperature|Gridded Source=DSS
Met BC=Air Temperature|Gridded Interpolation=
Met BC=Humidity|Expanded View=0
Met BC=Humidity|Point Interpolation=Nearest
Met BC=Humidity|Gridded Source=DSS
Met BC=Humidity|Gridded Interpolation=
Met BC=Air Pressure|Mode=Constant
Met BC=Air Pressure|Expanded View=0
Met BC=Air Pressure|Constant Value=1013.2
Met BC=Air Pressure|Constant Units=mb
Met BC=Air Pressure|Point Interpolation=Inv Distance
Met BC=Air Pressure|Gridded Source=DSS
Met BC=Air Pressure|Gridded Interpolation=
Non-Newtonian Method= 0 , 
Non-Newtonian Constant Vol Conc=0
Non-Newtonian Yield Method= 0 , 
Non-Newtonian Yield Coef=0, 0
User Yeild=   0
Non-Newtonian Sed Visc= 0 , 
Non-Newtonian Obrian B=0
User Viscosity=0
User Viscosity Ratio=0
Herschel-Bulkley Coef=0, 0
Clastic Method= 0 , 
Coulomb Phi=0
Voellmy X=0
Non-Newtonian Hindered FV= 0 
Non-Newtonian FV K=0
Non-Newtonian ds=0
Non-Newtonian Max Cv=0
Non-Newtonian Bulking Method= 0 , 
Non-Newtonian High C Transport= 0 , 
Lava Activation= 0 
Temperature=1300,15,,15,14,980
Heat Ballance=1,1200,0.5,1,70,0.95
Viscosity=1000,,,
Yield Strength=,,,
Consistency Factor=,,,
Profile Coefficient=4,1.3,
Lava Param=,2500,
''')

    # 尝试加载 HEC-RAS 控制器
    try:
        hec = win32com.client.Dispatch("RAS66.HECRASController")  # 根据版本调整
        print("HEC-RAS 控制器加载成功！")
    except Exception as e:
        print(f"加载 HEC-RAS 控制器失败: {e}")
        exit()

    # 打开 HEC-RAS 项目
    filepath = r"C:\Users\26389\Desktop\shelby\shelby.prj"
    ChangeBC()
    ChangeSimTime()
    hec.Project_Open(filepath)

    # 计算当前方案
    hec.Compute_CurrentPlan(None, None, True)

    # 保存并关闭项目
    hec.Project_Save()
    hec.Project_Close()
    hec.QuitRas()

    # =======================================================================
    # =======================================================================

    import shutil
    from rasterio.crs import CRS
    import rasterio
    import geopandas as gpd

    def ensure_raster_crs(tif_path, epsg=4326):
        """
        如果 tif_path 的 CRS 是 None，就补上 epsg 对应的坐标系，
        并把原文件备份为 .bak。
        """
        with rasterio.open(tif_path) as src:
            if src.crs is not None:
                # 已经有 CRS，直接返回
                print(f"{tif_path} 已含 CRS: {src.crs}")
                return
            profile = src.profile.copy()
            data = src.read()  # 读取所有波段

        # 更新 profile，补上 CRS
        profile.update(crs=CRS.from_epsg(epsg))

        # 写到临时文件
        tmp_path = tif_path.replace('.tif', '_tmp.tif')
        with rasterio.open(tmp_path, 'w', **profile) as dst:
            dst.write(data)

        # 备份原文件并替换
        bak_path = tif_path + '.bak'
        shutil.move(tif_path, bak_path)
        shutil.move(tmp_path, tif_path)

    def load_and_reproject_points(shp_path, crs):
        """
        读取点 Shapefile 并重投影到与栅格相同的坐标系
        """
        gdf = gpd.read_file(shp_path)

        if gdf.crs != crs:
            gdf = gdf.to_crs(crs)  # 重投影
        return gdf

    def sample_raster_values(raster, gdf, band=1, nodata=None):
        """
        对点 (gdf) 进行栅格采样，返回在指定波段上的数值列表。
        """
        band_data = raster.read(band)
        results = []
        for geom in gdf.geometry:
            try:
                row, col = raster.index(geom.x, geom.y)  # 找到点在栅格中的行列索引
                value = band_data[row, col]
            except IndexError:
                value = nodata  # 点超出栅格范围
            results.append(value)
        return results

    # 1. 设置文件路径
    depth_tif = r"C:\Users\26389\Desktop\shelby\Plan 01\Depth (Max).Terrain.output_USGS10m.tif"
    gas_shp   = "gas_nodes.shp"
    power_shp = "power_nodes.shp"
    water_shp = "water_nodes.shp"

    ensure_raster_crs(depth_tif, epsg=3857)

    # 2. 打开水深栅格 & 获取 CRS
    depth_raster = rasterio.open(depth_tif)
    raster_crs   = depth_raster.crs

    # 3. 读取并重投影三类基础设施点
    gas_gdf   = load_and_reproject_points(gas_shp, raster_crs)
    power_gdf = load_and_reproject_points(power_shp, raster_crs)
    water_gdf = load_and_reproject_points(water_shp, raster_crs)

    # 4. 采样栅格水深值
    gas_depth_vals   = sample_raster_values(depth_raster, gas_gdf, band=1, nodata=-9999)
    power_depth_vals = sample_raster_values(depth_raster, power_gdf, band=1, nodata=-9999)
    water_depth_vals = sample_raster_values(depth_raster, water_gdf, band=1, nodata=-9999)

    gas_gdf["DepthVal"]   = gas_depth_vals
    power_gdf["DepthVal"] = power_depth_vals
    water_gdf["DepthVal"] = water_depth_vals

    # 5. 根据阈值筛选受淹没的点
    gas_threshold   = 0.3048   # 根据需求自行设定
    power_threshold = 0.6096
    water_threshold = 1.83

    gas_in_flood   = gas_gdf[gas_gdf["DepthVal"] > gas_threshold].copy()
    power_in_flood = power_gdf[power_gdf["DepthVal"] > power_threshold].copy()
    water_in_flood = water_gdf[water_gdf["DepthVal"] > water_threshold].copy()

    # 6. 获取点的名称 (如果 shapefile 里有 "Code" 字段)
    def extract_point_names(gdf):
        """
        确保从 'Code' 字段提取点名称。
        如果 'Code' 不存在或为空，则使用默认编号 Point_0, Point_1...
        """
        if "Code" in gdf.columns:
            return gdf["Code"].astype(str).tolist()
        return [f"Point_{i}" for i in range(len(gdf))]  # 默认编号

    gas_names   = extract_point_names(gas_in_flood)
    power_names = extract_point_names(power_in_flood)
    water_names = extract_point_names(water_in_flood)

    # 7. 生成 JSON 结果
    all_names = gas_names + power_names + water_names
    output_data = {
        "all_failed_nodes": all_names,
        "number_of_failed_nodes": len(all_names)
    }

    # 8. 保存 JSON 文件
    output_json_path = "failure_node_after_HECRAS_simulations.json"
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)

    print(f"JSON file saved at: {output_json_path}")

    # 更新全局数据文件 Global_Data.json，将输出文件路径记录进去

    try:
        with open(global_json_path, 'r', encoding="utf-8") as f:
            global_data = json.load(f)
    except FileNotFoundError:
        global_data = {}

    global_data["failure_node_after_HECRAS_simulations"] = output_json_path
    with open(global_json_path, 'w', encoding="utf-8") as f:
        json.dump(global_data, f, indent=4)


global_json_path = "Global_Data.json"
failure_node_extractor_for_HECRAS_simulations(global_json_path)
