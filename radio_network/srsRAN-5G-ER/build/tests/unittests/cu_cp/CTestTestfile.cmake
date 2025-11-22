# CMake generated Testfile for 
# Source directory: /home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/cu_cp
# Build directory: /home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/build/tests/unittests/cu_cp
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
include("/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/build/tests/unittests/cu_cp/cu_cp_config_test[1]_include.cmake")
add_test(cu_cp_test "cu_cp_test")
set_tests_properties(cu_cp_test PROPERTIES  _BACKTRACE_TRIPLES "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/cu_cp/CMakeLists.txt;65;add_test;/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/cu_cp/CMakeLists.txt;0;")
subdirs("cell_meas_manager")
subdirs("cu_up_processor")
subdirs("du_processor")
subdirs("routines")
subdirs("ue_manager")
subdirs("up_resource_manager")
subdirs("mobility")
subdirs("metrics_handler")
set_directory_properties(PROPERTIES LABELS "cu_cp")
