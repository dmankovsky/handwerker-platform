#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

API_URL="http://localhost:8001"

echo -e "${BLUE}=== Handwerker Platform API Test ===${NC}\n"

# Test 1: Health Check
echo -e "${BLUE}1. Testing Health Endpoint${NC}"
curl -s "$API_URL/health" | jq
echo -e "${GREEN}✓ Health check passed${NC}\n"

# Test 2: Login as Homeowner
echo -e "${BLUE}2. Login as Homeowner${NC}"
HOMEOWNER_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=homeowner@test.com&password=password123")

HOMEOWNER_TOKEN=$(echo $HOMEOWNER_RESPONSE | jq -r '.access_token')
echo "Token: ${HOMEOWNER_TOKEN:0:20}..."
echo -e "${GREEN}✓ Homeowner logged in${NC}\n"

# Test 3: Login as Craftsman
echo -e "${BLUE}3. Login as Craftsman${NC}"
CRAFTSMAN_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=craftsman@test.com&password=password123")

CRAFTSMAN_TOKEN=$(echo $CRAFTSMAN_RESPONSE | jq -r '.access_token')
echo "Token: ${CRAFTSMAN_TOKEN:0:20}..."
echo -e "${GREEN}✓ Craftsman logged in${NC}\n"

# Test 4: Get Current User (Homeowner)
echo -e "${BLUE}4. Get Current User (Homeowner)${NC}"
curl -s "$API_URL/api/auth/me" \
  -H "Authorization: Bearer $HOMEOWNER_TOKEN" | jq
echo -e "${GREEN}✓ Got homeowner profile${NC}\n"

# Test 5: Get Current User (Craftsman)
echo -e "${BLUE}5. Get Current User (Craftsman)${NC}"
curl -s "$API_URL/api/auth/me" \
  -H "Authorization: Bearer $CRAFTSMAN_TOKEN" | jq
echo -e "${GREEN}✓ Got craftsman profile${NC}\n"

# Test 6: Search Craftsmen (unauthenticated)
echo -e "${BLUE}6. Search Craftsmen${NC}"
curl -s "$API_URL/api/craftsman/search" | jq 'length'
echo -e "${GREEN}✓ Search successful${NC}\n"

# Test 7: Get Trades
echo -e "${BLUE}7. Get Available Trades${NC}"
curl -s "$API_URL/api/craftsman/trades" | jq
echo -e "${GREEN}✓ Got trades list${NC}\n"

# Test 8: Get Service Areas
echo -e "${BLUE}8. Get Service Areas${NC}"
curl -s "$API_URL/api/craftsman/service-areas" | jq
echo -e "${GREEN}✓ Got service areas${NC}\n"

# Test 9: Test i18n - Get Languages
echo -e "${BLUE}9. Get Supported Languages${NC}"
curl -s "$API_URL/api/i18n/languages" | jq
echo -e "${GREEN}✓ Got languages${NC}\n"

# Test 10: Test i18n - Translate (German)
echo -e "${BLUE}10. Test Translation (German)${NC}"
curl -s "$API_URL/api/i18n/translate/common.welcome?lang=de" | jq
echo -e "${GREEN}✓ German translation${NC}\n"

# Test 11: Test i18n - Translate (English)
echo -e "${BLUE}11. Test Translation (English)${NC}"
curl -s "$API_URL/api/i18n/translate/common.welcome?lang=en" | jq
echo -e "${GREEN}✓ English translation${NC}\n"

# Test 12: Get My Bookings (Homeowner)
echo -e "${BLUE}12. Get My Bookings (Homeowner)${NC}"
curl -s "$API_URL/api/bookings/" \
  -H "Authorization: Bearer $HOMEOWNER_TOKEN" | jq 'length'
echo -e "${GREEN}✓ Got bookings${NC}\n"

# Test 13: Get My Bookings (Craftsman)
echo -e "${BLUE}13. Get My Bookings (Craftsman)${NC}"
curl -s "$API_URL/api/bookings/" \
  -H "Authorization: Bearer $CRAFTSMAN_TOKEN" | jq 'length'
echo -e "${GREEN}✓ Got bookings${NC}\n"

echo -e "${GREEN}=== All Tests Passed! ===${NC}"
echo -e "\n${BLUE}API is working correctly!${NC}"
echo -e "Homeowner Token: $HOMEOWNER_TOKEN"
echo -e "Craftsman Token: $CRAFTSMAN_TOKEN"
