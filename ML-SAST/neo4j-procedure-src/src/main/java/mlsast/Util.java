package mlsast;

import java.util.stream.Stream;

import org.neo4j.procedure.Context;
import org.neo4j.procedure.Description;
import org.neo4j.procedure.Mode;
import org.neo4j.graphdb.Transaction;
import org.neo4j.logging.Log;
import org.neo4j.procedure.Name;
import org.neo4j.procedure.Procedure;

import mlsast.Helpers.Tuple;

public class Util {

    @Context
    public Log log;

    @Context
    public Transaction tx;

    @Procedure(value = "mlsast.util.intvertGraph", mode = Mode.WRITE)
    @Description("Inverts all relationship of a given Graph.")
    public Stream<Records.StringRecord> invertGraph(@Name("nodeLabel") String nLabel) {
        return tx.execute("MATCH (n:`" + nLabel + "`)-[r]->(m:`" + nLabel + "`) "
                + "CREATE (n)<-[i:inverted]-(m) "
                + "RETURN count(i) as iCount;")
            .stream()
            .map(x -> new Records.StringRecord("Created " + x.get("iCount")
                + " inverted relationships."));
    }

    @Procedure(value = "mlsast.util.listProcedures", mode = Mode.READ)
    @Description("Procedures all functions of the program.")
    public Stream<Records.StringRecord> listProcedures() {
        return tx.execute("MATCH (n:ptacg) "
                + "WITH n.func_name as f "
                + "RETURN DISTINCT f "
                + "ORDER by f;")
                .stream()
                .map(row -> (String) row.get("f"))
                .map(Records.StringRecord::new);
    }

    @Procedure(value = "mlsast.util.rankedCallSites", mode = Mode.READ)
    @Description("Retrieves an ordered list of call sites.")
    public Stream<Records.RankRecord> rankedCallSites() {

        return tx.execute("MATCH (n:CallICFGNode) "
                + "WITH count(n.func_name) AS c, "
                + "n.func_name AS n "
                + "RETURN DISTINCT n, c "
                + "ORDER by c DESC;")
                .stream()
                .map(row -> new Tuple<String, Number>(
                        (String) row.get("n"),
                        (Number) row.get("c"))
                ).map(Records.RankRecord::new);
    }
}