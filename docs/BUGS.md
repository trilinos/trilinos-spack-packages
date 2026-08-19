# Known Trilinos Source Code Bugs

This file documents bugs found in the Trilinos source code that affect the Spack package builds.

## ShyLU_Node Header Bugs

**Status**: Workaround in place (disabled in generator)  
**Affected Package**: ShyLU_Node (and subpackages ShyLU_NodeBasker, ShyLU_NodeTacho)  
**File**: `packages/shylu/shylu_node/basker/src/shylubasker_order_scotch.hpp`  
**Trilinos Branch**: `changes-for-spack` (commit bcb7cd73)

### Bugs:

1. **Line 1225**: Macro call `BASKER_ASSERT(sptr < M.nnz);` requires 2 arguments but only 1 is given
   - The macro is defined in `shylubasker_types.hpp:116` as `#define BASKER_ASSERT(a,s)`
   - Fix: Add a second argument (error message string) to the macro call

2. **Line 1254**: Variable `num_doms` is not declared (should be `num_domains`)
   ```cpp
   for(Int i =0; i < num_doms; i++)
   ```
   - Fix: Change `num_doms` to `num_domains`

3. **Line 1259**: Variable `num_doms` is not declared (should be `num_domains`)
   ```cpp
   sg.rangtab[num_doms] = 0;
   ```
   - Fix: Change `num_doms` to `num_domains`

4. **Line 1283**: Variable `num_levels` is not declared in scope
   ```cpp
   err = SCOTCH_stratGraphOrderBuild(&strdat, flagval, num_levels, balrat);
   ```
   - Fix: Declare or pass `num_levels` variable properly

### Impact:
- Any package that has ShyLU_Node as an optional dependency will fail to compile when ShyLU_Node support is enabled
- Affected packages include: Amesos2, and potentially others

### Workaround:
- Added ShyLU_Node and its subpackages to `EXCLUDE_OPTIONAL_PACKAGES` in `generate_spack_packages.py`
- This prevents any generated package from depending on ShyLU_Node

### TODO:
- [ ] Create patch files for the Trilinos source
- [ ] Submit fixes upstream to Trilinos project
- [ ] Remove from exclusion list once fixed in the branch we're building

---

## SuperLU Version Incompatibility

**Status**: Workaround in place (disabled in generator)  
**Affected TPL**: SuperLU  
**Trilinos Branch**: `changes-for-spack` (commit bcb7cd73)

### Issue:
- Trilinos code expects SuperLU API from version 5.x
- Modern Spack-provided SuperLU is 7.0.1+ with breaking API changes
- User's system has very old SuperLU (older than Spack supports)

### Errors:
```
error: 'fact_t' does not name a type
error: 'yes_no_t' does not name a type
```

### Workaround:
- Disabled SuperLU in `INCLUDE_TPLS` dict in `generate_spack_packages.py`
- No generated packages will have SuperLU variants or dependencies

### TODO:
- [ ] Update Trilinos code to support SuperLU 7.x API
- [ ] Or pin to specific SuperLU version range that's compatible

---

## Teko CMakeLists.txt Parse Error

**Status**: FIXED (commit ea9c1f5)  
**Affected Package**: Teko  
**File**: `packages/teko/CMakeLists.txt`  
**Line**: 30  
**Trilinos Branch**: `changes-for-spack`

### Error:
```
CMake Error at packages/teko/CMakeLists.txt:30:
  Parse error.  Expected a newline, got identifier with text "x".
```

### Issue:
- Line 30 had a stray `x` character: `IF(${PACKAGE_NAME}_ENABLE_MueLu)x`
- Should be: `IF(${PACKAGE_NAME}_ENABLE_MueLu)`

### Fix:
- Removed the stray `x` character from line 30
- Committed to Trilinos changes-for-spack branch (commit ea9c1f5)

---

## MueLu External Belos/Xpetra Configuration Error

**Status**: FIXED (commit 4fedbfe)  
**Affected Package**: MueLu  
**File**: `packages/muelu/CMakeLists.txt`  
**Lines**: 155-160  
**Trilinos Branch**: `changes-for-spack`

### Error:
```
CMake Error at packages/muelu/CMakeLists.txt:156 (ASSERT_DEFINED):
  Error, the variable HAVE_BELOS_XPETRA is not defined!

CMake Error at packages/muelu/CMakeLists.txt:158 (MESSAGE):
  Option MueLu_ENABLE_Belos=ON requires Belos_ENABLE_Xpetra=ON.
```

### Issue:
- MueLu requires Belos to be built with Xpetra support
- When Belos is treated as an external TPL (pre-built package), the `HAVE_BELOS_XPETRA` variable is not defined
- The ASSERT_DEFINED check fails even though external Belos may have Xpetra support

### Fix:
- Modified CMake logic to handle external Belos gracefully
- When both Belos and Xpetra are external TPLs, assume Belos has Xpetra support
- Added informative error messages for other cases
- Committed to Trilinos changes-for-spack branch (commit 4fedbfe)
