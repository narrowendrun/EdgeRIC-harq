# CMake generated Testfile for 
# Source directory: /home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/phy/upper/channel_processors
# Build directory: /home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/build/tests/unittests/phy/upper/channel_processors
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(pdcch_processor_unittest "pdcch_processor_unittest")
set_tests_properties(pdcch_processor_unittest PROPERTIES  _BACKTRACE_TRIPLES "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/phy/upper/channel_processors/CMakeLists.txt;31;add_test;/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/phy/upper/channel_processors/CMakeLists.txt;0;")
add_test(pdsch_processor_unittest "pdsch_processor_unittest")
set_tests_properties(pdsch_processor_unittest PROPERTIES  _BACKTRACE_TRIPLES "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/phy/upper/channel_processors/CMakeLists.txt;35;add_test;/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/phy/upper/channel_processors/CMakeLists.txt;0;")
add_test(pdsch_processor_validator_test "pdsch_processor_validator_test")
set_tests_properties(pdsch_processor_validator_test PROPERTIES  _BACKTRACE_TRIPLES "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/phy/upper/channel_processors/CMakeLists.txt;47;add_test;/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/phy/upper/channel_processors/CMakeLists.txt;0;")
add_test(pucch_processor_format1_unittest "pucch_processor_format1_unittest")
set_tests_properties(pucch_processor_format1_unittest PROPERTIES  _BACKTRACE_TRIPLES "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/phy/upper/channel_processors/CMakeLists.txt;56;add_test;/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/phy/upper/channel_processors/CMakeLists.txt;0;")
add_test(pucch_processor_validators_test "pucch_processor_validators_test")
set_tests_properties(pucch_processor_validators_test PROPERTIES  _BACKTRACE_TRIPLES "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/phy/upper/channel_processors/CMakeLists.txt;70;add_test;/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/phy/upper/channel_processors/CMakeLists.txt;0;")
add_test(ssb_processor_unittest "ssb_processor_unittest")
set_tests_properties(ssb_processor_unittest PROPERTIES  _BACKTRACE_TRIPLES "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/phy/upper/channel_processors/CMakeLists.txt;74;add_test;/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/tests/unittests/phy/upper/channel_processors/CMakeLists.txt;0;")
subdirs("pusch")
subdirs("uci")
set_directory_properties(PROPERTIES LABELS "phy")
