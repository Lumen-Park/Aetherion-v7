<p align="center">
  <img src="https://img.shields.io/badge/AETHERION-v3.0.0-000000?style=for-the-badge&logo=starship&logoColor=white&labelColor=1a1a2e" alt="Version">
  <img src="https://img.shields.io/badge/PYTHON-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/OLLAMA-LOCAL-ffffff?style=for-the-badge&logo=ollama&logoColor=black" alt="Ollama">
  <img src="https://img.shields.io/badge/LICENSE-MIT-2ea44f?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/STATUS-PRODUCTION_READY-00c853?style=for-the-badge" alt="Status">
  <img src="https://github.com/Lumen-Park/Aetherion-/actions/workflows/main.yml/badge.svg?branch=main" alt="CI">
</p>

<h1 align="center">
  <span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
    ⚡ AETHERION v3
  </span>
</h1>

<h3 align="center">
  <i>The Autonomous AI Research Institution — Entirely Local, Entirely Yours</i>
</h3>

<p align="center">
  <b>67+ specialized agents · 11 academic colleges · 7‑judge Supreme Council · Self‑improving · Voice/Vision/Email</b>
</p>

<br>

<div align="center">
  <a href="#-quick-start">
    <img src="https://img.shields.io/badge/QUICK_START-▶-6c5ce7?style=for-the-badge&logo=rocket&logoColor=white" alt="Quick Start">
  </a>
  <a href="#-architecture">
    <img src="https://img.shields.io/badge/ARCHITECTURE-🏛-0984e3?style=for-the-badge" alt="Architecture">
  </a>
  <a href="#-the-aetherion-council">
    <img src="https://img.shields.io/badge/COUNCIL-⚖-d63031?style=for-the-badge" alt="Council">
  </a>
  <a href="#-agent-roster">
    <img src="https://img.shields.io/badge/AGENTS-67+-00b894?style=for-the-badge" alt="Agents">
  </a>
  <a href="#-security--safety">
    <img src="https://img.shields.io/badge/SECURITY-🛡-e17055?style=for-the-badge" alt="Security">
  </a>
</div>

---

<br>

> <div align="center"><b>“Without structure it becomes noise. With structure it becomes powerful.”</b></div>

<br>

## 📖 Overview

Aetherion v3 is not a chatbot. It is a **fully autonomous, self-governing research organization** that operates entirely on your local machine. It combines:

- 🧠 **67+ domain‑expert agents** — from physicists to patent examiners
- 🏛️ **A Supreme Council** with veto power and bias detection
- 🔁 **Recursive delegation** — fractal teams for complex tasks
- 🧬 **Self‑improvement** — audits, refactors, and proposes its own evolution
- 🎛️ **Hardware interfaces** — voice, vision, email, cron scheduler

No cloud. No API keys. No data leaves your laptop.

---

## 🧭 Quick Start

```bash
# 1. Install Ollama and required models
curl -fsSL https://ollama.com/install.sh | sh
ollama run llama3        # primary reasoning model
ollama pull llava        # vision model

# 2. Clone and install dependencies
git clone https://github.com/yourusername/aetherion_v3.git
cd aetherion_v3
pip install -r requirements.txt

# 3. Launch the institution
python main.py
```
💡 Optional: configure email reports — see Email Setup.

---

🏛️ Architecture

Aetherion v3 is structured as a three‑tier governance model that separates orchestration, execution, and validation.

