# syntax=docker/dockerfile:1

# The base image
FROM ubuntu:24.04
LABEL maintainer="Rudolf Hornig <rudi@omnetpp.org>"
LABEL org.opencontainers.image.source = "https://github.com/omnetpp/opp_env"

ARG USER=opp_env
ENV USER=${USER}

SHELL ["/bin/bash", "-c"]

# install base dependencies
ENV PIP_BREAK_SYSTEM_PACKAGES=1
RUN apt-get update && apt-get install --no-install-recommends -y \
      sudo curl gzip git xz-utils ca-certificates python3 python3-pip python3-venv \
      && apt-get clean && rm -rf /var/lib/apt/lists/*

# add the default user to the image
RUN useradd -m -s /bin/bash -g root ${USER}; echo "${USER}:${USER}" | chpasswd

# add wsl settings to change mount point and default user in WSL container
COPY ./wsl.conf /etc/wsl.conf

# specify the default user for WSL and enable 'sudo'
RUN echo "default=${USER}" >> /etc/wsl.conf; \
    echo "${USER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers;

# run as user opp_env after this point
USER ${USER}
WORKDIR /home/${USER}
COPY --chown=$USER:root ./nix.conf /home/${USER}/.config/nix/nix.conf
COPY --chown=$USER:root ./profile /home/${USER}/.profile

# install nix for the default user in single user mode
RUN set -o pipefail \
    && sh <(curl -L https://nixos.org/nix/install) --no-daemon \
    && mkdir -p .local/bin
# trick: check if the github repo has a new release and force a rebuild of the remaining layers    
ADD "https://api.github.com/repos/omnetpp/opp_env/releases?per_page=1" latest_commit  
RUN rm latest_commit \
    && python3 -m venv .venv \
    && . .venv/bin/activate \
    && pip install opp-env \
    && . .profile \
    && opp_env init --force

# set up the entrypoint script so all commands have an environment where .profile is sourced
COPY --chmod=0555 ./entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]
