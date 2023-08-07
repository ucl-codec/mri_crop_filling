
The Docker File does not include curl options for the FreeSurfer and Miniconda tar files. Reason for this is
to avoid downloading those files again and again in case changes in the code are made to improve the functionality.
Instead download this files and place them inside the folder: 
Miniconda3-py38_4.12.0-Linux-x86_64.sh and freesurfer-linux-ubuntu18_x86_64-7-dev.tar.gz

To create the singularity image run the following commands

```
podman build --quiet --squash-all --force-rm --tag freesurfer:dev .
podman save --format docker-archive --output freesurfer-dev.tar localhost/freesurfer:dev
mkdir /home/user_name/tmp
SINGULARITY_TMPDIR=/home/user_name/tmp singularity build --disable-cache freesurfer_dev.sif docker-archive://freesurfer-dev.tar
```


