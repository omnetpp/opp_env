#!/usr/bin/env docker build -t ghcr.io/omnetpp/opp_env:20230509 .

# The base image
FROM ubuntu:22.04
LABEL maintainer="Rudolf Hornig <rudi@omnetpp.org>"

ARG USER=opp_env
ARG VERSION=20230509
ENV USER=${USER}

# install base dependencies
RUN apt-get update && apt-get install --no-install-recommends -y sudo curl xz-utils ca-certificates \
      && apt-get clean && rm -rf /var/lib/apt/lists/*
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# add the default user to the image
RUN /bin/bash -c 'useradd -m -s /bin/bash -g root ${USER}; echo "${USER}:${USER}" | chpasswd'
WORKDIR /home/${USER}

# add wsl settings to change mount point and default user
COPY ./wsl.conf /etc/wsl.conf
COPY --chown=$USER:root ./nix.conf /home/${USER}/.config/nix/nix.conf
COPY --chown=$USER:root ./bashrc /home/${USER}/.bashrc

# specify the default user for WSL and enable 'sudo'
RUN /bin/bash -c 'echo "default=${USER}" >> /etc/wsl.conf; \
    echo "${USER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers; \
    echo "${VERSION}" >/etc/hostname;'

# install nix for the default user in single user mode
RUN sudo -u ${USER} /bin/bash -c 'set -o pipefail \
    && sh <(curl -L https://nixos.org/nix/install) --no-daemon \
    && source $HOME/.nix-profile/etc/profile.d/nix.sh \
    && nix profile install nixpkgs#python3 nixpkgs#python3Packages.pip \
       nixpkgs#git nixpkgs#gzip nixpkgs#wget \
    && pip3 install --user git+https://github.com/omnetpp/opp_env.git@topic/misc-av \
    && nix-collect-garbage '

# define a default shell. Note that the folder name for the user's profile is hardcoded here
CMD ["/bin/bash", "--init-file", "/home/opp_env/.profile"]