```mermaid
%%{init: {'theme':'base', 'themeVariables': {
  'primaryColor': '#4c51bf',
  'primaryTextColor': '#fff',
  'primaryBorderColor': '#2d3748',
  'lineColor': '#a0aec0',
  'secondaryColor': '#2b6cb0',
  'tertiaryColor': '#2d3748'
}}}%%
graph TB
    subgraph "🎮 Human Interface"
        UI[Web Dashboard / Voice / Terminal]
        style UI fill:#3182ce,stroke:#2b6cb0,color:#fff
    end
    
    subgraph "👑 Tier 1: Governance"
        MO[Meta-Orchestrator]
        CU[Curator]
        CM[Context Manager]
        CL[Cognitive Load Mgr]
        style MO fill:#e53e3e,stroke:#c53030,color:#fff
        style CU fill:#dd6b20,stroke:#c05621,color:#fff
        style CM fill:#3182ce,stroke:#2b6cb0,color:#fff
        style CL fill:#3182ce,stroke:#2b6cb0,color:#fff
    end
    
    subgraph "⚖️ Tier 2: The Supreme Council"
        direction LR
        SAN[Sanitizer] --> FOR[Forensic Analyst] --> EDGE[Edge-Case Gen]
        EDGE --> J1[Critic]
        EDGE --> J2[Security]
        EDGE --> J3[Alignment]
        EDGE --> J4[Constraint]
        EDGE --> J5[Evaluator]
        EDGE --> J6[Documentation]
        EDGE --> J7[Aetherion Prime]
        J1 & J2 & J3 & J4 & J5 & J6 & J7 --> VOTE{Voting}
        VOTE --> LIA[Liaison]
        style SAN fill:#805ad5,stroke:#6b46c1,color:#fff
        style FOR fill:#805ad5,stroke:#6b46c1,color:#fff
        style EDGE fill:#805ad5,stroke:#6b46c1,color:#fff
        style J1 fill:#e53e3e,stroke:#c53030,color:#fff
        style J2 fill:#e53e3e,stroke:#c53030,color:#fff
        style J3 fill:#e53e3e,stroke:#c53030,color:#fff
        style J4 fill:#e53e3e,stroke:#c53030,color:#fff
        style J5 fill:#e53e3e,stroke:#c53030,color:#fff
        style J6 fill:#e53e3e,stroke:#c53030,color:#fff
        style J7 fill:#e53e3e,stroke:#c53030,color:#fff
        style VOTE fill:#d69e2e,stroke:#b7791f,color:#fff
        style LIA fill:#38a169,stroke:#2f855a,color:#fff
    end
    
    subgraph "🎓 Tier 3: Academic Colleges"
        SCI[🧪 Science]
        BUS[💼 Business]
        DAT[📊 Data]
        HUM[📜 Humanities]
        ENG[🛠️ Engineering]
        HEA[🏥 Health]
        ENV[🌍 Environment]
        SEC[🔐 Security]
        LAW[⚖️ Law]
        ART[🎨 Arts]
        ADV[🔮 Advanced]
        style SCI fill:#2b6cb0,stroke:#2c5282,color:#fff
        style BUS fill:#2b6cb0,stroke:#2c5282,color:#fff
        style DAT fill:#2b6cb0,stroke:#2c5282,color:#fff
        style HUM fill:#2b6cb0,stroke:#2c5282,color:#fff
        style ENG fill:#2b6cb0,stroke:#2c5282,color:#fff
        style HEA fill:#2b6cb0,stroke:#2c5282,color:#fff
        style ENV fill:#2b6cb0,stroke:#2c5282,color:#fff
        style SEC fill:#2b6cb0,stroke:#2c5282,color:#fff
        style LAW fill:#2b6cb0,stroke:#2c5282,color:#fff
        style ART fill:#2b6cb0,stroke:#2c5282,color:#fff
        style ADV fill:#2b6cb0,stroke:#2c5282,color:#fff
    end
    
    UI <--> MO
    MO --> CU
    CU --> SCI & BUS & DAT & HUM & ENG & HEA & ENV & SEC & LAW & ART & ADV
    SCI & BUS & DAT --> SYN[Synthesizer]
    SYN --> SAN
    LIA --> UI
```

Directory Structure

```
aetherion_v3/
├── main.py                          # Entry point (all modes)
├── core/                            # Protocol, State Machine, Memory Graph
├── agents/
│   ├── governance/                  # Meta‑orchestration
│   ├── council/                     # 7‑judge panel + pipeline
│   ├── colleges/                    # 67+ domain experts (lazy‑loaded)
│   ├── pipeline/                    # Researcher, Developer, Tester...
│   ├── improvement/                 # Self‑audit and code generation
│   └── interfaces/                  # Voice, Vision, Email, Scheduler
├── missions/                        # Invention & open‑source mission modes
├── memory/                          # Persistent knowledge graph (ChromaDB)
├── output/                          # Generated code artifacts
├── reports/                         # Markdown mission reports
├── blueprints/                      # Approved invention blueprints
├── latex_docs/                      # Compiled LaTeX research documents
├── council_archive/                 # Versioned verdicts for self‑reflection
├── proposed_improvements/           # Agent changes awaiting human approval
├── backups/                         # Automatic rollback safety
└── changelog/                       # Applied improvement history
```

