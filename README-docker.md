# Docker Crop-Filling

Author: [Neil Oxtoby](https://github.com/noxtoby), UCL (August 2023).

This is a companion README to the singularity instructions in [README.md](./README.md), aimed at those who prefer to (or can only) use docker.

To build the dockers containers, follow the instructions in [README-docker-build.md](./README-docker-build.md).

Crop-Filling preprint: [Castro Leal, et al. medRxiv 2023](https://doi.org/10.1101/2023.03.06.23286839).

## Walk-through

I walked through the singularity commands in [README.md](./README.md) and translated them for docker, testing along the way and editing code as needed.

You should walk through these steps one at a time.

Notes:

- For the purpose of testing the docker containers, I mounted `run.py` to `/run.py` (which overwrides the version within the container).
- TODO: convert to a python script that can be run without docker/singularity. Requires FreeSurfer 7dev, but otherwise is just a matter of combining the functionality of the FreeSurfer [run.py](./FS_dev/run.py), the Crop-filling [run.py](./crop_fill/run.py), and the Crop-filling code ([Cropping.py](./crop_fill/Cropping.py)).

### Step 0: Define some environment variables

Manually copy each IMAGE ID (for FreeSurfer and Crop-Filling containers) and assign to environment variables for convenience
```
docker images
IMAGEIDFS=<edit me>
IMAGEIDCF=<edit-me-too>
```

FreeSurfer licence file
```
FSLICENCEPATH=/path/to/freesurfer_license.txt
```

Select clinical scans for testing
```
CLINICAL_BIDS_PATH=/Path/to/bids
SUB=001
SES=01
T1_PATH=${CLINICAL_BIDS_PATH}/sub-${SUB}/ses-${SES}/anat/sub-${SUB}_ses-${SES}_T1w.nii.gz
T2_PATH=${CLINICAL_BIDS_PATH}/sub-${SUB}/ses-${SES}/anat/sub-${SUB}_ses-${SES}_T2w.nii.gz
```

Allow for `run.py` development by mounting it within the container (thereby overwriting the original from image build time):
```
CROP_FILLING_REPO_PATH=/Path/to/CODEC_Crop-Filling
RUNPY_FS=${CROP_FILLING_REPO_PATH}/FS_dev/run.py
MOUNTRUNPY_FSTEXT="type=bind,source=${RUNPY_FS},target=/run.py"
RUNPY_CF=${CROP_FILLING_REPO_PATH}/crop_fill/run.py
MOUNTRUNPY_CFTEXT="type=bind,source=${RUNPY_CF},target=/run.py"
# Also some other mounts, for convenience
MOUNTFSLICENSE="type=bind,source=${FSLICENCEPATH},target=/license.txt"
MOUNTBIDS="type=bind,source=${CLINICAL_BIDS_PATH},target=/bids"
```

### Step 1: Crop T2 to match clinical data

This was a step performed on ADNI data in the Crop-filling paper (preprint: [Castro Leal, et al. medRxiv 2023](https://doi.org/10.1101/2023.03.06.23286839)).

Not necessary if running on clinical data.

### Step 2. Downsample T2 to match clinical T2

Another ADNI-specific step in the Crop-filling paper.

It _is_ necessary to run the code below because subsequent steps assume the corresponding output filename (`*_acq-ds_T2w.nii.gz`).

Either get the T2 image resolution from itself, or use "same" argument
```
export T2X=$(mri_info --cres ${T2_PATH})
export T2Y=$(mri_info --rres ${T2_PATH})
export T2Z=$(mri_info --sres ${T2_PATH})
```

Downsample `T2` => `acq-ds_T2`:
```
docker run -ti --rm --mount ${MOUNTRUNPY_FSTEXT} --mount ${MOUNTFSLICENSE} --mount ${MOUNTBIDS} ${IMAGEIDFS} --participant_label ${SUB} --session_label ${SES} --dev_tools mri_convert_tri --mri_convert_modality T2 --mri_convert_options ${T2X} ${T2Y} ${T2Z} --skip_bids_validator --3T false --license_file /license.txt --refine_pial_acquisition_label "" /bids /bids/derivatives developer
```

### Step 3. Register downsampled T2 to T1

Register `acq-ds_T2` to `T1` => `acq-reg_T2`:
```
PIALACQ=ds
docker run -ti --rm --mount ${MOUNTRUNPY_FSTEXT} --mount ${MOUNTFSLICENSE} --mount ${MOUNTBIDS} ${IMAGEIDFS} --participant_label ${SUB} --session_label ${SES} --dev_tools mri_robust_registration --mri_convert_modality T2 --skip_bids_validator --3T false --license_file /license.txt --refine_pial_acquisition_label ${PIALACQ} /bids /bids/derivatives developer
# Convert MGZ to NIFTI
docker run -ti --rm --mount ${MOUNTRUNPY_FSTEXT} --mount ${MOUNTFSLICENSE} --mount ${MOUNTBIDS} ${IMAGEIDFS} --participant_label ${SUB} --session_label ${SES} --dev_tools mri_convert_reg --mri_convert_modality T2 --skip_bids_validator --3T false --license_file /license.txt --refine_pial_acquisition_label "" /bids /bids/derivatives developer
```

### Step 4. Synthesise T1 from registered T2

Run SynthSR on `acq-reg_T2` => `acq-SRT2_T1`:
```
PIALACQ=reg
docker run -ti --rm --mount ${MOUNTRUNPY_FSTEXT} --mount ${MOUNTFSLICENSE} --mount ${MOUNTBIDS} ${IMAGEIDFS} --participant_label ${SUB} --session_label ${SES} --dev_tools synthsr_T2 --skip_bids_validator --3T false --license_file /license.txt --refine_pial_acquisition_label ${PIALACQ} /bids /bids/derivatives developer
```

### Step 5. Resample and trim synthetic T1

Refine `acq-SRT2_T1` => `acq-ds_T1`:
```
ACQ=SRT2
PIALACQ=reg
docker run -ti --rm --mount ${MOUNTRUNPY_FSTEXT} --mount ${MOUNTFSLICENSE} --mount ${MOUNTBIDS} ${IMAGEIDFS} --participant_label ${SUB} --session_label ${SES} --dev_tools mri_convert_tri --mri_convert_modality T1 --mri_convert_options same same same --skip_bids_validator --3T false --license_file /license.txt --acquisition_label ${ACQ} --refine_pial_acquisition_label ${PIALACQ} /bids /bids/derivatives developer
```

Match dimensions of synthetic `acq-ds_T1` to real `T1` => `acq-trimmed_T1w`:
```
ACQ=ds
docker run -ti --rm --mount ${MOUNTBIDS} ${IMAGEIDCF} --participant_label ${SUB} --session_label ${SES} --mri_crop_step trim --acquisition_label ${ACQ} /bids
```

### Step 6. Filling 1

Fill real `T1` => `acq-filled_T1w`:
```
ACQ=trimmed
docker run -ti --rm --mount ${MOUNTBIDS} ${IMAGEIDCF} --participant_label ${SUB} --session_label ${SES} --mri_crop_step fill --acquisition_label ${ACQ} --filling_label ds /bids
```

Rename filled to prevent overwriting => `acq-V1filled_T1w` (FIXME: make this elegant):
```
ACQ=filled
ACQRENAMED=V1filled
T1FILLED_PATH=${CLINICAL_BIDS_PATH}/sub-${SUB}/ses-${SES}/anat/sub-${SUB}_ses-${SES}_acq-${ACQ}_T1w.nii.gz
T1FILLEDRENAMED_PATH=${CLINICAL_BIDS_PATH}/sub-${SUB}/ses-${SES}/anat/sub-${SUB}_ses-${SES}_acq-${ACQRENAMED}_T1w.nii.gz
mv $T1FILLED_PATH $T1FILLEDRENAMED_PATH
```

### Step 7. Hyperfine

SynthSR Hyperfine => `acq-SRH_T1w`:
```
PIALACQ=reg
docker run -ti --rm --mount ${MOUNTRUNPY_FSTEXT} --mount ${MOUNTFSLICENSE} --mount ${MOUNTBIDS} ${IMAGEIDFS} --participant_label ${SUB} --session_label ${SES} --dev_tools synthsr_T1T2 --skip_bids_validator --3T false --license_file /license.txt --acquisition_label ${ACQRENAMED} --refine_pial_acquisition_label ${PIALACQ} /bids /bids/derivatives developer
```

### Final steps: repeat filling (steps 5 and 6) using the hyperfine image

Rename files from Steps 5 and 6 (to avoid overwriting):

- Step 5:
   - Input: `acq-SRT2_T1` => `acq-Step5SRT2_T1`
   - Output 1: `acq-ds_T1` => `acq-Step5ds_T1`
   - Output 2: `acq-trimmed_T1w` => `acq-Step5trimmed_T1w`
- Step 6:
   - Output: `acq-V1filled_T1w` => `acq-Step6V1filled_T1w`
- Step 6:
   - Output: `acq-SRH_T1w`
      - cp => `acq-Step7SRH_T1w`
      - cp => `acq-SRT1_T1w` # FIXME: required due to bug in `FS_dev/run.py:710` where it searches for `acq-SRT1_T1w`
      - mv => `acq-SRT2_T1w`

```
STEP5=Step5
STEP5INPUT=${CLINICAL_BIDS_PATH}/sub-${SUB}/ses-${SES}/anat/sub-${SUB}_ses-${SES}_acq-SRT2_T1w.nii.gz
STEP5INPUT_RENAMED=${CLINICAL_BIDS_PATH}/sub-${SUB}/ses-${SES}/anat/sub-${SUB}_ses-${SES}_acq-${STEP5}SRT2_T1w.nii.gz
STEP5OUTPUT1=${CLINICAL_BIDS_PATH}/sub-${SUB}/ses-${SES}/anat/sub-${SUB}_ses-${SES}_acq-ds_T1w.nii.gz
STEP5OUTPUT1_RENAMED=${CLINICAL_BIDS_PATH}/sub-${SUB}/ses-${SES}/anat/sub-${SUB}_ses-${SES}_acq-${STEP5}ds_T1w.nii.gz
STEP5OUTPUT2=${CLINICAL_BIDS_PATH}/sub-${SUB}/ses-${SES}/anat/sub-${SUB}_ses-${SES}_acq-trimmed_T1w.nii.gz
STEP5OUTPUT2_RENAMED=${CLINICAL_BIDS_PATH}/sub-${SUB}/ses-${SES}/anat/sub-${SUB}_ses-${SES}_${STEP5}acq-trimmed_T1w.nii.gz
STEP6=Step6
STEP6OUTPUT=${CLINICAL_BIDS_PATH}/sub-${SUB}/ses-${SES}/anat/sub-${SUB}_ses-${SES}_acq-V1filled_T1w.nii.gz
STEP6OUTPUT_RENAMED=${CLINICAL_BIDS_PATH}/sub-${SUB}/ses-${SES}/anat/sub-${SUB}_ses-${SES}_acq-${STEP6}V1filled_T1w.nii.gz
STEP7=Step7
STEP7OUTPUT=${CLINICAL_BIDS_PATH}/sub-${SUB}/ses-${SES}/anat/sub-${SUB}_ses-${SES}_acq-SRH_T1w.nii.gz
STEP7OUTPUT_RENAMED_CP1=${CLINICAL_BIDS_PATH}/sub-${SUB}/ses-${SES}/anat/sub-${SUB}_ses-${SES}_acq-${STEP7}SRH_T1w.nii.gz
STEP7OUTPUT_RENAMED_CP2=${CLINICAL_BIDS_PATH}/sub-${SUB}/ses-${SES}/anat/sub-${SUB}_ses-${SES}_acq-SRT1_T1w.nii.gz
STEP7OUTPUT_RENAMED_MV=${CLINICAL_BIDS_PATH}/sub-${SUB}/ses-${SES}/anat/sub-${SUB}_ses-${SES}_acq-SRT2_T1w.nii.gz

# Rename files
mv ${STEP5INPUT} ${STEP5INPUT_RENAMED}
mv ${STEP5OUTPUT1} ${STEP5OUTPUT1_RENAMED}
mv ${STEP5OUTPUT2} ${STEP5OUTPUT2_RENAMED}
mv ${STEP6OUTPUT} ${STEP6OUTPUT_RENAMED}
cp ${STEP7OUTPUT} ${STEP7OUTPUT_RENAMED_CP1}
cp ${STEP7OUTPUT} ${STEP7OUTPUT_RENAMED_CP2}
mv ${STEP7OUTPUT} ${STEP7OUTPUT_RENAMED_MV}
```

#### Repeat Step 5

Refine `acq-SRT1_T1` (renamed from `acq-SRH_T1`) => `acq-ds_T1`:
```
ACQ=SRT2
PIALACQ=reg
docker run -ti --rm --mount ${MOUNTRUNPY_FSTEXT} --mount ${MOUNTFSLICENSE} --mount ${MOUNTBIDS} ${IMAGEIDFS} --participant_label ${SUB} --session_label ${SES} --dev_tools mri_convert_tri --mri_convert_modality T1 --mri_convert_options same same same --skip_bids_validator --3T false --license_file /license.txt --acquisition_label ${ACQ} --refine_pial_acquisition_label ${PIALACQ} /bids /bids/derivatives developer
```

Match dimensions of synthetic `acq-ds_T1` to real `T1` => `acq-trimmed_T1w`:
```
ACQ=ds
docker run -ti --rm --mount ${MOUNTBIDS} ${IMAGEIDCF} --participant_label ${SUB} --session_label ${SES} --mri_crop_step trim --acquisition_label ${ACQ} /bids
```

#### Repeat Step 6

Fill real `T1` => `acq-filled_T1w`:
```
ACQ=trimmed
docker run -ti --rm --mount ${MOUNTRUNPY_CFTEXT} --mount ${MOUNTBIDS} ${IMAGEIDCF} --participant_label ${SUB} --session_label ${SES} --mri_crop_step fill --acquisition_label ${ACQ} --filling_label ds /bids
```

Rename filled to prevent overwriting => `acq-Finalfilled_T1w` (FIXME: make this elegant):
```
ACQ=filled
ACQRENAMED=Finalfilled
T1FILLED_PATH=${CLINICAL_BIDS_PATH}/sub-${SUB}/ses-${SES}/anat/sub-${SUB}_ses-${SES}_acq-${ACQ}_T1w.nii.gz
T1FILLEDRENAMED_PATH=${CLINICAL_BIDS_PATH}/sub-${SUB}/ses-${SES}/anat/sub-${SUB}_ses-${SES}_acq-${ACQRENAMED}_T1w.nii.gz
cp $T1FILLED_PATH $T1FILLEDRENAMED_PATH
```

