This branch was built on macOS M3 chip. Requires passing the `--platform linux/amd64` flag to docker, and possibly other quirks.

The Docker File does not include curl options for the FreeSurfer and Miniconda tar files. Reason for this is
to avoid downloading those files again and again in case changes in the code are made to improve the functionality.
Instead download this files and place them inside the folder: 
Miniconda3-py38_4.12.0-Linux-x86_64.sh and freesurfer-linux-ubuntu18_x86_64-7-dev.tar.gz

Note: `docker run --platform linux/amd64 --rm repronim/neurodocker:latest generate docker ...` failed (NeuroDocker fails on Mac M3 chip?).

So, pip install neurodocker instead: `pip install neurodocker`

First, I use NeuroDocker to produce the base Dockerfile for FreeSurfer 7.3.1 (7.4.1 not available in neurodocker at time of writing — see manual edits below) with MiniConda 4.12.0: 
```
neurodocker generate docker \
    --pkg-manager apt \
    --base-image ubuntu:22.04 \
    --freesurfer version=7.3.1 \
    --miniconda \
        version=4.12.0 \
        env_name=env_scipy \
        env_exists=false \
        conda_install=pandas \
        pip_install=scipy \
> freesurfer7p3p1.Dockerfile
```

Then manually edit the Dockerfile for FreeSurfer 7.4.1 and use your favourite editor to Find and Replace 7.3.1 with 7.4.1.
```
cp freesurfer7p3p1.Dockerfile freesurfer7p4p1.Dockerfile
sed -i 's/7.3.1/7.4.1/g' freesurfer7p4p1.Dockerfile
URLFS7p4p1=https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.4.1/freesurfer-linux-ubuntu22_amd64-7.4.1.tar.gz
URLFS7p3p1=https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.4.1/freesurfer-linux-centos7_x86_64-7.3.1.tar.gz
sed -i 's/$URLFS7p3p1/$URLFS7p4p1/g' freesurfer7p4p1.Dockerfile
```

Then you can build the docker image, per the [README-docker-build.md](../README-docker-build.md) instructions, replacing `Dockerfile` with `freesurfer7p4p1.Dockerfile`.

```
docker buildx build --platform linux/amd64 --progress=plain -t ${DOCKERTAG} -f freesurfer7p4p1.Dockerfile .
```

To create the singularity image run the following commands while in this folder. Change user_name with your user name

```
podman build --quiet --squash-all --force-rm --tag freesurfer:7.4.1 .
podman save --format docker-archive --output freesurfer-7.4.1.tar localhost/freesurfer:7.4.1
mkdir /home/user_name/tmp
SINGULARITY_TMPDIR=/home/user_name/tmp singularity build --disable-cache singularity-image_freesurfer-7.4.1.sif docker-archive://freesurfer-7.4.1.tar
```


