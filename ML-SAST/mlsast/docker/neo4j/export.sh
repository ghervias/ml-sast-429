#!/bin/bash

NEO_LOGFILE="/var/lib/neo4j/logs/NEO_LOG_$(date '+%y%m%d%H%m%S').txt"

echo ${MEM_CFG} >> ${NEO_LOGFILE}

if [ "${MEM_CFG}" = "auto" ]
then
    echo "Using auto memory configuration." >> ${NEO_LOGFILE}
    # Copy old config without memory settings
    cat  /var/lib/neo4j/conf/neo4j.conf \
        | grep -v "dbms\.memory\..*" \
        > /tmp/neo4j.conf

    # Write recommended settings to conf file.
    /var/lib/neo4j/bin/neo4j-admin memrec > /var/lib/neo4j/conf/neo4j.conf

    # Copy over all other settings.
    cat /tmp/neo4j.conf >> /var/lib/neo4j/conf/neo4j.conf
elif [ "${MEM_CFG}" = "manual" ]
then
    echo "Using manually configured memory settings." >> ${NEO_LOGFILE}
    # Copy old config without memory settings
    cat  /var/lib/neo4j/conf/neo4j.conf \
        | grep -v "dbms\.memory\..*" \
        > /tmp/neo4j.conf

    # Write settings from env.
    echo "dbms.memory.heap.initial_size=${HEAP_INITIAL}" \
        > /var/lib/neo4j/conf/neo4j.conf
    echo "dbms.memory.heap.max_size=${HEAP_MAX}" \
        >> /var/lib/neo4j/conf/neo4j.conf
    echo "dbms.memory.pagecache.size=${PAGECACHE}" \
        >> /var/lib/neo4j/conf/neo4j.conf
    echo "dbms.memory.off_heap.max_size=${OFF_HEAP_MAX}" \
        >> /var/lib/neo4j/conf/neo4j.conf

    # Copy over all other settings.
    cat /tmp/neo4j.conf >> /var/lib/neo4j/conf/neo4j.conf
else
    echo "WARNING! Using default memory settings. The memory configuration " \
        "used may exceed the machines actual memory causing this step to " \
        "fail." >> ${NEO_LOGFILE}

    echo "Please set the memory configuration manually through the projects " \
        "config.yaml or set the neo4j.memory key to 'auto' if in doubt." \
        >> ${NEO_LOGFILE}
fi

# Set password: This does not have to be a secure password, nothing will be
# exposed.
/var/lib/neo4j/bin/neo4j-admin set-initial-password neo4j \
    >> ${NEO_LOGFILE}

# Import the graphds.
/var/lib/neo4j/bin/neo4j-admin import \
    --database=neo4j \
    --force \
    --ignore-empty-strings \
    --nodes=/var/lib/neo4j/import/nodes_graphs.csv \
    --relationships=/var/lib/neo4j/import/edges_graphs.csv \
    >> ${NEO_LOGFILE} \
    && wait

# Start the database.
/var/lib/neo4j/bin/neo4j start >> ${NEO_LOGFILE}

# Attempt to execute the query. Unfortunately the neo4j start command returns
# immediately, meaning there is no way to determine when the database is
# actually ready to accept connections. A maximum of 36 attempts will be
# conducted, with pauses of 10 seconds in between. If the database is still not
# reachable by that time, it is likely that there is a serious fault, preventing
# the database from starting at all.
TRIES=1
until [ $TRIES -eq 360 ] || echo "MATCH (n) RETURN n LIMIT 1;" \
            | /var/lib/neo4j/bin/cypher-shell -u neo4j -p neo4j \
            >> ${NEO_LOGFILE}; do
        echo "Waiting for database (attempt ${TRIES}/360)" >> ${NEO_LOGFILE}
        TRIES=$((TRIES+1))
        sleep 10
done

cat ${QUERY_FILE} | /var/lib/neo4j/bin/cypher-shell \
    --format=plain \
    -u neo4j \
    -p neo4j > /var/lib/neo4j/export/query_result.json

echo "Finished" >> ${NEO_LOGFILE}