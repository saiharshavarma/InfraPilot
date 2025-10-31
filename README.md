# 🚀 InfraPilot: Natural Language-based DevOps Agent

InfraPilot is an **AI-driven DevOps assistant** that enables engineers to manage **cloud infrastructure using plain English commands**.  
Powered by **OpenAI’s GPT-4** (via LangChain), InfraPilot interprets natural language, maintains context across sessions, and performs operations on **Kubernetes**, **AWS**, and (coming soon) **Docker**—all from a Python-based command-line interface (CLI).

---

## 🌐 GitHub Repository
[https://github.com/saiharshavarma/InfraPilot](https://github.com/saiharshavarma/InfraPilot)

---

## 👥 Team Members
- **Sai Harsha Varma Sangaraju** (ss18851)  
- **Jasmine Wu** (yw7866)  
- **Mike Poon** (kp2653)  
- **Zhenzhen Chen** (zc3418)

---

## 🧠 Overview

InfraPilot bridges the gap between **DevOps engineers** and **complex cloud environments** by letting users control infrastructure through natural language.  
It converts English instructions like:

> “List all running pods in the default namespace.”  
> “Launch three EC2 instances in the test environment.”  
> “Delete the bucket I just created.”

into executable **Kubernetes** or **AWS** operations — with **safety gates** and **user approvals** before any destructive action.

---

## ⚙️ Core Features

### 🗣️ Conversational Intelligence
- **LLM Integration:** Uses GPT-4 via LangChain for intent recognition and reasoning.
- **Memory Context:** Keeps track of previous interactions to resolve pronouns (e.g., “that deployment”).
- **Reasoning Trace:** Displays model thought process in real time with dimmed console text.
- **Approval Gate:** Prompts for explicit confirmation before executing risky commands.

### ☁️ Cloud Toolkit Integrations
#### Kubernetes
- Helm chart management  
- Resource listing, applying, describing, deleting, and watching  
- TTL-based resource cache for performance optimization

#### AWS
- EC2 instance management (launch, terminate, modify)
- S3 bucket operations (create, upload, list, delete)
- DynamoDB table and item management
- Built-in retries and pagination

#### Docker *(In Progress)*
- Image building, container lifecycle, and registry operations

### 🖥️ Command-Line Interface (CLI)
- REPL-style loop: type → interpret → stream response  
- Rich **Markdown-formatted** output  
- Integrated audit logs for all actions  

---

## 🏗️ System Architecture

InfraPilot is organized into four main layers:

1. **Presentation Layer** — Command-line REPL interface for user input/output  
2. **Conversational Core** — Manages dialogue flow, memory, and reasoning  
3. **Tool Abstraction Layer** — Interfaces with Kubernetes, AWS, and (soon) Docker  
4. **External Services** — Integrates with LLM APIs, credentials, and logging systems  

---

## 🧩 Completed Components

| Component | Description |
|------------|-------------|
| **NLP & Agent** | Maps natural language to structured DevOps actions |
| **Toolkit Selector** | Determines which DevOps tool (AWS/K8s/Docker) to use |
| **Kubernetes Integration** | Full support for cluster and resource management |
| **AWS Integration** | EC2, S3, and DynamoDB support via boto3 and AWS CLI |
| **CLI Interface** | Functional REPL supporting Markdown streaming output |

---

## 🔄 In Progress
- Docker integration  
- Enhanced error handling and recovery  
- Multi-step reasoning improvement and response optimization  

---

## 🧰 Tech Stack

| Layer | Tools & Libraries |
|-------|-------------------|
| **Language Model** | OpenAI GPT-4 via LangChain ChatOpenAI |
| **Cloud SDKs** | Boto3 (AWS), kubectl & helm (Kubernetes) |
| **Backend Language** | Python 3.10 |
| **Libraries** | LangChain, OpenAI SDK, PyYAML, pytest |
| **Version Control** | GitHub |
| **Runtime** | Command-Line (REPL) |

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/saiharshavarma/InfraPilot.git
cd InfraPilot
```
### 2 Configure Environment Variables
Create a .env file in the project root:
```bash
OPENAI_API_KEY=<your-openai-api-key>
AWS_ACCESS_KEY_ID=<your-aws-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret>
AWS_REGION=us-east-1
MODEL_NAME=gpt-4
TEMPERATURE=0.3
```


> If you use profiles/role-assumption or kubeconfigs, ensure those are set up as you normally would on your machine.

---

## 🛠️ Makefile Commands

The project includes a **Makefile** that automates setup and running:

- `make help` — Show available targets  
- `make install` — Create conda env **`infrapilot-env`** (Python **3.10**) and install dependencies  
- `make run` — Activate the env and start InfraPilot (`python app.py`)

### Quickstart
