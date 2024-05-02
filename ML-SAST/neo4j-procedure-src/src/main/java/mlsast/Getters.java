package mlsast;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.neo4j.graphalgo.BasicEvaluationContext;
import org.neo4j.graphalgo.GraphAlgoFactory;
import org.neo4j.graphalgo.PathFinder;
import org.neo4j.graphdb.Direction;
import org.neo4j.graphdb.GraphDatabaseService;
import org.neo4j.graphdb.Label;
import org.neo4j.graphdb.Node;
import org.neo4j.graphdb.Path;
import org.neo4j.graphdb.PathExpanders;
import org.neo4j.graphdb.Relationship;
import org.neo4j.graphdb.RelationshipType;
import org.neo4j.graphdb.Result;
import org.neo4j.graphdb.Transaction;
import org.neo4j.logging.Log;
import org.neo4j.procedure.Context;
import org.neo4j.procedure.Description;
import org.neo4j.procedure.Mode;
import org.neo4j.procedure.Name;
import org.neo4j.procedure.Procedure;

import mlsast.Records.NodeRecord;

public class Getters {
    @Context
    public Log log;

    @Context
    public GraphDatabaseService db;

    @Context
    public Transaction tx;

    /**
     * Returns all nodes corresponding to the exit node of a given function.
     *
     * @param fun The name of the function.
     * @return A list of nodes corresponding to the exit nodes of the function provided by fun.
     */
    @Procedure(value = "mlsast.get.procedure.egressNodes", mode = Mode.READ)
    @Description("Returns all egress nodes of the SVFG for a given procedure, i.e., all "
        + "FormalOutSVFGNodes and ActualParmNodes.")
    public Stream<Records.NodeRecord> getEgressNodes(@Name("function") String fun) {

        // Retrieve all FormalOUTSVFGNodes and ActualParm
        List<Node> exitNodes = tx.findNodes(Labels.ICFG_EXIT, "func_name", fun)
            .stream()
            .flatMap(n -> Helpers.outRels(n, RelTypes.ALSO))
            .map(r -> r.getEndNode())
            .filter(n -> n.hasLabel(Labels.SVFG))
            .collect(Collectors.toList());

        List<Node> callNodes = tx.findNodes(Labels.ICFG_CALL, "func_name", fun)
            .stream()
            .flatMap(n -> Helpers.outRels(n, RelTypes.ALSO))
            .map(r -> r.getEndNode())
            .filter(n -> n.hasLabel(Labels.SVFG))
            .collect(Collectors.toList());

        return Stream.concat(exitNodes.stream(), callNodes.stream())
            .map(NodeRecord::new);
    }

    /**
     * Returns all nodes corresponding to the ingress node of a given function.
     *
     * @param fun The name of the function.
     * @return A list of nodes corresponding to the ingress nodes of the function provided by fun.
     */
    @Procedure(value = "mlsast.get.procedure.ingressNodes", mode = Mode.READ)
    @Description("Returns all ingress nodes of the SVFG for a given procedure, i.e., all "
        + "FormalIN- and FormalParmNodes.")
    public Stream<Records.NodeRecord> getInressNodes(@Name("procedure") String fun) {
        return tx.findNodes(Labels.ICFG_ENTRY, "func_name", fun)
            .stream()
            .flatMap(n -> Helpers.outRels(n, RelTypes.ALSO))
            .map(r -> r.getEndNode())
            .filter(n -> n.hasLabel(Labels.SVFG))
            .map(NodeRecord::new);
    }

    /**
     * Retrieves return nodes of the SVFG of a function that acts as sources in a taint-propagation
     * model.
     *
     * @param fun The function to be processed.
     *
     * @return The corresponding SVFG node.
     */
    @Procedure(value = "mlsast.get.call.source", mode = Mode.READ)
    @Description("Retrieves calls to source-like functions "
        + "by their return values, from the SVFG.")
    public Stream<Records.NodeRecord> getSources(@Name("function") String fun) {
        return tx.findNodes(Labels.ICFG_RETURN, "func_name", fun)
            .stream()
            .flatMap(n -> Helpers.outRels(n, RelTypes.ALSO))
            .map(r -> r.getEndNode())
            .filter(n -> n.hasLabel(Labels.SVFG_RETURN))
            .map(NodeRecord::new);
    }

