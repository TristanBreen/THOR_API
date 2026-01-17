#!/bin/bash
# PNES API Test Script
# This script fetches and displays the PNES analysis from the API

echo "=========================================="
echo "PNES Detection API Test"
echo "=========================================="
echo ""
echo "Fetching data from: http://localhost:3000/api/data"
echo ""

# Fetch the data and pretty-print the PNES section
curl -s http://localhost:3000/api/data | jq '.pnes_analysis' | head -100

echo ""
echo "=========================================="
echo "Full Response Fields:"
echo "=========================================="
curl -s http://localhost:3000/api/data | jq 'keys'

echo ""
echo "=========================================="
echo "PNES Analysis Structure:"
echo "=========================================="
curl -s http://localhost:3000/api/data | jq '.pnes_analysis | keys'

echo ""
echo "=========================================="
echo "Example: Risk Factors"
echo "=========================================="
curl -s http://localhost:3000/api/data | jq '.pnes_analysis.risk_factors'

echo ""
echo "=========================================="
echo "Example: Recommendations"
echo "=========================================="
curl -s http://localhost:3000/api/data | jq '.pnes_analysis.recommendations'

echo ""
echo "=========================================="
echo "PNES Score Summary"
echo "=========================================="
curl -s http://localhost:3000/api/data | jq '.pnes_analysis | {score: .pnes_likelihood_score, classification: .classification, risk_factor_count: (.risk_factors | length), recommendation_count: (.recommendations | length)}'
