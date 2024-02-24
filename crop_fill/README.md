This branch was built on macOS M3 chip. Requires passing the `--platform linux/amd64` flag to docker, and possibly other quirks.

The docker files do not include curl options for the FreeSurfer tar files. They must be pre-downloaded as part of the build process explained here: [README-docker-build.md](../README-docker-build.md).

As with the FreeSurfer container build ([FS_dev](../FS_dev)), the [original Dockerfile](./Dockerfile) was quite old at the time of writing (February 2024), so I used neurodocker to refresh everything:
```
neurodocker generate docker \
    --pkg-manager apt \
    --base-image ubuntu:22.04 \
    --miniconda \
        version=4.12.0 \
        env_name=env_scipy \
        env_exists=false \
        conda_install=pandas \
        pip_install=scipy \
> crop_fill.Dockerfile
```

As in [freesurfer7p4p1/README.md], use [Miniconda3-py39_23.11.0-2-Linux-x86_64.sh](https://repo.anaconda.com/miniconda/Miniconda3-py39_23.11.0-2-Linux-x86_64.sh) instead of the default one supplied by neurodocker. Then build away:

```
docker buildx build --platform linux/amd64 --progress=plain --tag ${DOCKERTAGCF} -f crop_fill.Dockerfile .
```
