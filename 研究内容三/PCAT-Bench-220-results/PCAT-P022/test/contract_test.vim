" Contract verification script for PCA-0001/PCA-0002
" Tests extend() and extendnew() behavior with NULL second argument
function! RunContractTests()
  let errors = 0
  
  " Test 1: extendnew with null list
  let l = [1, 2, 3]
  let l2 = extendnew(l, test_null_list())
  " New behavior: l2 should be a copy of l ([1, 2, 3])
  " Old behavior: l2 would be garbage/uninitialized
  if type(l2) != v:t_list
    echo "FAIL: extendnew(test_null_list) - l2 is not a list, type=" . type(l2)
    let errors += 1
  else
    echo "PASS: extendnew(test_null_list) returns list"
  endif
  if l2 != [1, 2, 3]
    echo "FAIL: extendnew(test_null_list) - expected [1,2,3], got " . string(l2)
    let errors += 1
  else
    echo "PASS: extendnew(test_null_list) returns correct copy"
  endif
  
  " Test 2: extendnew with null dict
  let d = {'a': 'A', 'b': 9}
  let d2 = extendnew(d, test_null_dict())
  if type(d2) != v:t_dict
    echo "FAIL: extendnew(test_null_dict) - d2 is not a dict, type=" . type(d2)
    let errors += 1
  else
    echo "PASS: extendnew(test_null_dict) returns dict"
  endif
  if d2 != {'a': 'A', 'b': 9}
    echo "FAIL: extendnew(test_null_dict) - expected {'a':'A','b':9}, got " . string(d2)
    let errors += 1
  else
    echo "PASS: extendnew(test_null_dict) returns correct copy"
  endif
  
  " Test 3: extend with null list (mutating)
  let l3 = [1, 2, 3]
  call extend(l3, test_null_list())
  if l3 != [1, 2, 3]
    echo "FAIL: extend(test_null_list) - expected [1,2,3], got " . string(l3)
    let errors += 1
  else
    echo "PASS: extend(test_null_list) preserves original"
  endif
  
  " Test 4: extend with null dict (mutating)
  let d3 = {'a': 'A', 'b': 9}
  call extend(d3, test_null_dict())
  if d3 != {'a': 'A', 'b': 9}
    echo "FAIL: extend(test_null_dict) - expected {'a':'A','b':9}, got " . string(d3)
    let errors += 1
  else
    echo "PASS: extend(test_null_dict) preserves original"
  endif
  
  " Test 5: extend empty list to list
  let l4 = [1, 2, 3]
  call extend(l4, [])
  if l4 != [1, 2, 3]
    echo "FAIL: extend([]) - expected [1,2,3], got " . string(l4)
    let errors += 1
  else
    echo "PASS: extend([]) works correctly"
  endif
  
  " Test 6: extend empty dict to dict
  let d4 = {'a': 'A'}
  call extend(d4, {})
  if d4 != {'a': 'A'}
    echo "FAIL: extend({}) - expected {'a':'A'}, got " . string(d4)
    let errors += 1
  else
    echo "PASS: extend({}) works correctly"
  endif
  
  if errors == 0
    echo "ALL CONTRACT TESTS PASSED"
  else
    echo "FAILED: " . errors . " contract test(s) failed"
  endif
  cq
endfunction

call RunContractTests()