---

⚖️ The Aetherion Council

Every output passes through a rigorous 7‑judge peer‑review before reaching you.

Judge Power Primary Question
Critic Soft Veto What is the single strongest argument against this?
Security ABSOLUTE VETO Any vulnerabilities, secrets, or unsafe patterns?
Alignment Vote Does this match the user's actual request?
Constraint Vote Within scope and resource limits?
Evaluator Vote Quality score (0–10). Is reasoning sound?
Documentation Vote Can a stranger understand this?
Aetherion Prime Tiebreaker Safest path forward given split vote?

Pre‑Council Pipeline

Agent Role
Sanitizer Strips markdown/noise — Council reviews clean work only.
Forensic Analyst Fact‑checks: imports exist? APIs real? RAM feasible?
Edge‑Case Generator Generates adversarial inputs and boundary tests.
Juror Detects groupthink, complexity bias, and anchoring.

Post‑Council

Agent Role
Liaison Translates complex verdict into simple ✅/⚠️/❌ card.
Telemetry Monitors Council health (too strict? too lenient?).
Archivist Stores rejection patterns for future reference.

---

🤖 Agent Roster

The Curator dynamically selects the minimal viable panel for each task — you never run all 67+ agents simultaneously.

<details>
<summary><b>🧪 Natural Sciences (6 agents)</b></summary>
<p>

Agent Focus
Physicist Physical laws, energy conservation, material feasibility
Chemist Reactions, material compatibility, synthesis pathways
Biologist Living systems, genetics, ecological impacts
Mathematician Proofs, convergence, numerical stability
Astronomer Orbital mechanics, astrophysical constraints
Geologist Earth systems, mineral resources, tectonics

</p>
</details>

<details>
<summary><b>💼 Business & Economics (6 agents)</b></summary>
<p>

Agent Focus
Economist Market forces, pricing models, TAM/SAM/SOM
Enterprise Architect Organizational fit, integration cost, scalability
Finance ROI analysis, break‑even, funding requirements
Marketing Analyst Positioning, competitive landscape, GTM strategy
Legal/Compliance Regulatory frameworks, liability assessment
Supply Chain Manufacturing, logistics, sourcing risks

</p>
</details>

<details>
<summary><b>📊 Data & Analytics (5 agents)</b></summary>
<p>

Agent Focus
Data Scientist ML model design, feature engineering, validation
Statistician Hypothesis testing, significance, bias detection
Geospatial Analyst Maps, location intelligence, spatial patterns
Forecasting Time series, trend extrapolation, uncertainty bounds
Operations Research Optimization, queueing theory, logistics efficiency

</p>
</details>

<details>
<summary><b>📜 Humanities (5 agents)</b></summary>
<p>

Agent Focus
Historian Past attempts, failed projects, historical patterns
Philosopher/Ethicist Ethical implications, unintended consequences
Sociologist Cultural adoption barriers, social dynamics
Linguist Terminology, translation, clarity
Design/Creative UX heuristics, accessibility, aesthetic cohesion

</p>
</details>

<details>
<summary><b>🛠️ Engineering (5 agents)</b></summary>
<p>

Agent Focus
Systems Architect High‑level design tradeoffs, technology selection
Performance Engineer Latency, throughput, scaling limits
DevOps Deployment, infrastructure as code, CI/CD
Network Engineer Protocols, latency, bandwidth constraints
Database Specialist Schema design, query optimization, data integrity

</p>
</details>

<details>
<summary><b>🏥 Health & Medicine (6 agents)</b></summary>
<p>

Agent Focus
Medical Doctor Clinical practice, diagnostic validity, patient safety
Pharmacologist Drug interactions, dosing, pharmacokinetics
Neuroscientist Brain function, cognitive load, neural mechanisms
Biomedical Engineer Implants, devices, biocompatibility
Nutritionist Dietary claims, metabolic effects
Geneticist DNA, heredity, CRISPR ethics

</p>
</details>

<details>
<summary><b>🌍 Environment & Climate (5 agents)</b></summary>
<p>

Agent Focus
Climate Scientist Models, carbon cycles, tipping points
Ecologist Ecosystems, biodiversity, invasive species
Hydrologist Water systems, aquifers, drought management
Disaster Resilience Earthquakes, floods, extreme weather engineering
Circular Economy Waste streams, recyclability, lifecycle analysis

