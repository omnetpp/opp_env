# syntax=docker/dockerfile:1

# The base image
FROM ubuntu:24.04
LABEL maintainer="Rudolf Hornig <rudi@omnetpp.org>"
LABEL org.opencontainers.image.source = "https://github.com/omnetpp/opp_env"

ARG USER=opp_env
ENV USER=${USER}
ENV OPP_ENV_LAST_WORKSPACE=/home/${USER}/default_workspace

SHELL ["/bin/bash", "-c"]

# install dependencies, add the default user to the image, specify the default user for WSL and enable 'sudo'
RUN apt-get update && apt-get install --no-install-recommends -y \
    sudo fontconfig curl gzip git xz-utils ca-certificates python3 python3-pip python3-venv \
    && apt-get clean && rm -rf /var/lib/apt/lists/* && mkdir -p /usr/lib/wsl; \
    userdel -f --remove ubuntu; \
    useradd -m -s /bin/bash --uid 1000 -g root ${USER}; echo "${USER}:${USER}" | chpasswd; \
    echo "${USER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers;

# add wsl settings to change mount point and default user in WSL container
COPY wsl.conf /etc/wsl.conf
COPY wsl-distribution.conf /etc/wsl-distribution.conf
COPY --chmod=0555 oobe.sh /etc/oobe.sh
COPY opp_env.ico /usr/lib/wsl/opp_env.ico
COPY terminal-profile.json /usr/lib/wsl/terminal-profile.json

# set up the entrypoint script so all commands have an environment where .profile is sourced
COPY --chmod=0555 ./entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]

# run as user opp_env after this point
USER ${USER}
WORKDIR /home/${USER}

# install nix for the default user in single user mode
RUN set -o pipefail \
    && sh <(curl -L https://nixos.org/nix/install) --no-daemon \
    && mkdir -p .local/bin \
    && mkdir -p $OPP_ENV_LAST_WORKSPACE

COPY --chown=$USER:root nix.conf /home/${USER}/.config/nix/nix.conf
COPY --chown=$USER:root keyfile.glib-2.0 /home/${USER}/.config/glib-2.0/keyfile
COPY --chown=$USER:root profile /home/${USER}/.profile

# trick: check if the github repo has a new release and force a rebuild of the remaining layers    
ADD "https://api.github.com/repos/omnetpp/opp_env/releases?per_page=1" latest_commit
RUN rm latest_commit \
    && python3 -m venv .venv \
    && . .venv/bin/activate \
    && pip install opp-env \
    && . .profile \
    && opp_env init --force
