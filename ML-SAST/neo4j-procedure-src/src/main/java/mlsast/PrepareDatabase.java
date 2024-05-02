package mlsast;

import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

import org.neo4j.graphdb.Direction;
import org.neo4j.graphdb.Label;
import org.neo4j.graphdb.Node;
import org.neo4j.graphdb.RelationshipType;
import org.neo4j.graphdb.Result;
import org.neo4j.graphdb.Transaction;
import org.neo4j.logging.Log;
import org.neo4j.procedure.Context;
import org.neo4j.procedure.Description;
import org.neo4j.procedure.Mode;
import org.neo4j.procedure.Name;
import org.neo4j.procedure.Procedure;

public class PrepareDatabase {
    @Context
    public Log log;

    @Context
    public Transaction tx;

    /**
     * This procedure generates labels for each graph in the database, such that the graphs may be
     * easily selected by their name. Also adds a master-label, such that all graphs may be selected
     * at once.
     */
    @Procedure(value = "mlsast.prepare.generateLabels", mode = Mode.SCHEMA)
    @Description("Generates labels for the different graph types.")
    public void generateLabels() {
        Result res = null;

        // Create union label for all nodes
        res = tx.execute("MATCH (n) SET n:master;");
        log.info("\n" + res.resultAsString());

        // Create labels for all graph types
        res = tx.execute("MATCH (n {graph:\"ICFG\"}) "
                + "SET n:icfg;");
        log.info("\n" + res.resultAsString());

        res = tx.execute("MATCH (n {graph:\"PTACG\"}) "
                + "SET n:ptacg;");
        log.info("\n" + res.resultAsString());

        res = tx.execute("MATCH (n {graph:\"SVFG\"}) "
                + "SET n:svfg;");
        log.info("\n" + res.resultAsString());

        res = tx.execute("MATCH (n {graph:\"TLDEP\"}) "
                + "SET n:tldep;");
        log.info("\n" + res.resultAsString());
    }

    /**
     * Generates indeces for the graphs, based on their function names. This way some of the queries
     * that rely heavily on the names of functions should be executed faster.
     */
    @Procedure(value = "mlsast.prepare.generateIndeces", mode = Mode.SCHEMA)
    @Description("Generates indeces over function names.")
    public void generateIndeces() {
        Result res = null;

        res = tx.execute("CREATE INDEX fun IF NOT EXISTS "
                + "FOR (n:icfg) ON (n.func_name);");
        log.info("\n" + res.resultAsString());

        res = tx.execute("CREATE INDEX fun IF NOT EXISTS "
                + "FOR (n:ptacg) ON (n.func_name);");
        log.info("\n" + res.resultAsString());

        res = tx.execute("CREATE INDEX fun IF NOT EXISTS "
                + "FOR (n:svfg) ON (n.func_name);");
        log.info("\n" + res.resultAsString());

        res = tx.execute("CREATE INDEX fun IF NOT EXISTS "
                + "FOR (n:tldep) ON (n.func_name);");
        log.info("\n" + res.resultAsString());

    }

