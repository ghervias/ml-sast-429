//===- MLSASTOptions.h -- Addtional cli options. -//

#include "Util/Options.h"

#ifndef MLSASTOPTIONS_H_
#define MLSASTOPTIONS_H_

namespace SVF {

class MLSASTOptions : Options
{
public:
    MLSASTOptions(void) = delete;
    
    static const llvm::cl::opt<bool> BuildSVFG;
    static const llvm::cl::opt<bool> BuildTLDG;
    static const llvm::cl::opt<bool> BuildICFG;
    static const llvm::cl::opt<bool> BuildPTACG;
    static const llvm::cl::opt<bool> Precise;
};
}

#endif // !MLSASTOPTIONS_H