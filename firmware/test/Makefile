# Host tests for the ESP32 firmware logic: make -C firmware/test
CXX      ?= g++
CXXFLAGS ?= -std=c++17 -Wall -Wextra -Werror -g -fsanitize=address,undefined
SRC      := ../esp32/kata_firmware
OBJS     := test_command_processor.cpp $(SRC)/CommandProcessor.cpp $(SRC)/DriveTrain.cpp

.PHONY: test clean
test: build/test_fw
	./build/test_fw

build/test_fw: $(OBJS) $(wildcard $(SRC)/*.h)
	@mkdir -p build
	$(CXX) $(CXXFLAGS) $(OBJS) -o $@

clean:
	rm -rf build
