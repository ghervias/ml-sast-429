// INIT DATABASE
CALL mlsast.prepare.generateLabels();
CALL mlsast.prepare.generateIndeces();
CALL mlsast.prepare.connectGraphs();
CALL mlsast.prepare.makeRelationships();
CALL mlsast.prepare.setIcfgProps();
CALL mlsast.prepare.buildIcfgPhis();

CALL apoc.export.json.query("// Get list of procedures in program.
CALL mlsast.util.listProcedures()
YIELD str AS f

// Find call sites for procedures.
WITH f
MATCH (n:FunEntryICFGNode {func_name: f})

// Find exit nodes for same procedures.
WITH f, n
MATCH (m:FunExitICFGNode {func_name: f})

// Find unique paths between call sites and exit points.
WITH f, n, collect(m) AS exits
  CALL apoc.path.expandConfig(n, {
      relationshipFilter: \"icfg>\",
      terminatorNodes: exits,
      uniqueness: \"NODE_LEVEL\",
      maxLevel: 75
  })

  YIELD path

// Return name of the procedure (f) and the
// associated paths (path).
RETURN f, path;
","/var/lib/neo4j/export/query_results.json");