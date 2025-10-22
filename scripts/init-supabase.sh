#!/usr/bin/env bash

# Supabase Initialization Script
# Purpose: Initialize Supabase project locally and apply migrations
# Usage: ./scripts/init-supabase.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SUPABASE_DIR="$REPO_ROOT/supabase"
MIGRATIONS_DIR="$SUPABASE_DIR/migrations"

echo -e "${YELLOW}=== Nexus Supabase Initialization ===${NC}"

# Check if Supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo -e "${RED}✗ Supabase CLI not found${NC}"
    echo "Install it with: brew install supabase/tap/supabase"
    exit 1
fi

echo -e "${GREEN}✓ Supabase CLI found${NC}"

# Check if .env file exists
if [ ! -f "$REPO_ROOT/.env" ]; then
    echo -e "${YELLOW}⚠ .env file not found${NC}"
    echo "Creating .env from .env.example..."
    cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
    echo -e "${YELLOW}⚠ Please update .env with your Supabase credentials${NC}"
fi

# Initialize Supabase project if not already initialized
if [ ! -d "$SUPABASE_DIR/.branches" ]; then
    echo -e "${YELLOW}Initializing Supabase project...${NC}"
    cd "$REPO_ROOT"
    supabase init
    echo -e "${GREEN}✓ Supabase project initialized${NC}"
fi

# Start Supabase local development server
echo -e "${YELLOW}Starting Supabase local development server...${NC}"
cd "$REPO_ROOT"
supabase start

# Wait for Supabase to be ready
echo -e "${YELLOW}Waiting for Supabase to be ready...${NC}"
sleep 5

# Apply migrations
echo -e "${YELLOW}Applying database migrations...${NC}"
supabase migration up

echo -e "${GREEN}✓ Database migrations applied${NC}"

# Seed test data (optional)
if [ -f "$SUPABASE_DIR/seed.sql" ]; then
    echo -e "${YELLOW}Seeding test data...${NC}"
    supabase db push --dry-run < "$SUPABASE_DIR/seed.sql"
    echo -e "${GREEN}✓ Test data seeded${NC}"
fi

# Display connection information
echo -e "${GREEN}=== Supabase Initialization Complete ===${NC}"
echo ""
echo "Local Supabase instance is running:"
echo "  API URL: http://localhost:54321"
echo "  DB URL: postgresql://postgres:postgres@localhost:54322/postgres"
echo "  Studio: http://localhost:54323"
echo ""
echo "To stop Supabase, run: supabase stop"
echo "To view logs, run: supabase logs"
