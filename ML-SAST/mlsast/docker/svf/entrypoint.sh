#!/usr/bin/env bash

SVF_LOGFILE="/project/logs/SVF_LOG_date$(date '+%y%m%d%H%m%S').txt"

source /root/.bashrc

echo "Verifying SVF container configuration."

if [ ! -d /project ]; then
	echo "Project directory bind mount at '/project' undefined. Exiting..."
	exit 1
fi

if [ ! -d /project/logs/svf ]; then
	echo "Creating logs directory at /project/logs/svf"
    mkdir -p /project/logs/svf

    touch ${SVF_LOGFILE}
    chmod 666 ${SVF_LOGFILE}
fi

if [ ! -e /project/build.sh ]; then
	echo "build.sh script cannot be found at /project/build.sh. Exititing..."
	exit 1
fi

echo "Copying build.sh to ${BUILD_ROOT}" >> ${SVF_LOGFILE}
cp /project/build.sh ${BUILD_ROOT}

echo "Building program source code." >> ${SVF_LOGFILE}
cd ${BUILD_ROOT}
bash build.sh

exit_code=$?

if [ "${exit_code}" != "0" ]; then
	echo "Build script exited with non-zero code of ${exit_code}. Exiting..." \
        >> ${SVF_LOGFILE}
	exit ${exit_code}
fi

echo "Copying ${BUILD_ROOT}/${BINARY} to /root/${BINARY}"
cp ${BINARY} /root
cd /root

echo "Extracting bitcode from ${BINARY}" >> ${SVF_LOGFILE}
extract-bc ${BINARY} >> ${SVF_LOGFILE} 2>&1

if [ ! -e ${BINARY}.bc ]; then
    echo "Extraction failed!" >> ${SVF_LOGFILE}
else
    echo "Extracted to $(realpath ${BINARY}.bc)"
fi

# Execute SVF command
SVF_COMMAND="${SVF_COMMAND} /root/${BINARY}.bc >> ${SVF_LOGFILE} 2>&1"

echo "Begin with graph generation." >> ${SVF_LOGFILE}
echo "Using command: ${SVF_COMMAND}" >> ${SVF_LOGFILE}
eval $SVF_COMMAND

exit_code=$?

if [ "${exit_code}" != "0" ]; then
	echo "SVF exited with a non-zero code of ${exit_code}. Exiting..." \
        >> ${SVF_LOGFILE}
	exit ${exit_code}
fi

if [ ! -d /project/svf ]; then
    echo "Creating csv folder at /project/svf." >> ${SVF_LOGFILE}
    mkdir /project/svf
fi

echo "Copying CSV files to /project/svf" >> ${SVF_LOGFILE}
cp /root/nodes_graphs.csv /root/edges_graphs.csv /project/svf

chmod -R 666 /project/svf/*

exit_code=$?

# Execute SVF command
if [ "${exit_code}" != "0" ]; then
	echo "Cannot copy CSV files to /project/svf. Exiting..." \
        >> ${SVF_LOGFILE}
	exit ${exit_code}
fi

echo "Successfully exported grahps to project/svf." >> ${SVF_LOGFILE}

exit 0
