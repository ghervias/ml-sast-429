#include <llvm/Support/CommandLine.h>
#include "MLSASTOptions.h"

namespace SVF
{
    const llvm::cl::opt<bool> MLSASTOptions::BuildSVFG(
        "build-svfg",
        llvm::cl::init(false),
        llvm::cl::desc("Generate Sparse Value Flow Graph (SVFG).")

    );
    const llvm::cl::opt<bool> MLSASTOptions::BuildTLDG(
        "build-tldg",
        llvm::cl::init(false),
        llvm::cl::desc("Generate Top-Level Dependency Graph (TLDG).")
    );
    const llvm::cl::opt<bool> MLSASTOptions::BuildICFG(
        "build-icfg",
        llvm::cl::init(false),
        llvm::cl::desc("Generate Interprocedural Control flow Graph (ICFG).")
    );
    const llvm::cl::opt<bool> MLSASTOptions::BuildPTACG(
        "build-ptacg",
        llvm::cl::init(false),
        llvm::cl::desc("Generate Points-To Analysis Call Graph Graph (PTACG).")
    );

    const llvm::cl::opt<bool> MLSASTOptions::Precise(
        "precise-analysis",
        llvm::cl::init(false),
        llvm::cl::desc("Use a precise (but slower) flow-sensitive analysis.")
    );
}