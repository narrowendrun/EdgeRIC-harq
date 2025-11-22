# CMake generated Testfile for 
# Source directory: /home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/scheduler
# Build directory: /home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/build/tests/unittests/scheduler
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
include("/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/build/tests/unittests/scheduler/scheduler_test[1]_include.cmake")
include("/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/build/tests/unittests/scheduler/scheduler_test_doubles_test[1]_include.cmake")
include("/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/build/tests/unittests/scheduler/multiple_ue_sched_test[1]_include.cmake")
include("/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/build/tests/unittests/scheduler/scheduler_metrics_handler_test[1]_include.cmake")
include("/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/build/tests/unittests/scheduler/multi_cell_scheduler_test[1]_include.cmake")
add_test(sched_no_ue_test "sched_no_ue_test")
set_tests_properties(sched_no_ue_test PROPERTIES  _BACKTRACE_TRIPLES "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/scheduler/CMakeLists.txt;42;add_test;/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/scheduler/CMakeLists.txt;0;")
add_test(pdcch_resource_allocator_test "pdcch_resource_allocator_test")
set_tests_properties(pdcch_resource_allocator_test PROPERTIES  _BACKTRACE_TRIPLES "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/scheduler/CMakeLists.txt;46;add_test;/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/scheduler/CMakeLists.txt;0;")
add_test(scheduler_test "scheduler_test")
set_tests_properties(scheduler_test PROPERTIES  _BACKTRACE_TRIPLES "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/scheduler/CMakeLists.txt;61;add_test;/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/scheduler/CMakeLists.txt;0;")
subdirs("test_utils")
subdirs("support")
subdirs("cell_resource_grid")
subdirs("common_scheduling")
subdirs("ue_scheduling")
subdirs("uci_and_pucch")
subdirs("policy")
subdirs("config")
subdirs("slicing")
set_directory_properties(PROPERTIES LABELS "sched")
