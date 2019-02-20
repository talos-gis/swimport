import example

from tests.examples.resources import *

assert_eq(example.crc(b"\x01\x25\x12"), 1 + 37 + 18)
assert_eq(example.crc(bytearray([1, 37, 18])), 1 + 37 + 18)

with AssertError(TypeError):
    example.crc("\x01\x25\x12")

bb = example.big_bytes(1000)
assert_eq(len(bb), 1000)
assert_eq(bb[556], 556 % 256)

assert_lt(check_memory_deg(lambda: example.big_bytes(1_000_000), 100), 0.2)

assert_eq(example.bytes_mul(b'012', 5), b'012' * 5)
assert_lt(check_memory_deg(lambda: example.bytes_mul(example.big_bytes(1000), 1_000), 100), 0.2)
