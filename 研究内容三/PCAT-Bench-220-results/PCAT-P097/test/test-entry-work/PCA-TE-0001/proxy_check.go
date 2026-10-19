package main

import (
	"fmt"
	"os"
)

func main() {
	// Test 1: Both uppercase and lowercase set with different values
	os.Setenv("HTTP_PROXY", "http://upper:8080")
	os.Setenv("http_proxy", "http://lower:8080")
	os.Setenv("HTTPS_PROXY", "https://upper:8443")
	os.Setenv("https_proxy", "https://lower:8443")
	os.Setenv("NO_PROXY", "upper.example.com")
	os.Setenv("no_proxy", "lower.example.com")

	httpProxy := os.Getenv("HTTP_PROXY")
	httpProxyLower := os.Getenv("http_proxy")

	fmt.Printf("HTTP_PROXY=%q\n", httpProxy)
	fmt.Printf("http_proxy=%q\n", httpProxyLower)
	fmt.Printf("HTTPS_PROXY=%q\n", os.Getenv("HTTPS_PROXY"))
	fmt.Printf("https_proxy=%q\n", os.Getenv("https_proxy"))
	fmt.Printf("NO_PROXY=%q\n", os.Getenv("NO_PROXY"))
	fmt.Printf("no_proxy=%q\n", os.Getenv("no_proxy"))

	// Verify: Lowercase should take precedence (new behavior)
	// getEnvAny would return the first non-empty value
	// With new behavior: lowercase first
	fmt.Println("\n--- ENV VAR RESOLVED (lowercase-first priority simulation) ---")
	resolve := func(lower, upper string) string {
		if v := os.Getenv(lower); v != "" {
			return v
		}
		return os.Getenv(upper)
	}
	fmt.Printf("Resolved HTTP_PROXY: %q\n", resolve("http_proxy", "HTTP_PROXY"))
	fmt.Printf("Resolved HTTPS_PROXY: %q\n", resolve("https_proxy", "HTTPS_PROXY"))
	fmt.Printf("Resolved NO_PROXY: %q\n", resolve("no_proxy", "NO_PROXY"))

	// Test 2: Only uppercase set
	os.Clearenv()
	os.Setenv("HTTP_PROXY", "http://uonly:8080")
	fmt.Printf("\nOnly uppercase: resolved=%q\n", resolve("http_proxy", "HTTP_PROXY"))

	// Test 3: Only lowercase set
	os.Clearenv()
	os.Setenv("http_proxy", "http://lonly:8080")
	fmt.Printf("Only lowercase: resolved=%q\n", resolve("http_proxy", "HTTP_PROXY"))

	fmt.Println("\nPROXY_ENV_TEST_COMPLETE")
}
