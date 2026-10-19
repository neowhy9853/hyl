package main

import (
	"bytes"
	"fmt"
	"io"
	"net"
	"net/http"
	"os"
	"strings"
	"time"
)

func main() {
	os.Exit(run())
}

func run() int {
	// Start an HTTP server that responds with 200 immediately,
	// without sending 100 Continue, for Expect: 100-continue requests.
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Write final status immediately - skip 100 Continue
		w.WriteHeader(http.StatusOK)
		// Try to read body - should not hang after patch
		body, err := io.ReadAll(r.Body)
		if err != nil {
			fmt.Fprintf(os.Stderr, "read body error: %v\n", err)
		}
		fmt.Fprintf(os.Stderr, "server: handler complete, body=%q\n", string(body))
	})

	// Create a listener on a random port
	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		fmt.Fprintf(os.Stderr, "listen error: %v\n", err)
		return 1
	}
	addr := listener.Addr().String()

	server := &http.Server{Handler: handler}
	serverDone := make(chan error, 1)
	go func() {
		serverDone <- server.Serve(listener)
	}()

	// Give server time to start
	time.Sleep(100 * time.Millisecond)

	// Create client request with Expect: 100-continue
	body := strings.NewReader("some body")
	req, err := http.NewRequest("POST", "http://"+addr+"/", body)
	if err != nil {
		fmt.Fprintf(os.Stderr, "new request error: %v\n", err)
		server.Close()
		return 1
	}
	req.Header.Set("Expect", "100-continue")

	client := &http.Client{
		Timeout: 5 * time.Second,
		Transport: &http.Transport{
			ExpectContinueTimeout: 10 * time.Second,
		},
	}

	start := time.Now()
	resp, err := client.Do(req)
	elapsed := time.Since(start)

	if err != nil {
		if strings.Contains(err.Error(), "timeout") || strings.Contains(err.Error(), "deadline") {
			fmt.Fprintf(os.Stderr, "HANG DETECTED: request timed out after %v: %v\n", elapsed, err)
			fmt.Println("RESULT: hang (old behavior)")
			server.Close()
			return 2
		}
		fmt.Fprintf(os.Stderr, "request error after %v: %v\n", elapsed, err)
		return 1
	}
	defer resp.Body.Close()

	// Read response
	respBody, _ := io.ReadAll(resp.Body)

	// Check for Connection: close header
	connHeader := resp.Header.Get("Connection")
	hasClose := connHeader == "close"

	fmt.Fprintf(os.Stderr, "response: status=%d, elapsed=%v, connection=%q\n",
		resp.StatusCode, elapsed, connHeader)

	if hasClose {
		fmt.Printf("RESULT: ok (fixed behavior) - status=%d elapsed=%v connection=close\n",
			resp.StatusCode, elapsed)
	} else {
		fmt.Printf("RESULT: ok (fixed behavior) - status=%d elapsed=%v connection=%q no_close\n",
			resp.StatusCode, elapsed, connHeader)
	}

	// Verify response
	if resp.StatusCode != http.StatusOK {
		fmt.Fprintf(os.Stderr, "expected 200 OK, got %d\n", resp.StatusCode)
		return 1
	}

	buf := new(bytes.Buffer)
	buf.ReadFrom(resp.Body)
	_ = respBody

	server.Close()
	<-serverDone

	return 0
}
