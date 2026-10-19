#!/usr/bin/env python3
"""
PCA-0001 Test: Non-QUERY TCP request forwarding behavior change

This test sends a non-QUERY DNS request (NOTIFY, opcode=4) over TCP
to dnsmasq and observes how it's handled:
- Before patch: request enters forwarding logic (flags guard missing)
- After patch:  request gets RCODE rejection (!flags guard prevents forwarding)

Usage:
  python3 reproducer.py <before_dnsmasq> <after_dnsmasq> <port>
"""

import socket
import struct
import sys
import subprocess
import tempfile
import os
import time
import signal

def make_dns_notify_tcp(transaction_id=0x1234):
    """
    Construct a DNS NOTIFY request (opcode=4) over TCP wire format.
    NOTIFY uses the same header structure as QUERY but with OPCODE=4.
    The question section contains the zone being notified about.
    """
    tid = transaction_id
    flags = 0x0000  # Standard query, OPCODE=4 in header byte
    
    # Build header: ID + flags + counts
    # flags byte 0: QR=0 (query), OPCODE=4 (NOTIFY)
    # flags byte 1: RD=0 (no recursion desired)
    hdr_flags = (4 << 11)  # OPCODE=4 is NOTIFY
    # QR=0 (bit 15), OPCODE=4 (bits 14-11)
    
    # Header: ID (2) + flags (2) + QDCOUNT (2) + ANCOUNT (2) + NSCOUNT (2) + ARCOUNT (2)
    header = struct.pack('!HHHHHH',
        tid,           # Transaction ID
        hdr_flags,     # Flags
        1,             # QDCOUNT = 1 question
        0,             # ANCOUNT
        0,             # NSCOUNT
        0              # ARCOUNT
    )
    
    # Question: example.com (type SOA, class IN)
    qname = b'\x07example\x03com\x00'  # example.com
    qtype = 6   # SOA (type for NOTIFY)
    qclass = 1  # IN
    
    question = qname + struct.pack('!HH', qtype, qclass)
    
    dns_msg = header + question
    
    # TCP wire format: 2-byte length prefix + DNS message
    return struct.pack('!H', len(dns_msg)) + dns_msg

def make_dns_notify_udp(transaction_id=0x1234):
    """Same but without TCP length prefix."""
    tid = transaction_id
    hdr_flags = (4 << 11)  # OPCODE=4 is NOTIFY
    header = struct.pack('!HHHHHH',
        tid,
        hdr_flags,
        1, 0, 0, 0
    )
    qname = b'\x07example\x03com\x00'
    qtype = 6
    qclass = 1
    question = qname + struct.pack('!HH', qtype, qclass)
    return header + question

