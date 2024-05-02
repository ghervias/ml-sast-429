#include <stddef.h>
#include <stdio.h>

#ifdef USE_LIBTIFF
#include "tiffio.h"
// #define USE_LIBTIFF_NEW // Library version later than 4.0.9 (4.5???)
#endif // #ifdef USE_LIBTIFF

#ifdef USE_ZLIB
#include "zlib.h"
#endif // #ifdef USE_ZLIB

#ifdef USE_LIBJPEG
#include "jpeglib.h"
#endif // #ifdef USE_LIBJPEG

#ifdef USE_OPENJPEG
#include "openjpeg.h"
#endif // #ifdef USE_OPENJPEG

#ifdef USE_MINIUPNP
#include "igd_desc_parse.h"
#include "miniupnpc.h"
#include "portlistingparse.h"
#include "miniwget.h"
#include "upnpcommands.h"
#include "upnperrors.h"
#include "upnpreplyparse.h"
#endif // #ifdef USE_MINIUPNP

#ifdef USE_MINIUPNP_2
#include "miniupnpc/igd_desc_parse.h"
#include "miniupnpc/miniupnpc.h"
#include "miniupnpc/portlistingparse.h"
#include "miniupnpc/miniwget.h"
#include "miniupnpc/upnpcommands.h"
#include "miniupnpc/upnperrors.h"
#include "miniupnpc/upnpreplyparse.h"
#endif // #ifdef USE_MINIUPNP

