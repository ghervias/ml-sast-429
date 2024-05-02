#ifndef CSVPRINTER_H_
#define CSVPRINTER_H_

#include <iostream>
#include <fstream>
#include <sstream>
#include <algorithm>

// Should likely use BasicTypes.h
#include "llvm/IR/Instruction.h"
#include "llvm/Support/Casting.h"

#include "CSVHelpers.h"

// List of node features to be exported:

#define K_LABEL ":LABEL"    // Kind of node as string
#define K_NNAME "node_name" // Name of node kind
#define K_NHASH "n_hash:ID" // Hash value of node (i.e. it's address)
#define K_NTYPE "node_type" // Kind of node as signed long long
#define K_IROPC "ir_opcode" // May be unstable between llvm versions
#define K_IHASH "inst_hash" // Hash of the instruction
#define K_INSTR "full_inst" // The full IR instruction
#define K_FNAME "func_name" // Name of the function called, returned from, etc.
#define K_FHASH "func_hash" // Node hash of the function called, returned, etc.
#define K_SRCLC "src_loc"   // Corresponding location in source code
#define K_PTSET "pts_set"   // Associated points-to set
#define K_DSTVA "dst_var"   // Destination variable for load and store statement
#define K_SRCVA "src_var"   // Source variable for load and store statement
#define K_VTYPE "val_type"  // Type of the value
#define K_CFGID "icfg_nid"  // ICFG Node ID
#define K_MRNID "mr_id"     // MRID of node
#define K_MSSAV "ssa_ver"   // MR SSA Version
#define K_CALLS "cs_hash"   // Call site as hash
#define K_CALLN "cs_name"   // Name of function called
#define K_ICFGN "icfg_node" // Corresponding icfg node
#define K_DTERM "dep_term"  // Whether this tldep node marks the head of a chain
#define K_MHASH "mem_hash"  // A hash value from the MRID, MVER and PTS

#define K_SEDGE ":START_ID" // ID of start node
#define K_EEDGE ":END_ID"   // ID of end node
#define K_ETYPE ":TYPE"     // Edge type in neo4j
#define K_EKIND "e_kind"    // Kind of edge as numeric value
#define K_EHASH "e_hash"    // Unique edge hash
#define K_ECALL "e_cs"      // Callsite of edge

#define K_GTYPE "graph" // Type of Graph for edges and nodes

// Set of all node property keys
static std::set<std::string> node_keys{K_NTYPE, K_LABEL, K_IROPC, K_INSTR,
                                       K_NHASH, K_FNAME, K_FHASH, K_SRCLC,
                                       K_PTSET, K_DSTVA, K_SRCVA, K_VTYPE,
                                       K_MRNID, K_MSSAV, K_CALLS, K_CALLN, 
                                       K_NNAME, K_CFGID, K_GTYPE, K_IHASH,
                                       K_ICFGN, K_DTERM, K_MHASH};

// Set of all edge property keys.
static std::set<std::string> edge_keys{K_SEDGE, K_EEDGE, K_ETYPE, K_EKIND,
                                       K_EHASH, K_ECALL, K_GTYPE};

namespace SVF
{

    namespace CSVPrinter
    {
        /**
         * @brief Generates the CSV header from the node and edge properties.
         * 
         * @param isEdge 
         * @return std::string 
         */
        inline std::string getHeader(bool isEdge = false)
        {
            std::stringstream stream;
            std::string ret;

            if (isEdge)
            {
                for (auto key : edge_keys)
                    stream << key << ",";
            }

            else
            {
                for (auto key : node_keys)
                    stream << key << ",";
            }

            ret = stream.str();

            if (!ret.empty())
                ret.pop_back();

            return ret + "\n";
        }

        /**
         * @brief Ensures that all fields are present for a given row, by adding
         * empty strings if the property is missing from the row map.
         * 
         * @param row a map of strings, constructed from the node and edge keys.
         * @param isEdge if set to true, generates the header for the edges CSV
         * required by Neo4j
         * 
         * @return std::string 
         */
        inline std::string finalizeRow(std::map<std::string, std::string> row,
                                       bool isEdge = false)
        {
            std::stringstream stream;
            std::string ret;

            // Insert does not overwrite existing keys.
            for (std::string key : (isEdge ? edge_keys : node_keys))
            {
                row.insert({key, ""});
            }

            for (std::map<std::string, std::string>::iterator col = row.begin();
                 col != row.end(); ++col)
            {
                stream << toField(&col->second);
            }

            ret = stream.str();

            if (!ret.empty())
                ret.pop_back();

            return ret + "\n"; 
        }

