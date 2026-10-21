# syntax=docker/dockerfile:1

# The base image
FROM ubuntu:26.04
LABEL maintainer="Rudolf Hornig <rudi@omnetpp.org>"
LABEL org.opencontainers.image.source="https://github.com/omnetpp/opp_env"

ARG USER=opp_env
ENV USER=${USER}
ENV OPP_ENV_LAST_WORKSPACE=/home/${USER}/default_workspace

# install dependencies, add the default user to the image, specify the default user for WSL and enable 'sudo'
RUN apt-get update && apt-get upgrade -y && apt-get install --no-install-recommends -y \
    sudo fontconfig curl gzip git xz-utils ca-certificates python3 \
    && apt-get clean && rm -rf /var/lib/apt/lists/* && mkdir -p /usr/lib/wsl && \
    userdel -f --remove ubuntu; \
    useradd -m -s /bin/bash --uid 1000 -g root ${USER}; echo "${USER}:${USER}" | chpasswd && \
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
RUN /bin/bash -c '\
    sh <(curl --proto "=https" --tlsv1.2 -L https://nixos.org/nix/install) --no-daemon \
    && mkdir -p .local/bin \
    && mkdir -p $OPP_ENV_LAST_WORKSPACE'

COPY --chown=$USER:root nix.conf /home/${USER}/.config/nix/nix.conf
COPY --chown=$USER:root keyfile.glib-2.0 /home/${USER}/.config/glib-2.0/keyfile
COPY --chown=$USER:root profile /home/${USER}/.profile

ARG OPP_ENV_VERSION

# install uv and then opp_env; retry because a just-published version may take a few minutes to show up on PyPI
RUN /bin/bash -c '\
    test -n "$OPP_ENV_VERSION" \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && source ~/.local/bin/env \
    && uv venv --clear --seed --no-project --prompt opp_env \
    && source ~/.venv/bin/activate \
    && for i in $(seq 20); do \
           uv pip install --no-cache "opp-env==$OPP_ENV_VERSION" && break; \
           [ $i = 20 ] && exit 1; \
           echo "opp-env $OPP_ENV_VERSION is not available on PyPI yet, retrying in 30s"; sleep 30; \
       done \
    && opp_env init --force'
