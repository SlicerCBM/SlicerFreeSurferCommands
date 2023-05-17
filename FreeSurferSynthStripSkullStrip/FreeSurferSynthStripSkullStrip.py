#!/usr/bin/env python-real

import sys


DEBUG = False


def convert_image(ifile, ofile):
    import SimpleITK as sitk

    reader = sitk.ImageFileReader()
    reader.SetFileName(ifile)
    image = reader.Execute()
    writer = sitk.ImageFileWriter()
    writer.SetFileName(ofile)
    writer.Execute(image)


def main(args):
    import tempfile
    import subprocess, os
    from pathlib import Path

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        if DEBUG:
            print("temp_path:", temp_path)

        # Temporary image files in FreeSurfer format
        input_temp_fname = str(temp_path / 'input.mgz')
        output_temp_fname = str(temp_path / 'stripped.mgz')
        mask_temp_fname = str(temp_path / 'mask.mgz')
        if DEBUG:
            print(input_temp_fname)

        # Convert image to FreeSurfer mgz format
        convert_image(args.image, input_temp_fname)

        if DEBUG:
            os.listdir(temp_path)

        fs_env = os.environ.copy()
        if DEBUG:
            print(fs_env)
        # Use FreeSurfer's Python environment
        fs_env['PYTHONHOME'] = ''
        print("FREESURFER_HOME:", fs_env['FREESURFER_HOME'])

        cmd = [fs_env['FREESURFER_HOME'] + '/bin/mri_synthstrip', '-i', input_temp_fname]
        if args.out:
            cmd.extend(['-o', output_temp_fname])
        if args.mask:
            cmd.extend(['-m', mask_temp_fname])
        if args.gpu:
            cmd.extend(['-g'])
        if args.border:
            cmd.extend(['--border', args.border])
        if args.nocsf:
            cmd.extend(['--no-csf'])
        print("Command:", " ".join(cmd))
        subprocess.check_output(cmd, env=fs_env)

        # Convert images to NRRD
        outputs = []
        if args.out is not None:
            outputs.append([output_temp_fname, args.out])
        if args.mask is not None:
            outputs.append([mask_temp_fname, args.mask])
        for tmp, out in outputs:
            convert_image(tmp, out)


if __name__ == "__main__":
    import argparse

    if DEBUG:
        print(sys.argv[0])

    # These arguments are based on those of the SynthStrip tool:
    # https://surfer.nmr.mgh.harvard.edu/docs/synthstrip/#usage
    # For additional options and command description, use the --help flag.

    parser = argparse.ArgumentParser()

    # Input image to skullstrip.
    parser.add_argument('-i', '--image',
                        help='Input image to skullstrip.')

    # Save stripped image to path.
    parser.add_argument('-o', '--out',
                        help='Save stripped image to path.')

    # Save binary brain mask to path.
    parser.add_argument('-m', '--mask',
                        help='Save binary brain mask to path.')

    # Use the GPU.
    parser.add_argument('-g', '--gpu', action=argparse.BooleanOptionalAction,
                        help='Use the GPU.')

    # Mask border threshold in mm. Default is 1.
    parser.add_argument('-b', '--border',
                        help='Mask border threshold in mm. Default is 1.')

    # Exclude CSF from brain border.
    # FIXME: should be --no-csf instead of --nocsf (hyphens not supported by 3D Slicer)
    parser.add_argument('--nocsf', action=argparse.BooleanOptionalAction,
                        help='Exclude CSF from brain border.')

    # TODO: Add this later if anyone requests it.
    #   --model file          Alternative model weights.

    args = parser.parse_args()
    if DEBUG:
        print(args)

    if not args.image:
        print("User must set the Input Volume.", file=sys.stderr)
        sys.exit(1)

    if not args.out and not args.mask:
        print("User must request output for either Stripped Volume or Mask Volume, or both.", file=sys.stderr)
        sys.exit(1)

    # NOTE: Do not print anything to stdout before this line (print errors only).

    main(args)

    print('Finished skull stripping')