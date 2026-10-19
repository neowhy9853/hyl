#!/bin/bash
# PCA-0001: Test dnsmasq auth zone NS response behavior
# Tests if secondary forward server NS records have correct owner names

set -e

BINARY="$1"
LABEL="$2"
TEST_DIR="$3"

if [ -z "$BINARY" ] || [ -z "$LABEL" ]; then
    echo "Usage: $0 <binary> <label> [test_dir]"
    exit 1
fi

CONF_DIR="${TEST_DIR:-/tmp}/dnsmasq-test-$$"
mkdir -p "${CONF_DIR}"

# Zone file for test.zone
cat > "${CONF_DIR}/test.zone" << 'EOF'
test.zone 3600 IN SOA ns1.test.zone admin.test.zone 2026000001 3600 900 86400 3600
test.zone 3600 IN NS ns1.test.zone
test.zone 3600 IN NS ns2.test.zone
ns1.test.zone 3600 IN A 192.0.2.1
ns2.test.zone 3600 IN A 192.0.2.2
EOF

# Clean up function
cleanup() {
    kill $DMS_PID 2>/dev/null || true
    rm -rf "${CONF_DIR}"
    echo "--- ${LABEL}: cleanup done"
}

trap cleanup EXIT INT TERM

# Start dnsmasq with auth zone config
# --auth-server=ns1.test.zone (no interface = zone transfer only)
# --auth-sec-servers=ns2.test.zone (secondary forward server)
# --auth-zone=test.zone defines the zone
$BINARY \
    --port=15353 \
    --no-daemon \
    --log-queries \
    --log-facility=- \
    --user=root \
    --auth-server=ns1.test.zone \
    --auth-sec-servers=ns2.test.zone \
    --auth-zone=test.zone \
    --auth-soa=2026000001,3600,900,86400,3600 \
    --auth-ttl=3600 \
    2>&1 &
DMS_PID=$!
sleep 1

# Check if dnsmasq started
if ! kill -0 ${DMS_PID} 2>/dev/null; then
    echo "--- ${LABEL}: dnsmasq failed to start"
    echo "BINARY: ${BINARY}"
    wait ${DMS_PID} 2>/dev/null || true
    exit 1
fi

echo "--- ${LABEL}: dnsmasq started (PID=${DMS_PID})"

# Use socat/netcat to send a DNS query for NS record of test.zone
# We'll use a hex-encoded DNS query since dig may not be available
echo "--- ${LABEL}: Attempting DNS query via socat"

# DNS query: test.zone NS type
# Header: ID=0x0001, flags=0x0100 (standard query, RD=0), QDCOUNT=1, ANCOUNT=0, NSCOUNT=0, ARCOUNT=0
# Question: test.zone (7 chars: t e s t . z o n e) NS type(0x0002) class IN(0x0001)
# 
# Wire format:
# 0001 0100 0001 0000 0000 0000
# 0474657374 057a6f6e6500 0002 0001
#
# Where:
# 0474657374 = 4 + "test"
# 057a6f6e65 = 5 + "zone"
# 00 = root terminator
# 0002 = NS type
# 0001 = IN class

# Try using /dev/udp if available (bash has it)
echo -n '
0001 0100 0001 0000 0000 0000
0474657374 057a6f6e6500 0002 0001
' | xxd -r -p | timeout 3 socat - UDP:127.0.0.1:15353 2>/dev/null | xxd | head -20 || true

# Try with netcat too
echo -n '
0001 0100 0001 0000 0000 0000
0474657374 057a6f6e6500 0002 0001
' | xxd -r -p | timeout 3 nc -u -w2 127.0.0.1 15353 2>/dev/null | xxd | head -20 || echo "--- ${LABEL}: netcat query failed/timed out"

echo "--- ${LABEL}: stopping dnsmasq"
kill ${DMS_PID} 2>/dev/null
wait ${DMS_PID} 2>/dev/null || true

echo "--- ${LABEL}: test complete"