        /**
         * @brief Generates a CSV row for a SVFG type node.
         * 
         * @param node a pointer to a SVFG node.
         * @return std::string 
         */
        inline std::string SVFGNodeToRow(SVFGNode *node)
        {
            std::map<std::string, std::string> row;

            uint kind = node->getNodeKind();

            switch (kind)
            {

            // Handle statement SVFG nodes, we need to check every type
            // individually, as the StmtVFGNode class is an agglomerative type
            // that checks against all cases below instead of being it's own
            // type.

            case SVFGNode::VFGNodeK::Addr:
            {
                AddrSVFGNode* naddr = SVFUtil::dyn_cast<AddrSVFGNode>(node);

                row.insert({K_FNAME, getSVFGFunctionName(naddr)});
                row.insert({K_FHASH, getSVFGFunctionHash(naddr)});
                row.insert({K_SRCVA, std::to_string(naddr->getPAGSrcNodeID())});
                row.insert({K_DSTVA, std::to_string(naddr->getPAGDstNodeID())});
                row.insert({K_CALLS, getCallSite(naddr)});
                row.insert({K_CALLN, getCallSiteName(naddr)});

                break;
            }
            
            case SVFGNode::VFGNodeK::Copy:
            {
                CopySVFGNode* ncopy = SVFUtil::dyn_cast<CopySVFGNode>(node);

                row.insert({K_FNAME, getSVFGFunctionName(ncopy)});
                row.insert({K_FHASH, getSVFGFunctionHash(ncopy)});
                row.insert({K_SRCVA, std::to_string(ncopy->getPAGSrcNodeID())});
                row.insert({K_DSTVA, std::to_string(ncopy->getPAGDstNodeID())});
                row.insert({K_CALLS, getCallSite(ncopy)});
                row.insert({K_CALLN, getCallSiteName(ncopy)});

                break;
            }
            
            case SVFGNode::VFGNodeK::Load:
            {
                LoadSVFGNode* nload = SVFUtil::dyn_cast<LoadSVFGNode>(node);

                row.insert({K_FNAME, getSVFGFunctionName(nload)});
                row.insert({K_FHASH, getSVFGFunctionHash(nload)});
                row.insert({K_SRCVA, std::to_string(nload->getPAGSrcNodeID())});
                row.insert({K_DSTVA, std::to_string(nload->getPAGDstNodeID())});
                row.insert({K_CALLS, getCallSite(nload)});
                row.insert({K_CALLN, getCallSiteName(nload)});

                break;
            }

            case SVFGNode::VFGNodeK::Store:
            {
                StoreSVFGNode* nstore = SVFUtil::dyn_cast<StoreSVFGNode>(node);

                row.insert({K_FNAME, getSVFGFunctionName(nstore)});
                row.insert({K_FHASH, getSVFGFunctionHash(nstore)});
                row.insert({K_SRCVA, std::to_string(nstore->getPAGSrcNodeID())});
                row.insert({K_DSTVA, std::to_string(nstore->getPAGDstNodeID())});
                row.insert({K_CALLS, getCallSite(nstore)});
                row.insert({K_CALLN, getCallSiteName(nstore)});

                break;
            }

            case SVFGNode::VFGNodeK::Gep:
            {
                GepSVFGNode* ngep = SVFUtil::dyn_cast<GepSVFGNode>(node);

                row.insert({K_FNAME, getSVFGFunctionName(ngep)});
                row.insert({K_FHASH, getSVFGFunctionHash(ngep)});
                row.insert({K_SRCVA, std::to_string(ngep->getPAGSrcNodeID())});
                row.insert({K_DSTVA, std::to_string(ngep->getPAGDstNodeID())});
                row.insert({K_CALLS, getCallSite(ngep)});
                row.insert({K_CALLN, getCallSiteName(ngep)});

                break;
            }

            case SVFGNode::VFGNodeK::FPIN:
            {
                FormalINSVFGNode *nfpin
                    = SVFUtil::dyn_cast<FormalINSVFGNode>(node);
                row.insert({K_MRNID, getMRID(nfpin)});
                row.insert({K_MSSAV, getSSA(nfpin)});
                row.insert({K_PTSET, getPTS(nfpin)});
                row.insert({K_CALLS, getCallSite(nfpin)});
                row.insert({K_CALLN, getCallSiteName(nfpin)});

                break;
            }

            case SVFGNode::VFGNodeK::FPOUT:
            {
                FormalOUTSVFGNode *nfpout
                    = SVFUtil::dyn_cast<FormalOUTSVFGNode>(node);
                row.insert({K_MRNID, getMRID(nfpout)});
                row.insert({K_MSSAV, getSSA(nfpout)});
                row.insert({K_PTSET, getPTS(nfpout)});

                break;
            }

            case SVFGNode::VFGNodeK::APIN: 
            {
                ActualINSVFGNode *napin
                    = SVFUtil::dyn_cast<ActualINSVFGNode>(node);

                row.insert({K_MRNID, getMRID(napin)});
                row.insert({K_MSSAV, getSSA(napin)});
                row.insert({K_PTSET, getPTS(napin)});

                if (const SVFFunction *callee
                    = SVFUtil::getCallee(napin->getCallSite()->getCallSite()))
                {
                    row.insert({K_FNAME, callee->getName()});
                    row.insert({K_FHASH, getHash(callee)});
                }

                // ActualINSVFGNodes have no source location, but their
                // callsites do.
                if (const Value *cs
                    = SVFUtil::dyn_cast<Value>(
                        napin->getCallSite()->getCallSite()))
                {
                    row.insert({K_SRCLC, SVFUtil::getSourceLoc(cs)});
                }

                break;
            }

            case SVFGNode::VFGNodeK::APOUT: 
            {
                ActualOUTSVFGNode *napout
                    = SVFUtil::dyn_cast<ActualOUTSVFGNode>(node);

                row.insert({K_MRNID, getMRID(napout)});
                row.insert({K_MSSAV, getSSA(napout)});
                row.insert({K_PTSET, getPTS(napout)});
                row.insert({K_CALLS, getCallSite(napout)});
                row.insert({K_CALLN, getCallSiteName(napout)});

                if (const SVFFunction *callee
                    = SVFUtil::getCallee(napout->getCallSite()->getCallSite()))
                {
                    row.insert({K_FNAME, callee->getName()});
                    row.insert({K_FHASH, getHash(callee)});
                }

                // ActualOutSVFGNodes have no source location, but their
                // callsites do.
                if (const Value *cs
                    = SVFUtil::dyn_cast<Value>(
                        napout->getCallSite()->getCallSite()))
                {
                    row.insert({K_SRCLC, SVFUtil::getSourceLoc(cs)});
                }

                break;
            }

            case SVFGNode::VFGNodeK::AParm: 
            {
                ActualParmSVFGNode *naparm
                    = SVFUtil::dyn_cast<ActualParmSVFGNode>(node);

                row.insert({K_CALLS, getCallSite(naparm)});
                row.insert({K_CALLN, getCallSiteName(naparm)});

                if (const SVFFunction *callee
                    = SVFUtil::getCallee(naparm->getCallSite()->getCallSite()))
                {
                    row.insert({K_FNAME, callee->getName()});
                    row.insert({K_FHASH, getHash(callee)});
                }

                break;
            }

            case SVFGNode::VFGNodeK::ARet:
            {
                ActualRetSVFGNode *naret
                    = SVFUtil::dyn_cast<ActualRetSVFGNode>(node);

                row.insert({K_CALLS, getCallSite(naret)});
                row.insert({K_CALLN, getCallSiteName(naret)});

                if (const SVFFunction *callee
                    = SVFUtil::getCallee(naret->getCallSite()->getCallSite()))
                {
                    row.insert({K_FNAME, callee->getName()});
                    row.insert({K_FHASH, getHash(callee)});
                }

                break;
            }

            case SVFGNode::VFGNodeK::MPhi: 
            {
                MSSAPHISVFGNode *nmphi
                    = SVFUtil::dyn_cast<MSSAPHISVFGNode>(node);
                    
                row.insert({K_MRNID, getMRID(nmphi)});
                row.insert({K_PTSET, getPTS(nmphi)});

                break;
            }

            case SVFGNode::VFGNodeK::MIntraPhi: 
            {
                MSSAPHISVFGNode *nmintraphi
                    = SVFUtil::dyn_cast<MSSAPHISVFGNode>(node);
                    
                row.insert({K_MRNID, getMRID(nmintraphi)});
                row.insert({K_PTSET, getPTS(nmintraphi)});

                break;
            }

            case SVFGNode::VFGNodeK::MInterPhi: 
            {
                MSSAPHISVFGNode *nminterphi
                    = SVFUtil::dyn_cast<MSSAPHISVFGNode>(node);

                row.insert({K_MRNID, getMRID(nminterphi)});
                row.insert({K_PTSET, getPTS(nminterphi)});

                break;
            }
            
            default: {
                break;
            }

            }

            // Handle everything else for all other nodes.

            if (const Value *val = node->getValue())
            {
                if (const Instruction *inst
                    = SVFUtil::dyn_cast<Instruction>(val))
                {
                    std::stringstream opcode;
                    opcode << std::to_string(inst->getOpcode());
                    row.insert({K_IROPC, opcode.str()});

                    std::string inst_hash
                        = std::to_string((std::uintptr_t)inst);
                    row.insert({K_IHASH, inst_hash});

                    // Add full instruction to map.
                    std::string full_inst;
                    raw_string_ostream stream(full_inst);
                    inst->print(stream);
                    row.insert({K_INSTR, stream.str()});
                }

                // Handle source location.
                row.insert({K_SRCLC, SVFUtil::getSourceLoc(val)});

                // Handle value type
                std::string type_name;
                raw_string_ostream stream(type_name);
                val->getType()->print(stream);
                row.insert({K_VTYPE, stream.str()});
            }

            // Handle type of node.
            row.insert({K_NTYPE, std::to_string(node->getNodeKind())});
            row.insert({K_LABEL, getSVFGNodeType(node)});
            row.insert({K_NNAME, getSVFGNodeType(node)});

            // Handle hash of node.
            row.insert({K_NHASH, getHash(node)});

            // Handle associated function.
            if (const SVFFunction *fun = node->getFun())
            {
                row.insert({K_FNAME, fun->getName()});
                row.insert({K_FHASH, getHash(fun)});
            }

            // Insert hash of ICFG node
            row.insert({K_ICFGN, getHash(node->getICFGNode())});

            row.insert({K_GTYPE, "SVFG"});

            return finalizeRow(row);
        }

