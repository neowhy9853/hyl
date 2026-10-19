package main

import (
	"fmt"
	"net/http"
	"os"
)

func main() {
	p := http.NewCrossOriginProtection()
	fail := false

	test := func(origin string, wantErr bool, desc string) {
		err := p.AddTrustedOrigin(origin)
		gotErr := err != nil
		status := "PASS"
		if gotErr != wantErr {
			status = "FAIL"
			fail = true
		}
		if gotErr {
			fmt.Printf("%s: %s AddTrustedOrigin(%q) error=%v (wantErr=%v)\n", status, desc, origin, err, wantErr)
		} else {
			fmt.Printf("%s: %s AddTrustedOrigin(%q) accepted (wantErr=%v)\n", status, desc, origin, wantErr)
		}
	}

	// Valid origins (should be accepted)
	test("https://example.com", false, "valid origin")
	test("https://example.com:8080", false, "valid origin with port")
	test("http://example.com", false, "http origin")

	// Invalid origins - userinfo (should be rejected per new behavior)
	test("https://@example.com", true, "empty userinfo")
	test("https://user:pass@example.com", true, "nonempty userinfo")
	test("https://user@example.com", true, "username only")

	// Invalid origins - path/query/fragment (should still be rejected)
	test("https://example.com/", true, "trailing slash")
	test("https://example.com/path", true, "with path")
	test("https://example.com?query=value", true, "with query")
	test("https://example.com#fragment", true, "with fragment")

	// Invalid origins - missing scheme/host
	test("example.com", true, "missing scheme")
	test("https://", true, "missing host")
	test("", true, "empty string")

	if fail {
		fmt.Println("\nOVERALL: FAIL")
		os.Exit(1)
	}
	fmt.Println("\nOVERALL: PASS")
}
