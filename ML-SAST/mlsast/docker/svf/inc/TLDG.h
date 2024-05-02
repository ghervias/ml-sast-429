#ifndef TLDEPBUILDER_H_
#define TLDEPBUILDER_H_

#include "MemoryModel/SVFIR.h"
#include "Util/SVFUtil.h"
#include "Util/WorkList.h"
#include "llvm/IR/InstIterator.h"
#include "llvm/IR/Instruction.h"
#include "llvm/IR/User.h"
#include "llvm/IR/Value.h"
#include "llvm/ADT/DenseSet.h"

#include <set>

namespace SVF
{
    class SVFModule;
    
    // Edges are stored as simple pairs of IR-instructions, but we only want
    // unique edges, so a custom comperator must be implemented as well.
    typedef std::pair<const llvm::Value*, const llvm::Value*> TLDGEdge;

    struct TLDGEdgeCmp {
        bool operator() (const TLDGEdge* a, const TLDGEdge* b) const{
            return a->first < b->first || a->second < b->second;
        }
    };

    class TLDG
    {

    private:
        /**
         * @brief Build the top level dependency graph based on the specified
         * module.
         * 
         * @param module The module to retrieve the bitcode from.
         */
        void build(SVFModule* module);

        /**
         * @brief Inserts a value into the set of nodes. Values may be global
         * values or local values, which are deemed unique on the bases of their
         * memory addresses. After completion is graph is available in the form
         * of a adjacency list in the "edges" set, a public class member. The
         * nodes can be retrieved similarly from the member "nodes" to somewhat
         * preserve the compatibility to the SVF API.
         * 
         * @param value The value to be inserted.
         */
        void insert(const Value* value);

    public:
        std::set<TLDGEdge*, TLDGEdgeCmp> edges;
        std::set<const Value*> nodes;

        TLDG(SVFModule* module = nullptr)
        {
            if (!module)
            {
                return;
            }

            build(module);
        }
    };

}

#endif /*TLDEPBUILDER_H_*/