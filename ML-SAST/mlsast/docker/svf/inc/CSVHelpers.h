#ifndef CSVHELPERS_H_
#define CSVHELPERS_H_

#include <regex>

#include "Graphs/SVFG.h"
#include "Graphs/VFGNode.h"
#include "Graphs/PTACallGraph.h"
#include "TLDG.h"
#include "Util/SVFUtil.h"

namespace SVF
{
    /**
     * @brief Escapes CSV fields.
     * 
     * @param value The string to be escaped.
     * @return std::string 
     */
    inline std::string toField(std::string* value)
    {
        // bool modified = false;

        if (!value)
            return "";

        for (char& c : *value)
        {
            if (c == '\"' || c == '\''|| c == ',' || c == '\n' || c == '\r')
            {
                c = '_';
                // llvm::errs() << "Caught offending character: " << c << "\n";
                // modified = true;
            }

            // if (modified)
            // {
            //     llvm::errs() << *value << "\n";
            // }
        }

        return "\"" + *value + "\",";
    }

    /**
     * @brief Retrieves the sub type of a svfg node.
     * 
     * @param node a svfg node pointer.
     * @return std::string 
     */
    inline std::string getSVFGNodeType(SVFGNode *node)
    {
        if (StmtSVFGNode *stmtNode = SVFUtil::dyn_cast<StmtSVFGNode>(node))
        {
            const PAGEdge *edge = stmtNode->getPAGEdge();
            if (SVFUtil::isa<AddrStmt>(edge))
            {
                return "AddrStmt";
            }
            else if (SVFUtil::isa<CopyStmt>(edge))
            {
                return "CopyStmt";
            }
            else if (SVFUtil::isa<RetPE>(edge))
            {
                return "RetPE";
            }
            else if (SVFUtil::isa<GepStmt>(edge))
            {
                return "GepStmt";
            }
            else if (SVFUtil::isa<StoreStmt>(edge))
            {
                return "StoreStmt";
            }
            else if (SVFUtil::isa<LoadStmt>(edge))
            {
                return "LoadStmt";
            }

            return "Unkown_StmtNode_Type";
        }
        else if (SVFUtil::isa<MSSAPHISVFGNode>(node))
        {
            return "MSSAPHISVFGNode";
        }
        else if (SVFUtil::isa<PHISVFGNode>(node))
        {
            return "PHISVFGNode";
        }
        else if (SVFUtil::isa<NullPtrSVFGNode>(node))
        {
            return "NullPtrSVFGNode";
        }
        else if (SVFUtil::isa<FormalINSVFGNode>(node))
        {
            return "FormalINSVFGNode";
        }
        else if (SVFUtil::isa<FormalOUTSVFGNode>(node))
        {
            return "FormalOUTSVFGNode";
        }
        else if (SVFUtil::isa<FormalParmSVFGNode>(node))
        {
            return "FormalParmSVFGNode";
        }
        else if (SVFUtil::isa<ActualINSVFGNode>(node))
        {
            return "ActualINSVFGNode";
        }
        else if (SVFUtil::isa<ActualOUTSVFGNode>(node))
        {
            return "ActualOUTSVFGNode";
        }
        else if (SVFUtil::isa<ActualParmSVFGNode>(node))
        {
            return "ActualParmSVFGNode";
        }
        else if (SVFUtil::isa<ActualRetSVFGNode>(node))
        {
            return "ActualRetSVFGNode";
        }
        else if (SVFUtil::isa<FormalRetSVFGNode>(node))
        {
            return "FormalRetSVFGNode";
        }
        else if (SVFUtil::isa<BinaryOPVFGNode>(node))
        {
            return "BinaryOPVFGNode";
        }
        else if (SVFUtil::isa<CmpVFGNode>(node))
        {
            return "CmpVFGNode";
        }
        else if (SVFUtil::isa<UnaryOPVFGNode>(node))
        {
            return "UnaryOPVFGNode";
        }
        else if (SVFUtil::isa<GenericNode<VFGNode, VFGEdge>>(node))
        {
            return "ICFGNode";
        }

        return "Unkown_Node_Type";
    }

