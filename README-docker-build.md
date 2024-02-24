# How to build the docker containers for Crop-filling

Requirements:

- Miniconda installer: [Miniconda3-py39_23.11.0-2-Linux-x86_64.sh](https://repo.anaconda.com/miniconda/Miniconda3-py39_23.11.0-2-Linux-x86_64.sh)
- FreeSurfer 7.4.1: `freesurfer-linux-ubuntu22_amd64-7.4.1.tar.gz`

1. Change into repo directory (after cloning, obviously)
```
cd /path/to/mri_crop_filling
```

2. Change into FreeSurfer container directory and download Dockerfile requirements:
   - MiniConda installer (takes seconds)
   - FreeSurfer v7-dev, ubuntu 18 (takes minutes to hours, depending on your connection)
```
cd freesurfer7p4p1
wget https://repo.anaconda.com/miniconda/Miniconda3-py39_23.11.0-2-Linux-x86_64.sh
wget https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/dev/freesurfer-linux-ubuntu22_amd64-7.4.1.tar.gz
```

3. Build FreeSurfer docker container
```
USER=$(id -un)
DOCKERTAG=${USER}/mri_crop_filling:fs7p4p1
docker **buildx** build **--platform linux/amd64** --progress=plain -t ${DOCKERTAG} -f freesurfer7p4p1.Dockerfile .
```

4. Build Crop-filling container
```
cd ../crop_fill
DOCKERTAGCF=${USER}/mri_crop_filling:crop_fill
docker **buildx** build **--platform linux/amd64** --progress=plain --tag ${DOCKERTAGCF} -f Dockerfile .
```

5. Save IMAGE ID for both docker images
```
docker images
# Manually copy the IMAGE ID and assign an environment variable
IMAGEIDFS=<some-hash>
IMAGEIDCF=<another-hash>
```

Now you can follow the Crop Filling [docker walkthrough](./README-docker.md).
