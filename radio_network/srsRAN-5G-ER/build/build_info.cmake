
execute_process(
COMMAND git rev-parse --abbrev-ref HEAD
WORKING_DIRECTORY "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER"
OUTPUT_VARIABLE GIT_BRANCH
OUTPUT_STRIP_TRAILING_WHITESPACE
)

execute_process(
COMMAND git log -1 --format=%h
WORKING_DIRECTORY "/home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER"
OUTPUT_VARIABLE GIT_COMMIT_HASH
OUTPUT_STRIP_TRAILING_WHITESPACE
)

message(STATUS "Generating build information")
configure_file(
  /home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/lib/support/build_info/hashes.h.in
  /home/EdgeRIC-A-real-time-RIC/srsRAN-5G-ER/build/hashes.h
)
