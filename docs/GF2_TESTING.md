# GF-2 PMS2 Test

本项目当前主测试数据为本地未处理 GF-2 PMS2 多光谱数据。输入目录需要包含：

- `*MSS*.tif`
- `*MSS*.xml`
- `*MSS*.rpb`

## 环境

```powershell
conda create -n atmocorr311 --override-channels -c https://conda.anaconda.org/conda-forge python=3.11 gdal numpy tqdm py6s -y
```

## 本地测试命令

```powershell
conda run -n atmocorr311 python scripts\run_gf.py `
  --input-dir "D:\Lry\预研\图像融合\NND\GF-2\GF2_PMS2_E115.9_N22.9_20211210_L1A0006125619" `
  --output-dir "D:\tmp\AtmosphericCorrection_GF2_test"
```

也可以传入包含多个 GF 场景目录的父目录。

## 定标说明

当前 `data/RadiometricCorrectionParameter.json` 中 `GF2/PMS2` 定标参数只到 2019。测试影像年份为 2021，因此默认使用 `--fallback-year 2019`，脚本会输出警告。该 fallback 适合流程测试，不建议作为最终科学产品依据。
