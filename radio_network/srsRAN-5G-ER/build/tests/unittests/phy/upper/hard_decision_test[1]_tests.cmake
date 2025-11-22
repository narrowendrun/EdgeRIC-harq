add_test( HardDecision.valid_results /home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/build/tests/unittests/phy/upper/hard_decision_test [==[--gtest_filter=HardDecision.valid_results]==] --gtest_also_run_disabled_tests)
set_tests_properties( HardDecision.valid_results PROPERTIES WORKING_DIRECTORY /home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/build/tests/unittests/phy/upper)
set( hard_decision_test_TESTS HardDecision.valid_results)
