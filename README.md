# Clara Retell Agent Pipeline

An intelligent agent configuration pipeline that processes call transcripts to automatically extract account data and generate AI receptionist agent specifications for the Retell platform.

## Demo Video

Loom Demo (3–5 minutes):

https://drive.google.com/file/d/1_XPJxzCEHU1B_6tWBfU7k_pN3CCSSbMR/view?usp=drive_link

## 📋 Table of Contents

- [Architecture & Data Flow](#architecture--data-flow)
- [Local Setup & Installation](#local-setup--installation)
- [Running the Pipeline](#running-the-pipeline)
- [Dataset Structure](#dataset-structure)
- [Output Locations](#output-locations)
- [API Endpoints](#api-endpoints)
- [Known Limitations](#known-limitations)
- [Production Roadmap](#production-roadmap)

---

## 🏗️ Architecture & Data Flow

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  Audio Files (.mp3, .wav)     │     Transcripts (.txt)          │
│  (demo_calls/, onboarding/)   │     (pre-transcribed)           │
└──────────┬─────────────────────────────────────────┬────────────┘
           │                                         │
      [Optional]                              [Primary Route]
           │                                         │
           ▼                                         ▼
    ┌─────────────────┐                  ┌────────────────────────┐
    │  Transcribe     │                  │  Clean Transcript      │
    │  Audio (Whisper)│                  │  (remove filler words, │
    │                 │                  │   normalize spacing)   │
    └────────┬────────┘                  └───────────┬────────────┘
             │                                        │
             └────────────────┬──────────────────────┘
                              │
                              ▼
                    ┌──────────────────────────┐
                    │ Extract Account Data     │
                    │ (Uses Ollama LLM)        │
                    │ - Company info           │
                    │ - Business hours         │
                    │ - Services offered       │
                    │ - Routing rules          │
                    │ - Emergency procedures   │
                    └──────────────┬───────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
            ┌──────────────────┐       ┌──────────────────────┐
            │ Account Memo     │       │ Apply Onboarding     │
            │ (v1)             │       │ Updates (v2)         │
            │ account_memo.json│       │                      │
            └────────┬─────────┘       └──────────┬───────────┘
                     │                            │
                     └────────────┬───────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │ Generate Agent Spec      │
                    │ (System & User Prompts)  │
                    │ agent_spec.json          │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ Generate Diff Report     │
                    │ (v1 vs v2 changes)       │
                    │ changes.md               │
                    └──────────────────────────┘
```

### Data Flow Details

1. **Input Stage**: Transcripts are placed in dated call folders (demo or onboarding)
2. **Cleaning Stage**: If raw transcript, cleanup removes filler words and normalizes formatting
3. **Extraction Stage**: Ollama LLM extracts structured account data from conversation context
4. **Memo Generation**: Structured JSON memo created with all account information
5. **Specification Generation**: Agent spec created with system prompts for receptionist behavior
6. **Comparison Stage**: Onboarding updates compared against v1 to highlight changes

### Key Dependencies

- **Ollama**: Local LLM (required for data extraction) - runs on `http://localhost:11434`
- **OpenAI Whisper**: Audio transcription (optional, for .mp3/.wav files)
- **Flask**: API server for orchestrating pipelines
- **Python 3.8+**: Core runtime

---

## 🚀 Local Setup & Installation

### Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai) installed and running locally
- FFmpeg (for audio processing) - optional

### Step 1: Clone and Install Dependencies

```bash
# Navigate to project directory
cd clara-retell-agent-pipeline

# Create virtual environment (recommended)
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Start Ollama Service

```bash
# Ensure Ollama is running (default: http://localhost:11434)
ollama serve

# In another terminal, pull the required model (if needed)
ollama pull mistral  # or your preferred model
```

### Step 3: Verify Setup

```bash
# Test transcript cleaning
python scripts/clean_transcript.py dataset/demo_calls/bens_electric/transcript.txt dataset/demo_calls/bens_electric/transcript_clean.txt

# Logs will be created at: logs/pipeline.log
```

### Step 4: Start the API Server

```bash
python scripts/pipeline_api.py
# Server will run on http://localhost:5000
```

---

## 🔄 Running the Pipeline

### Option 1: API Endpoints

#### Demo Pipeline (Initial Agent Creation)
```bash
curl -X POST http://localhost:5000/run-demo-pipeline
```

**What it does:**
1. Reads: `dataset/demo_calls/bens_electric/transcript_clean.txt`
2. Extracts account data → `outputs/account_memo.json`
3. Generates agent spec → `outputs/accounts/bens_electric/v1/agent_spec.json`

**Response:**
```json
{"status": "demo pipeline executed"}
```

#### Onboarding Pipeline (Update Agent)
```bash
curl -X POST http://localhost:5000/run-onboarding-pipeline
```

**What it does:**
1. Reads: `outputs/account_memo.json` + `dataset/onboarding_calls/bens_electric/transcript.txt`
2. Applies onboarding updates → `outputs/accounts/bens_electric/v2/account_memo.json`
3. Generates updated spec → `outputs/accounts/bens_electric/v2/agent_spec.json`
4. Creates diff report → `outputs/accounts/bens_electric/changes.md`

### Option 2: Command Line

```bash
# Extract account data
python scripts/extract_account_data.py <input_transcript> <output_memo>

# Generate agent spec
python scripts/generate_agent_spec.py <account_memo> <output_spec>

# Apply onboarding updates
python scripts/apply_onboarding_updates.py <v1_memo> <onboarding_transcript> <v2_memo>

# Generate diff report
python scripts/generate_diff.py <v1_memo> <v2_memo> <output_changes>

# Clean raw transcript
python scripts/clean_transcript.py <raw_transcript> <cleaned_transcript>

# Transcribe audio
python scripts/transcribe_audio.py <audio_file> <output_transcript>
```

### Batch Processing (Bulk Accounts)

A helper script processes every company folder under `dataset/demo_calls` in one go. It runs the extraction and spec generation for each account, creating
supporting output directories as needed. After completion the script writes a summary file.

```bash
python scripts/batch_process_accounts.py
```

- **input**: `dataset/demo_calls/<company>/transcript_clean.txt` for each account
- **outputs**:
  - `outputs/accounts/<company>/v1/account_memo.json`
  - `outputs/accounts/<company>/v1/agent_spec.json`
  - **batch summary**: `outputs/batch_summary.json` (accounts processed, successes, failures, time)

Use this when onboarding multiple customers simultaneously or re-generating specs for an entire directory.


---

## 📁 Dataset Structure

### Directory Layout

```
dataset/
├── demo_calls/
│   └── bens_electric/
│       ├── transcript.txt          # Raw transcript from initial sales call
│       └── transcript_clean.txt    # Cleaned version (no filler words)
│
└── onboarding_calls/
    └── bens_electric/
        └── transcript.txt          # Transcript from onboarding/update call
```

### How to Plug In New Datasets

#### For a New Company (Demo)
1. Create folder: `dataset/demo_calls/<company_name>/`
2. Add transcript file: `transcript.txt` (or raw audio to transcribe)
3. If raw: Run `python scripts/transcribe_audio.py <audio> <transcript.txt>`
4. Clean transcript: `python scripts/clean_transcript.py transcript.txt transcript_clean.txt`
5. Run demo pipeline

#### For Onboarding Updates
1. Create folder: `dataset/onboarding_calls/<company_name>/`
2. Add onboarding transcript: `transcript.txt`
3. Run onboarding pipeline (uses existing v1 memo)

#### Transcript Format Requirements
- Plain text (.txt) UTF-8 encoded
- Natural conversation format (no special formatting needed)
- Include both receptionist prompts and customer responses
- Context should cover:
  - Company/business name
  - Hours of operation
  - Services/departments offered
  - Call transfer/routing procedures
  - Emergency handling procedures
  - Special rules or constraints

---

## 📤 Output Locations

### Generated Files & Descriptions

```
outputs/
├── account_memo.json                    # Initial account data (v1)
│
└── accounts/
    └── bens_electric/
        ├── changes.md                   # Diff report (v1→v2 changes)
        │
        ├── v1/
        │   └── agent_spec.json          # Initial agent spec (system & user prompts)
        │
        └── v2/
            ├── account_memo.json        # Updated account data
            └── agent_spec.json          # Updated agent spec
```

### File Descriptions

| File | Purpose | Format |
|------|---------|--------|
| `account_memo.json` | Structured company/receptionist data | JSON |
| `agent_spec.json` | Agent configuration with prompts | JSON |
| `changes.md` | Change report from v1→v2 | Markdown |

### Sample account_memo.json Structure
```json
{
  "account_id": "bens_electric_001",
  "company_name": "Ben's Electric",
  "business_hours": {
    "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "start": "9:00 AM",
    "end": "5:00 PM",
    "timezone": "EST"
  },
  "office_address": "123 Main St, City, State",
  "services_supported": ["residential", "commercial", "emergency repair"],
  "emergency_definition": ["fire", "electrical hazard", "outage"],
  "emergency_routing_rules": "Route to on-call technician",
  "after_hours_flow_summary": "Take customer info, callback next business day"
}
```

### Sample agent_spec.json Structure
```json
{
  "system_prompt": "You are an AI receptionist for Ben's Electric...",
  "user_prompt_template": "Incoming call from {caller_name}...",
  "routing_rules": [...],
  "emergency_procedures": [...]
}
```

### Logs

All pipeline execution logs are stored in:
```
logs/pipeline.log
```

Format: `TIMESTAMP - LOG_LEVEL - MESSAGE`

---

## 🔌 API Endpoints

### Base URL
```
http://localhost:5000
```

### Endpoints

| Method | Endpoint | Description | Returns |
|--------|----------|-------------|---------|
| POST | `/run-demo-pipeline` | Extract initial account data & generate v1 spec | `{"status": "demo pipeline executed"}` |
| POST | `/run-onboarding-pipeline` | Apply updates & generate v2 spec with diff | `{"status": "onboarding pipeline executed"}` |

### Example Usage

```python
import requests

# Run demo pipeline
response = requests.post('http://localhost:5000/run-demo-pipeline')
print(response.json())

# Run onboarding pipeline
response = requests.post('http://localhost:5000/run-onboarding-pipeline')
print(response.json())
```

---

## ⚠️ Known Limitations

### Current Constraints

1. **Single Account Dependency**: Pipeline hardcoded for `bens_electric` company
   - Output paths cannot be easily parameterized
   - Onboarding pipeline requires existing v1 memo

2. **Ollama Dependency**: Requires local LLM service
   - Cannot run without Ollama running on `localhost:11434`
   - Model selection is not configurable
   - No fallback to cloud-based LLMs

3. **Sequential Processing**: All steps run synchronously
   - Large datasets or multiple companies cause blocking
   - No parallel processing or queuing system

4. **Limited Error Handling**
   - Subprocess failures don't return detailed error messages
   - API returns generic status regardless of success/failure
   - No validation of input data before processing

5. **Transcript Cleaning**: Basic regex-based approach
   - May not handle all filler word variations
   - No context-aware cleaning (removes all duplicates blindly)
   - Audio transcription depends on Whisper model accuracy

6. **No Versioning System**: 
   - Only v1 and v2 outputs supported
   - No ability to track multiple iterations
   - Diffs only compare v1→v2

7. **Manual Data Extraction**: Relies on LLM to extract from natural conversation
   - Accuracy depends on transcript quality and LLM capability
   - No structured interview process to ensure all fields captured

8. **Integration Constraints Not Enforced**:
   - System captures but doesn't validate integration requirements
   - No checks against actual Retell platform capabilities

---

## 🚀 Production Roadmap

### With Production Access, We Would Implement:

#### 1. **Dynamic Multi-Company Support**
```python
# Instead of hardcoded paths:
/pipeline/demo/<company_id>/<version>
/pipeline/onboarding/<company_id>/<version>

# API endpoints would accept company_id parameter:
POST /run-demo-pipeline?company=bens_electric
POST /run-onboarding-pipeline?company=bens_electric
```

#### 2. **Cloud LLM Integration**
- Support for OpenAI GPT-4, Claude, or other cloud models
- Fallback mechanism if Ollama unavailable
- Configurable model selection per company
- Better extraction accuracy with state-of-the-art models

#### 3. **Database Backend**
- Store all account memos and specs in database
- Track full version history (not just v1→v2)
- Enable branching and merging workflows
- API-driven data persistence

#### 4. **Async Job Queue**
- Redis/Celery for background processing
- Handle multiple companies/transcripts simultaneously
- Job status tracking and webhooks
- Retry mechanisms for failed steps

#### 5. **Structured Data Extraction**
```python
# Instead of free-form LLM extraction:
class StructuredInterview:
    def get_business_hours(self) -> BusinessHours
    def get_services(self) -> List[Service]
    def get_emergency_procedures(self) -> List[Procedure]
    # Asks specific questions if info incomplete
```

#### 6. **Validation & Quality Assurance**
- Validate extracted data against schema
- Confidence scoring for LLM extractions
- Manual review workflow for low-confidence fields
- A/B testing on agent specs

#### 7. **Direct Retell Platform Integration**
```python
retell_api = RetellAPI(api_key=os.getenv('RETELL_API_KEY'))
agent = retell_api.create_agent(spec_json)
# Deploy directly instead of saving to file
```

#### 8. **Advanced Analytics**
- Track agent performance across conversations
- A/B test different system prompts
- Identify common customer issues
- Optimize routing rules based on success metrics

#### 9. **Multi-language Support**
- Generate agent specs for different languages
- Multilingual transcript analysis
- Regional business hour templates

#### 10. **Automated Testing & Validation**
```python
# Simulate calls to new agents
agent_simulator = AgentSimulator(agent_spec)
results = agent_simulator.test_scenarios([
    "Customer calls about billing",
    "Emergency electrical hazard",
    "After-hours callback request"
])
# Report on agent performance before deployment
```

---

## 📊 Workflow Summary

### Demo Pipeline (First-Time Setup)
```
Input Transcript → Clean → Extract Data → Generate v1 Spec → Output Files
```
- Creates initial agent configuration
- Perfect for new customer onboarding
- Generates account_memo.json with all extracted data

### Onboarding Pipeline (Updates)
```
v1 Memo + New Transcript → Apply Updates → Generate v2 Spec → Compare → Output
```
- Updates agent based on customer feedback/new information
- Generates comparison report showing what changed
- Preserves v1 for auditing

---

## 🛠️ Troubleshooting

### Ollama Connection Error
```
Error: Failed to connect to http://localhost:11434
```
**Solution**: Ensure Ollama is running:
```bash
ollama serve
```

### Missing Transcript File
```
Error: Transcript file not found
```
**Solution**: Verify path exists and matches structure:
```bash
ls dataset/demo_calls/bens_electric/transcript_clean.txt
```

### No Output Generated
**Check logs**:
```bash
cat logs/pipeline.log  # Windows: type logs\pipeline.log
```

### Flask Server Already Running
```
Error: Address already in use
```
**Solution**:
```bash
# Kill existing process on port 5000 (Windows)
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

---

## 📝 License & Notes

This pipeline is designed for enterprise customer onboarding to Retell AI receptionist agents.

For technical questions or enhancements, refer to individual script documentation in the `scripts/` directory.

---

**Last Updated**: March 2026
