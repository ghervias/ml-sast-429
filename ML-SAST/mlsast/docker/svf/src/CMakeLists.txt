llvm_map_components_to_libnames(llvm_libs bitwriter core ipo irreader instcombine instrumentation target linker analysis scalaropts support )
file (GLOB SOURCES
   *.cpp
)
add_executable(svf-mlsast ${SOURCES})
include_directories(${CMAKE_SOURCE_DIR}/inc)


target_link_libraries(svf-mlsast ${SVF_LIB} ${llvm_libs})
target_link_libraries(svf-mlsast ${Z3_LIBRARIES})
set_target_properties( svf-mlsast PROPERTIES
                       RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin )
