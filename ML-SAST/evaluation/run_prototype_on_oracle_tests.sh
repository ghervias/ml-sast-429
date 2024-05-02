#!/bin/bash
################################################
# activate python venv before running the script
################################################

MINIUPNP_HASHES=( \
        79cca974a4c2ab1199786732a67ff6d898051b78 \
        140ee8d2204b383279f854802b27bdb41c1d5d1a \
        b238cade9a173c6f751a34acf8ccff838a62aa47 \
        7aeb624b44f86d335841242ff427433190e7168a \
        cb8a02af7a5677cf608e86d57ab04241cf34e24f \
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
        c16bc057ba3f125051c9966cf1f5b68a05681de4 \
        e078172b1c3f98d2219c37076b238fb759c751ea \
        940100c28ae28931722290794889cf84a92c5f6f \
        dcac91b8c72f743bda7dbfa9032356bc8110098a \
        afb308b9ccbe129608c9205cf3bb39bbefad90b9 \
        e5285319229a5d77bf316bb0d3a6cbd3cb8666d9 \
        2cd30c2b06ce332dede81cccad8b334cde997281 \
        baf0c1ad4572daa89caa3b12985bdd93530f0dd7 \
        d27ccf01c68a31ad62b33d2dc1ba2bb1eeaafe7b \
        397f62c0a838e15d667ef50e27d5d011d2c79c04 \
        162f6199c0cd3ec1c6c6dc65e41b2faab92b2d91 \
        15f081c89650dccee4aa4ae66f614c3fdb268767 \
        8ee335227bbcaf1614124046aa25e53d67b11ec3 \
        c58df149900df862806d0e892859b41115875845 \
        c277159986c80142180fbe5efb256bbf3bdf3edc \
        c5bd64ea146162967c29bd2af0cbb845ba3eaaaf \
        5d00b719f4b93b1445e6fb4c766b9a9883c57949 \
        ef01f18dfc6780b776d0674ed3e7415c6ef54d24 \
)

ZLIB_HASHES=( \
        d1d577490c15a0c6862473d7576352a9f18ef811 \
        e54e1299404101a5a9d0cf5e45512b543967f958 \
        9aaec95e82117c1cb0f9624264c3618fc380cecb \
        6a043145ca6e9c55184013841a67b2fef87e44c0 \
)
BUILD_SCRIPT='build.sh'
OUT_FILE='oracle.log'

ROOT_DIR=$(pwd)
RESULT_DIR="$ROOT_DIR"/results
PARENT_DIR="$(dirname $ROOT_DIR)"
cd $PARENT_DIR

function execute_prototype() {
  local dir="$1"
  shift
  local hashes=("$@")
  thresholds=(1.0)
  for i in "${hashes[@]}";
    do
      for t in "${thresholds[@]}";
        do
          current_project_dir="$ROOT_DIR"/"$dir""$i"
          echo "STARTING_PROTOTYP_FOR:"
          echo $current_project_dir
          echo "STARTING_PROTOTYP_FOR:" $current_project_dir >> $OUT_FILE
          # replace threshold
          replace_threshold $current_project_dir 1 "$t"
          python3 -m mlsast --project $current_project_dir
          status=$?
          if [ $status -eq 0 ]
          then
            mkdir -p "$RESULT_DIR"/"$dir""$i"/"$t"
            # copy report to new dir
            cp $current_project_dir/report.json "$RESULT_DIR"/"$dir""$i"/"$t"/report.json
            cp $current_project_dir/merged_report.json "$RESULT_DIR"/"$dir""$i"/"$t"/merged_report.json
          else
            echo "failed to run prototype on $ROOT_DIR/$dir$i"
          fi
          # revert replacement of threshold
          replace_threshold $current_project_dir "$t" 1
      done
    done
}

function replace_threshold() {
  local dir="$1"
  local old="$2"
  local new="$3"
  sed -i "s/threshold_scaling: $2/threshold_scaling: $new/g" "$dir"/"config.yaml"
}

#/bin/bash $BUILD_SCRIPT

execute_prototype "lib/miniupnp/" "${MINIUPNP_HASHES[@]}"
execute_prototype "lib/libtiff/" "${LIBTIFF_HASHES[@]}"
execute_prototype "lib/openjpeg/" "${OPENJPEG_HASHES[@]}"
execute_prototype "lib/zlib/" "${ZLIB_HASHES[@]}"