    /**
     * Retrieves address nodes of a function that acts as a allocation site in the SVFG, in a
     * taint-propagation model.
     *
     * @param fun The function to be processed.
     *
     * @return The corresponding SVFG node.
     */
    @Procedure(value = "mlsast.get.call.allocation", mode = Mode.READ)
    @Description("Retrieves potential calls to source-like functions "
        + "that generate memory regions, from the SVFG.")
    public Stream<Records.NodeRecord> getMemSources(@Name("fun") String fun) {
        return tx.findNodes(Labels.ICFG_CALL, "func_name", fun)
            .stream()
            .flatMap(n -> Helpers.outRels(n, RelTypes.ALSO))
            .map(r -> r.getEndNode())
            .filter(n -> n.hasLabel(Labels.SVFG_ADDR))
            .map(NodeRecord::new);
    }

        /**
     * Retrieves param nodes of the SVFG of a function that acts as sinks in the SVFG in a
     * taint-propagation model.
     *
     * @param fun The function to be processed.
     *
     * @return The corresponding SVFG node.
     */
    @Procedure(value = "mlsast.get.call.sink", mode = Mode.READ)
    @Description("Retrieves potential calls to functions that act as sinks, "
        + "from the SVFG.")
    public Stream<Records.NodeRecord> getSinks(@Name("fun") String fun) {
        return tx.findNodes(Labels.ICFG_CALL, "func_name", fun)
            .stream()
            .flatMap(n -> Helpers.outRels(n, RelTypes.ALSO))
            .map(r -> r.getEndNode())
            .filter(n -> n.hasLabel(Labels.SVFG_PARM))
            .map(NodeRecord::new);
    }

    /**
     * Retrieves all paths between two nodes in the SVFG on a global scale. Computationally, this is
     * a very hard problem that scales badly with a growing number of nodes.
     *
     * @param start The node to start the traversal from.
     * @param target The node to be reached.
     * @param relType The type of relationship to be used for the traversal.
     * @param algo If set to true, uses the simple (loop-less) algorithm (recommended).
     * @param depth Maximum depth of the traversal (A depth of 75 is feasible, but lower is better).
     *
     * @return A List of paths in the SVFG that connect the start and target node.
     */
    @Procedure(value = "mlsast.get.global.paths", mode = Mode.READ)
    @Description("Retrieves all paths between two nodes for a given graph type.")
    public Stream<Records.PathRecord> getPaths(@Name("startNode") Node start,
            @Name("targetNode") Node target,
            @Name("relationship") String relType,
            @Name("simplePaths") Boolean algo,
            @Name("depth") Number depth) {

        RelationshipType svfgEdge = RelationshipType.withName(relType);

        PathFinder<Path> finder = null;
        if (algo) {
            finder = GraphAlgoFactory.allSimplePaths(new BasicEvaluationContext(tx, db),
                    PathExpanders.forTypeAndDirection(svfgEdge, Direction.OUTGOING),
                            depth.intValue());

            log.debug("Using simple path algorithm (loop-less).");
        } else {
            finder = GraphAlgoFactory.allPaths(new BasicEvaluationContext(tx, db),
                    PathExpanders.forTypeAndDirection(svfgEdge, Direction.OUTGOING),
                            depth.intValue());

            log.debug("Using standard path algorithm (may cotain loops).");
        }

        return Helpers.stream(finder.findAllPaths(start, target))
                .map(Records.PathRecord::new);
    }

    /**
     * Retrieves all SVFG paths within a single procedure, starting at the ingress nodes and ending
     * at the egress nodes.
     *
     * @param fun The function to traverse.
     * @param max The maximum depth of the traversal.
     *
     * @return A list of all paths that connect the ingress and egress node of the function fun.
     */
    @Procedure(value = "mlsast.get.procedure.SVFGPaths", mode = Mode.READ)
    @Description("Retrieves the SVFG paths within a single procedure.")
    public Stream<Records.PathRecord> getInternalVFGPaths(@Name("Procedure") String fun,
            @Name("max") Number max) {
        List<Node> ingressNodes = getInressNodes(fun)
                .map(n -> n.node)
                .collect(Collectors.toList());

        List<Node> egressNodes = getEgressNodes(fun)
                .map(n -> n.node)
                .collect(Collectors.toList());

        PathFinder<Path> finder = GraphAlgoFactory.allPaths(
                new BasicEvaluationContext(tx, db), PathExpanders.forTypeAndDirection(
                        RelTypes.SVFG, Direction.OUTGOING), max.intValue());

        ArrayList<Path> paths = new ArrayList<>();
        for (Node iNode : ingressNodes) {
            for (Node eNode : egressNodes) {
                finder.findAllPaths(iNode, eNode)
                    .forEach(paths::add);
            }
        }

        return paths
            .stream()
            .map(Records.PathRecord::new);
    }