    /**
     * This procedure adds also-edges to between graphs, i.e., for each pair of equvialent nodes of
     * two different graphs a new edge is added with the kind "also". Two nodes are considered to be
     * equivalent, iff they they correspond to the same llvm-instruction at the same position in the
     * program.
     */
    @Procedure(value = "mlsast.prepare.connectGraphs", mode=Mode.WRITE)
    @Description("Generates connecting edges between the graphs.")
    public void connectGraphs() {
        Result res = null;

        // This will connect the call site nodes of the ICFG to the nodes of
        // all other graphs that match this instruction.
        res = tx.execute("MATCH (n {graph:\"ICFG\"}), (m) "
                + "WHERE n.n_hash = m.icfg_node "
                + "AND n.n_hash<>\"\" "
                + "AND m.icfg_node<>\"\" "
                + "AND NOT((n)-[:also]->(m)) "
                + "CREATE (n)-[:also]->(m)");

        res = tx.execute("MATCH (n {graph:\"ICFG\"}), (m) "
                + "WHERE n.n_hash = m.icfg_node "
                + "AND n.n_hash<>\"\" "
                + "AND m.icfg_node<>\"\" "
                + "AND NOT((n)<-[:also]-(m)) "
                + "CREATE (n)<-[:also]-(m)");

        // This creates edges between all nodes of all graphs where the
        // instructions match, i.e., the general case of the code above.
        res = tx.execute("MATCH (n), (m) "
                + "WHERE n.inst_hash = m.inst_hash "
                + "AND n.inst_hash<>\"\" "
                + "AND n.graph<>m.graph "
                + "AND NOT((n)-[:also]->(m)) "
                + "CREATE (n)-[:also]->(m);");
        log.info("\n" + res.resultAsString());

        res = tx.execute("MATCH (n), (m) "
                + "WHERE n.inst_hash = m.inst_hash "
                + "AND n.inst_hash<>\"\" "
                + "AND n.graph<>m.graph "
                + "AND NOT((n)<-[:also]-(m)) "
                + "CREATE (n)<-[:also]-(m);");
        log.info("\n" + res.resultAsString());

        // Connect the PTACG to the ICFG
        res = tx.execute("MATCH (n:ptacg), (m:FunEntryICFGNode) "
                + "WHERE n.func_hash = m.func_hash "
                + "AND n.func_hash<>\"\" "
                + "AND NOT((n)-[:also]->(m)) "
                + "CREATE (n)-[:also]->(m);");
        log.info("\n" + res.resultAsString());

        res = tx.execute("MATCH (n:ptacg), (m:FunEntryICFGNode) "
                + "WHERE n.func_hash = m.func_hash "
                + "AND n.func_hash<>\"\" "
                + "AND NOT((n)<-[:also]-(m)) "
                + "CREATE (n)<-[:also]-(m);");
        log.info("\n" + res.resultAsString());
    }

    /**
     * Generates simple edges for every type of graph in the database, e.g., where there are
     * multiple different kinds of edges in the ICFG, such as inter or intra edges, there will be
     * a simple icfg edge added between connected nodes. This simplyfies the traversal of the graph
     * as there now is only one kind of edge that must be attended to.
     */
    @Procedure(value = "mlsast.prepare.makeRelationships", mode = Mode.WRITE)
    @Description("Generate union edges for each type of graph.")
    public void makeRelationships() {
        for (var node : tx.getAllNodes()) {
            for (var rel : node.getRelationships(Direction.OUTGOING)) {

                // Skip this relationship if there is no graph property present.
                if (!rel.hasProperty("graph")) {
                    continue;
                }

                RelationshipType type = RelTypes.getRel(rel.getProperty("graph"));

                // Do not create the same relationship twice.
                boolean hasRel = false;
                for (var otherRel : node.getRelationships()) {
                    if (otherRel.isType(type) && rel.getEndNode() == otherRel.getEndNode()) {
                        hasRel = true;
                        break;
                    }
                }

                if (!hasRel) {
                    node.createRelationshipTo(rel.getEndNode(), type);

                }
            }
        }
    }

