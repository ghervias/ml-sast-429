package mlsast;

import java.util.Set;

import org.neo4j.graphdb.Label;

public class Labels {
    public static final Label ICFG_CALL = Label.label("CallICFGNode");
    public static final Label ICFG_EXIT = Label.label("FunExitICFGNode");
    public static final Label ICFG_ENTRY = Label.label("FunEntryICFGNode");
    public static final Label ICFG_RETURN = Label.label("RetICFGNode");
    public static final Label SVFG_ADDR = Label.label("AddrStmt");
    public static final Label SVFG_PARM = Label.label("ActualParmSVFGNode");
    public static final Label SVFG_RETURN = Label.label("ActualRetSVFGNode");

    public static final Label ICFG = Label.label("icfg");
    public static final Label PTACG = Label.label("ptacg");
    public static final Label SVFG = Label.label("svfg");
    public static final Label TLDEP = Label.label("tldep");
    public static final Label MASTER = Label.label("master");

    public static Set<Label> allLabels = Set.of(MASTER, ICFG, PTACG, SVFG, TLDEP);
}
