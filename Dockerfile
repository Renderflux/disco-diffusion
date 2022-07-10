FROM entmike/disco-diffusion-1:basemodels as base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ENV DEBIAN_FRONTEND noninteractive\
    SHELL=/bin/bash

# Install a few dependencies
RUN apt-get update --yes && \
    # - apt-get upgrade is run to patch known vulnerabilities in apt-get packages as
    #   the ubuntu base image is rebuilt too seldom sometimes (less than once a month)
    apt-get upgrade --yes && \
    apt install --yes --no-install-recommends\
    wget\
    curl\
    net-tools\
    bash\
    git\
    make\
    gcc-5\
    g++-5\
    build-essential\
    tzdata\
    imagemagick\
    ffmpeg\
    zip\
    sudo\
    unzip\
    openssh-server &&\
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen

# Loosen up /workspace perms
RUN chmod a+rw /workspace

# Create a disco user
RUN useradd -ms /bin/bash disco -p disco && adduser disco sudo
RUN echo "disco ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/disco

USER disco
# Run this first since it's slow
RUN pip install git+https://github.com/facebookresearch/pytorch3d.git@stable
# Install the rest of the pips this way since they aren't slow and can be changed easier
ADD docker-requirements.txt docker-requirements.txt
RUN pip install -r docker-requirements.txt

ENV TORCH_HOME=/workspace/disco-diffusion-1/models
ADD welcome-banner.txt /home/disco/welcome-banner.txt
ARG REPO=https://github.com/entmike/disco-diffusion-1.git
ARG BRANCH=main
ENV DD_VERSION=2.6.runpod
RUN echo 'cat ~/welcome-banner.txt && echo ${DD_VERSION}' >> ~/.bashrc 
RUN git clone --single-branch --branch $BRANCH $REPO
WORKDIR /workspace/disco-diffusion-1
RUN pip install jupyterlab

# model_path based on whether models are predownloaded
ARG model_path
ENV TORCH_HOME=/models
ENV mp=/models

# Disco ENV vars are all string literals for strings becase they are JSON parsed because reasons
ENV model_path="\""/models"\""
RUN echo 'export PATH="$HOME/.local/bin:$HOME/.local/bin/jupyter-lab:$PATH"' >> ~/.bashrc

# Install JupyterLab for root but I don't know why anymore.
USER root
RUN pip install jupyterlab
RUN echo 'export PATH="$HOME/.local/bin:$HOME/.local/bin/jupyter-lab:$PATH"' >> ~/.bashrc

# Change ownership of model folder to disco user
ENV model_path=/models
RUN chown disco $(echo $model_path | tr -d '"')

USER disco
ADD start.sh /start.sh
RUN mkdir -p ${mp}/hub/checkpoints/ && cp ${mp}/vgg16-397923af.pth ${mp}/hub/checkpoints/vgg16-397923af.pth || true
CMD [ "/start.sh" ]