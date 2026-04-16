# ⚡ AETHERION v3 — Full Autonomous AI Organisation

> *"Without structure it becomes noise. With structure it becomes powerful."*

Your dedicated-laptop AI institution: 67+ agents, 11 academic colleges,
a 7-judge Supreme Council, voice control, self-improvement, and an invention pipeline.

---

## 🏗️ Architecture

```
aetherion_v3/
├── main.py                          ← Entry point (all modes)
├── core/
│   ├── protocol.py                  ← AgentMessage SIP standard + LLM wrapper
│   ├── task_state.py                ← Task State Manager (full lifecycle)
│   └── memory.py                    ← KV store + knowledge graph + reputation
├── agents/
│   ├── governance/
│   │   ├── meta_orchestrator.py     ← Supreme controller (loop detection, budget)
│   │   └── curator.py               ← Expert panel selector + Constraint/Alignment
│   ├── council/
│   │   └── council.py               ← 7-judge panel + pre/post council pipeline
│   ├── colleges/
│   │   ├── science.py               ← Physicist, Chemist, Biologist, Mathematician...
│   │   └── all_colleges.py          ← All 11 colleges + master registry
│   ├── pipeline/
│   │   └── pipeline_agents.py       ← Researcher, Developer, Partner, Tester...
│   ├── improvement/
│   │   └── self_improve.py          ← CodeAudit, RefactorArchitect, AgentForge...
│   └── interfaces/
│       └── interfaces.py            ← Voice, Vision, Email, Scheduler
├── missions/
│   ├── invention_pipeline.py        ← Idea → Blueprint → LaTeX
│   └── mission_agent.py             ← Scout → Solve → Human approval
├── memory/                          ← All persistent data
├── output/                          ← Generated code
├── reports/                         ← Mission reports
├── blueprints/                      ← Approved invention blueprints
├── latex_docs/                      ← LaTeX invention documents
├── council_archive/                 ← Every council verdict (versioned)
├── proposed_improvements/           ← Agent code changes awaiting human approval
├── backups/                         ← Automatic backups before any change
└── changelog/                       ← Applied improvement log
```

---

## 🤖 Full Agent Roster (67+)

### 🏛️ Governance Layer
| Agent | Role |
|---|---|
| 👑 Aetherion | Lead AI. Your direct partner. Coordinates everything. |
| 🧭 MetaOrchestrator | Supreme controller. Loop detection, budget, timeout. |
| 🗂️ Curator | Selects minimum viable expert panel (prevents paralysis). |
| 📏 Constraint | Enforces scope, time, line limits. |
| 🎯 Alignment | Ensures output matches original intent. |
| ⏰ Deadline | Time-boxes every operation. |
| 🧭 Navigator | Decides between strategic paths before work begins. |

### ⚖️ Council (7 Core Judges)
| Judge | Power | Question |
|---|---|---|
| Critic | Soft veto | What's the strongest argument against this? |
| Security | **ABSOLUTE VETO** | Any vulnerabilities, secrets, unsafe patterns? |
| Alignment | Vote | Does this match the user's actual request? |
| Constraint | Vote | Within scope and resource limits? |
| Evaluator | Vote | Quality score (0-10). Is reasoning sound? |
| Documentation | Vote | Can a stranger understand this? |
| Aetherion Prime | **Tiebreaker** | Safest path forward given split vote? |

### 🧪 Pre-Council Pipeline
| Agent | Role |
|---|---|
| 🧹 Sanitizer | Strips markdown/noise — Council reviews clean work |
| 🔎 Forensic Analyst | Fact-checks: imports exist? APIs real? RAM feasible? |
| 🧪 Edge-Case Generator | Adversarial inputs + boundary tests |
| 🗳️ Juror | Detects groupthink, complexity bias, anchoring |

### 📋 Post-Council
| Agent | Role |
|---|---|
| 📞 Liaison | Translates verdict into plain ✅/⚠️/❌ card |
| 📈 Telemetry | Monitors Council health (too strict? too lenient?) |
| 📜 Archivist | Stores rejection patterns for future reference |

### 🎓 Academic Colleges (activate via Curator)

**🧪 Natural Sciences** — Physicist, Chemist, Biologist, Mathematician, Astronomer, Geologist

**💼 Business & Economics** — Economist, Enterprise Architect, Finance, Marketing, Legal/Compliance, Supply Chain

**📊 Data & Analytics** — Data Scientist, Statistician, Geospatial, Forecasting, Operations Research

**📜 Humanities** — Historian, Philosopher, Sociologist, Linguist, Design/Creative

**🛠️ Engineering** — Systems Architect, Performance Engineer, DevOps, Network Engineer, Database Specialist

**🏥 Health & Medicine** — Medical Doctor, Pharmacologist, Neuroscientist, Biomedical Engineer, Nutritionist, Geneticist

