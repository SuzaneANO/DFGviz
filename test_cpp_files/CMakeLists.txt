cmake_minimum_required(VERSION 3.10)
project(TestDataflowAnalysis)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include directories
include_directories(${CMAKE_SOURCE_DIR}/include)
include_directories(${CMAKE_SOURCE_DIR}/src)

# Compile definitions
add_definitions(-DDEBUG_MODE)
add_definitions(-DVERSION_MAJOR=1)
add_definitions(-DVERSION_MINOR=0)

# Source files
# Note: src/processor.cpp is intentionally excluded for testing auto-detect
set(SOURCES
    src/main.cpp
    src/calculator.cpp
    # src/processor.cpp  # Excluded file - should NOT be auto-detected
)

# Header files
set(HEADERS
    include/calculator.h
    include/processor.h
    include/utils.h
)

# Create executable
add_executable(test_app ${SOURCES} ${HEADERS})

# Link libraries if needed
# target_link_libraries(test_app some_lib)

