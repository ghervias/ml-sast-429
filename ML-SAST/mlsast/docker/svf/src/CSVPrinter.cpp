#include "CSVPrinter.h"
#include "MemoryModel/PointerAnalysis.h"

namespace SVF
{

void CSVPrinter::WriteCSV(const std::string file, std::vector<std::string> rows)
{
    std::ofstream csv(file, std::ofstream::trunc);

    for (auto row : rows) {
        csv << row;
    }

    csv.close();
}

void CSVPrinter::WriteGraphToCSV(const std::string file, SVFG* svfg,
        TLDG* tldg, ICFG* icfg, PTACallGraph* ptacg)
{
    std::vector<std::string> nodes;
    std::vector<std::string> edges;
    std::vector<const SVFFunction*> functions;
    std::vector<VFGNode*> values;

    nodes.push_back(CSVPrinter::getHeader());
    edges.push_back(CSVPrinter::getHeader(/* isEdge */ true));


    if (svfg)
    {
        for (SVFG::iterator it = svfg->begin(); it != svfg->end(); ++it)
        {
            SVFGNode *node = it->second;

            // Insert all SVFG-related Nodes
            nodes.push_back(CSVPrinter::SVFGNodeToRow(node));

            // Insert all SVFG-related edges.
            for(SVFGEdge* edge : node->getOutEdges())
            {
                edges.push_back(CSVPrinter::SVFGEdgeToRow(edge));
            }
        }
    }

    if (ptacg)
    {
    for (PTACallGraph::iterator it = ptacg->begin(); it != ptacg->end(); ++it)
        {
            PTACallGraphNode* node = it->second;
            nodes.push_back(CSVPrinter::PTACGNodeToRow(node));

            for (PTACallGraphEdge* edge : node->getOutEdges())
            {
                edges.push_back(CSVPrinter::PTACGEdgeToRow(edge));
            }
        }
    }

    if (icfg)
    {
        for (ICFG::iterator it = icfg->begin(); it != icfg->end(); ++it)
        {
            ICFGNode* node = it->second;
            nodes.push_back(CSVPrinter::ICFGNodeToRow(node));

            for (ICFGEdge* edge : node->getOutEdges())
            {
                edges.push_back(CSVPrinter::ICFGEdgeToRow(edge));
            }
        }
    }

    // Insert top-level dependencies
    if (tldg)
    {
        for (const Value* val : tldg->nodes)
        {
            nodes.push_back(CSVPrinter::TLDGNodeToRow(val));

            
        }

        for (TLDGEdge* edge : tldg->edges)
        {
            edges.push_back(CSVPrinter::TLDGEdgeToRow(edge));
        }
    }

    SVFUtil::outs() << "Dumping Neo4J nodes...\n";
    WriteCSV("nodes_" + file + ".csv", nodes);

    SVFUtil::outs() << "Dumping Neo4J edges...\n";
    WriteCSV("edges_" + file + ".csv", edges);
}
}
