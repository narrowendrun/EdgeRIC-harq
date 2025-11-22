# CMake generated Testfile for 
# Source directory: /home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/integrationtests/phy/upper/channel_processors
# Build directory: /home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/build/tests/integrationtests/phy/upper/channel_processors
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
include("/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/build/tests/integrationtests/phy/upper/channel_processors/pxsch_chain_test[1]_include.cmake")
add_test(pxsch_bler_test "pxsch_bler_test" "-R" "10")
set_tests_properties(pxsch_bler_test PROPERTIES  _BACKTRACE_TRIPLES "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/integrationtests/phy/upper/channel_processors/CMakeLists.txt;35;add_test;/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/integrationtests/phy/upper/channel_processors/CMakeLists.txt;0;")
set_directory_properties(PROPERTIES LABELS "phy;tsan;NO_MEMCHECK")
