# ================================
# CONFIG
# ================================
$projectId = "PVT_kwHOAlw_pM4BKSh6"
$fieldId   = "PVTIF_lAHOAlw_pM4BKSh6zg6NA3Y"  # Sprint field ID

# Iteration IDs (confirmed)
$Sprint1 = "ce78e29b"
$Sprint2 = "32cf11d4"
$Sprint3 = "59a0813e"

# Issue distribution
$Group1 = 1..7     # Sprint 1
$Group2 = 8..14    # Sprint 2
$Group3 = 15..22   # Sprint 3

# ================================
# Function: Fetch Issue Node ID
# ================================
function Get-IssueNodeId($number) {
    $query = @"
query {
  repository(owner: "sanathharish", name: "lira") {
    issue(number: $number) {
      id
    }
  }
}
"@

    $resp = gh api graphql -f query="$query" | ConvertFrom-Json
    return $resp.data.repository.issue.id
}

# ================================
# Function: Assign iteration
# ================================
function Set-IssueIteration($itemId, $iterationId) {
    $mutation = @"
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "$projectId",
    itemId: "$itemId",
    fieldId: "$fieldId",
    value: {
      iterationId: "$iterationId"
    }
  }) {
    projectV2Item {
      id
    }
  }
}
"@

    gh api graphql -f query="$mutation" > $null
}

Write-Host "`n=== Assigning issues to sprints ===`n"

# ================================
# Process each group
# ================================
function Assign-Group($issues, $iterationId, $sprintName) {
    Write-Host "`n--- $sprintName ---"

    foreach ($i in $issues) {
        Write-Host "Issue #$i → fetching Node ID..."
        $nodeId = Get-IssueNodeId $i

        if (-not $nodeId) {
            Write-Host "   ❌ Could not fetch node ID for issue $i"
            continue
        }

        Write-Host "   Node ID: $nodeId → assigning..."
        Set-IssueIteration $nodeId $iterationId

        Write-Host "   ✓ Assigned Issue #$i to $sprintName"
    }
}

Assign-Group $Group1 $Sprint1 "Sprint 1"
Assign-Group $Group2 $Sprint2 "Sprint 2"
Assign-Group $Group3 $Sprint3 "Sprint 3"

Write-Host "`n🎉 Done! All issues assigned to their sprints."