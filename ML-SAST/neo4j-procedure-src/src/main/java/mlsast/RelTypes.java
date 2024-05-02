package mlsast;

import org.neo4j.graphdb.RelationshipType;

public class RelTypes {
    public static RelationshipType ALSO = RelationshipType.withName("also");
    public static RelationshipType ICFG = RelationshipType.withName("icfg");
    public static RelationshipType PTACG = RelationshipType.withName("ptacg");
    public static RelationshipType SVFG = RelationshipType.withName("svfg");
    public static RelationshipType TLDEP = RelationshipType.withName("tldep");

    /**
     * Retrieves the RelationshipType by its string representation.
     *
     * @param relName The name of the relationship as a string.
     *
     * @return The relationship that corresponds to the string representation or null.
     */
    public static RelationshipType getRel(Object relName) {
        String name =  ((String) relName).toLowerCase();

        switch (name) {
            case "also":
                return ALSO;
            case "icfg":
                return ICFG;
            case "ptacg":
                return PTACG;
            case "svfg":
                return SVFG;
            case "tldep":
                return TLDEP;
            default:
                break;
        }

        return null;
    }
}
