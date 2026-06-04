cmake_minimum_required(VERSION 3.10.0)

if (${CMAKE_VERSION} VERSION_GREATER "3.13.0")
    cmake_policy(SET CMP0079 NEW)
    set_property(GLOBAL PROPERTY USE_FOLDERS ON)
endif()

project(rtccli LANGUAGES CXX)

if(NOT CMAKE_SYSTEM_NAME STREQUAL "Linux")
    message(FATAL_ERROR "仅支持 Linux 构建")
endif()
if(NOT CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64")
    message(FATAL_ERROR "仅支持 x86_64，当前: ${CMAKE_SYSTEM_PROCESSOR}")
endif()

list(APPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake)

set(RTC_OUTPUT_DIR "${CMAKE_SOURCE_DIR}/../rtc_runtime")
get_filename_component(RTC_OUTPUT_DIR "${RTC_OUTPUT_DIR}" ABSOLUTE)
message(STATUS "RTC_OUTPUT_DIR: ${RTC_OUTPUT_DIR}")

set(BYTERTC_SDK_DIR "${CMAKE_SOURCE_DIR}/third_party/Linux/VolcEngineRTC_x86_64")
set(BYTERTC_LIB_DIR "${BYTERTC_SDK_DIR}/lib")

file(GLOB RTC_SOURCES
    "src/*.cc"
    "src/util/*.cc"
)
list(APPEND RTC_SOURCES "src/util/json11/json11.cpp")

add_executable(${PROJECT_NAME} ${RTC_SOURCES})
set_target_properties(${PROJECT_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${RTC_OUTPUT_DIR}")
target_include_directories(${PROJECT_NAME} PUBLIC
    ${CMAKE_SOURCE_DIR}/src/util/json11
    ${BYTERTC_SDK_DIR}/include
)
target_link_directories(${PROJECT_NAME} PUBLIC ${BYTERTC_LIB_DIR})
target_link_libraries(${PROJECT_NAME} PUBLIC VolcEngineRTC)

target_link_options(${PROJECT_NAME} PUBLIC -Wl,-rpath-link=${BYTERTC_LIB_DIR}/libVolcEngineRTC.so)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -ggdb -std=c++14 -fPIC -pthread")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,-rpath='$ORIGIN'")

find_package(OpenGL REQUIRED)
target_link_libraries(${PROJECT_NAME} PUBLIC OpenGL::GL)

find_package(FFmpeg COMPONENTS AVCODEC AVFORMAT AVUTIL SWSCALE SWRESAMPLE REQUIRED)
target_link_libraries(${PROJECT_NAME} PUBLIC ${FFMPEG_LIBRARIES})
if(SWSCALE_LIBRARIES)
    target_link_libraries(${PROJECT_NAME} PUBLIC ${SWSCALE_LIBRARIES})
endif()
if(SWRESAMPLE_LIBRARIES)
    target_link_libraries(${PROJECT_NAME} PUBLIC ${SWRESAMPLE_LIBRARIES})
endif()
target_compile_definitions(${PROJECT_NAME} PUBLIC WITH_FFMPEG=1)

execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory ${RTC_OUTPUT_DIR})
foreach(_so libVolcEngineRTC.so libRTCFFmpeg.so libbytertc_nico_extension.so libbytenn.so)
    execute_process(COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${BYTERTC_LIB_DIR}/${_so}" "${RTC_OUTPUT_DIR}/")
endforeach()
