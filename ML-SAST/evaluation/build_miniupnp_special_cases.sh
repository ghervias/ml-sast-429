#!/bin/bash

ROOT_DIR=`pwd`

SCRIPTS_DIR=$ROOT_DIR/scripts

MINIUPNP_SRC="https://github.com/miniupnp/miniupnp.git"

MINIUPNP_DIR=$ROOT_DIR/lib/miniupnp

ENTRYPOINT_DIR="${ROOT_DIR}/special_cases/miniupnp/"
BUILD_DIR="${ROOT_DIR}/special_cases/miniupnp/"

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
                THIS_ENTRYPOINT_FILE=entrypoints_"${COMMIT_HASH}".c
                THIS_ENTRYPOINT_FULL_PATH="$ENTRYPOINT_DIR""$THIS_ENTRYPOINT_FILE"
                echo "DEBUG"
                echo "$THIS_ENTRYPOINT_FILE"
                echo "$THIS_ENTRYPOINT_FULL_PATH"
                THIS_BUILD_FILE=build_"${COMMIT_HASH}".sh
                THIS_BUILD_FULL_PATH="$BUILD_DIR""$THIS_BUILD_FILE"
                echo "DEBUG"
                echo "$THIS_BUILD_FILE"
                echo "$THIS_BUILD_FULL_PATH"

                if [ $? == 0 ]; then
                    echo "Copying scripts to ${REV_DIR}..."
                    cp $SCRIPTS_DIR/$SW_NAME/build.sh $REV_DIR \
                        && cp $SCRIPTS_DIR/$SW_NAME/config.yaml $REV_DIR \
                        && cp $THIS_ENTRYPOINT_FULL_PATH $REV_DIR \
                        && mv "$REV_DIR"/"$THIS_ENTRYPOINT_FILE" "$REV_DIR"/entrypoints.c \
                        && cp $THIS_BUILD_FULL_PATH $REV_DIR \
                        && mv "$REV_DIR"/"$THIS_BUILD_FILE" "$REV_DIR"/build.sh
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

MINIUPNP_HASHES=( \
        79cca974a4c2ab1199786732a67ff6d898051b78 \
        b238cade9a173c6f751a34acf8ccff838a62aa47 \
        7aeb624b44f86d335841242ff427433190e7168a \
        cb8a02af7a5677cf608e86d57ab04241cf34e24f \
)

clone_software "miniupnp" $MINIUPNP_DIR $MINIUPNP_SRC ${MINIUPNP_HASHES[@]}
