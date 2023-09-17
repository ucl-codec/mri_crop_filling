#!/usr/bin/env python3
import argparse
import os
from glob import glob
from Cropping import crop_img, collage_img, zero_pad, trim

parser = argparse.ArgumentParser(description='FreeSurfer recon-all + custom template generation.')

parser.add_argument('bids_dir', help='The directory with the input dataset '
                                     'formatted according to the BIDS standard.')
parser.add_argument('--participant_label', help='The label of the participant that should be analyzed. The label '
                                                'corresponds to sub-<participant_label> from the BIDS spec '
                                                '(so it does not include "sub-"). If this parameter is not '
                                                'provided all subjects should be analyzed. Multiple '
                                                'participants can be specified with a space separated list.',
                    nargs="+")
parser.add_argument('--session_label', help='The label of the session that should be analyzed. The label '
                                            'corresponds to ses-<session_label> from the BIDS spec '
                                            '(so it does not include "ses-"). If this parameter is not '
                                            'provided all sessions should be analyzed. Multiple '
                                            'sessions can be specified with a space separated list.',
                    nargs="+")
parser.add_argument('--mri_crop_step',
                    help='Which step of the crop_fill pipeline should be performed',
                    choices=["crop", "fill", "zero_pad", "trim"]
                    )
parser.add_argument('--acquisition_label',
                    help='If the dataset contains multiple T1 weighted images from different acquisitions which one '
                         'should be used? Corresponds to "acq-<acquisition_label>"')
parser.add_argument('--filling_label',
                    help='Label of the image that is going to be used for filling. Corresponds to "acq-<filling_label>"')
parser.add_argument('--zeropad_label',
                    help='Label of the image that is going to be used for reference to zeropad. Corresponds to '
                         '"acq-<zeropad_label>"')

args = parser.parse_args()

subject_dirs = glob(os.path.join(args.bids_dir, "sub-*"))

# Got to combine acq_tpl and rec_tpl
if args.acquisition_label:
    ar_tpl = "*_acq-%s*" % args.acquisition_label
else:
    ar_tpl = "*"

# if there are session folders, check if study is truly longitudinal by
# searching for the first subject with more than one valid sessions

if glob(os.path.join(args.bids_dir, "sub-*", "ses-*")):
    subjects = [subject_dir.split("-")[-1] for subject_dir in subject_dirs]
    for subject_label in subjects:
        session_dirs = glob(os.path.join(args.bids_dir, "sub-%s" % subject_label, "ses-*"))
        sessions = [os.path.split(dr)[-1].split("-")[-1] for dr in session_dirs]
        n_valid_sessions = 0
        for session_label in sessions:
            if glob(os.path.join(args.bids_dir, "sub-%s" % subject_label,
                                 "ses-%s" % session_label,
                                 "anat",
                                 "%s_T1w.nii*" % ar_tpl)):
                n_valid_sessions += 1

subjects_to_analyze = []
# only for a subset of subjects
if args.participant_label:
    subjects_to_analyze = args.participant_label
    print("Subject to analyze: ", subjects_to_analyze)
# for all subjects
else:
    subject_dirs = glob(os.path.join(args.bids_dir, "sub-*"))
    subjects_to_analyze = [subject_dir.split("-")[-1] for subject_dir in subject_dirs]

for subject_label in subjects_to_analyze:
    if glob(os.path.join(args.bids_dir, "sub-%s" % subject_label, "ses-*")):
        T1s = glob(os.path.join(args.bids_dir,
                                "sub-%s" % subject_label,
                                "ses-*",
                                "anat",
                                "%s_T1w.nii*" % ar_tpl))
        sessions = set([os.path.normpath(t1).split(os.sep)[-3].split("-")[-1] for t1 in T1s])
        if args.session_label:
            sessions = sessions.intersection(args.session_label)
        for session_label in sessions:
            T1s = glob(os.path.join(args.bids_dir,
                                    "sub-%s" % subject_label,
                                    "ses-%s" % session_label,
                                    "anat",
                                    "%s_T1w.nii*" % ar_tpl))
            input_args_t1 = ""
            output_args_t1_crop = ""
            output_args_t1_fill = ""
            for T1 in T1s:
                input_args_t1 += "%s" % T1
                out = input_args_t1.split("acq-{acq}_T1w".format(acq=args.acquisition_label))
                output_args_t1_crop = "{out1}acq-cropped_T1w{out2}".format(out1=out[0], out2=out[1])
                output_args_t1_filled = "{out1}acq-filled_T1w{out2}".format(out1=out[0], out2=out[1])
                output_args_t1_zeropadded = "{out1}acq-zeropadded_T1w{out2}".format(out1=out[0], out2=out[1])
                input_args_t1_fill = "{out1}acq-{fill}_T1w{out2}".format(out1=out[0], fill=args.filling_label, out2=out[1])
                input_args_t2_zeropad = "{out1}acq-{zeropad}_T2w{out2}".format(out1=out[0], zeropad=args.zeropad_label, out2=out[1])
                input_args_t1_ds = "{out1}acq-ds_T1w{out2}".format(out1=out[0], out2=out[1])
                output_args_t1_trimmed = "{out1}acq-trimmed_T1w{out2}".format(out1=out[0], out2=out[1])

            if args.mri_crop_step == "crop":
                print("Cropping")
                crop_img(input_args_t1, output_args_t1_crop)
            elif args.mri_crop_step == "fill":
                print("Filling")
                collage_img(input_args_t1, input_args_t1_fill, output_args_t1_filled)
            elif args.mri_crop_step == "zero_pad":
                print("Zero padding")
                zero_pad(input_args_t1, input_args_t1_zeropad, output_args_t1_zeropadded)
            elif args.mri_crop_step == "trim":
                print("Trimming")
                trim(input_args_t1, input_args_t1_ds, output_args_t1_trimmed)
