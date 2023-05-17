# Slicer FreeSurfer Commands

Run [FreeSurfer](https://freesurfer.net) commands using [3D Slicer](https://www.slicer.org)'s graphical user interface.

Features include:
- (TODO) segmentation
- skull stripping

![](Screenshot01.jpg)

## Modules

The FreeSurfer Commands extension for 3D Slicer contains the following modules:

- **(TODO) FreeSurfer MRI Watershed Skull Strip:** Skull stripping using FreeSurfer's [MRI watershed (FSW) algorithm](https://surfer.nmr.mgh.harvard.edu/fswiki/mri_watershed).

- **(TODO) FreeSurfer SynthSeg Brain MRI Segmentation:** Brain MRI segmentation using [SynthSeg](https://github.com/BBillot/SynthSeg) packaged in [FreeSurfer](https://surfer.nmr.mgh.harvard.edu/fswiki/SynthSeg)

- **FreeSurfer SynthStrip Skull Strip:** Skull stripping using FreeSurfer's [SynthStrip](https://surfer.nmr.mgh.harvard.edu/docs/synthstrip) tool.

## Installation

You must have FreeSurfer (version 7.3.2 or higher) installed on your computer
and have the `$FREESURFER_HOME` environment variable set correctly.
Please refer to the [FreeSurfer](https://freesurfer.net) documentation for further details.

## Feature Requests

Please open an [issue](https://github.com/SlicerCBM/SlicerFreeSurferCommands/issues) if you would like to suggest a new feature or FreeSurfer command to be added.

## Contributing

Pull requests are welcome.
For major changes, please open an [issue](https://github.com/SlicerCBM/SlicerFreeSurferCommands/issues) first to discuss what you would like to change.