**🌍 Environment & Climate** — Climate Scientist, Ecologist, Hydrologist, Disaster Resilience, Circular Economy

**🔐 Security & Defense** — Red Team, Cryptographer, Signals Intel, Privacy Officer

**⚖️ Law & Policy** — Patent Examiner, Regulatory Affairs, International Trade, Compliance

**🎨 Arts & Media** — Copywriter, Multimedia, Journalist, Localization

**🔮 Advanced Research** — Futurist, Systems Thinker, Interdisciplinary Bridge, Epistemologist

**🌌 Esoteric (rare triggers)** — Theoretical Physics, Synthetic Biology, Game Theorist, Contrarian, and more

### 🔄 Core Pipeline Agents
| Agent | Role |
|---|---|
| 🎯 Goal Refiner | "Make app" → "Create Python CLI calculator with +/-/*/÷" |
| 🔬 Researcher | Deep technical research with knowledge context |
| 🧠 Synthesizer | Merges multi-agent findings into unified brief |
| 🎤 Presenter | Formats brief as Council presentation |
| 👨‍💻 Developer | Writes code. Forces new strategy each retry. |
| 🤝 Partner | Reviews and improves code |
| 🧪 Tester | Auto-runs. **Forces different fix approach each retry.** |
| 📄 Reporter | Full markdown mission report |
| 🌐 Scout | DuckDuckGo web search (no API key needed) |
| 📝 Documentation | README + docstrings + plain-English explanation |

### 🔧 Self-Improvement System
| Agent | Role |
|---|---|
| 🔬 Code Audit | Scans agent files for bugs/inefficiencies |
| 🛠️ Refactor Architect | Generates code improvement diffs |
| 🧪 Integration Validator | Syntax + logic checks in isolation |
| ⚗️ Agent Forge | Designs and generates entirely new agents |
| 💀 Post-Mortem | Analyses failed tasks for root causes |
| 🧬 Reflection + Learning | Stores winning patterns, improves prompts |

### 🎛️ Hardware Interfaces
| Interface | Capability |
|---|---|
| 🎤 Voice Agent | Mic input (SpeechRecognition) + TTS (pyttsx3) |
| 📷 Vision Agent | Screenshot + llava analysis |
| 📧 Email Agent | SMTP auto-reports with attachments |
| ⏰ Scheduler | Cron-style autonomous job scheduling |

---

## 🔑 Key Design Principles

### Task State Machine
Every task moves through: `QUEUED → REFINING → CURATING → RESEARCHING → DEVELOPING → REVIEWING → TESTING → SANITIZING → FORENSICS → EDGE_CASES → EVALUATING → COUNCIL → HUMAN_REVIEW → APPROVED/REJECTED/DONE`

**No backward transitions without explicit retry logic.**

### Confidence Gate
Outputs are only stored to memory if confidence ≥ 0.45.
Council stores only if score ≥ 0.50.

### Security Absolute Veto
If the Security judge votes REJECT, the entire Council is overridden.
Human can manually force-approve with explicit warning.

### Human-in-the-Loop (Always)
- No code is auto-committed to GitHub
- No agent improvements auto-applied
- Every major output shown to you with [Approve / Reject / Override] options

### Loop Protection
- MetaOrchestrator detects same state 3× in a row → forces forward
- Hard budget: 50 agent calls max per task
- Hard timeout: 420 seconds per task

---

## ⚙️ Setup

```bash
# 1. Install Ollama + models
curl -fsSL https://ollama.com/install.sh | sh
ollama run llama3
ollama pull llava          # for Vision Agent

# 2. Python dependencies
pip install ollama psutil requests beautifulsoup4 schedule \
            SpeechRecognition pyttsx3 pyaudio Pillow pyautogui

# 3. Run
cd aetherion_v3
python main.py
```

### Email setup (optional)
```python
from agents.interfaces.interfaces import configure_email
configure_email("smtp.gmail.com", 587, "you@gmail.com", "app_password", "you@gmail.com")
```

---

## 🚫 What the system NEVER does
- Auto-push to GitHub
- Auto-apply code changes to itself
- Store low-confidence outputs in memory
- Run code from the host OS without your review
- Make Council decisions without showing you the verdict

---

## 🛡️ Security Blocked Patterns
`sudo`, `rm -rf`, `os.system(`, `eval(`, `exec(`, `chmod 777`,
`open('/etc/`, `fork bombs`, `base64.b64decode(`, hardcoded secrets

---

## 📈 System Evolution
After each run, the Reflection Agent stores winning patterns.
The Code Audit Agent can propose improvements to agent files.
All proposals go to: `proposed_improvements/` for your review.
**You decide what gets applied.** The system never modifies itself without you.

