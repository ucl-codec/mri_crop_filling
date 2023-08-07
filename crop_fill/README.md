To create the singularity image run the following commands while in this folder.

```
podman build --quiet --squash-all --force-rm --tag freesurfer:dev .
podman save --format docker-archive --output freesurfer-dev.tar localhost/freesurfer:dev
mkdir /home/manuel/tmp
SINGULARITY_TMPDIR=/home/manuel/tmp singularity build --disable-cache freesurfer_dev.sif docker-archive://freesurfer-dev.tar
```
