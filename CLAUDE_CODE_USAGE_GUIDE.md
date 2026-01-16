# How to Use These Instructions with Claude Code

## Best Approach: Iterative, Phase-by-Phase Development

Claude Code works best when given **clear, focused objectives** rather than trying to build everything at once. Here's the optimal workflow:

---

## Step 1: Initial Setup (Single Command)

**What to ask Claude Code:**
```
Using the RAG_PROJECT_INSTRUCTIONS.md file, create the initial project structure with:
1. Directory layout as specified
2. requirements.txt with all dependencies
3. Basic FastAPI backend skeleton (main.py)
4. Basic Streamlit frontend skeleton (app.py)
5. Empty placeholder files for all modules mentioned
6. Initial collections.yaml config file
7. README.md with setup instructions
The current directory already has a git repo configured and was initialized with uv 
Do NOT implement any logic yet - just create the structure and empty files with docstrings explaining what each will do.
```

**Why this works:**
- Claude Code can see the full project structure
- Validates the architecture before writing code
- Provides a foundation to build upon

---

## Step 2: Build Phase by Phase

Follow the implementation priority from the instructions, but break each phase into **specific, testable tasks**.

### Phase 1 Example: Basic Pipeline

**Task 1a: PDF Parser**
```
Implement the PDF parser in backend/ingestion/parsers.py:
- Use pypdf and pdfplumber as specified
- Extract text and tables
- Handle multi-page documents
- Return structured data with metadata
- Include error handling for corrupted PDFs

Write a simple test script to verify it works with a sample PDF.
```

**Task 1b: Vector Store**
```
Implement backend/retrieval/vector_store.py:
- Use ChromaDB as specified
- Create collection management functions
- Implement document indexing with nomic-embed-text-v1.5
- Implement basic vector search
- Add persistence to ./vector_db directory

Include a test that indexes 3 sample documents and retrieves them.
```

**Task 1c: Ingestion Endpoint**
```
Implement POST /api/ingest endpoint in backend/main.py:
- Accept PDF uploads
- Use the PDF parser we created
- Index into ChromaDB
- Return job status
- Add proper error handling

Test with curl or httpx.
```

**Task 1d: Basic Streamlit UI**
```
Implement frontend/app.py:
- File upload widget for PDFs
- Call /api/ingest endpoint
- Display success/error messages
- Keep it minimal for now

Test by running both servers and uploading a file.
```

---

## Step 3: Incremental Testing Strategy

After each task, ask Claude Code to:

```
Create a test script test_[feature].py that verifies:
1. The component works correctly
2. Edge cases are handled
3. Errors are caught and logged

Run the test and show me the output.
```

---

## Step 4: Iterate with Checkpoints

After completing each major phase:

```
Review the current implementation:
1. What's working well?
2. What needs refactoring?
3. Are there any bottlenecks or issues?
4. Update the README with current capabilities

Then commit the code with a clear message.
```

---

## Optimal Task Size for Claude Code

### ✅ GOOD Task Sizes (1-3 files, clear scope)
```
"Implement the HTML parser using trafilatura and BeautifulSoup"
"Add BM25 indexing to the retrieval system"
"Create the hybrid fusion algorithm using RRF"
"Implement the collections.yaml loader and routing logic"
```

### ❌ TOO LARGE (will be overwhelming)
```
"Build the entire backend system"
"Implement all document parsers at once"
"Create the complete retrieval system with hybrid search"
```

### ❌ TOO SMALL (inefficient)
```
"Add an import statement for pypdf"
"Create an empty function called parse_pdf"
```

---

## Recommended Task Sequence

### Week 1: Core Functionality
1. Project structure + dependencies
2. PDF parser + tests
3. Vector store (ChromaDB) + tests
4. Basic ingestion endpoint
5. Simple Streamlit UI
6. End-to-end test: Upload PDF → Search → Get results

### Week 2: Multi-Format Support
7. DOCX parser
8. PPTX parser
9. TXT/MD/CSV parsers
10. HTML parser (trafilatura)
11. Update ingestion endpoint to handle all formats
12. Test each format

### Week 3: Advanced Retrieval
13. BM25 implementation
14. Hybrid fusion (RRF)
15. Collection routing from YAML
16. Update search endpoint
17. Performance testing

### Week 4: Images & MCP
18. Image extraction from documents
19. Image-to-text using vision model
20. MCP tool index
21. MCP-based collection selection
22. Integration testing

### Week 5: URL-based Ingestion
23. HTTP fetcher implementation
24. URL normalization & deduplication
25. Collections.yaml source_url support
26. Files directory fallback
27. Refresh endpoint

### Week 6: Polish & Deploy
28. Error handling improvements
29. Logging and monitoring
30. Docker setup
31. Documentation
32. Final integration tests

