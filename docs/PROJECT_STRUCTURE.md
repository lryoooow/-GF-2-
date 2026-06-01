# Project Structure

项目按“公共核心 + 传感器模块”组织。

## 公共模块

- `atmcorr/common/dem.py`：DEM 均值高程计算。
- `atmcorr/common/sixs.py`：6S 几何、气溶胶、大气廓线和校正系数计算。
- `atmcorr/common/raster.py`：块处理、输出栅格创建、反射率缩放和 dtype 转换。
- `atmcorr/common/coordinates.py`：GDAL/OSR 坐标转换工具。

## 传感器模块

- `atmcorr/sensors/gf/`：当前主要维护模块，支持 GF MSS 单景和父目录批量处理。
- `atmcorr/sensors/sentinel/`：保留独立模块边界，后续从 legacy 脚本迁移。
- `atmcorr/sensors/landsat/`：保留独立模块边界，后续从 legacy 脚本迁移。

## 数据与历史代码

- `data/GMTED2km.tif`：平均高程使用的 DEM。
- `data/RadiometricCorrectionParameter.json`：GF 辐射定标和 SRF 参数。
- `legacy/`：原始脚本备份，不作为当前主流程入口。
