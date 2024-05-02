#!/bin/bash

ROOT_DIR=`pwd`

SCRIPTS_DIR=$ROOT_DIR/scripts

MINIUPNP_SRC="https://github.com/miniupnp/miniupnp.git"
LIBTIFF_SRC="https://github.com/vadz/libtiff"
OPENJPEG_SRC="https://github.com/uclouvain/openjpeg.git"
ZLIB_SRC="https://github.com/madler/zlib.git"

MINIUPNP_DIR=$ROOT_DIR/lib/miniupnp
LIBTIFF_DIR=$ROOT_DIR/lib/libtiff
OPENJPEG_DIR=$ROOT_DIR/lib/openjpeg
ZLIB_DIR=$ROOT_DIR/lib/zlib

ENTRYPOINT_FILE="${ROOT_DIR}/entrypoints.c"

EXIT_ON_ERROR=0

function check_error {
    if [ $EXIT_ON_ERROR==1 ]; then
        exit 1
    fi
}

function clone_software {
    SW_NAME=$1
    shift
    OUT_DIR=$1
    shift
    SW_SRC=$1
    shift

    echo "Cloning ${SW_NAME}"

    while (( "$#" )); do
        COMMIT_HASH=$1
        shift

        echo "Commit hash with fix is ${COMMIT_HASH}"

        # Specify directory for every revision
        REV_DIR=$OUT_DIR/$COMMIT_HASH

        if [ ! -d $REV_DIR ]; then
            echo "Cloning to ${REV_DIR}..."

            git clone $SW_SRC $REV_DIR/code

            if [ $? == 0 ]; then
                # Checkout vulnerable revision

                CUR_DIR=`pwd`

                echo "Checking out vulnerable commit..."
                cd $REV_DIR/code && git checkout ${COMMIT_HASH}~1

                if [ $? == 0 ]; then
                    echo "Copying scripts to ${REV_DIR}..."
                    cp $SCRIPTS_DIR/$SW_NAME/build.sh $REV_DIR \
                        && cp $SCRIPTS_DIR/$SW_NAME/config.yaml $REV_DIR \
                        && cp $ENTRYPOINT_FILE $REV_DIR
                    if [ $? != 0 ]; then
                        echo "Error copying scripts to ${REV_DIR}..."
                        check_error
                    fi
                else
                    echo "Error checking out vulnerable commit ${COMMIT_HASH}..."
                    check_error
                fi
            else
                echo "Error cloning to ${REV_DIR}..."
                check_error
            fi
        else
            echo "${SW_NAME} in revision ${COMMIT_HASH} was already cloned"
        fi
    done
}

# Define commit hashes known to have fixes for security related bugs.
# During checkout the version prior to this commit will be used.
MINIUPNP_HASHES=( \
        140ee8d2204b383279f854802b27bdb41c1d5d1a \
)

LIBTIFF_HASHES=( \
        ce6841d9e41d621ba23cf18b190ee6a23b2cc833 \
        5ad9d8016fbb60109302d558f7edb2cb2a3bb8e3 \
        ae9365db1b271b62b35ce018eac8799b1d5e8a53 \
        3ca657a8793dd011bf869695d72ad31c779c3cc1 \
        b18012dae552f85dcc5c57d3bf4e997a15b1cc1c \
        5c080298d59efa53264d7248bbe3a04660db6ef7 \
        9657bbe3cdce4aaa90e07d50c1c70ae52da0ba6a \
        9a72a69e035ee70ff5c41541c8c61cd97990d018 \
        1044b43637fa7f70fb19b93593777b78bd20da86 \
        5397a417e61258c69209904e652a1f409ec3b9df \
        43bc256d8ae44b92d2734a3c5bc73957a4d7c1ec \
        438274f938e046d33cb0e1230b41da32ffe223e1 \
        c7153361a4041260719b340f73f2f76 \
        787c0ee906430b772f33ca50b97b8b5ca070faec \
        391e77fcd217e78b2c51342ac3ddb7100ecacdd2 \
        3c5eb8b1be544e41d2c336191bc4936300ad7543 \
        6a984bf7905c6621281588431f384e79d11a2e33 \
)

OPENJPEG_HASHES=( \
        e078172b1c3f98d2219c37076b238fb759c751ea \
        162f6199c0cd3ec1c6c6dc65e41b2faab92b2d91 \
        15f081c89650dccee4aa4ae66f614c3fdb268767 \
        ef01f18dfc6780b776d0674ed3e7415c6ef54d24 \
)

ZLIB_HASHES=( \
        d1d577490c15a0c6862473d7576352a9f18ef811 \
        e54e1299404101a5a9d0cf5e45512b543967f958 \
        9aaec95e82117c1cb0f9624264c3618fc380cecb \
        6a043145ca6e9c55184013841a67b2fef87e44c0 \
)

# Clone the sources for the libraries
clone_software "miniupnp" $MINIUPNP_DIR $MINIUPNP_SRC ${MINIUPNP_HASHES[@]}
clone_software "libtiff" $LIBTIFF_DIR $LIBTIFF_SRC ${LIBTIFF_HASHES[@]}
clone_software "openjpeg" $OPENJPEG_DIR $OPENJPEG_SRC ${OPENJPEG_HASHES[@]}
clone_software "zlib" $ZLIB_DIR $ZLIB_SRC ${ZLIB_HASHES[@]}
