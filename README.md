# 🛡️ Wazuh 4.14 SOC Lab — Custom Email Integration & Dual-NIC Routing

A hands-on Security Operations Center (SOC) lab built on **Wazuh 4.14 OVA (Amazon Linux 2023)** with a **Windows 11 agent**, featuring a fully working alert-to-email pipeline via Mailtrap — achieved by independently root-causing and solving four engineering failures not covered by standard documentation.

---

## 📌 Project Overview

The goal of this lab was a functional SIEM alerting pipeline. The standard Wazuh email configuration **failed** in this environment for multiple technical reasons. Instead of accepting the defaults, each failure was diagnosed and solved with custom engineering:

- ✅ Custom Python SMTP integration replacing the unstable native email module
- ✅ Dual-NIC virtual networking (isolated management + outbound internet)
- ✅ Static routing fix for asymmetric traffic across two adapters
- ✅ Manual Base64 `AUTH PLAIN` authentication to bypass OpenSSL 3 legacy-crypto restrictions

---

## 🏗️ Lab Architecture

| Component | Detail |
|---|---|
| **SIEM Server** | Wazuh 4.14 OVA (Amazon Linux 2023) on VirtualBox |
| **Endpoint** | Windows 11 VM with Wazuh agent |
| **Adapter 1** | Host-only — `192.168.75.0/24` (management + agent traffic) |
| **Adapter 2** | NAT — outbound internet for SMTP delivery |
| **Alert Delivery** | Mailtrap sandbox inbox via custom integration |

---

## 🛠️ Engineering Challenges Solved

### Bug 1 — Native `<smtp_username>` tags crash the manager
**Problem:** On this OVA build, Wazuh's native SMTP tags crash the email module.
**Solution:** Bypassed native email entirely. Wrote a custom Python integration script, triggered from `ossec.conf` via an `<integration>` block.

### Bug 2 — VM had no internet connectivity
**Problem:** The host-only adapter isolated the server, so it could not reach external SMTP relays.
**Solution:** Added a second VirtualBox adapter in **NAT** mode — outbound internet without exposing the management network.

### Bug 3 — Dual-NIC broke SSH / Dashboard routing
**Problem:** With NAT active, Linux sent return traffic for `192.168.75.0/24` out of the wrong interface, breaking SSH and dashboard access.
**Solution:** Pinned the lab subnet to the host-only interface with a static route:

```bash
sudo ip route add 192.168.75.0/24 dev eth1 src 192.168.75.5 metric 100
```

### Bug 4 — OpenSSL 3 silently kills `smtplib.login()`
**Problem:** Mailtrap offered **CRAM-MD5** auth, but OpenSSL 3 (Amazon Linux 2023) disables MD5 — so Python's `smtplib.login()` failed silently.
**Solution:** Skipped the high-level login wrapper and injected a manual Base64 **AUTH PLAIN** command directly into the SMTP session:

```python
c = base64.b64encode(("\x00" + USER + "\x00" + PASS).encode()).decode()
s.docmd("AUTH", "PLAIN " + c)
```

---

## 💻 Custom Integration Script

📁 Uploaded in this repo as `custom-email.py` (server path: `/var/ossec/integrations/`)

Key techniques:
- `smtplib` + `STARTTLS` on port 587
- Manual Base64 `AUTH PLAIN` (OpenSSL 3 compatible)
- Credentials **redacted** for public release

---

## ⚙️ Wazuh Configuration (`ossec.conf`)

```xml
<integration>
    <name>custom-email</name>
    <level>7</level>
    <alert_format>json</alert_format>
</integration>
```

---

## 📸 Lab Evidence

| Mailtrap inbox receiving alerts | Wazuh dashboard |
|---|---|
| ![mailtrap](mailtrap-inbox.png) | ![dashboard](wazuh-dashboard-alerts.png) |

---

## 🎯 Skills Demonstrated

SIEM deployment • Linux troubleshooting • Network routing • Python scripting • SMTP/TLS authentication • OpenSSL security policy • Technical documentation

*Every failure documented. Every fix explained.*
