To create the singularity image run the following commands while in this folder.
Change user_name with your user name.

```
podman build --quiet --squash-all --force-rm --tag crop_fill:v0 .
podman save --format docker-archive --output crop_fill-v0.tar localhost/crop_fill:v0
mkdir /home/user_name/tmp
SINGULARITY_TMPDIR=/home/user_name/tmp singularity build --disable-cache singularity-image_crop-fill.sif docker-archive://crop_fill-v0.tar
```
