package mlsast;

import java.util.stream.Stream;

import org.neo4j.graphdb.GraphDatabaseService;
import org.neo4j.graphdb.Transaction;
import org.neo4j.logging.Log;
import org.neo4j.procedure.Context;
import org.neo4j.procedure.Description;
import org.neo4j.procedure.Name;
import org.neo4j.procedure.Procedure;

public class Gds {
    @Context
    public Log log;

    @Context
    public Transaction tx;

    @Context
    public GraphDatabaseService db;

    /**
     * Projects a graph into the graph datascience library representation using a cypher query.
     *
     * @param graph The type of graph to be projected, e.g., ICFG, SVFG, etc.
     *
     * @return A stream of ProjectionRecords.
     */
    @Procedure(value = "mlsast.gds.projectCypher")
    @Description("Generates a projection of the graph.")
    public Stream<Records.ProjectionRecord> project(@Name("graph") String graph) {
        return tx.execute("call gds.graph.project.cypher('" + graph + "', "
            + "'MATCH (n:`" + graph + "`) return id(n) as id', "
            + "'MATCH (src:`" + graph + "`)-[]-(dst:`" + graph + "`) "
            + "RETURN id(src) AS source, id(dst) AS target') "
            + "YIELD graphName, nodeQuery, nodeCount, "
            + "relationshipQuery, relationshipCount, projectMillis")
                .stream()
                .map(x -> new Records.ProjectionRecord(
                    (String) x.get("graphName"),
                    (String) x.get("nodeQuery"),
                    (Long) x.get("nodeCount"),
                    (String) x.get("relationshipQuery"),
                    (Long) x.get("relationshipCount"),
                    (Long) x.get("projectMillis")));
    }

    /**
     * Projects a graph into the graph datascience library representation using the native method,
     * which is to be preferred over cypher queries.
     *
     * @param graph The graph to be projected, e.g., ICFG, SVFG, etc.
     * @param inverted Invertes the edges of the graph if set to true, i.e., their direction.
     *
     * @return A stream of ProjectionRecords.
     */
    @Procedure(value = "mlsast.gds.projectNative")
    @Description("Generates a projection of the graph using native "
        + "projections. This is the preferred way of creating projections, "
        + "as it is faster.")
    public Stream<Records.ProjectionRecord> projectNative(@Name("graph") String graph,
            @Name("inverted") Boolean inverted) {
        String orientation = inverted ? "REVERSE" : "NATURAL";

        return tx.execute("CALL gds.graph.project('"
            + graph + "', '" + graph + "', {`"
            + graph + "`: {orientation: '" + orientation + "'}}) "
            + "YIELD graphName, nodeCount, relationshipCount, projectMillis")
                .stream()
                .map(x -> new Records.ProjectionRecord(
                    (String) x.get("graphName"),
                    "",
                    (Long) x.get("nodeCount"),
                    "",
                    (Long) x.get("relationshipCount"),
                    (Long) x.get("projectMillis")));
    }
}