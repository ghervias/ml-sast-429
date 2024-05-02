//===- svf-ex.cpp -- A driver example of SVF-------------------------------------//
//
//                     SVF: Static Value-Flow Analysis
//
// Copyright (C) <2013->  <Yulei Sui>
//

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
//===-----------------------------------------------------------------------===//

/*
 // A driver program of SVF including usages of SVF APIs
 //
 // Author: Yulei Sui,
 */

#include "SVF-FE/LLVMUtil.h"
#include "Graphs/SVFG.h"
#include "WPA/Andersen.h"
#include "WPA/FlowSensitive.h"
#include "SVF-FE/SVFIRBuilder.h"

#include "MLSASTOptions.h"
#include "TLDG.h"
#include "CSVPrinter.h"

using namespace llvm;
using namespace std;
using namespace SVF;

static llvm::cl::opt<std::string> InputFilename(cl::Positional,
        llvm::cl::desc("<input bitcode>"), llvm::cl::init("-"));


int main(int argc, char ** argv)
{
    int arg_num = 0;
    char **arg_value = new char*[argc];

    std::vector<std::string> moduleNameVec;
    LLVMUtil::processArguments(argc, argv, arg_num, arg_value, moduleNameVec);
    cl::ParseCommandLineOptions(arg_num, arg_value,
            "SVF Graph Generator for ML-SAST.\n");
    
    SVFModule* svfModule =
            LLVMModuleSet::getLLVMModuleSet()->buildSVFModule(moduleNameVec);
    svfModule->buildSymbolTableInfo();

    SVFIRBuilder builder;
    SVFIR* pag = builder.build(svfModule);
    PointerAnalysis* pta = nullptr;


    SVFUtil::errs() << "Begin Points-To analysis... ";
    if (MLSASTOptions::Precise)
    {
        pta = new FlowSensitive(pag);
    }
    
    else
    {
        pta = new AndersenWaveDiff(pag);
    }

    pta->analyze();

    SVFUtil::errs() << "Done\n";

    SVFG* svfg = nullptr;
    TLDG* tldg = nullptr;
    ICFG* icfg = nullptr;
    PTACallGraph* ptacg = nullptr;

    if (MLSASTOptions::BuildSVFG) {
        SVFUtil::errs() << "Building SVFG... ";
        SVFGBuilder svfBuilder;
        svfg = svfBuilder.buildFullSVFG((BVDataPTAImpl*) pta);
        SVFUtil::errs() << "Done\n";
    }

    if (MLSASTOptions::BuildTLDG) {
        SVFUtil::errs() << "Building TLDG... ";
        tldg = new TLDG(svfModule);   
        SVFUtil::errs() << "Done\n";
    }

    if (MLSASTOptions::BuildPTACG || MLSASTOptions::BuildICFG) {
        SVFUtil::errs() << "Building PTACG... ";
        ptacg = pta->getPTACallGraph();
        SVFUtil::errs() << "Done\n";
    }

    if (MLSASTOptions::BuildICFG) {
        SVFUtil::errs() << "Building ICFG... ";
        icfg = pag->getICFG();
        icfg->updateCallGraph(ptacg);
        SVFUtil::errs() << "Done\n";
    }

    SVFUtil::errs() << "Dumping CSV files:\n";
    CSVPrinter::WriteGraphToCSV("graphs",
        svfg,
        tldg,
        icfg,
        ptacg
    ); 
    SVFUtil::errs() << "Done\n";

    if (svfg)
        delete svfg;
    if (tldg)
        delete tldg;

    AndersenWaveDiff::releaseAndersenWaveDiff();
    SVFIR::releaseSVFIR();
    SVF::LLVMModuleSet::releaseLLVMModuleSet();

    llvm::llvm_shutdown();
    return 0;
}