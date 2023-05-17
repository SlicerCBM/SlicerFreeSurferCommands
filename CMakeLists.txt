cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(FreeSurferCommands)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/SlicerCBM/SlicerFreeSurferCommands")
set(EXTENSION_CATEGORY "Segmentation")
set(EXTENSION_CONTRIBUTORS "Benjamin Zwick")
set(EXTENSION_DESCRIPTION "Run FreeSurfer commands within 3D Slicer.")
set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/SlicerFreeSurferCommands.png")
set(EXTENSION_SCREENSHOTURLS "https://www.example.com/Slicer/Extensions/SlicerFreeSurferCommands/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(FreeSurferMRIWatershedSkullStrip)
add_subdirectory(FreeSurferSynthStripSkullStrip)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
