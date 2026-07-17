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
flowchart TB
  %% Remote Access
  User((Me<br>on train)) -. "Approve" .-> Discord[Discord Chat UI]

  %% Frontend Segment (Everything lives here primarily)
  subgraph Frontend[Frontend Network : 172.16.0.0/24]
    direction TB
    
    subgraph Proxmox[Proxmox VE - Ryzen 5300U]
      direction TB
      Architect{LXC 999: Architect<br>AI Co-Pilot}
      
      %% Grouping other nodes to keep it compact
      subgraph Nodes[Containers & VMs]
        Network[LXC 101: Network]
        Immich[LXC 100: Immich]
        HA[QEMU 102: HAOS]
        Whoop[LXC 103: Whoop]
      end
      
      Architect ~~~ Nodes
    end
  end

  Discord -- "Context & Commands" --> Architect

  %% Backend Segment (Isolated)
  subgraph Backend[Backend Network : 10.0.0.0/24 / Isolated]
    direction TB
    QNAP[(QNAP TS-233<br>NFS Storage)]
  end

  %% Connections to Backend
  Immich ===|NIC 2| Backend
  HA -.-|Planned| Backend
  Whoop -.-|Planned| Backend

  %% Styling
  style Frontend fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
  style Backend fill:#ffebee,stroke:#c62828,stroke-width:2px
  style Architect fill:#f3e5f5,stroke:#8e24aa,stroke-width:2px
  style QNAP fill:#fff3e0,stroke:#e65100,stroke-width:2px
  style Proxmox fill:#fafafa,stroke:#424242,stroke-dasharray: 5 5
  style Nodes fill:none,stroke:none
