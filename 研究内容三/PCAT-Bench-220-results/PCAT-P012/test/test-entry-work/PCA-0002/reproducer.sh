#!/bin/bash
# PCA-0002: INPUT_CONTRACT_CHANGE - Relay option iteration bounds checking
# Tests: Send truncated DHCPv6 RELAY-FORW messages to verify safe handling

set -euo pipefail

echo "=== PCA-0002: DHCPv6 RELAY-FORW truncated message test ==="
echo ""
echo "This test requires raw packet crafting capability."
echo ""
echo "To test manually:"
echo " 1. Build scapy script to craft DHCPv6 RELAY-FORW with sz between 4-36"
echo " 2. Start dnsmasq (before/after) in network namespace"
echo " 3. Send truncated RELAY-FORW:"
echo "    - sz=4: minimal header (msg_type + trans_id)"  
echo "    - sz=10: partial header"
echo "    - sz=34: no options section (opts == end)"
echo "    - sz=36: options start just past end"
echo "    - sz=37: minimum valid RELAY-FORW"
echo " 4. Before: expected potential crash"
echo " 5. After: expected clean handling (return 0 or graceful skip)"
echo " 6. Run gcov to verify opt6_first() on line 2118-2136 was exercised"
echo ""
echo "=== Skipped: requires raw socket / network namespace ==="
exit 0
