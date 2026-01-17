# PNES API Test Script (PowerShell)
# This script fetches and displays the PNES analysis from the API

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "PNES Detection API Test" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Fetching data from: http://localhost:3000/api/data" -ForegroundColor Yellow
Write-Host ""

try {
    # Fetch the full data
    $response = Invoke-WebRequest -Uri "http://localhost:3000/api/data" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    
    # Display PNES Analysis
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "PNES Analysis Results:" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
    $pnes = $data.pnes_analysis
    
    # Score
    Write-Host "PNES Likelihood Score:" -ForegroundColor Yellow
    Write-Host "  Score: $($pnes.pnes_likelihood_score)" -ForegroundColor Green
    Write-Host "  Classification: $($pnes.classification)" -ForegroundColor Green
    Write-Host ""
    
    # Risk Factors
    Write-Host "Risk Factors Detected:" -ForegroundColor Yellow
    Write-Host "  Count: $($pnes.risk_factors.Count)" -ForegroundColor Green
    if ($pnes.risk_factors.Count -gt 0) {
        Write-Host ""
        foreach ($factor in $pnes.risk_factors) {
            Write-Host "  • $($factor.indicator)" -ForegroundColor Cyan
            Write-Host "    Score: $($factor.score)%" -ForegroundColor White
            Write-Host "    Description: $($factor.description)" -ForegroundColor White
            Write-Host "    PNES Relevance: $($factor.pnes_relevance)" -ForegroundColor White
            Write-Host ""
        }
    }
    
    # Recommendations
    Write-Host "Clinical Recommendations:" -ForegroundColor Yellow
    Write-Host "  Count: $($pnes.recommendations.Count)" -ForegroundColor Green
    if ($pnes.recommendations.Count -gt 0) {
        Write-Host ""
        $i = 1
        foreach ($rec in $pnes.recommendations) {
            Write-Host "  $i. $rec" -ForegroundColor Cyan
            $i++
        }
        Write-Host ""
    }
    
    # Summary Stats
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "Summary Statistics:" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "  Total Seizures: $($data.statistics.total_seizures)" -ForegroundColor White
    Write-Host "  Average Duration: $($data.statistics.avg_duration) seconds" -ForegroundColor White
    Write-Host "  Recent Seizures (7 days): $($data.statistics.recent_seizures_7_days)" -ForegroundColor White
    Write-Host "  Average Pain Level: $($data.statistics.avg_pain)" -ForegroundColor White
    Write-Host ""
    
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "API Response Complete ✓" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    
} catch {
    Write-Host "Error: Could not fetch data from API" -ForegroundColor Red
    Write-Host "Make sure the app is running at http://localhost:3000" -ForegroundColor Yellow
    Write-Host "Error details: $_" -ForegroundColor Red
}
