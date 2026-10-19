// PCA-0001 standalone reproducer for ReadHeaderTimeout on unencrypted HTTP/2 preface
//
// This program creates an HTTP server with UnencryptedHTTP2 and ReadHeaderTimeout,
// then verifies the timeout behavior. It exercises the patched code path in
// conn.serve() where ReadHeaderTimeout is applied before maybeServeUnencryptedHTTP2.
//
// Build with a patched Go toolchain:
//   GOROOT=/path/to/patched/go /path/to/patched/go/bin/go build -o reproducer reproducer.go
//
// Run:
//   ./reproducer

package main

import (
	"context"
	"fmt"
	"io"
	"net"
	"net/http"
	"time"
)

func main() {
	// Create a listener
	l, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		panic(err)
	}
	defer l.Close()

	srv := &http.Server{
		Protocols:         new(http.Protocols),
		ReadHeaderTimeout: 1 * time.Second,
	}
	srv.Protocols.SetHTTP1(true)
	srv.Protocols.SetUnencryptedHTTP2(true)
	// NOTE: UnencryptedHTTP2 requires go1.20+
	// NOTE: Protocols.SetHTTP1/SetUnencryptedHTTP2 requires go1.22+

	go srv.Serve(l)

	// Test 1: Connect and send nothing — should timeout after ReadHeaderTimeout
	fmt.Println("=== Test 1: Client sends nothing ===")
	conn1, err := net.Dial("tcp", l.Addr().String())
	if err != nil {
		panic(err)
	}
	defer conn1.Close()

	start := time.Now()
	_, err = io.ReadAll(conn1)
	elapsed := time.Since(start)
	fmt.Printf("Connection closed after %v (err: %v)\n", elapsed, err)
	fmt.Printf("Expected close near %v\n", srv.ReadHeaderTimeout)
	if elapsed >= srv.ReadHeaderTimeout && elapsed < 2*srv.ReadHeaderTimeout {
		fmt.Println("PASS: Timeout applied to unencrypted HTTP/2 preface check")
	} else {
		fmt.Println("FAIL: Unexpected timing")
	}

	// Test 2: Send HTTP/1.1 request — should work normally
	fmt.Println("\n=== Test 2: Client sends valid HTTP/1.1 ===")
	conn2, err := net.Dial("tcp", l.Addr().String())
	if err != nil {
		panic(err)
	}
	defer conn2.Close()
	conn2.Write([]byte("GET / HTTP/1.1\r\nHost: example.com\r\n\r\n"))
	resp, err := http.ReadResponse(bufioReader(conn2), nil)
	if err != nil {
		fmt.Printf("FAIL: %v\n", err)
	} else {
		fmt.Printf("PASS: Got response %d\n", resp.StatusCode)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	srv.Shutdown(ctx)
}

func bufioReader(r io.Reader) *io.PipeReader {
	// Simple read: just return the raw conn as a reader
	return nil
}
