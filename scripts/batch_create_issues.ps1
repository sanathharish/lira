# ---------------------------------------------
# CONFIG
# ---------------------------------------------
$projectId = "PVT_kwHOAlw_pM4BKSh6"
$repoOwner = "sanathharish"
$repoName  = "lira"

# ---------------------------------------------
# Helper: Create issue + attach to project
# ---------------------------------------------
function Add-Issue {
    param(
        [string]$title,
        [string]$body
    )

    Write-Host ""
    Write-Host "=== Creating Issue: $title ==="

    # 1. Create the issue in the repo
    $issueUrl = gh issue create --repo "$repoOwner/$repoName" --title "$title" --body "$body"
    Write-Host "Issue URL: $issueUrl"

    # 2. Extract issue number from URL
    if ($issueUrl -match "issues/(\d+)$") {
        $issueNumber = $matches[1]
        Write-Host "Issue Number: $issueNumber"
    } else {
        Write-Host "ERROR: Could not extract issue number from URL."
        return
    }

    # 3. Get issue GraphQL node ID
    $query = "{ repository(owner: `"$repoOwner`", name: `"$repoName`") { issue(number: $issueNumber) { id } } }"
    $issueId = gh api graphql -f query="$query" --jq ".data.repository.issue.id"
    Write-Host "Issue GraphQL ID: $issueId"

    if (-not $issueId) {
        Write-Host "ERROR: Could not resolve issue GraphQL ID."
        return
    }

    # 4. Add issue to ProjectV2
    $mutation = "mutation { addProjectV2ItemById(input: { projectId: `"$projectId`", contentId: `"$issueId`" }) { item { id } } }"
    gh api graphql -f query="$mutation" > $null

    Write-Host "Added to project board."
}

# ---------------------------------------------
# ISSUE SET (around 20 detailed tasks)
# ---------------------------------------------
Write-Host ""
Write-Host "=== Creating core LIRA issues and linking to project ==="

# Milestone 1 - Agent Core (MVP)
Add-Issue `
  "Setup LangChain and project structure" `
  "Initialize the LIRA project structure, set up virtual environment, install LangChain, LangGraph, Chroma, and Ollama integration. Document setup steps in README."

Add-Issue `
  "Implement basic LLM chain with Ollama" `
  "Create a simple LangChain Runnable that uses an Ollama model (for example llama3.2) to answer a prompt. This acts as the base building block for the agent."

Add-Issue `
  "Design AgentState model for LangGraph" `
  "Define the AgentState data structure that flows through the LangGraph nodes, including user question, plan, retrieved docs, and final answer fields."

Add-Issue `
  "Implement planner node in LangGraph" `
  "Create a planner node that takes the user question and returns a JSON plan describing which tools to use (search, RAG, summarizer) and in what order."

Add-Issue `
  "Implement summarizer node in LangGraph" `
  "Create a summarizer node that takes retrieved content and generates a concise, user friendly answer, keeping it grounded to the provided context."

# Milestone 2 - RAG Memory Layer
Add-Issue `
  "Setup Chroma vector store for LIRA" `
  "Configure Chroma as the local vector database, define an embeddings model, and create helper utilities for storing and querying text chunks."

Add-Issue `
  "Implement document chunking and storage" `
  "Write utilities to split long documents into chunks, create LangChain Documents, and store them in Chroma with appropriate metadata."

Add-Issue `
  "Implement RAG retrieval node in LangGraph" `
  "Create a LangGraph node that takes the user query, runs a similarity search against Chroma, and attaches the top relevant chunks to AgentState."

Add-Issue `
  "Add simple local knowledge base (demo docs)" `
  "Seed the vector store with a small demo knowledge base (for example project architecture notes or quantum computing notes) for demo queries."

# Milestone 3 - API and Backend
Add-Issue `
  "Create FastAPI backend skeleton for LIRA" `
  "Initialize a FastAPI app with basic routing and a health check endpoint. Ensure it can run alongside the LangChain agent pipeline code."

Add-Issue `
  "Implement /query endpoint for agent" `
  "Expose a POST /query endpoint that accepts a question, runs it through the LangGraph workflow (planner, tools, summarizer), and returns the answer."

Add-Issue `
  "Add streaming response support to FastAPI" `
  "Modify the /query endpoint to optionally stream partial responses back to the client using Server Sent Events or similar streaming mechanism."

Add-Issue `
  "Add simple logging and request tracing" `
  "Introduce structured logging for incoming queries, node transitions in the graph, and final answers for debugging and observability."

# Milestone 4 - Next.js UI
Add-Issue `
  "Setup Next.js frontend for LIRA" `
  "Create a Next.js app that will serve as the chat UI for LIRA. Add a basic layout and a simple chat style page."

Add-Issue `
  "Implement chat UI for agent queries" `
  "Build a chat style interface in Next.js that lets the user send messages to the FastAPI backend and display the agent responses."

Add-Issue `
  "Add loading, error states, and history" `
  "Enhance the frontend to handle loading spinners, error states, and show the history of user queries and agent responses in a user friendly way."

# Milestone 5 - Safety and Guardrails
Add-Issue `
  "Implement basic query safety filter" `
  "Add a pre processing step that checks for obviously harmful queries and either blocks them or responds with a safe fallback message."

Add-Issue `
  "Add timeouts and error handling in graph" `
  "Ensure that long running or failed tool calls are handled gracefully with timeouts, retries where appropriate, and clear user error messages."

# Milestone 6 - Deployment and Documentation
Add-Issue `
  "Dockerize FastAPI and agent backend" `
  "Create a Dockerfile for running the FastAPI and LangGraph agent backend. Ensure environment variables and model configuration are configurable."

Add-Issue `
  "Document architecture and setup in README" `
  "Write a clear architecture overview of the LIRA project, including diagrams if possible, and document how to run the backend, frontend, and agent pipeline."

Add-Issue `
  "Add sample prompts and demo scenarios" `
  "Create a small set of example prompts and demo scenarios (for example RAG question, planning question, simple answer) to showcase LIRA capabilities."