    /**
     * Generates floating point values from the node values that are otherwise stored as strings.
     * Requires a lot of memory and may cause the database to crash if it runs out of memeory. This
     * is rather a limitation in how neo4j handles memory allocation rather than this particular
     * procedure. It is thus recommended to cast values from strings to floats in the application
     * itself.
     *
     * @param nodes A list of nodes.
     */
    @Procedure(value = "mlsast.prepare.floatify", mode = Mode.WRITE)
    @Description(value = "Casts all properties in the graph to floating point values if possible. "
        + "This operation is likely to fail for very large databases.")
    public void floatify(@Name("nodes") List<Node> nodes) {
        nodes.stream().forEach(node -> {
            node.getAllProperties()
            .entrySet()
            .stream()
            .forEach(entry -> {
                switch (entry.getKey()) {
                    case "cs_hash":
                        node.setProperty(entry.getKey(),
                            Float.valueOf((String) entry.getValue()));
                            break;

                    case "func_hash":
                        node.setProperty(entry.getKey(),
                            Float.valueOf((String) entry.getValue()));
                            break;

                    case "icfg_node":
                        node.setProperty(entry.getKey(),
                            Float.valueOf((String) entry.getValue()));
                            break;

                    case "mem_hash":
                        node.setProperty(entry.getKey(),
                            Float.valueOf((String) entry.getValue()));
                            break;

                    case "mr_id":
                        node.setProperty(entry.getKey(),
                            Float.valueOf((String) entry.getValue()));
                            break;

                    case "n_hash":
                        node.setProperty(entry.getKey(),
                            Float.valueOf((String) entry.getValue()));
                            break;

                    case "node_type":
                        node.setProperty(entry.getKey(),
                            Float.valueOf((String) entry.getValue()));
                            break;

                    case "ssa_ver":
                        node.setProperty(entry.getKey(),
                            Float.valueOf((String) entry.getValue()));
                            break;

                    case "dst_var":
                        node.setProperty(entry.getKey(),
                            Float.valueOf((String) entry.getValue()));
                            break;

                    case "inst_hash":
                        node.setProperty(entry.getKey(),
                            Float.valueOf((String) entry.getValue()));
                            break;

                    case "ir_opcode":
                        node.setProperty(entry.getKey(),
                            Float.valueOf((String) entry.getValue()));
                            break;

                    case "src_var":
                        node.setProperty(entry.getKey(),
                            Float.valueOf((String) entry.getValue()));
                            break;

                    case "icfg_nid":
                        node.setProperty(entry.getKey(),
                            Float.valueOf((String) entry.getValue()));
                            break;

                    case "dep_term":
                        if (Boolean.valueOf((String) entry.getValue())) {
                            node.setProperty(entry.getKey(), 1.0);
                        } else {
                            node.setProperty(entry.getKey(), 0.0);
                        }
                        break;

                    case "pts_set":
                        node.setProperty(entry.getKey(),
                            ((String) entry.getValue())
                                .split(" "));
                        break;

                    default:
                        break;
                }
            });
        });
    }

    /**
     * Generates hashes for each instruction and a corresponding points-to set if present. May be
     * used for generating embeddings, but is very slow and memory intese, which may cause the
     * database to crash.
     */
    @Procedure(value = "mlsast.prepare.hash", mode = Mode.WRITE)
    @Description("Generates hashes for IR-instructions and pts sets (may be very slow on large graphs).")
    public void hashValues() {
        Result res = null;

        // Hash all value types for IR instructions
        res = tx.execute("MATCH (n)"
            + " WHERE n.val_type IS NOT null"
            + " WITH DISTINCT n.val_type AS t"
            + " WITH count(t) AS num, collect(t) AS types"
            + " UNWIND range(0, num - 1) AS index"
            + " WITH types[index] AS t, toFloat(index) AS i"
            + " MATCH (n)"
            + " WHERE n.val_type = t"
            + " SET n.val_hash = i;");
        log.info("\n" + res.resultAsString());

        // Generate hashes for all points-to-sets
        res = tx.execute("MATCH (n)"
            + " WHERE n.pts_set IS NOT null"
            + " WITH DISTINCT n.pts_set AS p "
            + " WITH count(p) AS num, collect(p) AS pts"
            + " UNWIND range(0, num - 1) AS index"
            + " WITH pts[index] AS p, toFloat(index) AS i"
            + " MATCH (n)"
            + " WHERE n.pts_set = p"
            + " SET n.pts_hash = i;");
        log.info("\n" + res.resultAsString());
    }

    /**
     * Creates unique identification numbers for earch type of node in the graph. May be slow,
     * depending on the number of nodes passed.
     *
     * @param nodes A list of nodes to be labelled.
     */
    @Procedure(value = "mlsast.prepare.globalNodeTypes", mode = Mode.WRITE)
    @Description("Overwrites the 'node_type' property of all nodes with a"
            + "globally unique ID.")
    public void globalNodeTypes(@Name("nodes") List<Node> nodes) {
        Set<Label> labels = StreamSupport.stream(tx.getAllLabels().spliterator(), false)
            .collect(Collectors.toSet());
        labels.removeAll(Labels.allLabels);

        List<Label> labelList = labels.stream().collect(Collectors.toList());
        for (int i = 0; i < labels.size(); i++) {
            for (Node node : nodes) {
                if (node == null) {
                    continue;
                }
                if (node.hasLabel(labelList.get(i))) {
                    node.setProperty("node_type", Float.valueOf(i));
                }
            }
        }
    }

