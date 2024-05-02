#!/bin/bash

ROOT_DIR=`pwd`

SCRIPTS_DIR=$ROOT_DIR/scripts

OPENJPEG_SRC="https://github.com/uclouvain/openjpeg.git"

OPENJPEG_DIR=$ROOT_DIR/lib/openjpeg

BUILD_DIR="${ROOT_DIR}/special_cases/openjpeg/"

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
                THIS_BUILD_FILE=build_"${COMMIT_HASH}".sh
                THIS_BUILD_FULL_PATH="$BUILD_DIR""$THIS_BUILD_FILE"
                echo "DEBUG"
                echo "$THIS_BUILD_FILE"
                echo "$THIS_BUILD_FULL_PATH"

                if [ $? == 0 ]; then
                    echo "Copying scripts to ${REV_DIR}..."
                    cp $SCRIPTS_DIR/$SW_NAME/config.yaml $REV_DIR \
                        && cp $ENTRYPOINT_FILE $REV_DIR \
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

OPENJPEG_HASHES=( \
        c16bc057ba3f125051c9966cf1f5b68a05681de4 \
        940100c28ae28931722290794889cf84a92c5f6f \
        dcac91b8c72f743bda7dbfa9032356bc8110098a \
        afb308b9ccbe129608c9205cf3bb39bbefad90b9 \
        e5285319229a5d77bf316bb0d3a6cbd3cb8666d9 \
        2cd30c2b06ce332dede81cccad8b334cde997281 \
        baf0c1ad4572daa89caa3b12985bdd93530f0dd7 \
        # da940424816e11d624362ce080bc026adffa26e8 \ # no custom build.sh yet
        d27ccf01c68a31ad62b33d2dc1ba2bb1eeaafe7b \
        397f62c0a838e15d667ef50e27d5d011d2c79c04 \
        8ee335227bbcaf1614124046aa25e53d67b11ec3 \
        c58df149900df862806d0e892859b41115875845 \
        c277159986c80142180fbe5efb256bbf3bdf3edc \
        c5bd64ea146162967c29bd2af0cbb845ba3eaaaf \
        5d00b719f4b93b1445e6fb4c766b9a9883c57949 \
)

clone_software "openjpeg" $OPENJPEG_DIR $OPENJPEG_SRC ${OPENJPEG_HASHES[@]}
