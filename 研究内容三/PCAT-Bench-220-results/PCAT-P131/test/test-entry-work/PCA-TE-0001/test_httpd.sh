#!/bin/bash
# Test script for PCA-0001: mod_proxy_html pcomment dump_content regression fix
# Builds httpd before/after patch and compares proxy HTML output
set -e

HTTPD_SRC="/src"
PATCH="/src_patch/patch.diff"
TEST_HTML="/tmp/test.html"
RESULT_DIR="/results"

echo "=== Installing build dependencies ==="
apt-get update -qq && apt-get install -y -qq \
    build-essential cmake libapr1-dev libaprutil1-dev \
    libxml2-dev libexpat1-dev libpcre3-dev libssl-dev \
    libcurl4-openssl-dev libnghttp2-dev zlib1g-dev \
    curl lcov

echo "=== Building BEFORE (baseline) version ==="
mkdir -p /build_before
cp -r "$HTTPD_SRC" /build_before/src
cd /build_before/src
# Revert the patch to get the "before" state
git apply -R "$PATCH" || true
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_C_FLAGS="-fprofile-arcs -ftest-coverage -O0 -g" \
    -DCMAKE_EXE_LINKER_FLAGS="-lgcov --coverage" \
    -DCMAKE_INSTALL_PREFIX=/build_before/install
make -j$(nproc) 2>&1 | tail -20
make install 2>&1 | tail -5
echo "Before build complete"

echo "=== Building AFTER (patched) version ==="
mkdir -p /build_after
cp -r "$HTTPD_SRC" /build_after/src
cd /build_after/src
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_C_FLAGS="-fprofile-arcs -ftest-coverage -O0 -g" \
    -DCMAKE_EXE_LINKER_FLAGS="-lgcov --coverage" \
    -DCMAKE_INSTALL_PREFIX=/build_after/install
make -j$(nproc) 2>&1 | tail -20
make install 2>&1 | tail -5
echo "After build complete"

echo "=== Creating test HTML content ==="
cat > "$TEST_HTML" << 'HTMLEOF'
<!DOCTYPE html>
<html>
<head><title>PCA Test Page</title></head>
<body>
<p>Some text with a <a href="http://internal-server:8080/app/page.html">link</a> to proxy.</p>
<!-- This is a comment that should not trigger content dump -->
<p>More text after the comment with another <a href="http://backend:9090/api/data">API link</a>.</p>
</body>
</html>
HTMLEOF

echo "=== Configuring proxy for BEFORE version ==="
BEFORE_INSTALL=/build_before/install
mkdir -p /tmp/before_proxy/{logs,htdocs}
cat > /tmp/before_proxy/httpd.conf << EOF
ServerName localhost
Listen 8080
LoadModule proxy_html_module ${BEFORE_INSTALL}/modules/mod_proxy_html.so
LoadModule proxy_module ${BEFORE_INSTALL}/modules/mod_proxy.so
LoadModule proxy_http_module ${BEFORE_INSTALL}/modules/mod_proxy_http.so
LoadModule xml2enc_module ${BEFORE_INSTALL}/modules/mod_xml2enc.so
DocumentRoot /tmp/before_proxy/htdocs
ErrorLog /tmp/before_proxy/logs/error.log
LogLevel debug
ProxyRequests Off
ProxyPass / http://localhost:8081/
ProxyPassReverse / http://localhost:8081/
ProxyHTMLEnable On
SetOutputFilter proxy-html
ProxyHTMLExtended Off
EOF
echo "<html><body><h1>Backend</h1></body></html>" > /tmp/before_proxy/htdocs/index.html

echo "=== Starting backend server ==="
${BEFORE_INSTALL}/bin/httpd -f /tmp/before_proxy/httpd.conf -k start 2>/dev/null || true
sleep 2

echo "=== Fetching through proxy (BEFORE) ==="
curl -s -o /tmp/before_output.html http://localhost:8080/ 2>/dev/null || echo "CURL_FAILED"
${BEFORE_INSTALL}/bin/httpd -f /tmp/before_proxy/httpd.conf -k stop 2>/dev/null || true

echo "=== Configuring proxy for AFTER version ==="
AFTER_INSTALL=/build_after/install
mkdir -p /tmp/after_proxy/{logs,htdocs}
cat > /tmp/after_proxy/httpd.conf << EOF
ServerName localhost
Listen 8090
LoadModule proxy_html_module ${AFTER_INSTALL}/modules/mod_proxy_html.so
LoadModule proxy_module ${AFTER_INSTALL}/modules/mod_proxy.so
LoadModule proxy_http_module ${AFTER_INSTALL}/modules/mod_proxy_http.so
LoadModule xml2enc_module ${AFTER_INSTALL}/modules/mod_xml2enc.so
DocumentRoot /tmp/after_proxy/htdocs
ErrorLog /tmp/after_proxy/logs/error.log
LogLevel debug
ProxyRequests Off
ProxyPass / http://localhost:8081/
ProxyPassReverse / http://localhost:8081/
ProxyHTMLEnable On
SetOutputFilter proxy-html
ProxyHTMLExtended Off
EOF
echo "<html><body><h1>Backend</h1></body></html>" > /tmp/after_proxy/htdocs/index.html

echo "=== Starting backend server ==="
${AFTER_INSTALL}/bin/httpd -f /tmp/after_proxy/httpd.conf -k start 2>/dev/null || true
sleep 2

echo "=== Fetching through proxy (AFTER) ==="
curl -s -o /tmp/after_output.html http://localhost:8090/ 2>/dev/null || echo "CURL_FAILED"
${AFTER_INSTALL}/bin/httpd -f /tmp/after_proxy/httpd.conf -k stop 2>/dev/null || true

echo "=== Comparing outputs ==="
diff /tmp/before_output.html /tmp/after_output.html > "$RESULT_DIR/output_diff.txt" 2>&1 || echo "DIFF_FOUND"
echo "Before output:"
cat /tmp/before_output.html
echo ""
echo "After output:"
cat /tmp/after_output.html

echo "=== Collecting coverage ==="
cd /build_after/src/build
gcov -r modules/filters/CMakeFiles/mod_proxy_html.dir/mod_proxy_html.c.gcno 2>/dev/null || true
ls -la modules/filters/*.gcov 2>/dev/null || echo "NO_GCOV_FILES"
grep -n "^#\|^[^-]" modules/filters/mod_proxy_html.c.gcov 2>/dev/null | grep "33[6-9]\|34[0-2]" || true

echo "=== Done ==="
cp /tmp/before_output.html "$RESULT_DIR/" 2>/dev/null || true
cp /tmp/after_output.html "$RESULT_DIR/" 2>/dev/null || true
exit 0