    /**
     * Creates readable names for InstTLDG nodes.
     */
    @Procedure(value = "mlsast.prepare.opCodeToName", mode = Mode.WRITE)
    @Description("Converts all InstTLDG node_name properties to their respective opcode.")
    public void opcToNodeName() {
        Result res = tx.execute("MATCH (n:InstTLDepNode) "
            + "SET n.node_name = toInteger(n.ir_opcode) "
            + "RETURN n;");

        log.debug("\n" + res.resultAsString());
    }

    /**
     * Attempts to complete the properties of ICFG nodes, by finding other equivalent nodes from
     * other graphs. Improvements on the graph generator side render this procedure more or less
     * deprecated or at least superfluous.
     */
    @Procedure(value = "mlsast.prepare.setIcfgProps", mode = Mode.WRITE)
    @Description("Sets the src_loc, full_inst and ir_opcode fields in for ICFG nodes if possible.")
    public void setIcfgProps() {
        Result res = null;

        res = tx.execute("MATCH (t:tldep)<-[:also]-(n:svfg)-[:also]->(c:icfg)"
            + " MATCH (t:tldep)<-[:also]-(n:svfg)-[:also]->(c:icfg)"
            + " WITH t, c"
            + " SET c.full_inst = t.full_inst"
            + " SET c.ir_opcode = t.ir_opcode"
            + " SET c.src_loc = t.src_loc;");

        if (res != null) {
            log.debug("\n" + res.resultAsString());
        }
    }

    /**
     * Assigns special node types to those nodes in the ICFG that are either merging points for
     * control flows, or vice versa, points in the graph where the control flow diverges. This may
     * be useful when using the node type for the graph embeddings, however, research has shown that
     * the llvm-instructions themselves are likely more exrpessive and should be used instead for
     * embedding purposes.
     */
    @Procedure(value = "mlsast.prepare.buildIcfgPhis", mode = Mode.WRITE)
    @Description("Genereates a new ICFG node type for nodes in the ICFG where"
        + " the control flow diverges or merges.")
    public void buildIcfgPhis() {
        Result res = null;
        // Make extra type for diverging paths
        res = tx.execute("MATCH (n:icfg)"
            + " WITH DISTINCT n.node_type AS typ"
            + " WITH toString(toInteger(max(typ))+1) AS typ"
            + " MATCH (n:IntraICFGNode)"
            + " WITH n, typ, apoc.node.degree.out(n, \"icfg\") AS deg"
            + " WHERE deg > 1"
            + " SET n.node_type = typ"
            + " WITH toString(toInteger(typ)+1) AS typ"
            + " MATCH (n:IntraICFGNode)"
            + " WITH n, typ, apoc.node.degree.in(n, \"icfg\") AS deg"
            + " WHERE deg > 1"
            + " SET n.node_type = typ;");

        if (res != null) {
            log.debug("\n" + res.resultAsString());
        }
    }

    /**
     * Convenience procedure that calls all procedures necessary important for the embedding of the
     * ICFG by node type, however, research has shown that the llvm-instructions themselves are
     * likely more exrpessive and should be used instead for embedding purposes.
     */
    @Procedure(value = "mlsast.prepare.graphs", mode = Mode.WRITE)
    @Description("Calls all preparation procedures concerning the graphs themselves.")
    public void graphs() {
        log.debug("Connecting graphs...");
        connectGraphs();

        log.debug("Creating relationships...");
        makeRelationships();

        log.debug("Fixing up ICFG nodes...");
        setIcfgProps();

        log.debug("Building ICFG Phis...");
        buildIcfgPhis();
    }
}