    /**
     * @brief Retrieves the sub type of a svfg edge.
     * 
     * @param edge a svfg edge pointer.
     * @return std::string 
     */
    inline std::string getSVFGEdgeType(SVFGEdge *edge)
    {
        if (SVFUtil::isa<DirectSVFGEdge>(edge))
        {
            if (SVFUtil::isa<CallDirSVFGEdge>(edge))
            {
                return "CallDirSVFGEdge";
            }
            else if (SVFUtil::isa<RetDirSVFGEdge>(edge))
            {
                return "RetDirSVFGEdge";
            }

            return "DirectSVFGEdge";
        }
        else if (SVFUtil::isa<IndirectSVFGEdge>(edge))
        {
            if (SVFUtil::isa<CallIndSVFGEdge>(edge))
            {
                return "CallIndSVFGEdge";
            }
            else if (SVFUtil::isa<RetIndSVFGEdge>(edge))
            {
                return "RetIndSVFGEdge";
            }

            return "IndirectSVFGEdge";
        }

        return "";
    }

    /**
     * @brief Retrieves the sub type of an icfg node.
     * 
     * @param node a icfg node pointer.
     * @return std::string 
     */
    inline std::string getICFGNodeType(ICFGNode *node)
    {
        if (SVFUtil::isa<GlobalICFGNode>(node))
        {
            return "GlobalICFGNode";
        }
        else if (SVFUtil::isa<IntraICFGNode>(node))
        {
            return "IntraICFGNode";
        }
        else if (SVFUtil::isa<FunEntryICFGNode>(node))
        {
            return "FunEntryICFGNode";
        }
        else if (SVFUtil::isa<FunExitICFGNode>(node))
        {
            return "FunExitICFGNode";
        }
        else if (SVFUtil::isa<CallICFGNode>(node))
        {
            return "CallICFGNode";
        }
        else if (SVFUtil::isa<RetICFGNode>(node))
        {
            return "RetICFGNode";
        }
        else if (SVFUtil::isa<ICFGNode>(node))
        {
            return "ICFGNode";
        }

        return "Unknown ICFGNode";
    }

    /**
     * @brief Retrieves the sub type of an icfg edge.
     * 
     * @param edge a icfg edge pointer.
     * @return std::string 
     */
    inline std::string getICFGEdgeType(ICFGEdge *edge)
    {
        if (SVFUtil::isa<IntraCFGEdge>(edge))
        {
            return "IntraCFGEdge";
        }
        else if (SVFUtil::isa<CallCFGEdge>(edge))
        {
            return "CallCFGEdge";
        }
        else if (SVFUtil::isa<RetCFGEdge>(edge))
        {
            return "RetCFGEdge";
        }
        else if (SVFUtil::isa<ICFGEdge>(edge))
        {
            return "ICFGEdge";
        }

        return "Unkown ICFGEdge";
    }

    /**
     * @brief Retrieves the hash value (i.e. the address in memory) of a node or
     * edge (any pointer really).
     * 
     * @param pointer The pointer to an object in memory.
     * @return std::string 
     */
    inline std::string getHash(const void *pointer)
    {
        return std::to_string((std::uintptr_t)pointer);
    }

    /**
     * @brief Retrieves the memory region id of an mr-type svfg node.
     * 
     * @param node a svfg node. 
     * @return std::string 
     */
    inline std::string getMRID(const SVFGNode *node)
    {
        std::string mrid;
        raw_string_ostream stream(mrid);

        if (const FormalINSVFGNode *actualout = SVFUtil::dyn_cast<FormalINSVFGNode>(node))
        {
            stream << actualout->getMRVer()->getMR()->getMRID();
        }

        else if (const FormalOUTSVFGNode *actualout = SVFUtil::dyn_cast<FormalOUTSVFGNode>(node))
        {
            stream << actualout->getMRVer()->getMR()->getMRID();
        }

        else if (const ActualINSVFGNode *actualout = SVFUtil::dyn_cast<ActualINSVFGNode>(node))
        {
            stream << actualout->getMRVer()->getMR()->getMRID();
        }

        else if (const ActualOUTSVFGNode *actualout = SVFUtil::dyn_cast<ActualOUTSVFGNode>(node))
        {
            stream << actualout->getMRVer()->getMR()->getMRID();
        }

        else if (const MSSAPHISVFGNode *casted = SVFUtil::dyn_cast<MSSAPHISVFGNode>(node))
        {
            stream << casted->getResVer()->getMR()->getMRID();
        }

        return stream.str();
    }