---

## Tips for Working with Claude Code

### 1. **Always Reference the Instructions**
```
"According to RAG_PROJECT_INSTRUCTIONS.md, implement the [feature]..."
```

### 2. **Request Explanations**
```
"Before implementing, explain your approach to [feature] based on the instructions."
```

### 3. **Ask for Trade-offs**
```
"The instructions suggest trafilatura for HTML. Are there any trade-offs vs BeautifulSoup alone?"
```

### 4. **Iterate on Design**
```
"Review the collections.yaml schema I designed. Does it match the requirements? Any improvements?"
```

### 5. **Request Code Review**
```
"Review the PDF parser implementation. Does it follow the project standards? Any issues?"
```

### 6. **Handle Blockers Explicitly**
```
"I'm stuck on the RRF fusion algorithm. Can you explain it step-by-step, then implement it?"
```

---

## Example First Conversation with Claude Code

```
Claude Code, I have a comprehensive specification for a RAG system in RAG_PROJECT_INSTRUCTIONS.md.

Let's start by:
1. Reading the instructions file to understand the full scope
2. Creating the complete project directory structure
3. Generating requirements.txt with all dependencies
4. Creating skeleton files with docstrings for each module
5. Writing a detailed README.md with setup steps

Do NOT implement any business logic yet. Just create the scaffolding so we have a solid foundation.

After that's done, we'll implement Phase 1 step by step.
```

**Claude Code will:**
- Read the instructions
- Create all directories
- Generate proper Python package structure
- Add __init__.py files
- Create empty modules with clear docstrings
- Write a comprehensive README

**You then review the structure before proceeding.**

---

## Example Phase Implementation

```
Great! Now let's implement Phase 1, Task 1: PDF Parser.

According to the instructions:
- Use pypdf and pdfplumber
- Extract text and tables
- Handle images (we'll process them later)
- Return structured data with metadata

Implement backend/ingestion/parsers.py with:
1. A parse_pdf(file_path) function
2. Proper error handling
3. Metadata extraction (page count, title if available)
4. Docstrings explaining the approach

Then create a simple test script that:
- Tests with a normal PDF
- Tests with a PDF containing tables
- Tests error handling with a corrupted file

Show me the implementation and test results.
```

---

## Debugging Strategy

When something doesn't work:

```
The PDF parser is failing on PDFs with images. According to the instructions, we should extract images separately for vision processing. Let's:

1. First, show me the current error
2. Explain what's happening
3. Modify the parser to skip/extract images appropriately
4. Add a TODO comment for Phase 3 (image processing)
5. Test again
```

---

## Key Success Factors

### ✅ DO:
- Break work into **single-responsibility tasks**
- Reference the instructions explicitly
- Test after each implementation
- Commit working code frequently
- Ask Claude Code to explain before implementing
- Request code reviews

### ❌ DON'T:
- Ask to build everything at once
- Skip testing phases
- Move to next feature before current one works
- Ignore the phased approach in the instructions
- Forget to update documentation

---

## Progress Tracking

Create a `PROGRESS.md` file and ask Claude Code to update it:

```
After completing each task, update PROGRESS.md with:
- ✅ Completed features
- 🚧 In progress
- ⏳ Not started
- Known issues and TODOs
```

Example PROGRESS.md:
```markdown
# RAG Project Progress

## Phase 1: Basic Pipeline
- ✅ Project structure created
- ✅ PDF parser implemented and tested
- ✅ ChromaDB vector store integrated
- ✅ Basic ingestion endpoint working
- 🚧 Streamlit UI (80% complete, needs error display)

## Phase 2: Multi-Format Support
- ⏳ DOCX parser
- ⏳ PPTX parser
- ⏳ HTML parser

## Known Issues
- PDF parser fails on password-protected PDFs (need to add detection)
- ChromaDB persistence path is hardcoded (should be in config)

## Next Steps
1. Complete Streamlit error display
2. Add password-protected PDF detection
3. Move to DOCX parser
```

---

## Final Recommendation

**Start with this exact prompt to Claude Code:**

```
I have comprehensive instructions for building a RAG system in RAG_PROJECT_INSTRUCTIONS.md.

Please:
1. Read and summarize the key requirements
2. Confirm you understand the 5-phase implementation approach
3. Create the complete project structure with empty modules
4. Generate requirements.txt
5. Write a detailed README.md with setup instructions

Do NOT implement any business logic yet. After you create the scaffolding, I'll guide you through implementing Phase 1 step by step.

Let me know when you're ready to start.
```

This approach ensures Claude Code:
- Understands the full scope
- Builds incrementally
- Tests thoroughly
- Delivers working code at each step