</p>
</details>

<details>
<summary><b>🔐 Security & Defense (4 agents)</b></summary>
<p>

Agent Focus
Red Team Adversarial thinking, penetration testing mindset
Cryptographer Encryption, hashing, key management best practices
Signals Intelligence RF, side‑channel attacks, TEMPEST
Privacy Officer GDPR/CCPA compliance, data minimization

</p>
</details>

<details>
<summary><b>⚖️ Law & Policy (4 agents)</b></summary>
<p>

Agent Focus
Patent Examiner Prior art search, novelty assessment
Regulatory Affairs FDA, FCC, FAA, SEC compliance pathways
International Trade Export controls, tariffs, sanctions
Compliance ISO, SOC2, HIPAA, PCI‑DSS requirements

</p>
</details>

<details>
<summary><b>🎨 Arts & Media (4 agents)</b></summary>
<p>

Agent Focus
Copywriter Clarity, persuasion, tone of voice
Multimedia Video/audio production feasibility, rendering estimates
Journalist Fact‑checking, source verification, narrative structure
Localization Cultural adaptation, translation nuance

</p>
</details>

<details>
<summary><b>🔮 Advanced Research (4 agents)</b></summary>
<p>

Agent Focus
Futurist Long‑term trends, scenario planning
Systems Thinker Feedback loops, unintended consequences
Interdisciplinary Bridge Cross‑domain connections, analogical transfer
Epistemologist Confidence limits, knowledge validation

</p>
</details>

---

🧬 Self‑Improvement (Controlled Evolution)

Aetherion v3 can audit its own source code, propose improvements, and even design new agents — but never without your approval.

```mermaid
%%{init: {'theme':'base', 'themeVariables': {
  'primaryColor': '#805ad5',
  'primaryTextColor': '#fff',
  'primaryBorderColor': '#2d3748',
  'lineColor': '#a0aec0'
}}}%%
flowchart TD
    A[Task Completed] --> B{Council Score ≥ 7?}
    B -->|Yes| C[Reflection Agent analyzes success]
    B -->|No| D[Post-Mortem analyzes failure]
    
    C --> E[Store winning pattern in Knowledge Graph]
    D --> F[Identify root cause + mitigation]
    
    E & F --> G[Code Audit Agent scans agent files]
    G --> H[Refactor Architect generates diff]
    H --> I[Integration Validator tests in Docker sandbox]
    I --> J{Council reviews proposal}
    J -->|Approve| K[Proposal saved to proposed_improvements/]
    J -->|Reject| L[Discard]
    
    K --> M[👤 HUMAN REVIEW]
    M -->|Approve| N[Safe Apply: backup → patch → changelog]
    M -->|Reject| L
    
    N --> O[Agent module reloaded]
    
    style M fill:#ecc94b,stroke:#d69e2e,color:#1a202c,font-weight:bold
    style N fill:#38a169,stroke:#2f855a,color:#fff
```

The Agent Forge

When no existing agent can handle a task, the Agent Forge designs a new one:

1. Spec Writer drafts YAML specification (name, role, prompt, college)
2. Council reviews necessity and safety
3. Human approves creation
4. Agent Factory generates Python class and registers it

---

🛡️ Security & Safety

Absolute Veto

The Security judge has absolute veto power. If it flags any of the following, output is instantly rejected:

```
sudo · rm -rf · eval() · exec() · chmod 777 · /etc/ · fork bombs · base64 secrets
```

Human‑in‑the‑Loop (Always)

Action Automatic? Human Gate
Git commit / push ❌ Never Must manually run git push
Apply code improvements ❌ Never Review and approve diff
Store to long‑term memory ⚠️ Conditional Only if confidence ≥ 0.45
Council verdict ❌ Advisory You always have final override
Run generated code ❌ Never on host Executes only in sandboxed Docker container

Loop Protection

Mechanism Threshold
Same‑state detection 3 identical states → force forward
Agent call budget 50 max per task
Timeout 420 seconds per task
Cognitive load monitor Pauses agents if CPU/RAM exceed threshold

Sandboxed Execution

All generated code runs inside a disposable Docker container with no network, read‑only root, and automatic destruction.

---

⚙️ Task State Machine

Every mission follows a formal, non‑reversible state graph.

