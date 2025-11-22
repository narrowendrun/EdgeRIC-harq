# Install script for directory: /home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/srsran" TYPE FILE FILES
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/cell_cfg_max_128_ues.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/cell_cfg_max_32_ues.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/cell_cfg_max_64_ues.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/cu.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/du_rf_b200_tdd_n78_20mhz.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/geo_ntn.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/gnb_b210_20MHz_apal_n1.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/gnb_b210_20MHz_apal_n3.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/gnb_b210_20MHz_apal_n44.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/gnb_b210_20MHz_apal_n48.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/gnb_b210_20MHz_apal_n78.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/gnb_custom_cell_properties.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/gnb_rf_b200_tdd_n78_20mhz.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/gnb_rf_b210_fdd_n3_20mhz.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/gnb_rf_b210_fdd_srsUE.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/gnb_rf_n310_fdd_n3_20mhz.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/gnb_ru_picocom_scb_tdd_n78_20mhz.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/gnb_ru_ran550_tdd_n78_100mhz_4x2.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/gnb_ru_ran550_tdd_n78_20mhz.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/gnb_ru_rpqn4800e_tdd_n78_20mhz_2x2.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/low_latency.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/mimo_usrp.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/mobility.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/n320-ota-amrisoft.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/qam256.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/qos.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/slicing.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/srb.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/testmode.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/zmq-mode-multi-ue.yml"
    "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/configs/zmq-mode.yml"
    )
endif()

