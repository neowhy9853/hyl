# PCA-0001: INPUT_CONTRACT_CHANGE - Time.xmlschema whitespace handling
# Tests that leading/trailing whitespace is now correctly stripped

require 'time'

passed = 0
failed = 0

def check(label, expected, actual)
  if expected == actual
    puts "  PASS: #{label}"
    return true
  else
    puts "  FAIL: #{label} - expected #{expected}, got #{actual}"
    return false
  end
end

# Reference time
ref = Time.utc(1985, 4, 12, 23, 20, 50, 520000)

# Test 1: Leading whitespace (spaces + tabs)
t1 = Time.xmlschema("  \t  1985-04-12T23:20:50.52Z")
if check("leading whitespace", ref, t1)
  passed += 1
else
  failed += 1
end

# Test 2: Trailing whitespace (spaces + tabs)
t2 = Time.xmlschema("1985-04-12T23:20:50.52Z  \t ")
if check("trailing whitespace", ref, t2)
  passed += 1
else
  failed += 1
end

# Test 3: Both leading and trailing whitespace
t3 = Time.xmlschema("  1985-04-12T23:20:50.52Z  ")
if check("both leading and trailing whitespace", ref, t3)
  passed += 1
else
  failed += 1
end

# Test 4: No whitespace (should still work as before)
t4 = Time.xmlschema("1985-04-12T23:20:50.52Z")
if check("no whitespace", ref, t4)
  passed += 1
else
  failed += 1
end

# Test 5: Time.iso8601 with leading whitespace
t5 = Time.iso8601("  1985-04-12T23:20:50.52Z")
if check("iso8601 leading whitespace", ref, t5)
  passed += 1
else
  failed += 1
end

# Test 6: Time.rfc3339 with trailing whitespace
t6 = Time.rfc3339("1985-04-12T23:20:50.52Z  ")
if check("rfc3339 trailing whitespace", ref, t6)
  passed += 1
else
  failed += 1
end

# Test 7: Only whitespace (should raise ArgumentError since no actual content)
begin
  Time.xmlschema("   ")
  puts "  FAIL: only whitespace should raise ArgumentError"
  failed += 1
rescue ArgumentError
  puts "  PASS: only whitespace raises ArgumentError"
  passed += 1
end

# Summary
puts
puts "=== Summary ==="
puts "Passed: #{passed}"
puts "Failed: #{failed}"
exit(failed > 0 ? 1 : 0)