    /**
     * @brief retreives the SSA version of a mr-type svfg node.
     * 
     * @param node a svfg node.
     * @return std::string 
     */
    inline std::string getSSA(const SVFGNode *node)
    {
        std::string mrid;
        raw_string_ostream stream(mrid);

        if (const FormalINSVFGNode *casted = SVFUtil::dyn_cast<FormalINSVFGNode>(node))
        {
            stream << casted->getMRVer()->getSSAVersion();
        }

        else if (const FormalOUTSVFGNode *casted = SVFUtil::dyn_cast<FormalOUTSVFGNode>(node))
        {
            stream << casted->getMRVer()->getSSAVersion();
        }

        else if (const ActualINSVFGNode *casted = SVFUtil::dyn_cast<ActualINSVFGNode>(node))
        {
            stream << casted->getMRVer()->getSSAVersion();
        }

        else if (const ActualOUTSVFGNode *casted = SVFUtil::dyn_cast<ActualOUTSVFGNode>(node))
        {
            stream << casted->getMRVer()->getSSAVersion();
        }

        else if (const MSSAPHISVFGNode *casted = SVFUtil::dyn_cast<MSSAPHISVFGNode>(node))
        {
            stream << std::to_string(casted->getResVer()->getSSAVersion());
        }

        return stream.str();
    }

    /**
     * @brief Retrieves the points-to set of a svfg node.
     * 
     * @param node a svfg node.
     * @return std::string 
     */
    inline std::string getPTS(const SVFGNode *node)
    {
        //std::smatch sm;
        std::string ssa;
        raw_string_ostream stream(ssa);

        if (const FormalINSVFGNode *formalin
            = SVFUtil::dyn_cast<FormalINSVFGNode>(node))
        {
            stream << formalin->getMRVer()->getMR()->dumpStr();
        }

        else if (const FormalOUTSVFGNode *formalout
            = SVFUtil::dyn_cast<FormalOUTSVFGNode>(node))
        {
            stream << formalout->getMRVer()->getMR()->dumpStr();
        }

        else if (const ActualINSVFGNode *actualin
            = SVFUtil::dyn_cast<ActualINSVFGNode>(node))
        {
            stream << actualin->getMRVer()->getMR()->dumpStr();
        }

        else if (const ActualOUTSVFGNode *actualout
            = SVFUtil::dyn_cast<ActualOUTSVFGNode>(node))
        {
            stream << actualout->getMRVer()->getMR()->dumpStr();
        }

        else if (const MSSAPHISVFGNode *mssaphi
            = SVFUtil::dyn_cast<MSSAPHISVFGNode>(node))
        {
            stream << mssaphi->getResVer()->getMR()->dumpStr();
        }

        ssa = stream.str();

        // std::string res = "[";

        // auto ssa_begin
        //     = std::sregex_iterator(ssa.begin(), ssa.end(), re_ptslist);
        // auto ssa_end = std::sregex_iterator();
 
        // std::sregex_iterator i = ssa_begin;
        // while (i != ssa_end) {
        //     std::smatch match = *i;                                                 
        //     std::string match_str = 
        //     res += match.str();

        //     std::advance(i, 1);

        //     if (i != ssa_end) {
        //         res += ", ";
        //     }
        // }   
        

        // res += "]";
        
        // return res;

        return ssa;
    }

    /**
     * @brief Generates a single hash value that is made up of the MRID of node
     * and it's version. The hash fits into a single unsigned long long type
     * integer.
     * 
     * THIS FUNCTION IS LARGELY UNTESTED, COLLISIONS ARE LIKELY!
     * 
     * USE WITH CARE!
     * 
     * @param node a mr-kind svfg node pointer.
     * @return std::string 
     */
    inline std::string getMemHash(const SVFGNode *node)
    {
        const MemRegion *reg = nullptr;
        NodeID ver = 0;
        const NodeBS *pts = nullptr;

        if (const FormalINSVFGNode *casted = SVFUtil::dyn_cast<FormalINSVFGNode>(node))
        {
            reg = casted->getMRVer()->getMR();
            ver = casted->getMRVer()->getSSAVersion();
            pts = &reg->getPointsTo();
        }

        else if (const FormalOUTSVFGNode *casted = SVFUtil::dyn_cast<FormalOUTSVFGNode>(node))
        {
            reg = casted->getMRVer()->getMR();
            ver = casted->getMRVer()->getSSAVersion();
            pts = &reg->getPointsTo();
        }

        else if (const ActualINSVFGNode *casted = SVFUtil::dyn_cast<ActualINSVFGNode>(node))
        {
            reg = casted->getMRVer()->getMR();
            ver = casted->getMRVer()->getSSAVersion();
            pts = &reg->getPointsTo();
        }

        else if (const ActualOUTSVFGNode *casted = SVFUtil::dyn_cast<ActualOUTSVFGNode>(node))
        {
            reg = casted->getMRVer()->getMR();
            ver = casted->getMRVer()->getSSAVersion();
            pts = &reg->getPointsTo();
        }

        else if (const MSSAPHISVFGNode *casted = SVFUtil::dyn_cast<MSSAPHISVFGNode>(node))
        {
            reg = casted->getResVer()->getMR();
            ver = casted->getResVer()->getSSAVersion();
            pts = &reg->getPointsTo();
        }

        unsigned long long int sum = 0;

        for (NodeBS::iterator ii = pts->begin(), ie = pts->end();
             ii != ie; ii++)
        {
            sum += (unsigned long long int)*ii;
        }

        sum *= 100000;
        sum += reg->getMRID() * 1000;
        sum += ver;

        return std::to_string(sum);
    }

