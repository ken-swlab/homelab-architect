# Project "Architect": A Self-Hosted HomeLab Co-Pilot using LLM/Agents

## 1. Background & Motivation
I am a 3rd-year on-premise infrastructure engineer in Japan. While physical networking and hardware setups are second nature to me, modern container orchestration, Python, and API integrations were relatively new. 

When building my home lab, I quickly realized I had become a **"copy-paste slave"** to AI—endlessly prompt-engineering, copying code from ChatGPT/Gemini, pasting it into the terminal, hitting dependency/environment errors, and repeating the cycle. I built this home lab for freedom, yet the process felt like digital servitude. 

To break free, I am hosting my own AI partner, **"Architect"**, inside a lightweight LXC container in my Proxmox cluster. By giving it the context of my entire infrastructure, it will safely automate and orchestrate my HomeLab via Discord.

---

## 2. Current Status (Phase 1 Complete)
Architect is built using LangChain and the Gemini API, with Read-Only Proxmox tokens, Tavily Web search, and Discord interactions. 

Currently, Architect can flawlessly read the infrastructure's context. When pinged on Discord, it scans the cluster and returns a detailed Markdown report. 
*(For example, it correctly identifies that my Immich LXC's network and NFS mounts are handled directly by Proxmox `mp0` and not by internal `/etc/fstab`, and logs all active VMs like Home Assistant OS).*

---

## 3. The Current Challenge: "Deep Reasoning & Planning"
While Architect is great at gathering data, it currently lacks **deep sequential reasoning**. If I ask it to *"Deploy a password manager container,"* it tries to output code immediately. 

What I want Architect to do is **take its time to think, reason, and plan** before spitting out code. It needs to:
1. **Analyze Constraints:** "This is a password manager, so it *must* use HTTPS. Where should the SSL certificates live?"
2. **Gather Fresh Knowledge:** "What is the latest stable Docker image for this service? Let me search the web via Tavily first."
3. **Map Dependencies:** "Before installing the service, I need to check the OS baseline and run an update script first. What should the static IP be within the private segment?"

I am currently figuring out how to enforce this "Thinking Process" within the agent workflow.

---

## 4. Hardware & Network Topology
* **Host Machine:** GenMachine MD Ryzen 5300U (4C/8T), 16GB DDR4, 500GB SSD, Dual 2.5G LAN (Running Proxmox VE).
* **Storage:** QNAP TS-233 (4TB) connected via a dedicated storage path.
* **Network Isolation:** 
    * **NIC 1 (Frontend):** Connected to the Provider Wi-Fi segment (`172.16.0.0/24`).
    * **NIC 2 (Backend):** Connected **directly** to the QNAP NAS (`10.0.0.0/24` private segment). The backend network is completely invisible from the frontend.
* **Remote Management:** Tailscale VPN + AdGuard Home, allowing secure configuration via Termius (SSH) during my daily 1-hour train commute.

### Architecture Diagram

```mermaid
flowchart LR
  %% Remote Section
  User((Me<br>on train))
  Discord[Discord<br>Chat UI]
  User -- "Approve & Deploy" --> Discord

  %% Proxmox Host
  subgraph Proxmox[Proxmox VE - Ryzen 5300U]
    direction TB
    Architect{LXC 999: Architect<br>LangChain + Gemini API}
    Immich[LXC 100: Immich<br>Photo Pipeline]
    HA[QEMU 102: HAOS<br>Smart Home]
  end

  Discord -- "Context & Commands" --> Architect

  %% Networks
  Frontend((Frontend Net<br>172.16.0.0/24))
  Backend((Backend Net<br>10.0.0.0/24<br>Isolated))

  %% External Storage
  QNAP[(QNAP TS-233<br>NFS Storage)]

  %% Connections (Frontend)
  Architect -.-> Frontend
  Immich -.-> Frontend
  HA -.-> Frontend

  %% Connections (Backend / Secure)
  Architect === Backend
  Immich === Backend
  Backend === QNAP

  %% Styling (Nerd Sniping Visuals)
  style Backend fill:#ffebee,stroke:#c62828,stroke-width:2px
  style Frontend fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
  style Architect fill:#f3e5f5,stroke:#8e24aa,stroke-width:2px
  style QNAP fill:#fff3e0,stroke:#e65100,stroke-width:2px
  style Proxmox fill:#fafafa,stroke:#424242,stroke-dasharray: 5 5