```mermaid
%%{init: {'theme':'base', 'themeVariables': {
  'primaryColor': '#3182ce',
  'primaryTextColor': '#fff',
  'lineColor': '#a0aec0'
}}}%%
stateDiagram-v2
    [*] --> QUEUED
    QUEUED --> REFINING : Goal Refiner
    REFINING --> CURATING : Curator selects panel
    CURATING --> RESEARCHING : Researcher + colleges
    RESEARCHING --> DEVELOPING : Developer writes code
    DEVELOPING --> REVIEWING : Partner reviews
    REVIEWING --> TESTING : Tester executes
    TESTING --> SANITIZING : Sanitizer cleans output
    
    SANITIZING --> FORENSICS : Forensic fact-check
    FORENSICS --> EDGE_CASES : Edge-case generation
    EDGE_CASES --> EVALUATING : Council deliberation
    EVALUATING --> COUNCIL : 7-judge vote
    
    COUNCIL --> HUMAN_REVIEW : Liaison presents verdict
    HUMAN_REVIEW --> APPROVED : Human accepts
    HUMAN_REVIEW --> REJECTED : Human rejects
    HUMAN_REVIEW --> REVISION : Human requests changes
    
    REVISION --> DEVELOPING : Retry with new strategy
    APPROVED --> DONE
    REJECTED --> DONE
```

---

📡 Interfaces

Interface Capability Requirements
Voice Agent Microphone input → STT → TTS response SpeechRecognition, pyttsx3, pyaudio
Vision Agent Screenshot → llava analysis Pillow, pyautogui, ollama pull llava
Email Agent SMTP reports with attachments SMTP credentials (optional)
Scheduler Cron‑style autonomous job scheduling schedule library

Email Setup (optional)

```python
from agents.interfaces.interfaces import configure_email
configure_email("smtp.gmail.com", 587, "you@gmail.com", "app_password", "recipient@example.com")
```

---

🚀 Example: Invention Mode

```bash
python main.py --mode invent "Self-healing road material using bacteria"
```

Internal Flow:

```
Idea → Theory → Hypothesis → Simulation → Design → Blueprint
    ↓
Colleges Review: [Chemist, Biologist, Civil Engineer, Economist, Patent Examiner]
    ↓
Council Deliberation (7 judges + pre/post pipeline)
    ↓
Human Approval
    ↓
LaTeX Blueprint → /blueprints/self_healing_road.pdf
```

Sample Output:

· Full research document with figures
· Feasibility score and dissenting opinions
· Patent prior art analysis
· Estimated development cost and timeline

---

🚫 What Aetherion v3 Will NEVER Do

· Auto‑push to GitHub or any remote repository
· Auto‑apply code changes to its own source files
· Store low‑confidence outputs in long‑term memory
· Run untrusted code on your host operating system
· Make Council decisions without showing you the verdict and reasoning
· Bypass the Security judge's veto (unless you explicitly override)

---

🤝 Contributing

Aetherion v3 is designed to improve itself with your guidance. To contribute:

1. Run the system on diverse tasks to build its knowledge graph.
2. Review proposals in proposed_improvements/ and approve those that make sense.
3. Manually edit agent prompts in the source files if you notice systematic biases.
4. Share interesting Council verdicts and invention blueprints with the community.

Human Approval Workflow for Self‑Improvement

```bash
# List pending improvements
ls proposed_improvements/

# Review a specific proposal
cat proposed_improvements/2026-04-16_developer_prompt_optimization.diff

# Approve and apply
python main.py --apply-improvement 2026-04-16_developer_prompt_optimization

# Or manually apply with git
git apply proposed_improvements/2026-04-16_developer_prompt_optimization.diff
```

---

📜 License

MIT License — free for personal, academic, and commercial use.

---

<br>

<div align="center">
  <p>
    <b>Built for the curious. Governed by reason. Always asks permission.</b>
  </p>
  <p>
    <i>“Without structure it becomes noise. With structure it becomes powerful.”</i>
  </p>
  <br>
  <img src="https://img.shields.io/badge/MADE_WITH_⚡_AETHERION-1a1a2e?style=for-the-badge" alt="Made with Aetherion">
</div>


<br>

<div align="center">
  <h3>⚡ The institution is open. The Council is seated. Your first mission awaits.</h3>
</div>
