# MRI Crop Filling 

**MRI Crop Filling** is a pipeline developed in 2022 by Gonzalo Castro that makes use of FreeSurfer 
tools `SynthSR` and `SynthSR Hyperfine` to solve the partial brain coverage (cropping) issue 
encountered in the CODEC (Essex Memory Clinic, UK) brain MRI dataset. 

For more information on this pipeline please read the paper:

- [Crop Filling: a pipeline for repairing memory clinic MRI corrupted by partial brain coverage](https://doi.org/10.1101/2023.03.06.23286839), Gonzalo Castro Leal, _et al._, Neil P Oxtoby, medR&chi;iv (2023).

<hr/>

# MRI Crop Filling (Singularity/Apptainer instructions)

This README explains the steps of the pipeline using commands of the singluarity container. <br/>
For Docker instructions, see [README-docker.md](./README-docker.md).

Sometimes the acq-labels input in the singularity command will be the actual ones that the pipeline
will use, but in other cases the acq-label will be used as a reference to locate the necessary file.

## STEP 1. CROP/ZEROPAD
This step involves the reduction of the FOV of full brain scans (The equivalent in partial brain
coverage scans would be to zeropad the image in the appropriate directions, and reset the affine
if appropriate). The command for this is as follows:
```
singularity run --bind /directory/to/bind singularity-image_crop-fill.sif folder/with/BIDS/format
--participant_label <sub-label> --mri_crop_step crop --acquisition_label <acq-label>
```   
[In]: acq-label of the actual T1w file to crop   
[Out]: acq-cropped_T1w

## STEP 2. DOWNSAMPLING T2
This step involves the downsampling of T2 scans to match clinical considerations.
``` 
singularity run --bind /directory/to/bind singularity-image_freedurfer-dev.sif folder/with/BIDS/format
folder/with/BIDS/format developer --participant_label <sub-label> --license_file prueba/license.txt
--dev_tools mri_convert_tri --mri_convert_modality T2 --mri_convert_options <sizex> <sizey> <sizez>
--refine_pial_acquisition_label <acq-label> --skip_bids_validator
``` 
[In]: acq-label of the actual T2w file to downsample   
[Out]: acq-ds_T2w

## STEP 3. REGISTRATION T2 to T1
SynthSR Hyperfine requires that the T2 and T1 scans are registered to the same space. So the T2 needs
to be moved to the T1 space.
``` 
singularity run --bind /directory/to/bind singularity-image_freedurfer-dev.sif folder/with/BIDS/format
folder/with/BIDS/format developer --participant_label <sub-label> --license_file prueba/license.txt
--dev_tools mri_robust_registration --mri_convert_modality T2 --acquisition_label <acq-label>
--refine_pial_acquisition_label <acq-label> --skip_bids_validator
``` 
[In]: acq-label of the actual T1w file & acq-label of any T2w file   
[Out]: T2_to_T1.mgz   

The output of the previous comand would be a T2_to_T1.mgz, and so it needs to be converted to an appropriate
nii image
``` 
singularity run --bind /directory/to/bind singularity-image_freedurfer-dev.sif folder/with/BIDS/format
folder/with/BIDS/format developer --participant_label <sub-label> --license_file prueba/license.txt
--dev_tools mri_convert_reg --mri_convert_modality T2 --refine_pial_acquisition_label <acq-label>
--skip_bids_validator
``` 
[In]: acq-label of any T2w file   
[Out]: acq-reg_T2w

## STEP 4. SYNTHSR
In order to obtain the first filled image, the synthetic T1 from the T2 (SRT2_T1w) needs to be obtained first.
Since we already have a reg_T2w image, is convinient to use it to ensure that the synthetic one will be in the
same space as the cropped_T1w that we aim to fill.
``` 
singularity run --bind /directory/to/bind singularity-image_freedurfer-dev.sif folder/with/BIDS/format
folder/with/BIDS/format developer --participant_label <sub-label> --license_file prueba/license.txt
--dev_tools synthsr_T2 --refine_pial_acquisition_label <acq-label> --skip_bids_validator
``` 
[In]: acq-label of the actual T2w file to use   
[Out]: acq-SRT2_T1w

## STEP 5. RESAMPLING AND TRIMMING
Although the option is used mainly on T2 downsampling, this needs to be used as well on synthetic
T1s before the filling step to ensure they match the dimensions of the original T1 scan. Therefore,
we need to specify an acq-label for the T2 scan to find the SynthSR ouput from the T2 and an acquisi-
tion label for the T1 that we want to match.
``` 
singularity run --bind /directory/to/bind singularity-image_freedurfer-dev.sif folder/with/BIDS/format
folder/with/BIDS/format developer --participant_label <sub-label> --license_file prueba/license.txt
--dev_tools mri_convert_tri --mri_convert_modality T1 --mri_convert_options same same same
--acquisition_label <acq-label> --refine_pial_acquisition_label <acq-label> --skip_bids_validator
``` 
[In]: acq-label of any T2w file & acq-label of the T1w file to match   
[Out]: acq-ds_T1w   

This is one of the tricky steps (and probably the one that might need some correction, along with the
zeropad, since the affine mention issue has not been taken into account). The issue comes from the fact
that tho the synthetic T1 (from the T2 + T1 using synthSR hyperfine) should cover the same FOV as the
T1 and T2, and is in fact as described above been resampled to the same dimensions as the T1 that is going
to be filled. The number of voxels is not the same, but the size of the brain and overall structures is,
it is like the resampling adds some extra voxels, at the end of one or more of the axes, of nothing, so
that needs to be trimmed for the filling to make sense. It will always trim a T1w scan with an acqui-
sition label as "ds" which only happens as an output of the previous command.
``` 
singularity run --bind /directory/to/bind singularity-image_crop-fill.sif folder/with/BIDS/format
--participant_label <sub-label> --mri_crop_step trim --acquisition_label <acq-label>
``` 
[In]: acq-label of the T1w file which matrix dimensions need to be matched   
[Out]: acq-trimmed_T1w

## STEP 6. FILLING
The end goal is to be able to fill the missing data of the T1 cropped
``` 
singularity run --bind --bind /directory/to/bind singularity-image_crop-fill.sif folder/with/BIDS/format
--participant_label <sub-label> --mri_crop_step fill --acquisition_label <acq-label> --filling_label <acq-label>
``` 
[In]: acq-label of the T1w file that needs to be filled & acq-label of the image used for the filling   
[Out]: acq-filled_T1w

## STEP 7. SYNTHSR HYPERFINE
After the appropirate steps the synthetic T1 from T2 + T1 scan can be obtained. Before performing this step the 
file of the acq-filled_T1w image should be renamed to acq-V1filled_T1w.
``` 
singularity run --bind /directory/to/bind singularity-image_freedurfer-dev.sif folder/with/BIDS/format
folder/with/BIDS/format developer --participant_label <sub-label> --license_file prueba/license.txt
--dev_tools synthsr_T1T2 --acquisition_label <acq-label> --refine_pial_acquisition_label <acq-label>
--skip_bids_validator
``` 
[In]: acq-label of the actual T1w scan & acq-label of any T2 image   
[Out]: acq-SRH_T1w   

Re-do STEPS 5 and 6 using SRH_T1w output
