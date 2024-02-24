This branch was built on macOS M3 chip. Requires passing the `--platform linux/amd64` flag to docker, and possibly other quirks.

The docker files do not include curl options for the FreeSurfer tar files. They must be pre-downloaded as part of the build process explained here: [README-docker-build.md](../README-docker-build.md).

Notes:

- NeuroDocker docker container fails: `docker run --platform linux/amd64 --rm repronim/neurodocker:latest generate docker ...` failed.
- So, pip install neurodocker instead: `pip install neurodocker`

Step 1: use NeuroDocker to produce the base Dockerfile for FreeSurfer 7.3.1 (7.4.1 not available in neurodocker at time of writing — see manual edits below) with MiniConda 4.12.0: 
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

Then manually edit `freesurfer7p3p1.Dockerfile` for FreeSurfer 7.4.1 and use your favourite editor to Find and Replace 7.3.1 with 7.4.1, e.g.:

```
cp freesurfer7p3p1.Dockerfile freesurfer7p4p1.Dockerfile
sed -i 's/7.3.1/7.4.1/g' freesurfer7p4p1.Dockerfile
URLFS7p4p1=https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.4.1/freesurfer-linux-ubuntu22_amd64-7.4.1.tar.gz
URLFS7p3p1=https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.4.1/freesurfer-linux-centos7_x86_64-7.3.1.tar.gz
sed -i 's/$URLFS7p3p1/$URLFS7p4p1/g' freesurfer7p4p1.Dockerfile
```

Then use [Miniconda3-py39_23.11.0-2-Linux-x86_64.sh](https://repo.anaconda.com/miniconda/Miniconda3-py39_23.11.0-2-Linux-x86_64.sh) instead of the default one supplied by neurodocker (my docker build failed).

Then you can build the FreeSurfer docker image, per the [README-docker-build.md](../README-docker-build.md) instructions, replacing `Dockerfile` with `freesurfer7p4p1.Dockerfile`.

```
docker buildx build --platform linux/amd64 --progress=plain -t ${DOCKERTAG} -f freesurfer7p4p1.Dockerfile .
```

# Next: crop filling

See [Crop Filling build README.md](../cropfill/README.md)
