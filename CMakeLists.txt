cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(FreeSurferCommands)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/SlicerCBM/SlicerFreeSurferCommands")
set(EXTENSION_CATEGORY "Segmentation")
set(EXTENSION_CONTRIBUTORS "Benjamin Zwick")
set(EXTENSION_DESCRIPTION "Run FreeSurfer commands within 3D Slicer.")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/SlicerCBM/SlicerFreeSurferCommands/main/SlicerFreeSurferCommands.png")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/SlicerCBM/SlicerFreeSurferCommands/main/Screenshot01.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
# add_subdirectory(FreeSurferMRIWatershedSkullStrip) # TODO: not implemented yet
add_subdirectory(FreeSurferSynthStripSkullStrip)
add_subdirectory(FreeSurferSynthStripSkullStripScripted)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
