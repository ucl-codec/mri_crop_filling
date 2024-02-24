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
   - FreeSurfer v7.4.1, ubuntu 22 (takes minutes to hours, depending on your connection)
```
MINICONDA_INSTALLER=Miniconda3-py39_23.11.0-2-Linux-x86_64.sh
FREESURFER_TARBALL=freesurfer-linux-ubuntu22_amd64-7.4.1.tar.gz
wget https://repo.anaconda.com/miniconda/${MINICONDA_INSTALLER}
wget https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.4.1/${FREESURFER_TARBALL}
# Copy into relevant folders
cp ${MINICONDA_INSTALLER} cropfill/miniconda_installer.sh
cp ${MINICONDA_INSTALLER} freesurfer7p4p1/miniconda_installer.sh
mv ${FREESURFER_TARBALL} freesurfer7p4p1/
```

3. Build FreeSurfer docker container
```
USER=$(id -un)
DOCKERTAG=${USER}/mri_crop_filling:fs7p4p1
docker build --progress=plain -t ${DOCKERTAG} -f freesurfer7p4p1.Dockerfile .
```

On an M3 mac:
```
docker buildx build --platform linux/amd64 --progress=plain -t ${DOCKERTAG} -f freesurfer7p4p1.Dockerfile .
```

4. Build Crop-filling container
```
cd ../crop_fill
DOCKERTAGCF=${USER}/mri_crop_filling:crop_fill
docker build --progress=plain --tag ${DOCKERTAGCF} -f crop_fill.Dockerfile .
```

On an M3 mac:
```
docker buildx build --platform linux/amd64 --progress=plain --tag ${DOCKERTAGCF} -f crop_fill.Dockerfile .
```

5. Save IMAGE ID for both docker images
```
docker images
# Automatically copy the IMAGE ID and assign environment variables
IMAGEIDFS=`docker images --format="{{.Repository}}:{{.Tag}} {{.ID}}" | grep "^${DOCKERTAG} " | cut -d' ' -f2`
IMAGEIDCF=`docker images --format="{{.Repository}}:{{.Tag}} {{.ID}}" | grep "^${DOCKERTAGCF} " | cut -d' ' -f2`
```

Now you can follow the Crop Filling [docker walkthrough](./README-docker.md).
