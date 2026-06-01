# AtmosphericCorrection

基于 Python、GDAL 和 Py6S 的遥感影像大气校正项目。

项目已重构为“公共核心 + 传感器模块”的结构。当前稳定维护的是 GF/GF-2 多光谱影像处理流程；Sentinel 和 Landsat 已预留独立模块，旧版实现保存在 `legacy/` 中，便于后续逐步迁移和升级。

## 功能状态

| 传感器 | 状态 | 说明 |
| --- | --- | --- |
| GF/GF-2 | 可运行 | 当前主线，已完成模块化重构和本地 GF-2 PMS2 数据验证 |
| Sentinel | 待迁移 | 已预留模块入口，旧实现保存在 `legacy/` |
| Landsat | 待迁移 | 已预留模块入口，旧实现保存在 `legacy/` |

当前 GF-2 流程包括：

- 读取 GF MSS 影像、XML 元数据和 RPB 文件
- 读取辐射定标参数
- 计算场景平均 DEM 高程
- 调用 Py6S 获取大气校正系数
- 按块处理多光谱波段，输出缩放后的地表反射率 GeoTIFF

## 目录结构

```text
AtmosphericCorrection/
  atmcorr/
    common/              # DEM、6S、栅格处理、坐标转换等公共能力
    sensors/
      gf/                # GF/GF-2 当前可运行主线
      sentinel/          # Sentinel 后续迁移模块
      landsat/           # Landsat 后续迁移模块
  data/
    GMTED2km.tif
    RadiometricCorrectionParameter.json
  docs/
    GF2_TESTING.md
    PROJECT_STRUCTURE.md
    img/
  scripts/
    run_gf.py
    run_gf_batch.py
    run_sentinel.py
    run_landsat.py
  legacy/                # 原始旧脚本备份
  environment.yml
  README.md
```

## 环境安装

推荐使用 conda-forge 创建环境：

```powershell
conda create -n atmocorr311 --override-channels -c https://conda.anaconda.org/conda-forge python=3.11 gdal numpy tqdm py6s -y
```

也可以使用项目中的环境文件：

```powershell
conda env create -f environment.yml
```

验证环境：

```powershell
conda run -n atmocorr311 python -c "from osgeo import gdal; from Py6S import SixS; import numpy; print('ok')"
```

## GF-2 单景运行

请在项目根目录执行：

```powershell
conda run -n atmocorr311 python scripts\run_gf.py `
  --input-dir "<GF-2 scene directory>" `
  --output-dir "<output directory>"
```

输入目录应包含同一景 GF 多光谱数据的以下文件：

```text
*MSS*.tif
*MSS*.xml
*MSS*.rpb
```

示例：

```powershell
conda run -n atmocorr311 python scripts\run_gf.py `
  --input-dir "D:\data\GF2_PMS2_xxx" `
  --output-dir "D:\output\gf2_corrected"
```

也可以把 `--input-dir` 指向包含多个 GF 场景目录的父目录，程序会自动查找含 MSS 影像的 GF 场景。

## 常用参数

```text
--fallback-year 2019
--aot550 0.14497
--ground-reflectance 0.36
--aerosol-profile Continental
--block-size 2048
--output-dtype int16
```

参数说明：

- `--fallback-year`：影像年份在定标表中缺失时使用的备用年份。
- `--aot550`：550 nm 气溶胶光学厚度。
- `--ground-reflectance`：6S 中使用的均一朗伯地表反射率。
- `--aerosol-profile`：气溶胶类型，默认 `Continental`。
- `--block-size`：块处理大小。
- `--output-dtype`：输出数据类型，默认 `int16`。

输出反射率默认放大 `10000` 倍，nodata 为 `-9999`。

## GF 批处理

批处理入口用于处理 `.tar.gz` 格式 GF 场景压缩包：

```powershell
conda run -n atmocorr311 python scripts\run_gf_batch.py `
  --input-dir "<directory containing tar.gz files>" `
  --work-dir "<temporary extraction directory>" `
  --output-dir "<output directory>" `
  --workers 3
```

该入口保留了旧版批处理能力，后续还可以继续增强错误恢复、日志和任务队列。

## 开发说明

核心模块职责：

- `atmcorr/common/dem.py`：DEM 读取和平均高程计算。
- `atmcorr/common/sixs.py`：Py6S 参数构建和校正系数计算。
- `atmcorr/common/raster.py`：GDAL 读写、块处理、反射率缩放和 dtype 转换。
- `atmcorr/common/coordinates.py`：坐标转换工具。
- `atmcorr/sensors/gf/`：GF/GF-2 元数据解析、定标参数读取和处理流程。

代码检查：

```powershell
python -m compileall -q atmcorr scripts
```

## 注意事项

- 当前 `data/RadiometricCorrectionParameter.json` 中部分 GF2/PMS2 定标参数只到 2019。如果处理更晚年份影像，程序会按 `--fallback-year` 使用备用年份并输出警告。
- `fallback-year` 适合流程测试，不建议直接作为最终科学产品依据。
- Sentinel 和 Landsat 模块当前只是结构化入口，正式迁移前请参考 `legacy/` 中原始脚本。
