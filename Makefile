OS := $(shell uname)
CFLAGS = -I. -Wall 
ifeq ($(OS), Darwin)
CFLAGS += -framework Security
endif
ifeq ($(OS), Linux)
CFLAGS = -pthread -Wl,--no-as-needed -ldl -lm
endif

release: 
	cargo build --release --features=uniffi/cli

python: release
	cargo run --release --features=uniffi/cli --bin uniffi_bindgen generate src/c2pa_uniffi.udl -n --language python -o target/python
	cp target/release/libc2pa_uniffi.dylib target/python/libuniffi_c2pa.dylib

swift: release
	cargo run --release --features=uniffi/cli --bin uniffi_bindgen generate src/c2pa_uniffi.udl -n --language swift -o target/swift
	cp target/release/libc2pa_uniffi.dylib target/swift/libuniffi_c2pa.dylib

build_c: 
	$(CC) $(CFLAGS) src/main.c -o target/ctest -lc2pa_uniffi -L./target/release 

build_node: release
	cd tests/nodejs && npm install

test_c: release build_c
	target/ctest

test_python: release
	python tests/test.py

test_node: release build_node
	cd tests/nodejs && npm start

test: test_c test_python test_node
