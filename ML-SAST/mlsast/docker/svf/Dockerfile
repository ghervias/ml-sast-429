FROM ubuntu:20.04

ARG SVF_PATH=./svf

# Stop ubuntu-20 interactive options.
ENV DEBIAN_FRONTEND noninteractive

# Stop script if any individual command fails.
RUN set -e

# Define LLVM version.
ENV llvm_version=13.0.0

# Define home directory
ENV HOME=/root
ENV MLSAST_DIR=${HOME}/svf-mlsast

# Define dependencies.
ENV lib_deps="make g++-8 gcc-8 git zlib1g-dev \
    libncurses5-dev build-essential libssl-dev libpcre2-dev zip npm"
ENV build_deps="wget xz-utils cmake git gdb tcl"
ENV mlsast_deps="python3 python3-pip libncurses5"
ENV llvm_deps="lsb-release software-properties-common"
ENV project_home="/root/svf-mlsast"
ENV llvm_home="llvm-13.0.0.obj"
ENV z3_home="z3.obj"
ENV install_path="/root/node_modules"

# Set up SVF envrionment variables
ENV LLVM_DIR=${install_path}/${llvm_home}
ENV Z3_DIR=${install_path}/${z3_home}
ENV PATH=${LLVM_DIR}/bin:${PATH}
ENV PATH=${project_home}/bin:${PATH}
ENV SVF_DIR=${install_path}/SVF/

RUN echo "export LLVM_DIR=${install_path}/${llvm_home}" \
    >> /root/.bashrc
RUN echo "export Z3_DIR=${install_path}/${z3_home}" \
    >> /root/.bashrc
RUN echo "export PATH=${LLVM_DIR}/bin:${project_home}/bin:${PATH}" \
    >> /root/.bashrc
RUN echo "export SVF_DIR=${install_path}/SVF/" \
    >> /root/bashrc

RUN echo "LLVM_DIR="$LLVM_DIR
RUN echo "SVF_DIR="$SVF_DIR
RUN echo "Z3_DIR="$Z3_DIR

# Fetch dependencies.
RUN apt-get update --fix-missing
RUN apt-get install -y $build_deps $lib_deps
RUN apt-get install -y $mlsast_deps
RUN apt-get install -y $llvm_deps


RUN wget https://apt.llvm.org/llvm.sh
RUN chmod +x llvm.sh
RUN ./llvm.sh 13
RUN pip3 install wllvm

# Fetch and build SVF
RUN echo "Installing SVF library ..."
RUN npm i --silent svf-lib@1.0.1267 --prefix ${HOME}

# Copy build files
RUN echo "Building SVF ..."
WORKDIR ${MLSAST_DIR}
COPY . .

RUN env
RUN cmake .
RUN make -j4

RUN echo "Testing installation ..."
RUN svf-mlsast \
    -versioning-threads=7 \
    -precise-analysis \
    -build-svfg \
    -build-tldg \
    -build-icfg \
    -build-ptacg \
    ${MLSAST_DIR}/example.ll

RUN mkdir /input
RUN mkdir /output
COPY ./entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]