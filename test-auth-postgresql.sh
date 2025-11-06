#!/bin/bash
# Test API Gateway Authentication with PostgreSQL Storage

API_URL="http://localhost:8000/api/v1"
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}API Gateway PostgreSQL Auth Test${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Test 1: User Registration
echo -e "${BLUE}Test 1: User Registration${NC}"
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User",
    "organization": "Test Organization"
  }')

if echo "$REGISTER_RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ User registration successful${NC}"
    ACCESS_TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.access_token')
    REFRESH_TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.refresh_token')
    echo "  Access Token: ${ACCESS_TOKEN:0:30}..."
    echo "  Refresh Token: ${REFRESH_TOKEN:0:30}..."
else
    echo -e "${RED}✗ User registration failed${NC}"
    echo "$REGISTER_RESPONSE" | jq .
    # Check if user already exists
    if echo "$REGISTER_RESPONSE" | grep -q "already registered"; then
        echo -e "${BLUE}User already exists, testing login instead...${NC}"
        
        # Test Login
        LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
          -H "Content-Type: application/json" \
          -d '{
            "email": "testuser@example.com",
            "password": "SecurePass123!"
          }')
        
        if echo "$LOGIN_RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Login successful${NC}"
            ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
            REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.refresh_token')
        else
            echo -e "${RED}✗ Login failed${NC}"
            exit 1
        fi
    else
        exit 1
    fi
fi
echo ""

# Test 2: Get User Profile
echo -e "${BLUE}Test 2: Get User Profile${NC}"
PROFILE_RESPONSE=$(curl -s -X GET "$API_URL/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$PROFILE_RESPONSE" | jq -e '.email' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Profile retrieval successful${NC}"
    echo "$PROFILE_RESPONSE" | jq .
else
    echo -e "${RED}✗ Profile retrieval failed${NC}"
    echo "$PROFILE_RESPONSE" | jq .
fi
echo ""

# Test 3: Update Profile
echo -e "${BLUE}Test 3: Update Profile${NC}"
UPDATE_RESPONSE=$(curl -s -X PUT "$API_URL/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Test User",
    "organization": "Updated Organization"
  }')

if echo "$UPDATE_RESPONSE" | jq -e '.full_name' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Profile update successful${NC}"
    echo "  New Name: $(echo "$UPDATE_RESPONSE" | jq -r '.full_name')"
    echo "  New Organization: $(echo "$UPDATE_RESPONSE" | jq -r '.organization')"
else
    echo -e "${RED}✗ Profile update failed${NC}"
    echo "$UPDATE_RESPONSE" | jq .
fi
echo ""

# Test 4: Refresh Token
echo -e "${BLUE}Test 4: Refresh Access Token${NC}"
REFRESH_RESPONSE=$(curl -s -X POST "$API_URL/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}")

if echo "$REFRESH_RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Token refresh successful${NC}"
    NEW_ACCESS_TOKEN=$(echo "$REFRESH_RESPONSE" | jq -r '.access_token')
    echo "  New Access Token: ${NEW_ACCESS_TOKEN:0:30}..."
else
    echo -e "${RED}✗ Token refresh failed${NC}"
    echo "$REFRESH_RESPONSE" | jq .
fi
echo ""

# Test 5: Create API Key
echo -e "${BLUE}Test 5: Create API Key${NC}"
APIKEY_RESPONSE=$(curl -s -X POST "$API_URL/auth/api-keys" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test API Key",
    "expires_in_days": 30
  }')

if echo "$APIKEY_RESPONSE" | jq -e '.api_key' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API key creation successful${NC}"
    API_KEY=$(echo "$APIKEY_RESPONSE" | jq -r '.api_key')
    echo "  API Key: ${API_KEY:0:20}..."
    echo "  Name: $(echo "$APIKEY_RESPONSE" | jq -r '.name')"
else
    echo -e "${RED}✗ API key creation failed${NC}"
    echo "$APIKEY_RESPONSE" | jq .
fi
echo ""

# Test 6: List API Keys
echo -e "${BLUE}Test 6: List API Keys${NC}"
LIST_KEYS_RESPONSE=$(curl -s -X GET "$API_URL/auth/api-keys" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$LIST_KEYS_RESPONSE" | jq -e '.api_keys' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API keys listing successful${NC}"
    KEY_COUNT=$(echo "$LIST_KEYS_RESPONSE" | jq '.api_keys | length')
    echo "  Number of API keys: $KEY_COUNT"
else
    echo -e "${RED}✗ API keys listing failed${NC}"
    echo "$LIST_KEYS_RESPONSE" | jq .
fi
echo ""

# Test 7: Database Verification
echo -e "${BLUE}Test 7: PostgreSQL Database Verification${NC}"
echo "Users in database:"
docker exec researcher-postgres psql -U researcher -d research_papers -c "SELECT user_id, email, full_name, role FROM users WHERE email LIKE '%testuser%';" 2>/dev/null

echo ""
echo "Refresh tokens for user:"
USER_ID=$(echo "$PROFILE_RESPONSE" | jq -r '.user_id')
docker exec researcher-postgres psql -U researcher -d research_papers -c "SELECT id, LEFT(token_hash, 20) as token_hash, expires_at, revoked FROM refresh_tokens WHERE user_id = '$USER_ID' ORDER BY created_at DESC LIMIT 3;" 2>/dev/null

echo ""
echo "API keys for user:"
docker exec researcher-postgres psql -U researcher -d research_papers -c "SELECT id, name, LEFT(api_key, 15) as api_key_preview, created_at FROM api_keys WHERE user_id = '$USER_ID';" 2>/dev/null

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}All Tests Completed!${NC}"
echo -e "${BLUE}========================================${NC}"
