# GF-2 PMS2 Test

GF-2 PMS2 多光谱场景目录需要包含：

- `*MSS*.tif`
- `*MSS*.xml`
- `*MSS*.rpb`

## Environment

```powershell
conda create -n atmocorr311 --override-channels -c https://conda.anaconda.org/conda-forge python=3.11 gdal numpy tqdm py6s -y
```

## Command

在项目根目录执行：

```powershell
conda run -n atmocorr311 python scripts\run_gf.py `
  --input-dir "<GF-2 scene directory>" `
  --output-dir "<output directory>"
```

也可以传入包含多个 GF 场景目录的父目录。程序会递归查找包含 MSS 影像的目录，不要求目录名以 `GF` 开头。

## Calibration Note

当前 `data/RadiometricCorrectionParameter.json` 中部分 `GF2/PMS2` 定标参数只到 2019。处理更晚年份影像时，程序默认使用 `--fallback-year 2019`，并输出警告。该 fallback 适合流程测试，不建议作为最终科学产品依据。

## Output

输出反射率默认放大 `10000` 倍，nodata 为 `-9999`，默认数据类型为 `int32`。
