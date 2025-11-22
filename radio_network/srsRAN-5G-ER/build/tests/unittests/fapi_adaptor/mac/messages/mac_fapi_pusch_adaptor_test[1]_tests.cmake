add_test( mac_to_fapi_pusch_pdu_test.valid_pusch_pdu_shoul_pass /home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/build/tests/unittests/fapi_adaptor/mac/messages/mac_fapi_pusch_adaptor_test [==[--gtest_filter=mac_to_fapi_pusch_pdu_test.valid_pusch_pdu_shoul_pass]==] --gtest_also_run_disabled_tests)
set_tests_properties( mac_to_fapi_pusch_pdu_test.valid_pusch_pdu_shoul_pass PROPERTIES WORKING_DIRECTORY /home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/build/tests/unittests/fapi_adaptor/mac/messages)
set( mac_fapi_pusch_adaptor_test_TESTS mac_to_fapi_pusch_pdu_test.valid_pusch_pdu_shoul_pass)