def send_tcp_dns(host, port, packet):
    """Send DNS request over TCP and get response."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect((host, port))
        sock.sendall(packet)
        # Read response length
        resp_len_bytes = sock.recv(2)
        if len(resp_len_bytes) < 2:
            return b'', 0
        resp_len = struct.unpack('!H', resp_len_bytes)[0]
        # Read response
        resp = b''
        while len(resp) < resp_len:
            chunk = sock.recv(resp_len - len(resp))
            if not chunk:
                break
            resp += chunk
        return resp, resp_len
    except socket.timeout:
        return b'', -1
    except ConnectionRefusedError:
        return b'', -2
    except Exception as e:
        return b'', -3
    finally:
        sock.close()

def parse_dns_header(data):
    """Parse DNS header and return (id, flags, qdcount, ancount, nscount, arcount)"""
    if len(data) < 12:
        return None
    hdr = struct.unpack('!HHHHHH', data[:12])
    return hdr

def opcode_from_flags(flags):
    """Extract OPCODE from DNS flags."""
    return (flags >> 11) & 0xF

def rcode_from_flags(flags):
    """Extract RCODE from DNS flags."""
    return flags & 0xF

def test_dnsmasq(binary_path, port, timeout=10):
    """
    Start dnsmasq with a simple config, send a non-QUERY TCP request,
    and return the response info.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        conf_path = os.path.join(tmpdir, "dnsmasq.conf")
        lease_path = os.path.join(tmpdir, "dnsmasq.leases")
        pid_path = os.path.join(tmpdir, "dnsmasq.pid")
        
        # Minimal config - listen on high port, no upstream forwarders
        # Use --no-daemon and --keep-in-foreground for immediate response
        # Add --log-facility=- for stderr logging
        config = f"""port={port}
interface=lo
bind-interfaces
except-interface=
no-daemon
no-hosts
no-resolv
log-facility=-
log-queries
"""
        with open(conf_path, 'w') as f:
            f.write(config)
        
        # Start dnsmasq
        proc = subprocess.Popen(
            [binary_path, "-C", conf_path, "-l", lease_path,
             "--pid-file=" + pid_path, "--no-daemon",
             "--log-queries", "--log-facility=-"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            preexec_fn=lambda: os.setsid() if hasattr(os, 'setsid') else None
        )
        
        # Wait for startup (check stderr for "started" message)
        start_time = time.time()
        stdout_lines = []
        stderr_lines = []
        
        # Give it time to start
        time.sleep(0.5)
        
        result = {
            'binary': binary_path,
            'port': port,
            'response': None,
            'opcode': None,
            'rcode': None,
            'response_len': 0,
            'exit_code': None,
            'stdout': '',
            'stderr': ''
        }
        
        try:
            # Send non-QUERY TCP request
            packet = make_dns_notify_tcp(0x5678)
            resp, resp_len = send_tcp_dns("127.0.0.1", port, packet)
            
            result['response_len'] = resp_len
            
            if resp_len > 0:
                hdr = parse_dns_header(resp)
                if hdr:
                    result['response'] = resp.hex()
                    result['tid'] = hdr[0]
                    result['flags'] = hdr[1]
                    result['opcode'] = opcode_from_flags(hdr[1])
                    result['rcode'] = rcode_from_flags(hdr[1])
                    result['ancount'] = hdr[3]
            elif resp_len == -1:
                result['error'] = 'timeout'
            elif resp_len == -2:
                result['error'] = 'connection_refused'
            elif resp_len == -3:
                result['error'] = 'socket_error'
                
        except Exception as e:
            result['error'] = str(e)
        finally:
            # Kill dnsmasq
            if proc.poll() is None:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                    proc.wait()
            
            # Collect output
            out, err = proc.communicate(timeout=2)
            result['stdout'] = out.decode('utf-8', errors='replace')
            result['stderr'] = err.decode('utf-8', errors='replace')
            result['exit_code'] = proc.returncode
        
        return result

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 reproducer.py <before_binary> <after_binary> <port>")
        sys.exit(1)
    
    before_bin = sys.argv[1]
    after_bin = sys.argv[2]
    port = int(sys.argv[3])
    
    print(f"Testing BEFORE binary: {before_bin}")
    print(f"Testing AFTER  binary: {after_bin}")
    print(f"Using port: {port}")
    print()
    
    before_result = test_dnsmasq(before_bin, port + 1)
    after_result = test_dnsmasq(after_bin, port + 2)
    
    print("=== BEFORE (baseline) ===")
    print(f"  Response length: {before_result['response_len']}")
    if 'error' in before_result:
        print(f"  Error: {before_result['error']}")
    else:
        print(f"  Response OPCODE: {before_result.get('opcode')} (QUERY=0, NOTIFY=4)")
        print(f"  RCODE: {before_result.get('rcode')}")
        print(f"  Answer count: {before_result.get('ancount')}")
    if before_result.get('stderr'):
        # Show last few lines of log
        lines = before_result['stderr'].split('\n')
        relevant = [l for l in lines if 'forward' in l.lower() or 'query' in l.lower() or 'rcode' in l.lower() or 'notify' in l.lower() or 'opcode' in l.lower()]
        if relevant:
            print("  Relevant logs:")
            for l in relevant[-5:]:
                print(f"    {l.strip()}")
    
    print()
    print("=== AFTER (patched) ===")
    print(f"  Response length: {after_result['response_len']}")
    if 'error' in after_result:
        print(f"  Error: {after_result['error']}")
    else:
        print(f"  Response OPCODE: {after_result.get('opcode')} (QUERY=0, NOTIFY=4)")
        print(f"  RCODE: {after_result.get('rcode')}")
        print(f"  Answer count: {after_result.get('ancount')}")
    if after_result.get('stderr'):
        lines = after_result['stderr'].split('\n')
        relevant = [l for l in lines if 'forward' in l.lower() or 'query' in l.lower() or 'rcode' in l.lower() or 'notify' in l.lower() or 'opcode' in l.lower()]
        if relevant:
            print("  Relevant logs:")
            for l in relevant[-5:]:
                print(f"    {l.strip()}")
    
    print()
    
    # Compare
    if before_result.get('opcode') is not None:
        print(f"BEFORE: OPCODE={before_result['opcode']}, RCODE={before_result.get('rcode')}, ancount={before_result.get('ancount')}")
    else:
        print(f"BEFORE: error={before_result.get('error', 'unknown')}")
    
    if after_result.get('opcode') is not None:
        print(f"AFTER:  OPCODE={after_result['opcode']}, RCODE={after_result.get('rcode')}, ancount={after_result.get('ancount')}")
    else:
        print(f"AFTER:  error={after_result.get('error', 'unknown')}")
    
    # Determine result
    print()
    if 'error' in before_result and 'error' in after_result:
        if before_result['error'] == after_result['error']:
            print("RESULT: IDENTICAL (both failed same way)")
        else:
            print("RESULT: DIFFERENT (different error modes)")
    elif 'error' in before_result and 'error' not in after_result:
        print("RESULT: DIFFERENT (before failed, after succeeded)")
    elif 'error' not in before_result and 'error' in after_result:
        print("RESULT: DIFFERENT (before succeeded, after failed)")
    else:
        same_rcode = before_result.get('rcode') == after_result.get('rcode')
        same_opcode = before_result.get('opcode') == after_result.get('opcode')
        if same_opcode and same_rcode:
            print("RESULT: IDENTICAL behavior (same opcode and rcode)")
        else:
            print("DIFFERENT behavior (opcode or rcode changed)")
            print("  -> This confirms PCA-0001: non-QUERY TCP handling changed")

if __name__ == '__main__':
    main()