        /**
         * @brief Generates a CSV row for a given SVFG type edge.
         * 
         * @param edge a pointer to a SVFG edge.
         * @return std::string 
         */
        inline std::string SVFGEdgeToRow(SVFGEdge *edge)
        {
            std::map<std::string, std::string> row;

            row.insert({K_SEDGE, getHash(edge->getSrcNode())});
            row.insert({K_EEDGE, getHash(edge->getDstNode())});
            row.insert({K_EHASH, getHash(edge)});
            row.insert({K_ETYPE, getSVFGEdgeType(edge)});
            row.insert({K_EKIND, std::to_string(edge->getEdgeKind())});

            row.insert({K_GTYPE, "SVFG"});

            return finalizeRow(row, /*isEdge*/ true);
        }

        /**
         * @brief Generates a CSV row for a given call graph type edge.
         * 
         * @param node a pointer to a PTACAllGraphNode
         * @return std::string 
         */
        inline std::string PTACGNodeToRow(PTACallGraphNode *node)
        {
            std::map<std::string, std::string> row;

            row.insert({K_GTYPE, "PTACG"});
            row.insert({K_FNAME, node->getFunction()->getName()});
            row.insert({K_FHASH, getHash(node->getFunction())});
            row.insert({K_LABEL, "PTACallGraphNode"});
            row.insert({K_NNAME, "PTACallGraphNode"});
            row.insert({K_NTYPE, std::to_string(node->getNodeKind())});
            row.insert({K_NHASH, getHash(node)});
            row.insert({K_SRCLC, SVFUtil::getSourceLoc(
                                     node->getFunction()->getLLVMFun())});

            return finalizeRow(row);
        }