int main(const int argc, const char **arg)
{

#ifdef USE_LIBTIFF

    TIFFOpen(NULL, "r");
    TIFFAccessTagMethods(NULL);
    TIFFReadBufferSetup(NULL, NULL, 0);
    TIFFWriteBufferSetup(NULL, NULL, 0);
    TIFFGetClientInfo(NULL, NULL);
    TIFFSetClientInfo(NULL, NULL, NULL);
    TIFFFindCODEC(0);
    TIFFRegisterCODEC(0, NULL, NULL);
    TIFFUnRegisterCODEC(NULL);
    TIFFIsCODECConfigured(0);
    TIFFGetConfiguredCODECs();
    TIFFYCbCrToRGBInit(NULL, NULL, NULL);
    TIFFYCbCrtoRGB(NULL, 0, 0, 0, NULL, NULL, NULL);
    TIFFCIELabToRGBInit(NULL, NULL, NULL);
    TIFFCIELabToXYZ(NULL, 0, 0, 0, NULL, NULL, NULL);
    TIFFXYZToRGB(NULL, 0.0, 0.0, 0.0, NULL, NULL, NULL);
    TIFFCreateDirectory(NULL);
    TIFFFreeDirectory(NULL);
    TIFFUnlinkDirectory(NULL, 0);
    TIFFCreateCustomDirectory(NULL, NULL);
    TIFFCreateEXIFDirectory(NULL);
    TIFFWriteCustomDirectory(NULL, NULL);
    TIFFReadCustomDirectory(NULL, 0, NULL);
    TIFFReadEXIFDirectory(NULL, 0);
    TIFFGetTagListCount(NULL);
    TIFFGetTagListEntry(NULL, 0);
    TIFFDataWidth(0);
    TIFFError(NULL, NULL);
    TIFFErrorExt(0, NULL, NULL);
    TIFFSetErrorHandler(NULL);
    TIFFSetErrorHandlerExt(NULL);
    TIFFFieldDataType(NULL);
    TIFFFieldName(NULL);
    TIFFFieldPassCount(NULL);
    TIFFFieldWithName(NULL, NULL);
    TIFFFieldWithTag(NULL, 0);
    TIFFFindField(NULL, 0, 0);
    TIFFFieldReadCount(NULL);
    TIFFFieldTag(NULL);
    TIFFFieldWriteCount(NULL);
    TIFFFlush(NULL);
    TIFFFlushData(NULL);
    TIFFGetField(NULL, 0, NULL);
    TIFFVGetField(NULL, 0, NULL);
    TIFFGetFieldDefaulted(NULL, 0, NULL);
    TIFFVGetFieldDefaulted(NULL, 0, NULL);
    _TIFFmalloc(0);
    _TIFFrealloc(NULL, 0);
    _TIFFfree(NULL);
    _TIFFmemset(NULL, 0, 0);
    _TIFFmemcpy(NULL, NULL, 0);
    _TIFFmemcmp(NULL, NULL, 0);
    TIFFMergeFieldInfo(NULL, NULL, 0);
    TIFFPrintDirectory(NULL, NULL, 0L);
    TIFFGetCloseProc(NULL);
    TIFFGetMapFileProc(NULL);
    TIFFGetReadProc(NULL);
    TIFFGetSeekProc(NULL);
    TIFFGetSizeProc(NULL);
    TIFFGetUnmapFileProc(NULL);
    TIFFGetWriteProc(NULL);
    TIFFCurrentDirectory(NULL);
    TIFFCurrentDirOffset(NULL);
    TIFFLastDirectory(NULL);
    TIFFNumberOfDirectories(NULL);
    TIFFCurrentRow(NULL);
    TIFFCurrentStrip(NULL);
    TIFFCurrentTile(NULL);
    TIFFFileno(NULL);
    TIFFFileName(NULL);
    TIFFGetMode(NULL);
    TIFFIsTiled(NULL);
    TIFFIsBigEndian(NULL);
    TIFFIsByteSwapped(NULL);
    TIFFIsMSB2LSB(NULL);
    TIFFIsUpSampled(NULL);
    TIFFGetVersion();
    TIFFReadDirectory(NULL);
    TIFFReadEncodedStrip(NULL, 0, NULL, 0);
    TIFFReadEncodedTile(NULL, 0, NULL, 0);
    TIFFReadRawStrip(NULL, 0, NULL, 0);
    TIFFReadRawTile(NULL, 0, NULL, 0);
    TIFFReadRGBAImage(NULL, 0, 0, NULL, 0);
    TIFFReadRGBAImageOriented(NULL, 0, 0, NULL, 0, 0);
    TIFFReadRGBAStrip(NULL, 0, NULL);
//    TIFFReadRGBAStripExt(NULL, 0, NULL, 0);
    TIFFReadRGBATile(NULL, 0, 0, NULL);
//    TIFFReadRGBATileExt(NULL, 0, 0, NULL, 0);
    TIFFReadScanline(NULL, 0, 0, 0);
    TIFFReadTile(NULL, 0, 0, 0, 0, 0);
    TIFFRGBAImageOK(NULL, NULL);
    TIFFRGBAImageBegin(NULL, NULL, 0, NULL);
    TIFFRGBAImageGet(NULL, NULL, 0, 0);
    TIFFRGBAImageEnd(NULL);
    TIFFSetDirectory(NULL, 0);
    TIFFSetSubDirectory(NULL, 0);
    TIFFSetField(NULL, 0, 0);
    TIFFVSetField(NULL, 0, NULL);
    TIFFUnsetField(NULL, 0);
    TIFFSetTagExtender(NULL);
    TIFFRasterScanlineSize(NULL);
    TIFFRasterScanlineSize64(NULL);
    TIFFScanlineSize(NULL);
    TIFFScanlineSize64(NULL);
    TIFFDefaultStripSize(NULL, 0);
    TIFFStripSize(NULL);
    TIFFStripSize64(NULL);
    TIFFVStripSize(NULL, 0);
    TIFFVStripSize64(NULL, 0);
    TIFFRawStripSize(NULL, 0);
    TIFFRawStripSize64(NULL, 0);
    TIFFComputeStrip(NULL, 0, 0);
    TIFFNumberOfStrips(NULL);
    TIFFSetupStrips(NULL);
    TIFFGetBitRevTable(0);
    TIFFReverseBits(NULL, 0L);
    TIFFSwabShort(NULL);
    TIFFSwabLong(NULL);
    TIFFSwabLong8(NULL);
    TIFFSwabFloat(NULL);
    TIFFSwabDouble(NULL);
    TIFFSwabArrayOfShort(NULL, 0);
    TIFFSwabArrayOfTriples(NULL, 0);
    TIFFSwabArrayOfLong(NULL, 0);
    TIFFSwabArrayOfLong8(NULL, 0);
    TIFFSwabArrayOfFloat(NULL, 0);
    TIFFSwabArrayOfDouble(NULL, 0);
    TIFFDefaultTileSize(NULL, NULL, NULL);
    TIFFTileSize(NULL);
    TIFFTileSize64(NULL);
    TIFFTileRowSize(NULL);
    TIFFTileRowSize64(NULL);
    TIFFVTileSize(NULL, 0);
    TIFFVTileSize64(NULL, 0);
    TIFFComputeTile(NULL, 0, 0, 0, 0);
    TIFFCheckTile(NULL, 0, 0, 0, 0);
    TIFFNumberOfTiles(NULL);
    TIFFWarning(NULL, NULL);
    TIFFWarningExt(0, NULL, NULL);
    TIFFSetWarningHandler(NULL);
    TIFFSetWarningHandlerExt(NULL);
    TIFFWriteDirectory(NULL);
    TIFFRewriteDirectory(NULL);
    TIFFCheckpointDirectory(NULL);
    TIFFSetWriteOffset(NULL, 0);
    TIFFWriteCheck(NULL, 0, NULL);
    TIFFWriteEncodedStrip(NULL, 0, NULL, 0);
    TIFFWriteEncodedTile(NULL, 0, NULL, 0);
    TIFFWriteRawStrip(NULL, 0, NULL, 0);
    TIFFWriteRawTile(NULL, 0, NULL, 0);
    TIFFWriteScanline(NULL, NULL, 0, 0);
    TIFFWriteTile(NULL, NULL, 0, 0, 0, 0);
    TIFFClose(NULL);

#endif // #ifdef USE_LIBTIFF

#ifdef USE_LIBTIFF_NEW

    TIFFSetCompressionScheme(NULL, 0);
    TIFFCreateGPSDirectory(NULL);
    TIFFDeferStrileArrayWriting(NULL);
    TIFFForceStrileArrayWriting(NULL);
    TIFFFieldIsAnonymous(NULL);
    TIFFFieldSetGetSize(NULL);
    TIFFFieldSetGetCountSize(NULL);
    _TIFFCheckMalloc(NULL, 0, 0, NULL);
    _TIFFCheckRealloc(NULL, NULL, 0, 0, NULL);
    TIFFIsBigTIFF(NULL);
    TIFFReadFromUserBuffer(NULL, 0, NULL, 0, NULL, 0);
    TIFFGetStrileByteCount(NULL, 0);
    TIFFGetStrileOffset(NULL, 0);
    TIFFGetStrileByteCountWithErr(NULL, 0, NULL);
    TIFFGetStrileOffsetWithErr(NULL, 0, NULL);
    _TIFFClampDoubleToUInt32(0.0);
    _TIFFMultiply32(NULL, 0, 0, NULL);
    _TIFFMultiply64(NULL, 0, 0, NULL);
    _TIFFRewriteField(NULL, 0, NULL, 0, NULL);

#endif // #ifdef USE_LIBTIFF_NEW


#ifdef USE_ZLIB

    zlibVersion();
    deflateInit(NULL, 0);
    deflate(NULL, 0);
    deflateEnd(NULL);
    inflateInit(NULL);
    inflate(NULL, 0);
    inflateEnd(NULL);
    deflateInit2(NULL, 0, 0, 0, 0, 0);
    deflateSetDictionary(NULL, NULL, 0);
//    deflateGetDictionary(NULL, NULL, NULL);
    deflateCopy(NULL, NULL);
    deflateReset(NULL);
    deflateParams(NULL, 0, 0);
    deflateTune(NULL, 0, 0, 0, 0);
    deflateBound(NULL, 0);
    deflatePending(NULL, NULL, NULL);
    deflatePrime(NULL, 0, 0);
    deflateSetHeader(NULL, NULL);
    inflateInit2(NULL, 0);
    inflateSetDictionary(NULL, NULL, 0);
    inflateGetDictionary(NULL, NULL, NULL);
    inflateSync(NULL);
    inflateCopy(NULL, NULL);
    inflateReset(NULL);
    inflateReset2(NULL, 0);
    inflatePrime(NULL, 0, 0);
    inflateMark(NULL);
    inflateGetHeader(NULL, NULL);
    inflateBackInit(NULL, 0, NULL);
    inflateBack(NULL, NULL, NULL, NULL, NULL);
    inflateBackEnd(NULL);
    zlibCompileFlags();
    compress(NULL, NULL, NULL, 0L);
    compress2(NULL, NULL, NULL, 0L, 0);
    compressBound(0L);
    uncompress(NULL, NULL, NULL, 0L);
    // uncompress2(NULL, NULL, NULL, NULL);
    gzopen(NULL, NULL);
    gzdopen(0, NULL);
    gzbuffer(NULL, 0);
    gzsetparams(NULL, 0, 0);
    gzread(NULL, NULL, 0);
    // gzfread(NULL, 0, 0, NULL);
    gzwrite(NULL, NULL, 0);
//    gzfwrite(NULL, 0, 0, NULL);
    gzprintf(NULL, NULL, NULL);
    gzputs(NULL, NULL);
    gzgets(NULL, NULL, 0);
    gzputc(NULL, 0);
    gzgetc((gzFile) NULL);
    gzungetc(0, NULL);
    gzflush(NULL, 0);
    gzseek(NULL, 0, 0);
    gzrewind(NULL);
    gztell(NULL);
    gzoffset(NULL);
    gzeof(NULL);
    gzdirect(NULL);
    gzclose(NULL);
    gzclose_r(NULL);
    gzclose_w(NULL);
    gzerror(NULL, NULL);
    gzclearerr(NULL);
    adler32(0L, NULL, 0);
//    adler32_z(0L, NULL, 0);
    adler32_combine(0L, 0L, 0);
    crc32(0L, NULL, 0);
//    crc32_z(0L, NULL, 0);
    crc32_combine(0L, 0L, 0);

#endif // #ifdef USE_ZLIB

#ifdef USE_LIBJPEG

    jpeg_std_error(NULL);
    jpeg_CreateCompress(NULL, 0, 0);
    jpeg_CreateDecompress(NULL, 0, 0);
    jpeg_destroy_compress(NULL);
    jpeg_destroy_decompress(NULL);
    jpeg_stdio_dest(NULL, NULL);
    jpeg_stdio_src(NULL, NULL);
    jpeg_mem_dest(NULL, NULL, NULL);
    jpeg_mem_src(NULL, NULL, 0L);
    jpeg_set_defaults(NULL);
    jpeg_set_colorspace(NULL, JCS_UNKNOWN);
    jpeg_default_colorspace(NULL);
    jpeg_set_quality(NULL, 0, 0);
    jpeg_set_linear_quality(NULL, 0, 0);
    jpeg_default_qtables(NULL, 0);
    jpeg_add_quant_table(NULL, 0, NULL, 0, 0);
    jpeg_quality_scaling(0);
    jpeg_simple_progression(NULL);
    jpeg_suppress_tables(NULL, 0);
    jpeg_alloc_quant_table(NULL);
    jpeg_start_compress(NULL, 0);
    jpeg_write_scanlines(NULL, NULL, 0);
    jpeg_finish_compress(NULL);
    jpeg_calc_jpeg_dimensions(NULL);
    jpeg_write_raw_data(NULL, NULL, 0);
    jpeg_write_marker(NULL, 0, NULL, 0);
    jpeg_write_m_header(NULL, 0, 0);
    jpeg_write_m_byte(NULL, 0);
    jpeg_write_tables(NULL);
    jpeg_read_header(NULL, 0);
    jpeg_start_decompress(NULL);
    jpeg_read_scanlines(NULL, NULL, 0);
    jpeg_skip_scanlines(NULL, 0);
    jpeg_crop_scanline(NULL, NULL, NULL);
    jpeg_finish_decompress(NULL);
    jpeg_read_raw_data(NULL, NULL, 0);
    jpeg_has_multiple_scans(NULL);
    jpeg_start_output(NULL, 0);
    jpeg_finish_output(NULL);
    jpeg_input_complete(NULL);
    jpeg_new_colormap(NULL);
    jpeg_consume_input(NULL);
    jpeg_core_output_dimensions(NULL);
    jpeg_calc_output_dimensions(NULL);
    jpeg_save_markers(NULL, 0, 0);
    jpeg_set_marker_processor(NULL, 0, NULL);
    jpeg_read_coefficients(NULL);
    jpeg_write_coefficients(NULL, NULL);
    jpeg_copy_critical_parameters(NULL, NULL);
    jpeg_abort_compress(NULL);
    jpeg_abort_decompress(NULL);
    jpeg_abort(NULL);
    jpeg_destroy(NULL);
    jpeg_resync_to_restart(NULL, 0);

#endif //#ifdef USE_LIBJPEG

#ifdef USE_OPENJPEG

    opj_version();
    opj_image_create(0, NULL, 0);
    opj_image_destroy(NULL);
    opj_image_tile_create(0, NULL, 0);
    opj_stream_default_create(0);
    opj_stream_create(0, 0);
    opj_stream_destroy(NULL);
    opj_stream_set_read_function(NULL, NULL);
    opj_stream_set_write_function(NULL, NULL);
    opj_stream_set_skip_function(NULL, NULL);
    opj_stream_set_seek_function(NULL, NULL);
    opj_stream_set_user_data(NULL, NULL, NULL);
    opj_stream_set_user_data_length(NULL, 0);
    opj_stream_create_default_file_stream(NULL, 0);
    opj_stream_create_file_stream(NULL, 0, 0);
    opj_set_info_handler(NULL, NULL, NULL);
    opj_set_warning_handler(NULL, NULL, NULL);
    opj_set_error_handler(NULL, NULL, NULL);
    opj_create_decompress(0);
    opj_destroy_codec(NULL);
    opj_end_decompress(NULL, NULL);
    opj_set_default_decoder_parameters(NULL);
    opj_setup_decoder(NULL, NULL);
    opj_read_header(NULL, NULL, NULL);
    opj_set_decode_area(NULL, NULL, 0, 0, 0, 0);
    opj_decode(NULL, NULL, NULL);
    opj_get_decoded_tile(NULL, NULL, NULL, 0);
    opj_set_decoded_resolution_factor(NULL, 0);
    opj_write_tile(NULL, 0, NULL, 0, NULL);
    opj_read_tile_header(NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
    opj_decode_tile_data(NULL, 0, NULL, 0, NULL);
    opj_create_compress(0);
    opj_set_default_encoder_parameters(NULL);
    opj_setup_encoder(NULL, NULL, NULL);
    opj_start_compress(NULL, NULL, NULL);
    opj_end_compress(NULL, NULL);
    opj_encode(NULL, NULL);
    opj_destroy_cstr_info(NULL);
    opj_dump_codec(NULL, 0, NULL);
    opj_get_cstr_info(NULL);
    opj_get_cstr_index(NULL);
    opj_destroy_cstr_index(NULL);
//    opj_get_jp2_metadata(NULL);
//    opj_get_jp2_index(NULL);
    opj_set_MCT(NULL, NULL, NULL, 0);

#endif //#ifdef USE_OPENJPEG

#ifdef USE_MINIUPNP

    // From miniupnpc.h
    simpleUPnPcommand(0, NULL, NULL, NULL, NULL, NULL);
    upnpDiscover(0, NULL, NULL, 0 , 0, 0);
//    upnpDiscover(0, NULL, NULL, 0 , 0, 0, NULL);
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
    miniwget(NULL, NULL, 0);
    miniwget_getaddr(NULL, NULL, NULL, 0, 0);
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
