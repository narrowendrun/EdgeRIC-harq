# CMake generated Testfile for 
# Source directory: /home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/gateways
# Build directory: /home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/build/tests/unittests/gateways
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
include("/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/build/tests/unittests/gateways/udp_network_gateway_test[1]_include.cmake")
add_test(sctp_network_gateway_test "sctp_network_gateway_test")
set_tests_properties(sctp_network_gateway_test PROPERTIES  LABELS "tsan" _BACKTRACE_TRIPLES "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/gateways/CMakeLists.txt;29;add_test;/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/gateways/CMakeLists.txt;0;")
set_directory_properties(PROPERTIES LABELS "gateways")
