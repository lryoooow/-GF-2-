# GF-2 PMS2 Smoke Test

This project now supports running atmospheric correction from an unpacked GF scene
directory that contains `*MSS*.tif`, `*MSS*.xml`, and `*MSS*.rpb`.

## Environment

Use the conda environment file:

```powershell
conda create -n atmocorr311 --override-channels -c https://conda.anaconda.org/conda-forge python=3.11 gdal numpy tqdm py6s -y
conda activate atmocorr311
```

The explicit conda-forge URL bypasses local `.condarc` mirror mappings.

Required runtime dependencies are GDAL, Py6S, NumPy, and tqdm.

## Local GF-2 Test Command

```powershell
python AtmosphericCorrection_GF.py `
  --Input_dir "D:\Lry\预研\图像融合\NND\GF-2\GF2_PMS2_E115.9_N22.9_20211210_L1A0006125619" `
  --Output_dir "D:\tmp\AtmosphericCorrection_GF2_test"
```

The script also accepts a parent directory containing one or more unpacked GF
scene folders.

## Calibration Note

The bundled parameter table has `GF2/PMS2` calibration parameters through 2019.
The local test image is from 2021, so the script falls back to 2019 by default
and prints a warning. This is only suitable for pipeline smoke testing, not for
final scientific output.