        /**
         * @brief Generates a CSV row for a given call graph edge.
         * 
         * @param edge a pointer to a call graph edge.
         * @return std::string 
         */
        inline std::string PTACGEdgeToRow(PTACallGraphEdge *edge)
        {
            std::map<std::string, std::string> row;

            row.insert({K_SEDGE, getHash(edge->getSrcNode())});
            row.insert({K_EEDGE, getHash(edge->getDstNode())});
            row.insert({K_ECALL, getHash(edge)});
            row.insert({K_ETYPE, "PTACallGraphEdge"});
            row.insert({K_EKIND, std::to_string(edge->getEdgeKind())});

            row.insert({K_GTYPE, "PTACG"});

            return finalizeRow(row, /*isEdge*/ true);
        }

        /**
         * @brief Generates a CSV row for a given CFG node.
         * 
         * @param node a pointer to a CFG node.
         * @return std::string 
         */
        inline std::string ICFGNodeToRow(ICFGNode *node)
        {
            std::map<std::string, std::string> row;
            uint kind = node->getNodeKind();

            switch (kind)
            {

            case ICFGNode::ICFGNodeK::FunCallBlock:
            {
                CallICFGNode *cn = SVFUtil::dyn_cast<CallICFGNode>(node);
                if (const SVFFunction *callee
                    = SVFUtil::getCallee(cn->getCallSite()))
                {
                    row.insert({K_FNAME, callee->getName()});
                    row.insert({K_FHASH, getHash(callee)});
                }

                std::string cs_name(
                    cn->getCallSite()->getFunction()->getName());

                row.insert({K_CALLS, getHash(cn->getCallSite())});
                row.insert({K_CALLN, cs_name});
                row.insert({K_SRCLC, SVFUtil::getSourceLoc(
                    node->getFun()->getLLVMFun())});

                break;
            }

            case ICFGNode::ICFGNodeK::FunRetBlock:
            {
                RetICFGNode *cn = SVFUtil::dyn_cast<RetICFGNode>(node);

                if (const SVFFunction *callee
                    = SVFUtil::getCallee(cn->getCallSite()))
                {
                    row.insert({K_FNAME, callee->getName()});
                    row.insert({K_FHASH, getHash(callee)});
                }

                std::string cs_name(
                    cn->getCallSite()->getFunction()->getName());

                row.insert({K_CALLS, getHash(cn->getCallSite())});
                row.insert({K_CALLN, cs_name});
                row.insert({K_SRCLC, SVFUtil::getSourceLoc(
                    node->getFun()->getLLVMFun())});

                break;
            }

            case ICFGNode::ICFGNodeK::FunEntryBlock: 
            {
                FunEntryICFGNode *cn
                    = SVFUtil::dyn_cast<FunEntryICFGNode>(node);

                row.insert({K_FNAME, cn->getFun()->getName()});
                row.insert({K_FHASH, getHash(cn->getFun())});
                row.insert({K_SRCLC, SVFUtil::getSourceLoc(
                    node->getFun()->getLLVMFun())});

                break;
            }

            case ICFGNode::ICFGNodeK::FunExitBlock: 
            {
                FunExitICFGNode *cn
                    = SVFUtil::dyn_cast<FunExitICFGNode>(node);

                row.insert({K_FNAME, cn->getFun()->getName()});
                row.insert({K_FHASH, getHash(cn->getFun())});
                row.insert({K_SRCLC, SVFUtil::getSourceLoc(
                     node->getFun()->getLLVMFun())});

                break;
            }

            case ICFGNode::ICFGNodeK::IntraBlock:
            {
                IntraICFGNode *in
                    = SVFUtil::dyn_cast<IntraICFGNode>(node);

                const Instruction* inst = in->getInst();

                if (inst)
                {
                    std::stringstream opcode;
                    opcode << std::to_string(inst->getOpcode());
                    row.insert({K_IROPC, opcode.str()});

                    std::string inst_hash
                        = std::to_string((std::uintptr_t)inst);
                    row.insert({K_IHASH, inst_hash});

                    // Add full instruction to map.
                    std::string full_inst;
                    raw_string_ostream stream(full_inst);
                    inst->print(stream);
                    row.insert({K_INSTR, stream.str()});

                    // Handle source location.
                    row.insert({K_SRCLC, SVFUtil::getSourceLoc(inst)});
                }

                row.insert({K_FNAME, in->getFun()->getName()});
                row.insert({K_FHASH, getHash(in->getFun())});

                break;
            }

            default: {
                break;
            }

            }

            row.insert({K_LABEL, getICFGNodeType(node)});
            row.insert({K_NNAME, getICFGNodeType(node)});
            row.insert({K_NTYPE, std::to_string(node->getNodeKind())});
            row.insert({K_CFGID, std::to_string(node->getId())});
            row.insert({K_NHASH, getHash(node)});

            row.insert({K_GTYPE, "ICFG"});

            return finalizeRow(row);
        }

