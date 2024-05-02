package mlsast;

import java.util.stream.Stream;
import java.util.stream.StreamSupport;

import org.neo4j.graphdb.Direction;
import org.neo4j.graphdb.Node;
import org.neo4j.graphdb.Relationship;
import org.neo4j.graphdb.RelationshipType;

public class Helpers {
    public static class Tuple<T0, T1> {
        private final T0 first;
        private final T1 second;

        /**
         * @param first The first element.
         * @param second The second element.
         */
        public Tuple(T0 first, T1 second) {
            this.first = first;
            this.second = second;
        }

        /**
         * @return The first element of the tuple.
         */
        public T0 getFirst() {
            return this.first;
        }

        /**
         * @return The second element of the tuple.
         */
        public T1 getSecond() {
            return this.second;
        }
    }

    /**
     * @param <T> Any Object.
     * @param iterable Iterable of Obejcts with type T.
     * @return A new stream created from the iterable.
     */
    public static <T> Stream<T> stream(Iterable<T> iterable) {
        return StreamSupport.stream(iterable.spliterator(), false);
    }

    /**
     * @param node Any node retrieved from the database.
     * @param types Zero or more types of relationships that should be returned. If no type is
     *      passed, all relationships, regardless of their type will be returned.
     * @return A stream of all outgoing relationships for the given node.
     */
    public static Stream<Relationship> outRels(Node node, RelationshipType... types) {
        return stream(node.getRelationships(Direction.OUTGOING, types));
    }

    /**
     * @param node Any node retrieved from the database.
     * @param types Zero or more types of relationships that should be returned. If no type is
     *      passed, all relationships, regardless of their type will be returned.
     * @return A stream of all incoming relationships for the given node.
     */
    public static Stream<Relationship> inRels(Node node, RelationshipType... types) {
        return stream(node.getRelationships(Direction.INCOMING, types));
    }

    /**
     * @param node Any node retrieved from the database.
     * @param types Zero or more types of relationships that should be returned. If no type is
     *      passed, all relationships, regardless of their type will be returned.
     * @return A stream of all, incoming and outgoing, relationships for the given node.
     */
    public static Stream<Relationship> rels(Node node, RelationshipType... types) {
        return stream(node.getRelationships(Direction.BOTH, types));
    }
}
