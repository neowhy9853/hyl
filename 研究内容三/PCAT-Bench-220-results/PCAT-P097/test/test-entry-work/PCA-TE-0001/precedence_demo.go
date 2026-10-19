package main

import (
	"fmt"
	"os"
)

func main() {
	// Read from the vendored httpproxy proxy.go getEnvAny function
	// var names order matters! The first non-empty value is used.
	
	// Set both uppercase and lowercase with different values
	os.Setenv("HTTP_PROXY", "http://UPPER-CASE:3128")
	os.Setenv("http_proxy", "http://lower-case:3128")
	os.Setenv("HTTPS_PROXY", "https://UPPER-CASE:8443")
	os.Setenv("https_proxy", "https://lower-case:8443")
	os.Setenv("NO_PROXY", "UPPER.example.com")
	os.Setenv("no_proxy", "lower.example.com")

	// Demonstrate what getEnvAny does in both orders
	fmt.Println("=== getEnvAny with NEW priority (lowercase first) ===")
	fmt.Printf("getEnvAny(\"http_proxy\", \"HTTP_PROXY\")  = %q\n", getEnvAny("http_proxy", "HTTP_PROXY"))
	fmt.Printf("getEnvAny(\"https_proxy\", \"HTTPS_PROXY\") = %q\n", getEnvAny("https_proxy", "HTTPS_PROXY"))
	fmt.Printf("getEnvAny(\"no_proxy\", \"NO_PROXY\")      = %q\n", getEnvAny("no_proxy", "NO_PROXY"))
	
	fmt.Println()
	fmt.Println("=== getEnvAny with OLD priority (uppercase first) ===")
	fmt.Printf("getEnvAny(\"HTTP_PROXY\", \"http_proxy\")  = %q\n", getEnvAny("HTTP_PROXY", "http_proxy"))
	fmt.Printf("getEnvAny(\"HTTPS_PROXY\", \"https_proxy\") = %q\n", getEnvAny("HTTPS_PROXY", "https_proxy"))
	fmt.Printf("getEnvAny(\"NO_PROXY\", \"no_proxy\")      = %q\n", getEnvAny("NO_PROXY", "no_proxy"))
	
	fmt.Println()
	fmt.Println("=== COMPATIBILITY ASSESSMENT ===")
	fmt.Println("PATCH changes proxy env var priority from uppercase-first to lowercase-first.")
	fmt.Println("When both are set with different values, the resolved proxy changes.")
	
	// Verify: the actual change in the vendored code
	// Old: getEnvAny("HTTP_PROXY", "http_proxy") -> returns uppercase value
	// New: getEnvAny("http_proxy", "HTTP_PROXY") -> returns lowercase value
	if getEnvAny("http_proxy", "HTTP_PROXY") != getEnvAny("HTTP_PROXY", "http_proxy") {
		fmt.Println("BEHAVIOR CHANGE CONFIRMED: old and new resolution differ!")
		os.Exit(0)
	} else {
		fmt.Println("No difference detected (both env vars have same value)")
		os.Exit(0)
	}
}

func getEnvAny(names ...string) string {
	for _, n := range names {
		if val := os.Getenv(n); val != "" {
			return val
		}
	}
	return ""
}