        /**
         * @brief Generates a CSV row for a CFG edge.
         * 
         * @param edge a pointer to a CFG edge.
         * @return std::string 
         */
        inline std::string ICFGEdgeToRow(ICFGEdge *edge)
        {
            std::map<std::string, std::string> row;

            row.insert({K_SEDGE, getHash(edge->getSrcNode())});
            row.insert({K_EEDGE, getHash(edge->getDstNode())});
            row.insert({K_EHASH, getHash(edge)});
            row.insert({K_ETYPE, "ICFGEdge"});
            row.insert({K_EKIND, std::to_string(edge->getEdgeKind())});

            row.insert({K_GTYPE, "ICFG"});
            return finalizeRow(row, /*isEdge*/ true);
        }

        /**
         * @brief Generates a CSV row for a TLDG node.
         * 
         * @param node a pointer to a CSV node.
         * @return std::string 
         */
        inline std::string TLDGNodeToRow(const Value* node)
        {
            std::map<std::string, std::string> row;

            row.insert({K_NHASH, getHash(node)});

            if (const Instruction* I = SVFUtil::dyn_cast<Instruction>(node))
            {
                if (I)
                {
                    std::string full_inst;
                    raw_string_ostream stream(full_inst);
                    I->print(stream);

                    row.insert({K_INSTR, stream.str()});
                    row.insert({K_IHASH, getHash(I)});

                    std::stringstream opcode;
                    opcode << std::to_string(I->getOpcode());
                    row.insert({K_IROPC, opcode.str()});

                    if (I->use_empty())
                    {
                        row.insert({K_DTERM, "true"});
                    }
                    else
                    {
                        row.insert({K_DTERM, "false"});
                    }
                }

                std::string fname = "";
                std::string fhash = "";
                if (const Function *fun = I->getFunction())
                {
                    fname = fun->getName().str();
                    fhash = getHash(fun);
                }

                row.insert({K_NNAME, "InstTLDepNode"});
                row.insert({K_LABEL, "InstTLDepNode"});
                row.insert({K_FNAME, fname});
                row.insert({K_FHASH, fhash});
                row.insert({K_SRCLC, SVFUtil::getSourceLoc(I)});
            }

            else
            {
                if (node)
                {
                    std::string full_val;
                    raw_string_ostream stream(full_val);
                    node->print(stream);

                    row.insert({K_INSTR, stream.str()});
                }

                row.insert({K_NNAME, "ValTLDepNode"});
                row.insert({K_LABEL, "ValTLDepNode"});
                row.insert({K_SRCLC, SVFUtil::getSourceLoc(node)});
            }

            row.insert({K_GTYPE, "TLDEP"});

            return finalizeRow(row);
        }

