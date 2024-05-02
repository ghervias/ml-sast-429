#include <time.h>
#include <stdlib.h>

#include "std_testcase.h"
#include "testcases.h"

int main(int argc, char *argv[])
{
    CWE122_Heap_Based_Buffer_Overflow__c_CWE129_rand_09_good();
    CWE122_Heap_Based_Buffer_Overflow__CWE135_21_good();
    CWE196_Unsigned_to_Signed_Conversion_Error__basic_04_good();
    CWE252_Unchecked_Return_Value__char_fprintf_14_good();
    CWE476_NULL_Pointer_Dereference__char_08_good();
    CWE478_Missing_Default_Case_in_Switch__basic_03_good();
    CWE484_Omitted_Break_Statement_in_Switch__basic_05_good();
    CWE675_Duplicate_Operations_on_Resource__fopen_13_good();
    CWE680_Integer_Overflow_to_Buffer_Overflow__malloc_fgets_32_good();
    CWE690_NULL_Deref_From_Return__struct_malloc_07_good();
   
    CWE122_Heap_Based_Buffer_Overflow__c_CWE129_rand_09_bad();
    CWE122_Heap_Based_Buffer_Overflow__CWE135_21_bad();
    CWE196_Unsigned_to_Signed_Conversion_Error__basic_04_bad();
    CWE252_Unchecked_Return_Value__char_fprintf_14_bad();
    CWE476_NULL_Pointer_Dereference__char_08_bad();
    CWE478_Missing_Default_Case_in_Switch__basic_03_bad();
    CWE484_Omitted_Break_Statement_in_Switch__basic_05_bad();
    CWE675_Duplicate_Operations_on_Resource__fopen_13_bad();
    CWE680_Integer_Overflow_to_Buffer_Overflow__malloc_fgets_32_bad();
    CWE690_NULL_Deref_From_Return__struct_malloc_07_bad();

    return 0;
}
