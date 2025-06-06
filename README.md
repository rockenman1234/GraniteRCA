# GraniteRCA
An RCA Agent using BeeAI with IBM Granite

### Example Screenshot:
<img width="756" alt="SCR-20250606-kwrg" src="https://github.com/user-attachments/assets/6083f41d-7a33-453e-b3a9-e98eb09f55d5" />

### Example Command:
```shell
python "rca_agent.py" --error "Users are getting 500 errors on the user profile page" --logfile 'sample.log'
```

---

### Potential idea?
Imagine a tool that reads and understands every error message your system throws at you - from cryptic kernel warnings during a Linux boot sequence to stubborn Java libraries blocked by SELinux policies. This project proposes an LLM-powered diagnostic assistant that leverages a local or remote large language model, built on the BeeAI framework, to automatically scan, interpret, and explain errors across your system. With a single command, the agent securely processes logs and system messages, providing actionable insights and tailored solutions regardless of your preferred AI provider. Whether you're debugging low-level system issues or resolving high-level application errors, this intelligent assistant bridges the gap between raw technical output and human understanding.
