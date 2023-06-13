# FreeSurfer SynthStrip Skull Strip

Skull stripping using FreeSurfer's [SynthStrip](https://surfer.nmr.mgh.harvard.edu/docs/synthstrip) tool.

For a detailed description of SynthStrip please refer to its documentation <a href="https://surfer.nmr.mgh.harvard.edu/docs/synthstrip">here</a>.

If you use SynthStrip in your analysis, please cite:

SynthStrip: Skull-Stripping for Any Brain Image
Andrew Hoopes, Jocelyn S. Mora, Adrian V. Dalca, Bruce Fischl*, Malte Hoffmann* (*equal contribution)
NeuroImage 260, 2022, 119474
https://doi.org/10.1016/j.neuroimage.2022.119474

## Panels and their use

### Input

- **Input image:** Image input volume to skull strip.

### Output

- **Stripped image:** Stripped image output volume.

- **Brain mask:** Binary brain mask output volume.

### Advanced

Advanced parameters are described in the [SynthStrip documentation](https://surfer.nmr.mgh.harvard.edu/fswiki/synthstrip).

## Tutorial

1. Download the "MRHead" sample data using the Sample Data module.

2. Switch to the FreeSurfer SynthStrip Skull Strip module.

3. Set the following parameters:
    - Input image: MRHead
    - Stripped image: Create new volume
    - Brain mask: Create new LabelMapVolume

4. Set advanced parameters as desired.

5. Click Apply.

The stripped image and brain mask will be saved in the new scalar volume and labelmap volume, respectively.
