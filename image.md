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
