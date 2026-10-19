package main

import (
	"bytes"
	"crypto/tls"
	"slices"
	"testing"
)

var testCert = testingCert(&testingKey)
var testKey = testingKey

func testingKey() tls.Certificate {
	cert, _ := tls.X509KeyPair([]byte(testingCertPEM), []byte(testingKeyPEM))
	return cert
}

func testingCert(key *tls.Certificate) tls.Certificate {
	c, _ := tls.X509KeyPair([]byte(testingCertPEM), []byte(testingKeyPEM))
	return c
}

func testLocalCertificateTLS12(t *testing.T, isServer bool) {
	cert := testCert
	clientConfig := &tls.Config{
		InsecureSkipVerify: true,
		MinVersion:         tls.VersionTLS12,
		MaxVersion:         tls.VersionTLS12,
	}
	serverConfig := &tls.Config{
		MinVersion: tls.VersionTLS12,
		MaxVersion: tls.VersionTLS12,
	}

	serverConfig.Certificates = []tls.Certificate{cert}
	serverConfig.ClientAuth = tls.RequestClientCert

	clientConfig.Certificates = []tls.Certificate{cert}

	client, server := netPipe()
	defer client.Close()
	defer server.Close()

	var serverState, clientState tls.ConnectionState
	done := make(chan error, 1)
	go func() {
		s := tls.Server(server, serverConfig)
		err := s.Handshake()
		serverState = s.ConnectionState()
		done <- err
	}()

	c := tls.Client(client, clientConfig)
	if err := c.Handshake(); err != nil {
		t.Fatalf("client handshake: %v", err)
	}
	clientState = c.ConnectionState()
	if err := <-done; err != nil {
		t.Fatalf("server handshake: %v", err)
	}

	if isServer {
		_ = serverState
		_ = clientState
	}
}

func TestLocalCertificateTLS12(t *testing.T) {
	testLocalCertificateTLS12(t, true)
}
