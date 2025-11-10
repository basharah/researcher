#!/bin/bash
# Test cookie-based authentication flow

set -e

API_BASE="http://localhost:8000/api/v1"
EMAIL="test@example.com"
PASSWORD="TestPass123!"

echo "========================================="
echo "Testing Cookie-Based Authentication Flow"
echo "========================================="
echo ""

# Register a test user (if not exists)
echo "1. Registering test user..."
REGISTER_RESPONSE=$(curl -s -i -X POST "$API_BASE/auth/register" \
  -H "Origin: http://localhost:3000" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"full_name\":\"Test User\",\"organization\":\"Test Org\"}" \
  2>&1 || echo "User may already exist")

echo "Register response headers:"
echo "$REGISTER_RESPONSE" | grep -i "set-cookie" || echo "No Set-Cookie headers found"
echo ""

# Login and save cookies
echo "2. Logging in..."
COOKIE_FILE="/tmp/test-cookies.txt"
rm -f "$COOKIE_FILE"

LOGIN_RESPONSE=$(curl -s -i -c "$COOKIE_FILE" -X POST "$API_BASE/auth/login" \
  -H "Origin: http://localhost:3000" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

echo "Login response headers:"
echo "$LOGIN_RESPONSE" | head -20
echo ""

echo "Checking for Set-Cookie headers:"
SET_COOKIE_COUNT=$(echo "$LOGIN_RESPONSE" | grep -i "set-cookie" | wc -l)
if [ "$SET_COOKIE_COUNT" -gt 0 ]; then
  echo "✓ Found $SET_COOKIE_COUNT Set-Cookie header(s):"
  echo "$LOGIN_RESPONSE" | grep -i "set-cookie"
else
  echo "✗ No Set-Cookie headers found!"
  exit 1
fi
echo ""

# Check if cookies were saved
echo "3. Checking saved cookies:"
if [ -f "$COOKIE_FILE" ]; then
  echo "✓ Cookie file created:"
  cat "$COOKIE_FILE"
else
  echo "✗ Cookie file not created"
  exit 1
fi
echo ""

# Try accessing /auth/me with cookies
echo "4. Testing /auth/me with cookies..."
ME_RESPONSE=$(curl -s -b "$COOKIE_FILE" "$API_BASE/auth/me")

if echo "$ME_RESPONSE" | grep -q "email"; then
  echo "✓ /auth/me succeeded with cookies:"
  echo "$ME_RESPONSE" | python -m json.tool 2>/dev/null || echo "$ME_RESPONSE"
else
  echo "✗ /auth/me failed:"
  echo "$ME_RESPONSE"
  exit 1
fi
echo ""

echo "========================================="
echo "✓ All cookie-based auth tests passed!"
echo "========================================="

# Cleanup
rm -f "$COOKIE_FILE"
