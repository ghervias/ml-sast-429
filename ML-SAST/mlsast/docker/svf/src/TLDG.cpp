#include "TLDG.h"

using namespace SVF;

void TLDG::insert(const Value* V)
{
    this->nodes.insert(V);

    for (const User* U : V->users())
    {
        this->nodes.insert(U);
        this->edges.insert(new TLDGEdge(V, U));
    }
}

void TLDG::build(SVFModule* module)
{
    for (SVFModule::iterator fit = module->begin(),
            efit = module->end(); fit != efit; ++fit)
    {
        Function* F = (**fit).getLLVMFun();

        if (!F)
            continue;

        for (Function::iterator bit = F->begin(),
                ebit = F->end(); bit != ebit; ++bit)
        {
            BasicBlock* BB = &*bit;

            for (BasicBlock::iterator iit = bit->begin(),
                eiit = bit->end(); iit != eiit; ++iit)
            {
                const Value* V = &*iit;
                insert(V);
            }
        }
    }

    for (SVFModule::global_iterator git = module->global_begin(),
        egit = module->global_end(); git != egit; ++git)
    {
        const Value* V = &**git;
        insert(V);
    }
}