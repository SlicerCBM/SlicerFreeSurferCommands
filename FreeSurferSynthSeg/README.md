# FreeSurfer SynthSeg Brain MRI Segmentation

Segmentation of brain MRI scans using [SynthSeg](https://github.com/BBillot/SynthSeg) packaged in [FreeSurfer](https://surfer.nmr.mgh.harvard.edu/fswiki/SynthSeg).

For a detailed description of SynthSeg please refer to its documentation <a href="https://surfer.nmr.mgh.harvard.edu/fswiki/SynthSeg">here</a>.

If you use SynthSeg in your analysis, please cite:

    SynthSeg: Segmentation of brain MRI scans of any contrast and resolution without retraining. B Billot, DN Greve, O Puonti, A Thielscher, K Van Leemput, B Fischl, AV Dalca, JE Iglesias. Medical Image Analysis, 83, 102789 (2023).

For the robust mode (see below), please cite:

    Robust machine learning segmentation for large-scale analysis of heterogeneous clinical brain MRI datasets. B Billot, C Magdamo, SE Arnold, S Das, JE Iglesias. PNAS, 120(9), e2216399120 (2023).

## Panels and their use

### Input

- **Input volume:** Brain MRI volume to be segmented.

### Output

- **Output segmentation:** Labelmap or Segmentation where the output segmentations will be saved. By default, this will use the [FreeSurferColorLUT](https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/AnatomicalROI/FreeSurferColorLUT) color table (see [here](https://github.com/SlicerCBM/SlicerFreeSurferCommands/blob/main/FreeSurferSynthSeg/FreeSurferColorLUT.ctbl) for the color table in 3D Slicer format).

- **Resampled volume (optional):** In order to return segmentations at 1mm resolution, the input images are internally resampled (except if they already are at 1mm). Use this optional scalar volume to save the resampled image. If the output segmentation is of type 'Segmentation' (not 'LabelMap') the resampled volume will be set as the segmentation's source geometry.

### Advanced

Advanced parameters are described in the [SynthSeg documentation](https://surfer.nmr.mgh.harvard.edu/fswiki/SynthSeg).

## Tutorial

1. Download the "MRHead" sample data using the Sample Data module.

2. Switch to the FreeSurfer SynthSeg Brain MRI Segmentation module.

3. Set the following parameters:
    - Input volume: MRHead
    - Output segmentation: Create new LabelMapVolume or Segmentation

4. Set advanced parameters as desired.

5. Click Apply.

The segmentation will be saved in the new LabelMapVolume or Segmentation.

![FreeSurfer SynthSeg Brain MRI Segmentation](https://raw.githubusercontent.com/SlicerCBM/SlicerFreeSurferCommands/main/Screenshot02.png)
