package mlsast;

import java.util.ArrayList;
import java.util.List;

import org.neo4j.graphdb.Node;
import org.neo4j.graphdb.Path;
import org.neo4j.graphdb.Relationship;

import mlsast.Helpers.Tuple;

public class Records {

    public static final class StringRecord {
        public final String str;

        public StringRecord(String str)
        {
            this.str = str;
        }
    }

    public static final class PathRecord {
        public final Path path;

        public final List<Node> nodes;

        PathRecord(Path path) {
            List<Node> temp = new ArrayList<>();
            this.path = path;
            path.nodes().forEach(temp::add);
            this.nodes = temp;
        }

        @Override
        public String toString() {
            return nodes.toString();
        }
    }

    public static final class ProjectionRecord {
        public final String graphName;
        public final String nodeQuery;
        public final Long nodeCount;
        public final String relationshipQuery;
        public final Long relationshipCount;
        public final Long projectMillis;

        public ProjectionRecord(String graphName, String nodeQuery,
                Long nodeCount, String relationshipQuery,
                Long relationshipCount, Long projectMillis) {
            this.graphName = graphName;
            this.nodeQuery = nodeQuery;
            this.nodeCount = nodeCount;
            this.relationshipQuery = relationshipQuery;
            this.relationshipCount = relationshipCount;
            this.projectMillis = projectMillis;
        }
    }

    public static final class FunctionRecord {
        public final List<Node> nodes;
        public final List<Relationship> relationships;

        public FunctionRecord(List<Node> nodes,
                List<Relationship> relationships)
        {
            this.nodes = nodes;
            this.relationships = relationships;
        }
    }

    public static final class RankRecord {
        public final String callSite;
        public final Number callSum;

        public RankRecord(Tuple<String, Number> args)
        {
            this.callSite = args.getFirst();
            this.callSum = args.getSecond();
        }
    }

    public static final class RelationshipRecord {
        public final Relationship relationship;

        public RelationshipRecord(Relationship relationship) {
            this.relationship = relationship;
        }
    }

    public static final class NodeRecord {
        public final Node node;

        public NodeRecord(Node node) {
            this.node = node;
        }
    }
    
    public static final class SubGraphRecord {
        public final List<Node> nodes;
        public final List<Relationship> relationships;
        public final String name;

        public SubGraphRecord(List<Node> nodes,
                List<Relationship> relationships,
                String name) {
            this.nodes = nodes;
            this.relationships = relationships;
            this.name = name;
        }
    }
}