    /**
     * This procedure is used to extract entire functions from the program under analysis, e.g., to
     * be imported using the networx library for the python programming language. The that case the
     * reIndex-flag must be set to true, in order to index nodes with consecutive sequence (stored
     * in the "tmp_index" property).
     *
     * @param graph The graph to extract the function from, e.g., ICFG, SVFG, etc.
     * @param reIndex Writes a consecutive index to the tmp_index property.
     * @param feature The feature to extract, i.e., the property of each node.
     * @return
     */
    @Procedure(value = "mlsast.get.procedure.all", mode = Mode.WRITE)
    @Description("Retrieves a function for a given graph that may then be used"
        + " for networkx imports. In that case, the reIndex-flag must be set to "
        + " true. Nodes will then be fitted with an extra propery 'tmp_index' that"
        + " corresponds to a consecutive sequence for each function starting at 0."
        + " Analogous to this, edges are supplemented with the properties 'tmp_start'"
        + " and 'tmp_end'."
        + " Additionally, long properties with the key provided by 'mapLongFeature'"
        + " will be mapped onto a property with the key 'feature', to allow for "
        + " an attributed Graph2Vec-embedding in networkx.")
    public Stream<Records.SubGraphRecord> getAllFunctions(@Name("graph") String graph,
            @Name("reIndex") Boolean reIndex, @Name("mapLongFeature") String feature) {
        Label label = Label.label(graph);
        List<Records.SubGraphRecord> result = new ArrayList<>();

        List<String> funcList = tx.execute("MATCH (n:ptacg)"
            +" RETURN DISTINCT n.func_name AS f;")
            .stream()
            .flatMap(c -> c.values().stream())
            .map(f -> (String) f)
            .collect(Collectors.toList());

        for (var fun : funcList) {
            List<Node> nodes = tx.findNodes(label, "func_name", fun)
                .stream()
                .collect(Collectors.toList());

            List<Relationship> rels = new ArrayList<>();

            for (Node node : nodes) {
                node.setProperty("feature", node.getProperty(feature, 0.0));

                for (Relationship rel : node.getRelationships(Direction.OUTGOING)) {
                    Node endNode = rel.getEndNode();

                    if (!endNode.hasProperty("func_name")
                            || !endNode.hasLabel(label)) {
                        continue;
                    }

                    String endFunc = ((String) endNode
                        .getProperty("func_name")).toLowerCase();

                    if (endFunc.equals(fun.toLowerCase())) {
                        rels.add(rel);
                    }
                }
            }

            if (reIndex) {
                HashSet<Node> nodeSet = new HashSet<Node>(nodes);
                HashMap<Long, String> nodeMap = new HashMap<>();

                int index = 0;
                for (Node node : nodeSet) {
                    nodeMap.put(node.getId(), String.valueOf(index));
                    index++;
                }

                for (var node : nodes) {
                    node.setProperty("tmp_index", nodeMap.get(node.getId()));
                }

                for (var rel : rels) {
                    Long startId = Long.valueOf((String) rel
                        .getStartNode()
                        .getProperty("tmp_index"));
                    Long endId = Long.valueOf((String) rel
                        .getEndNode()
                        .getProperty("tmp_index"));

                    rel.setProperty("tmp_start", startId);
                    rel.setProperty("tmp_end", endId);
                }
            }

            result.add(new Records.SubGraphRecord(nodes, rels, fun));
        }

        return result.stream();
    }

    /**
     * Retrieves all global ICFG paths sand persists them in a json-formatted file at the
     * file system path that is specified by the argument filePath. The maximum traversal depth is
     * fixed to a value of 75 (necessary to ensure consistency between models).
     *
     * @param filePath The path in the file system where the paths should be persisted to.
     */
    @Procedure(value = "mlsast.get.global.icfgPaths", mode=Mode.READ)
    @Description("Dumps the ICFG paths for every function call, from call to"
        + " to exit node that may then be used for the clustering step.")
    public void icfgAllPaths(@Name("filePath") String filePath) {
        Result res = tx.execute("CALL apoc.export.json.query("
            + " 'CALL mlsast.util.listProcedures()"
            + " YIELD str AS f"
            + " WITH f"
            + " MATCH (n:FunEntryICFGNode {func_name: f})"
            + " WITH f, n"
            + " MATCH (m:FunExitICFGNode {func_name: f})"
            + " WITH f, n, collect(m) AS exits"
            + " CALL apoc.path.expandConfig(n, {"
            + " relationshipFilter: \'icfg>\',"
            + " terminatorNodes: exits,"
            + " uniqueness: \'NODE_LEVEL\',"
            + " maxLevel: 75"
            + " })"
            + " YIELD path"
            + " RETURN f, path',"
            + " 'icfg_paths_all_procedures.json');");

            log.info("\n" + res.resultAsString());
    }
}