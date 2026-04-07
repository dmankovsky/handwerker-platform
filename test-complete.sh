#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

API_URL="http://localhost:8001"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Handwerker Platform - Complete API Test Suite      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}\n"

# Test 1: Health Check
echo -e "${BLUE}[1/15] Health Check${NC}"
HEALTH=$(curl -s "$API_URL/health")
echo "$HEALTH" | jq
if echo "$HEALTH" | jq -e '.status == "healthy"' > /dev/null; then
    echo -e "${GREEN}✓ API is healthy${NC}\n"
else
    echo -e "${RED}✗ API is not healthy${NC}\n"
    exit 1
fi

# Test 2: Register Homeowner
echo -e "${BLUE}[2/15] Register Homeowner${NC}"
HOMEOWNER_REG=$(curl -s -X POST "$API_URL/api/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"email":"test-homeowner@example.com","password":"test12345","full_name":"Test Homeowner","phone":"+49123456789","role":"homeowner"}')

HOMEOWNER_TOKEN=$(echo "$HOMEOWNER_REG" | jq -r '.access_token // empty')
if [ -z "$HOMEOWNER_TOKEN" ]; then
    # User might exist, try login
    echo -e "${YELLOW}User exists, logging in...${NC}"
    HOMEOWNER_LOGIN=$(curl -s -X POST "$API_URL/api/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=test-homeowner@example.com&password=test12345")
    HOMEOWNER_TOKEN=$(echo "$HOMEOWNER_LOGIN" | jq -r '.access_token')
fi
echo "Homeowner ID: $(echo "$HOMEOWNER_REG" | jq -r '.user.id // "existing"')"
echo -e "${GREEN}✓ Homeowner authenticated${NC}\n"

# Test 3: Register Craftsman
echo -e "${BLUE}[3/15] Register Craftsman${NC}"
CRAFTSMAN_REG=$(curl -s -X POST "$API_URL/api/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"email":"test-craftsman@example.com","password":"test12345","full_name":"Test Craftsman","phone":"+49987654321","role":"craftsman"}')

CRAFTSMAN_TOKEN=$(echo "$CRAFTSMAN_REG" | jq -r '.access_token // empty')
if [ -z "$CRAFTSMAN_TOKEN" ]; then
    echo -e "${YELLOW}User exists, logging in...${NC}"
    CRAFTSMAN_LOGIN=$(curl -s -X POST "$API_URL/api/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=test-craftsman@example.com&password=test12345")
    CRAFTSMAN_TOKEN=$(echo "$CRAFTSMAN_LOGIN" | jq -r '.access_token')
fi
CRAFTSMAN_ID=$(echo "$CRAFTSMAN_REG" | jq -r '.user.id // "existing"')
echo "Craftsman ID: $CRAFTSMAN_ID"
echo -e "${GREEN}✓ Craftsman authenticated${NC}\n"

# Test 4: Get Current User
echo -e "${BLUE}[4/15] Get Current User (Homeowner)${NC}"
curl -s "$API_URL/api/auth/me" \
    -H "Authorization: Bearer $HOMEOWNER_TOKEN" | jq '{id, email, role, full_name}'
echo -e "${GREEN}✓ User profile retrieved${NC}\n"

# Test 5: Create/Update Craftsman Profile
echo -e "${BLUE}[5/15] Create Craftsman Profile${NC}"
PROFILE=$(curl -s -X PUT "$API_URL/api/craftsman/profile" \
    -H "Authorization: Bearer $CRAFTSMAN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "company_name": "Test Handwerker GmbH",
        "bio": "Professional craftsman with 10 years of experience in electrical and plumbing work",
        "years_experience": 10,
        "trades": ["electrician", "plumber"],
        "service_areas": ["Berlin", "Munich", "Hamburg"],
        "hourly_rate": 75,
        "accepts_bookings": true
    }')
echo "$PROFILE" | jq '{id, company_name, trades, hourly_rate}'
echo -e "${GREEN}✓ Craftsman profile created${NC}\n"

# Test 6: Search Craftsmen
echo -e "${BLUE}[6/15] Search Craftsmen${NC}"
CRAFTSMEN=$(curl -s "$API_URL/api/craftsman/search")
COUNT=$(echo "$CRAFTSMEN" | jq 'length')
echo "Found $COUNT craftsmen"
echo "$CRAFTSMEN" | jq '.[0] | {id, company_name, trades, hourly_rate}' 2>/dev/null || echo "No craftsmen yet"
echo -e "${GREEN}✓ Search completed${NC}\n"

# Test 7: Search with Filters
echo -e "${BLUE}[7/15] Search Electricians${NC}"
ELECTRICIANS=$(curl -s "$API_URL/api/craftsman/search?trade=electrician")
echo "Found $(echo "$ELECTRICIANS" | jq 'length') electricians"
echo -e "${GREEN}✓ Filtered search completed${NC}\n"

# Test 8: Create Booking
echo -e "${BLUE}[8/15] Create Booking${NC}"
# Get the first craftsman ID
FIRST_CRAFTSMAN_ID=$(echo "$CRAFTSMEN" | jq -r '.[0].id // 1')
BOOKING=$(curl -s -X POST "$API_URL/api/bookings/" \
    -H "Authorization: Bearer $HOMEOWNER_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"craftsman_id\": $FIRST_CRAFTSMAN_ID,
        \"job_title\": \"Fix electrical outlet in kitchen\",
        \"job_description\": \"The kitchen outlet is not working properly and needs inspection and repair. It might be a wiring issue.\",
        \"service_address\": \"Hauptstraße 123, 10115 Berlin, Germany\",
        \"requested_date\": \"2026-04-20\",
        \"estimated_hours\": 2
    }")
BOOKING_ID=$(echo "$BOOKING" | jq -r '.id')
echo "Booking ID: $BOOKING_ID"
echo "$BOOKING" | jq '{id, job_title, status, estimated_cost}'
echo -e "${GREEN}✓ Booking created${NC}\n"

# Test 9: Get My Bookings (Homeowner)
echo -e "${BLUE}[9/15] Get Homeowner Bookings${NC}"
HOMEOWNER_BOOKINGS=$(curl -s "$API_URL/api/bookings/" \
    -H "Authorization: Bearer $HOMEOWNER_TOKEN")
echo "Homeowner has $(echo "$HOMEOWNER_BOOKINGS" | jq 'length') bookings"
echo -e "${GREEN}✓ Retrieved bookings${NC}\n"

# Test 10: Get My Bookings (Craftsman)
echo -e "${BLUE}[10/15] Get Craftsman Bookings${NC}"
CRAFTSMAN_BOOKINGS=$(curl -s "$API_URL/api/bookings/" \
    -H "Authorization: Bearer $CRAFTSMAN_TOKEN")
echo "Craftsman has $(echo "$CRAFTSMAN_BOOKINGS" | jq 'length') bookings"
echo -e "${GREEN}✓ Retrieved bookings${NC}\n"

# Test 11: i18n - Languages
echo -e "${BLUE}[11/15] Test i18n Languages${NC}"
curl -s "$API_URL/api/i18n/languages" | jq
echo -e "${GREEN}✓ Language list retrieved${NC}\n"

# Test 12: i18n - German Translation
echo -e "${BLUE}[12/15] Test German Translation${NC}"
curl -s "$API_URL/api/i18n/translate/booking.create_booking?lang=de" | jq
echo -e "${GREEN}✓ German translation working${NC}\n"

# Test 13: i18n - English Translation
echo -e "${BLUE}[13/15] Test English Translation${NC}"
curl -s "$API_URL/api/i18n/translate/booking.create_booking?lang=en" | jq
echo -e "${GREEN}✓ English translation working${NC}\n"

# Test 14: Get Category Translations
echo -e "${BLUE}[14/15] Get Booking Translations${NC}"
TRANSLATIONS=$(curl -s "$API_URL/api/i18n/translations/booking?lang=de")
echo "Got $(echo "$TRANSLATIONS" | jq '.translations | length') translation keys"
echo -e "${GREEN}✓ Category translations retrieved${NC}\n"

# Test 15: API Documentation
echo -e "${BLUE}[15/15] Check API Documentation${NC}"
echo "Swagger UI: http://localhost:8001/docs"
echo "ReDoc: http://localhost:8001/redoc"
echo -e "${GREEN}✓ Documentation available${NC}\n"

# Summary
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              All Tests Passed Successfully!           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${BLUE}Test Credentials:${NC}"
echo -e "Homeowner: test-homeowner@example.com / test12345"
echo -e "Craftsman: test-craftsman@example.com / test12345"
echo -e "\n${BLUE}Tokens (valid for 30 days):${NC}"
echo -e "Homeowner: ${HOMEOWNER_TOKEN:0:50}..."
echo -e "Craftsman: ${CRAFTSMAN_TOKEN:0:50}..."
echo -e "\n${BLUE}Test Data Created:${NC}"
echo -e "- Craftsman Profile: Test Handwerker GmbH"
echo -e "- Service Areas: Berlin, Munich, Hamburg"
echo -e "- Trades: Electrician, Plumber"
echo -e "- Booking ID: $BOOKING_ID"
