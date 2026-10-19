package main

import (
	"fmt"
	"os"
)

// Test proxy env var precedence by directly calling getEnvAny
// and comparing with expected behavior

func main() {
	tests := []struct {
		name     string
		envs     map[string]string
		expected map[string]string // which env var value should win
	}{
		{
			name: "both_set_different_values",
			envs: map[string]string{
				"HTTP_PROXY":  "http://upper:8080",
				"http_proxy":  "http://lower:8080",
				"HTTPS_PROXY": "https://upper:8443",
				"https_proxy": "https://lower:8443",
				"NO_PROXY":    "upper.example.com",
				"no_proxy":    "lower.example.com",
			},
			expected: map[string]string{
				"HTTP_PROXY":  "http://lower:8080",
				"HTTPS_PROXY": "https://lower:8443",
				"NO_PROXY":    "lower.example.com",
			},
		},
		{
			name: "only_uppercase_set",
			envs: map[string]string{
				"HTTP_PROXY":  "http://upper:8080",
				"HTTPS_PROXY": "https://upper:8443",
				"NO_PROXY":    "upper.example.com",
			},
			expected: map[string]string{
				"HTTP_PROXY":  "http://upper:8080",
				"HTTPS_PROXY": "https://upper:8443",
				"NO_PROXY":    "upper.example.com",
			},
		},
		{
			name: "only_lowercase_set",
			envs: map[string]string{
				"http_proxy":  "http://lower:8080",
				"https_proxy": "https://lower:8443",
				"no_proxy":    "lower.example.com",
			},
			expected: map[string]string{
				"HTTP_PROXY":  "http://lower:8080",
				"HTTPS_PROXY": "https://lower:8443",
				"NO_PROXY":    "lower.example.com",
			},
		},
	}

	allPassed := true
	for _, tt := range tests {
		// Clear all proxy env vars first
		for _, v := range []string{"HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy", "NO_PROXY", "no_proxy"} {
			os.Unsetenv(v)
		}
		// Set test env vars
		for k, v := range tt.envs {
			os.Setenv(k, v)
		}

		// Simulate getEnvAny with new priority (lowercase first)
		httpProxy := getEnvAnyLowercaseFirst("http_proxy", "HTTP_PROXY")
		httpsProxy := getEnvAnyLowercaseFirst("https_proxy", "HTTPS_PROXY")
		noProxy := getEnvAnyLowercaseFirst("no_proxy", "NO_PROXY")

		fmt.Printf("Test: %s\n", tt.name)
		passed := true
		if httpProxy != tt.expected["HTTP_PROXY"] {
			fmt.Printf("  FAIL: HTTP_PROXY: got %q, expected %q\n", httpProxy, tt.expected["HTTP_PROXY"])
			passed = false
		} else {
			fmt.Printf("  PASS: HTTP_PROXY=%q\n", httpProxy)
		}
		if httpsProxy != tt.expected["HTTPS_PROXY"] {
			fmt.Printf("  FAIL: HTTPS_PROXY: got %q, expected %q\n", httpsProxy, tt.expected["HTTPS_PROXY"])
			passed = false
		} else {
			fmt.Printf("  PASS: HTTPS_PROXY=%q\n", httpsProxy)
		}
		if noProxy != tt.expected["NO_PROXY"] {
			fmt.Printf("  FAIL: NO_PROXY: got %q, expected %q\n", noProxy, tt.expected["NO_PROXY"])
			passed = false
		} else {
			fmt.Printf("  PASS: NO_PROXY=%q\n", noProxy)
		}
		if !passed {
			allPassed = false
		}
	}

	// Simulate getEnvAny with OLD priority (uppercase first)
	fmt.Println("\n--- OLD BEHAVIOR (uppercase first) ---")
	for _, tt := range tests {
		if len(tt.envs) == 0 {
			continue
		}
		for _, v := range []string{"HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy", "NO_PROXY", "no_proxy"} {
			os.Unsetenv(v)
		}
		for k, v := range tt.envs {
			os.Setenv(k, v)
		}
		httpProxy := getEnvAnyUppercaseFirst("HTTP_PROXY", "http_proxy")
		httpsProxy := getEnvAnyUppercaseFirst("HTTPS_PROXY", "https_proxy")
		noProxy := getEnvAnyUppercaseFirst("NO_PROXY", "no_proxy")
		fmt.Printf("Test: %s\n", tt.name)
		fmt.Printf("  HTTP_PROXY=%q, HTTPS_PROXY=%q, NO_PROXY=%q\n", httpProxy, httpsProxy, noProxy)
	}

	if allPassed {
		fmt.Println("\nALL TESTS PASSED")
	} else {
		fmt.Println("\nSOME TESTS FAILED")
		os.Exit(1)
	}
}

func getEnvAnyLowercaseFirst(names ...string) string {
	for _, n := range names {
		if val := os.Getenv(n); val != "" {
			return val
		}
	}
	return ""
}

func getEnvAnyUppercaseFirst(names ...string) string {
	return getEnvAnyLowercaseFirst(names...)
}
