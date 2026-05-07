# Post-Mortem: CI/CD Quality Gate Failure & Environment Isolation

| Attribute | Details |
| :--- | :--- |
| **Incident ID** | `INC-20260507-01` |
| **Date** | 2026-05-07 |
| **Severity** | **SEV-3** (Workload Blocked) |
| **Status** | **RESOLVED** |
| **Service Affected** | GitHub Actions Runner / CI/CD Pipeline |
| **MTTR** | ~90 minutes |

---

## 1. Executive Summary
During the deployment of the `feature/quality-gates` branch, the CI/CD pipeline encountered a systemic failure in the `quality-gates` job. The GitHub Actions Self-Hosted Runner returned `Exit Code 127 (Command not found)` for `yamllint`, `ansible-lint`, and `trivy`, despite successful infrastructure provisioning logs. The issue was identified as a **Stale Environment State** and **Host-Provisioning Decoupling**. The system was stabilized by implementing a **Self-Provisioning** architecture and dynamic process-level environment refreshes.

---

## 2. Chronology (Timeline)
* **06:50 UTC:** Initial deployment triggered. Job `Lint & Security Scan` failed immediately with error `127`.
* **07:15 UTC [Detection]:** Manual inspection via `vagrant ssh` confirmed tools were physically present on disk in `/usr/bin/` but missing from the Runner's active `$PATH`.
* **07:30 UTC [Troubleshooting]:** Identified that the `Vagrantfile` was attempting to use the Host's Ansible engine, leading to relative path mismatches and fragile execution contexts.
* **08:10 UTC [RCA]:** Confirmed that even after manual installation, the GitHub Runner service (Systemd) did not inherit the updated environment variables.
* **08:30 UTC [Resolution]:** Refactored to **Internal Self-Provisioning** and implemented dynamic service restarts.
* **08:45 UTC [Validation]:** Pipeline successfully executed all quality gates.

---

## 3. Root Causes (RCA)

### 3.1 Provisioning Decoupling (The "Fragile Path" Problem)
The initial design relied on the developer's host machine to configure the Runner. This created a dependency where the `Vagrantfile` pathing (e.g., `../ansible/site.yml`) was relative to the host's directory structure. If the runner was deployed from a different hierarchy or without a local Ansible installation, the provisioning would fail silently or partially.

### 3.2 Process Environment Lifecycle (The "Stale PID" Problem)
The GitHub Actions Runner service starts during the initial bootstrap of the VM. In Linux, a running process inherits its environment variables (like `$PATH`) at the moment of the `fork()`. 
* **The Conflict:** Ansible installed the linting tools *after* the Runner process was already alive.
* **The Result:** The Runner remained "blind" to the new binaries in `/usr/bin/` because it was using a cached version of the environment from its boot time.

---

## 4. Technical Audit & Tooling
The following telemetry and commands were used to isolate the failure:

| Command / Tool | Technical Purpose | Finding |
| :--- | :--- | :--- |
| `which [tool]` | Binary presence check | Confirmed tools existed in `/usr/bin/` but were ignored by the Runner. |
| `systemctl status` | Process Telemetry | Revealed the service PID was older than the tool installation timestamp. |
| `[ ! -z "$VAR" ]` | Defensive Bash | Ensured the restart logic only triggered if the service name was resolved. |
| `rsync` | Data Sync | Used to move IaC code into the runner for host-independent execution. |

---

## 5. Mitigation & Resolution

### 5.1 Architectural Shift: Internal Self-Provisioning
We moved the "Control Plane" of the provisioning inside the Runner.
* **Implementation:** The `Vagrantfile` now mounts the `infrastructure/ansible` folder via `rsync`.
* **Benefit:** The Runner now configures itself using its own local Ansible engine, making the deployment **Host-Agnostic**.

### 5.2 Dynamic Service Refresh
Implemented a post-provisioning trigger to force an environment reload:
```bash
# SRE Logic: Force the runner to reload its $PATH
SERVICE_NAME=$(systemctl list-unit-files | grep actions.runner | awk '{print $1}')
if [ ! -z "$SERVICE_NAME" ]; then
    sudo systemctl restart "$SERVICE_NAME"
fi
```

---

## 6. Prevention Roadmap
* **[X] Stateless Pre-flight Checks:** Add a script to the pipeline to verify linter versions before execution.
* **[ ] Golden Image Baking:** Evaluate the use of **HashiCorp Packer** to pre-install all SRE tools into the base image, reducing runtime provisioning time by ~4 minutes.
* **[X] Documentation Update:** Update the `README.md` to reflect the new internal provisioning flow.

---
> **SRE Mindset:** We don't just fix bugs; we close the loop between infrastructure state and process execution.
