# ---------------------------------------------
# CONFIG
# ---------------------------------------------
$projectId = "PVT_kwHOAlw_pM4BKSh6"
$repoOwner = "sanathharish"
$repoName  = "lira"

# ---------------------------------------------
# Helper Function Header
# ---------------------------------------------
function Add-Issue {
    param(
        [string]$title,
        [string]$body,
        [string]$milestone
    )

    Write-Host "`n=== Creating Issue: $title ==="
    # 1. Create the issue
    $issueUrl = gh issue create --repo "$repoOwner/$repoName" --title "$title" --body "$body" --milestone "$milestone"
    Write-Host "Issue URL: $issueUrl"

    # Extract issue number
    if ($issueUrl -match "issues/(\d+)$") {
        $issueNumber = $matches[1]
        Write-Host "Issue Number: $issueNumber"
    } else {
        Write-Host "ERROR: Could not extract issue number."
        return
    }

    # 2. Get GraphQL Node ID
    $query = "{ repository(owner: `"$repoOwner`", name: `"$repoName`") { issue(number: $issueNumber) { id } } }"
    $issueId = gh api graphql -f query="$query" --jq ".data.repository.issue.id"
    Write-Host "Issue GraphQL ID: $issueId"

    # 3. Add issue to project board
    $mutation = "mutation { addProjectV2ItemById(input: { projectId: `"$projectId`", contentId: `"$issueId`" }) { item { id } } }"
    gh api graphql -f query="$mutation" > $null

    Write-Host "Added to project board"


}

# ---------------------------------------------
# CREATE MILESTONES
# ---------------------------------------------
Write-Host ""
Write-Host "=== Creating Milestones ==="

$milestones = @(
    "Milestone 1 - Agent Core (MVP)",
    "Milestone 2 - RAG Memory Layer",
    "Milestone 3 - API and Frontend",
    "Milestone 4 - Safety and Guardrails",
    "Milestone 5 - Deployment",
    "Milestone 6 - Documentation"
)

foreach ($m in $milestones) {
    gh milestone create "$m"
    Write-Host "Milestone created: $m"
}

# ---------------------------------------------
# CREATE ISSUES
# ---------------------------------------------
Write-Host ""
Write-Host "=== Creating Issues ==="

Add-Issue "Setup project structure" "Initialize Python project and folder structure." "Milestone 1 - Agent Core (MVP)"
Add-Issue "Build LangGraph StateGraph skeleton" "Set up agent workflow system." "Milestone 1 - Agent Core (MVP)"
Add-Issue "Implement LLM planner node" "Implement planner with JSON-safe output." "Milestone 1 - Agent Core (MVP)"
Add-Issue "Integrate web search tool" "Add search capability." "Milestone 1 - Agent Core (MVP)"
Add-Issue "Build LLM summarizer node" "Summarize retrieval results." "Milestone 1 - Agent Core (MVP)"

Add-Issue "Setup Chroma vector memory" "Initialize vector DB for RAG." "Milestone 2 - RAG Memory Layer"
Add-Issue "Implement RAG retrieval node" "Fetch relevant documents." "Milestone 2 - RAG Memory Layer"
Add-Issue "Implement memory storage node" "Store summaries in vector DB." "Milestone 2 - RAG Memory Layer"

Add-Issue "Build FastAPI backend" "Backend API for agent." "Milestone 3 - API and Frontend"
Add-Issue "Build Next.js Chat UI" "User interface for agent." "Milestone 3 - API and Frontend"
Add-Issue "Add streaming response support" "Enable streaming responses." "Milestone 3 - API and Frontend"

Add-Issue "Implement query safety filter" "Filter harmful or dangerous queries." "Milestone 4 - Safety and Guardrails"
Add-Issue "Add fallback behaviors" "Error recovery steps." "Milestone 4 - Safety and Guardrails"

Add-Issue "Deploy backend" "Deploy API service." "Milestone 5 - Deployment"
Add-Issue "Deploy frontend" "Deploy UI to Vercel." "Milestone 5 - Deployment"

Add-Issue "Final README" "Document everything clearly." "Milestone 6 - Documentation"
Add-Issue "Architecture diagram" "Add architecture diagram." "Milestone 6 - Documentation"


