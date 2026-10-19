# Integer#bit_count smoke test
# Validates the new Integer#bit_count method

failures = 0

def assert(desc, actual, expected)
  if actual == expected
    puts "PASS: #{desc}"
    0
  else
    puts "FAIL: #{desc} - expected #{expected.inspect}, got #{actual.inspect}"
    1
  end
end

def assert_raises(desc, exc_class)
  begin
    yield
    puts "FAIL: #{desc} - no exception raised"
    return 1
  rescue exc_class
    puts "PASS: #{desc}"
    return 0
  rescue => e
    puts "FAIL: #{desc} - expected #{exc_class}, got #{e.class}: #{e.message}"
    return 1
  end
end

failures += assert("0.bit_count", 0.bit_count, 0)
failures += assert("1.bit_count", 1.bit_count, 1)
failures += assert("2.bit_count", 2.bit_count, 1)
failures += assert("3.bit_count", 3.bit_count, 2)
failures += assert("7.bit_count", 7.bit_count, 3)
failures += assert("0b10101.bit_count", 0b10101.bit_count, 3)
failures += assert("0xff.bit_count", 0xff.bit_count, 8)
failures += assert("0x100.bit_count", 0x100.bit_count, 1)

# Fixnum boundaries
failures += assert("(2**30).bit_count", (2**30).bit_count, 1)
failures += assert("(2**62).bit_count", (2**62).bit_count, 1)

# Bignum
failures += assert("(2**64).bit_count", (2**64).bit_count, 1)
failures += assert("(2**64-1).bit_count", (2**64-1).bit_count, 64)
failures += assert("(2**1000).bit_count", (2**1000).bit_count, 1)
failures += assert("(2**1000-1).bit_count", (2**1000-1).bit_count, 1000)
failures += assert("(2**1000 + 2**500).bit_count", (2**1000 + 2**500).bit_count, 2)

# Negative numbers raise ArgumentError
failures += assert_raises("-1.bit_count raises ArgumentError", ArgumentError) { -1.bit_count }
failures += assert_raises("-19.bit_count raises ArgumentError", ArgumentError) { -19.bit_count }
failures += assert_raises("(-2**1000).bit_count raises ArgumentError", ArgumentError) { (-2**1000).bit_count }

# Exhaustive check for powers of 2
(0..100).each do |i|
  n = 2**i
  failures += assert("(2**#{i}).bit_count", n.bit_count, 1)
  failures += assert("(2**#{i}-1).bit_count", (n-1).bit_count, i)
  failures += assert("(2**#{i}+1).bit_count", (n+1).bit_count, 2) if i >= 1
end

puts
if failures == 0
  puts "ALL TESTS PASSED"
  exit 0
else
  puts "#{failures} TEST(S) FAILED"
  exit 1
end