        /**
         * @brief Generates a CSV row for a TLDGEdge.
         * 
         * @param edge a pointer to CSV edge.
         * @return std::string 
         */
        inline std::string TLDGEdgeToRow(TLDGEdge* edge)
        {
            std::map<std::string, std::string> row;

            row.insert({K_SEDGE, getHash(edge->first)});
            row.insert({K_EEDGE, getHash(edge->second)});
            row.insert({K_ETYPE, "UsedIn"});
            row.insert({K_EHASH, getHash(edge)});

            row.insert({K_GTYPE, "TLDEP"});

            return finalizeRow(row, /*isEdge=*/true);
        }

        /**
         * @brief Writes the final CSV files to disk: One for the nodes and
         * another one for the edges, hence why the file type suffix should be
         * ommitted for the "file" parameter.
         * 
         * @param file The file name without the file type suffix.
         * @param rows The map of rows that was finalized prior, using the
         * "finalizeRow()" function.
         */
        void WriteCSV(const std::string file, std::vector<std::string> rows);

        /**
         * @brief The entry point of the CSV writer. It reads the supplied
         * graphs and generates two CSV files: one for the nodes and one for the
         * edges, as expected by the neo4j-admin tool. The file name that is
         * supplied through the "file" parameter, must not have a file type
         * suffix.
         * 
         * @param file The file name without the file type suffix.
         * @param graph The svfg that the ptacg and icfg are extracted from.
         * @param tldg The top-level dependency graph.
         */
        void WriteGraphToCSV(const std::string file, SVFG *graph,
            TLDG *tldg, ICFG* icfg, PTACallGraph* ptacg);

    }

}

#endif /* CSVPRINTER_H_ */