    /**
     * @brief Retrieve the name of the call site of a svfg-kind node.
     * 
     * @param node pointer to a svfg node.
     * @return std::string 
     */
    inline std::string getCallSiteName(SVFGNode *node)
    {
        std::string name;
        raw_string_ostream stream(name);

        if (const ActualParmSVFGNode *actualparm = SVFUtil::dyn_cast<ActualParmSVFGNode>(node))
        {
            stream << actualparm->getCallSite()->getFun()->getName();
        }

        else if (const ActualRetSVFGNode *actualret = SVFUtil::dyn_cast<ActualRetSVFGNode>(node))
        {
            stream << actualret->getCallSite()->getFun()->getName();
        }

        else if (const ActualINSVFGNode *actualin = SVFUtil::dyn_cast<ActualINSVFGNode>(node))
        {
            stream << actualin->getCallSite()->getFun()->getName();
        }

        else if (const ActualOUTSVFGNode *actualout = SVFUtil::dyn_cast<ActualOUTSVFGNode>(node))
        {
            stream << actualout->getCallSite()->getFun()->getName();
        }

        return stream.str();
    }

    /**
     * @brief Get the call site of a svfg node.
     * 
     * @param node pointer to a svfg node.
     * @return std::string 
     */
    inline std::string getCallSite(SVFGNode *node)
    {
        std::string cs;
        raw_string_ostream stream(cs);

        if (const ActualParmSVFGNode *actualparm = SVFUtil::dyn_cast<ActualParmSVFGNode>(node))
        {
            stream << getHash(actualparm->getCallSite());
        }

        else if (const ActualRetSVFGNode *actualret = SVFUtil::dyn_cast<ActualRetSVFGNode>(node))
        {
            stream << getHash(actualret->getCallSite());
        }

        else if (const ActualINSVFGNode *actualin = SVFUtil::dyn_cast<ActualINSVFGNode>(node))
        {
            stream << getHash(actualin->getCallSite());
        }

        else if (const ActualOUTSVFGNode *actualout = SVFUtil::dyn_cast<ActualOUTSVFGNode>(node))
        {
            stream << getHash(actualout->getCallSite());
        }

        return stream.str();
    }

    inline std::string getSVFGFunctionName(StmtSVFGNode *node) {
        if (const PAGEdge *edge = node->getPAGEdge())
        {
            if (const AddrStmt *ad = SVFUtil::dyn_cast<AddrStmt>(edge))
            {
                if (const CallICFGNode *call
                    = SVFUtil::dyn_cast<CallICFGNode>(
                        ad->getICFGNode()))
                {
                    if (const SVFFunction *callee 
                        = SVFUtil::getCallee(call->getCallSite()))
                    {
                        return callee->getName();
                    }
                }
            }
        }

        return "";
    }

    inline std::string getSVFGFunctionHash(StmtSVFGNode *node) {
        if (const PAGEdge *edge = node->getPAGEdge())
        {
            if (const AddrStmt *ad = SVFUtil::dyn_cast<AddrStmt>(edge))
            {
                if (const CallICFGNode *call
                    = SVFUtil::dyn_cast<CallICFGNode>(
                        ad->getICFGNode()))
                {
                    if (const SVFFunction *callee 
                        = SVFUtil::getCallee(call->getCallSite()))
                    {
                        return getHash(callee);
                    }
                }
            }
        }

        return "";
    }
}

#endif // !CSVHELPERS_H_
