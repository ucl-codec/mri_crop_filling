# Generated by Neurodocker and Reproenv 2024-02-24
#
# Command:
# neurodocker generate docker \
#     --pkg-manager apt \
#     --base-image ubuntu:22.04 \
#     --freesurfer version=7.3.1 \
#     --miniconda \
#         version=4.12.0 \
#         env_name=env_scipy \
#         env_exists=false \
#         conda_install=pandas \
#         pip_install=scipy \
# > freesurfer7p3p1.Dockerfile
#
# Modified by noxtoby@github to use:
# - pre-downloaded FreeSurfer 7.4.1
# - a different Miniconda because the neurodocker one failed on docker build
#


FROM ubuntu:22.04
ENV OS="Linux" \
    PATH="/opt/freesurfer-7.4.1/bin:/opt/freesurfer-7.4.1/fsfast/bin:/opt/freesurfer-7.4.1/tktools:/opt/freesurfer-7.4.1/mni/bin:$PATH" \
    FREESURFER_HOME="/opt/freesurfer-7.4.1" \
    FREESURFER="/opt/freesurfer-7.4.1" \
    SUBJECTS_DIR="/opt/freesurfer-7.4.1/subjects" \
    LOCAL_DIR="/opt/freesurfer-7.4.1/local" \
    FSFAST_HOME="/opt/freesurfer-7.4.1/fsfast" \
    FMRI_ANALYSIS_DIR="/opt/freesurfer-7.4.1/fsfast" \
    FUNCTIONALS_DIR="/opt/freesurfer-7.4.1/sessions" \
    FS_OVERRIDE="0" \
    FIX_VERTEX_AREA="" \
    FSF_OUTPUT_FORMAT="nii.gz# mni env requirements" \
    MINC_BIN_DIR="/opt/freesurfer-7.4.1/mni/bin" \
    MINC_LIB_DIR="/opt/freesurfer-7.4.1/mni/lib" \
    MNI_DIR="/opt/freesurfer-7.4.1/mni" \
    MNI_DATAPATH="/opt/freesurfer-7.4.1/mni/data" \
    MNI_PERL5LIB="/opt/freesurfer-7.4.1/mni/share/perl5" \
    PERL5LIB="/opt/freesurfer-7.4.1/mni/share/perl5"
RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           bc \
           ca-certificates \
           curl \
           libgomp1 \
           libxmu6 \
           libxt6 \
           perl \
           tcsh \
    && rm -rf /var/lib/apt/lists/*
RUN echo "Copying FreeSurfer into image ..."
COPY freesurfer-linux-ubuntu22_amd64-7.4.1.tar.gz /tmp/freesurfer-linux-ubuntu22_amd64-7.4.1.tar.gz
RUN echo "Installing FreeSurfer ..."
RUN mkdir -p /opt/freesurfer-7.4.1 \
    # && curl -fL https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.4.1/freesurfer-linux-ubuntu22_amd64-7.4.1.tar.gz \
    # | tar -xz -C /opt/freesurfer-7.4.1 --owner root --group root --no-same-owner --strip-components 1 \
    && tar -xz -C /opt/freesurfer-7.4.1 --owner root --group root --no-same-owner --strip-components 1 -f /tmp/freesurfer-linux-ubuntu22_amd64-7.4.1.tar.gz \
         --exclude='average/mult-comp-cor' \
         --exclude='lib/cuda' \
         --exclude='lib/qt' \
         --exclude='subjects/V1_average' \
         --exclude='subjects/bert' \
         --exclude='subjects/cvs_avg35' \
         --exclude='subjects/cvs_avg35_inMNI152' \
         --exclude='subjects/fsaverage3' \
         --exclude='subjects/fsaverage4' \
         --exclude='subjects/fsaverage5' \
         --exclude='subjects/fsaverage6' \
         --exclude='subjects/fsaverage_sym' \
         --exclude='trctrain'
ENV CONDA_DIR="/opt/miniconda-4.12.0" \
    PATH="/opt/miniconda-4.12.0/bin:$PATH"
RUN echo "Copying Miniconda installer into image ..."
COPY miniconda_installer.sh /tmp/miniconda_installer.sh
RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           bzip2 \
           ca-certificates \
           curl \
    && rm -rf /var/lib/apt/lists/* \
    # Install dependencies.
    && export PATH="/opt/miniconda-4.12.0/bin:$PATH" \
    # && echo "Downloading Miniconda installer ..." \
    && conda_installer="/tmp/miniconda_installer.sh" \
    # && curl -fsSL -o "$conda_installer" https://repo.anaconda.com/miniconda/Miniconda3-py39_23.11.0-2-Linux-x86_64.sh \
    && echo "Running Miniconda installer ..." \
    && bash "$conda_installer" -b -p /opt/miniconda-4.12.0 \
    && rm -f "$conda_installer" \
    # Prefer packages in conda-forge
    && conda config --system --prepend channels conda-forge \
    # Packages in lower-priority channels not considered if a package with the same
    # name exists in a higher priority channel. Can dramatically speed up installations.
    # Conda recommends this as a default
    # https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-channels.html
    && conda config --set channel_priority strict \
    && conda config --system --set auto_update_conda false \
    && conda config --system --set show_channel_urls true \
    # Enable `conda activate`
    && conda init bash \
    && conda create -y  --name env_scipy \
    && conda install -y  --name env_scipy \
           "pandas" \
    && bash -c "source activate env_scipy \
    &&   python -m pip install --no-cache-dir  \
             "scipy"" \
    # Clean up
    && sync && conda clean --all --yes && sync \
    && rm -rf ~/.cache/pip/*

# Save specification to JSON.
RUN printf '{ \
  "pkg_manager": "apt", \
  "existing_users": [ \
    "root" \
  ], \
  "instructions": [ \
    { \
      "name": "from_", \
      "kwds": { \
        "base_image": "ubuntu:22.04" \
      } \
    }, \
    { \
      "name": "env", \
      "kwds": { \
        "OS": "Linux", \
        "PATH": "/opt/freesurfer-7.4.1/bin:/opt/freesurfer-7.4.1/fsfast/bin:/opt/freesurfer-7.4.1/tktools:/opt/freesurfer-7.4.1/mni/bin:$PATH", \
        "FREESURFER_HOME": "/opt/freesurfer-7.4.1", \
        "FREESURFER": "/opt/freesurfer-7.4.1", \
        "SUBJECTS_DIR": "/opt/freesurfer-7.4.1/subjects", \
        "LOCAL_DIR": "/opt/freesurfer-7.4.1/local", \
        "FSFAST_HOME": "/opt/freesurfer-7.4.1/fsfast", \
        "FMRI_ANALYSIS_DIR": "/opt/freesurfer-7.4.1/fsfast", \
        "FUNCTIONALS_DIR": "/opt/freesurfer-7.4.1/sessions", \
        "FS_OVERRIDE": "0", \
        "FIX_VERTEX_AREA": "", \
        "FSF_OUTPUT_FORMAT": "nii.gz# mni env requirements", \
        "MINC_BIN_DIR": "/opt/freesurfer-7.4.1/mni/bin", \
        "MINC_LIB_DIR": "/opt/freesurfer-7.4.1/mni/lib", \
        "MNI_DIR": "/opt/freesurfer-7.4.1/mni", \
        "MNI_DATAPATH": "/opt/freesurfer-7.4.1/mni/data", \
        "MNI_PERL5LIB": "/opt/freesurfer-7.4.1/mni/share/perl5", \
        "PERL5LIB": "/opt/freesurfer-7.4.1/mni/share/perl5" \
      } \
    }, \
    { \
      "name": "run", \
      "kwds": { \
        "command": "apt-get update -qq\\napt-get install -y -q --no-install-recommends \\\\\\n    bc \\\\\\n    ca-certificates \\\\\\n    curl \\\\\\n    libgomp1 \\\\\\n    libxmu6 \\\\\\n    libxt6 \\\\\\n    perl \\\\\\n    tcsh\\nrm -rf /var/lib/apt/lists/*\\necho \\"Downloading FreeSurfer ...\\"\\nmkdir -p /opt/freesurfer-7.4.1\\ncurl -fL https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.4.1/freesurfer-linux-ubuntu22_amd64-7.4.1.tar.gz \\\\\\n| tar -xz -C /opt/freesurfer-7.4.1 --owner root --group root --no-same-owner --strip-components 1 \\\\\\n  --exclude='"'"'average/mult-comp-cor'"'"' \\\\\\n  --exclude='"'"'lib/cuda'"'"' \\\\\\n  --exclude='"'"'lib/qt'"'"' \\\\\\n  --exclude='"'"'subjects/V1_average'"'"' \\\\\\n  --exclude='"'"'subjects/bert'"'"' \\\\\\n  --exclude='"'"'subjects/cvs_avg35'"'"' \\\\\\n  --exclude='"'"'subjects/cvs_avg35_inMNI152'"'"' \\\\\\n  --exclude='"'"'subjects/fsaverage3'"'"' \\\\\\n  --exclude='"'"'subjects/fsaverage4'"'"' \\\\\\n  --exclude='"'"'subjects/fsaverage5'"'"' \\\\\\n  --exclude='"'"'subjects/fsaverage6'"'"' \\\\\\n  --exclude='"'"'subjects/fsaverage_sym'"'"' \\\\\\n  --exclude='"'"'trctrain'"'"'" \
      } \
    }, \
    { \
      "name": "env", \
      "kwds": { \
        "CONDA_DIR": "/opt/miniconda-4.12.0", \
        "PATH": "/opt/miniconda-4.12.0/bin:$PATH" \
      } \
    }, \
    { \
      "name": "run", \
      "kwds": { \
        "command": "apt-get update -qq\\napt-get install -y -q --no-install-recommends \\\\\\n    bzip2 \\\\\\n    ca-certificates \\\\\\n    curl\\nrm -rf /var/lib/apt/lists/*\\n# Install dependencies.\\nexport PATH=\\"/opt/miniconda-4.12.0/bin:$PATH\\"\\necho \\"Downloading Miniconda installer ...\\"\\nconda_installer=\\"/tmp/miniconda.sh\\"\\ncurl -fsSL -o \\"$conda_installer\\" https://repo.anaconda.com/miniconda/Miniconda3-py39_23.11.0-2-Linux-x86_64.sh\\nbash \\"$conda_installer\\" -b -p /opt/miniconda-4.12.0\\nrm -f \\"$conda_installer\\"\\n# Prefer packages in conda-forge\\nconda config --system --prepend channels conda-forge\\n# Packages in lower-priority channels not considered if a package with the same\\n# name exists in a higher priority channel. Can dramatically speed up installations.\\n# Conda recommends this as a default\\n# https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-channels.html\\nconda config --set channel_priority strict\\nconda config --system --set auto_update_conda false\\nconda config --system --set show_channel_urls true\\n# Enable `conda activate`\\nconda init bash\\nconda create -y  --name env_scipy\\nconda install -y  --name env_scipy \\\\\\n    \\"pandas\\"\\nbash -c \\"source activate env_scipy\\n  python -m pip install --no-cache-dir  \\\\\\n      \\"scipy\\"\\"\\n# Clean up\\nsync && conda clean --all --yes && sync\\nrm -rf ~/.cache/pip/*" \
      } \
    } \
  ] \
}' > /.reproenv.json
# End saving to specification to JSON.
