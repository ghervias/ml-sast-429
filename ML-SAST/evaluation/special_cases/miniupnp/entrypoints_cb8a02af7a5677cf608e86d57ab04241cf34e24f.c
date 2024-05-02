#include <stddef.h>
#include <stdio.h>

#ifdef USE_MINIUPNP
#include "igd_desc_parse.h"
#include "miniupnpc.h"
#include "portlistingparse.h"
#include "miniwget.h"
#include "upnpcommands.h"
#include "upnperrors.h"
#include "upnpreplyparse.h"
#endif // #ifdef USE_MINIUPNP


int main(const int argc, const char **arg)
{

#ifdef USE_MINIUPNP

    // From miniupnpc.h
    simpleUPnPcommand(0, NULL, NULL, NULL, NULL, NULL);
    upnpDiscover(0, NULL, NULL, 0 , 0, 0, NULL);
    freeUPNPDevlist(NULL);
    parserootdesc(NULL, 0, NULL);
    UPNP_GetValidIGD(NULL, NULL, NULL, NULL, 0);
    UPNP_GetIGDFromUrl(NULL, NULL, NULL, NULL, 0);
    GetUPNPUrls(NULL, NULL, NULL, 0);
    FreeUPNPUrls(NULL);
    UPNPIGD_IsConnected(NULL, NULL);

    // From upnpcommands.h
    UPNP_GetTotalBytesSent(NULL, NULL);
    UPNP_GetTotalBytesReceived(NULL, NULL);
    UPNP_GetTotalPacketsSent(NULL, NULL);
    UPNP_GetTotalPacketsReceived(NULL, NULL);
    UPNP_GetStatusInfo(NULL, NULL, NULL, NULL, NULL);
    UPNP_GetConnectionTypeInfo(NULL, NULL, NULL);
    UPNP_GetExternalIPAddress(NULL, NULL, NULL);
    UPNP_GetLinkLayerMaxBitRates(NULL, NULL, NULL, NULL);
    UPNP_AddPortMapping(NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
//    UPNP_AddAnyPortMapping(NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
    UPNP_DeletePortMapping(NULL, NULL, NULL, NULL, NULL);
//    UPNP_DeletePortMappingRange(NULL, NULL, NULL, NULL, NULL, NULL);
    UPNP_GetPortMappingNumberOfEntries(NULL, NULL, NULL);
    UPNP_GetSpecificPortMappingEntry(NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
    UPNP_GetGenericPortMappingEntry(NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
    UPNP_GetListOfPortMappings(NULL, NULL, NULL, NULL, NULL, NULL, NULL);
    UPNP_GetFirewallStatus(NULL, NULL, NULL, NULL);
    UPNP_GetOutboundPinholeTimeout(NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
    UPNP_AddPinhole(NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
    UPNP_UpdatePinhole(NULL, NULL, NULL, NULL);
    UPNP_DeletePinhole(NULL, NULL, NULL);
    UPNP_CheckPinholeWorking(NULL, NULL, NULL, NULL);
    UPNP_GetPinholePackets(NULL, NULL, NULL, NULL);

    // From miniwget.h
    getHTTPResponse(0, NULL);
//    miniwget(NULL, NULL, 0); // TODO: 4 args
    miniwget(NULL, NULL, 0, NULL); // TODO: 4 args
//    miniwget_getaddr(NULL, NULL, NULL, 0, 0); // TODO: 6 args
    miniwget_getaddr(NULL, NULL, NULL, 0, 0, NULL); // TODO: 6 args
    parseURL(NULL, NULL, NULL, NULL, NULL);

    // From igd_desc_parse.h
    IGDstartelt(NULL, NULL, 0);
    IGDendelt(NULL, NULL, 0);
    IGDdata(NULL, NULL, 0);
//    printIGD(NULL);

    // From portlistingparse.h
    ParsePortListing(NULL, 0, NULL);
    FreePortListing(NULL);

    // From upnperrors.h
    strupnperror(0);

    // From upnpreplyparse.h
    ParseNameValue(NULL, 0, NULL);
    ClearNameValueList(NULL);
    GetValueFromNameValueList(NULL, NULL);

#endif // #ifdef USE_MINIUPNP

    return 0;
}
