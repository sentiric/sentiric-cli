# Sentiric CLI (Command Line Interface)

**Description:** A command-line interface tool for developers and administrators to manage and automate the Sentiric platform.

**Core Responsibilities:**
*   Providing a convenient interface to interact with various Sentiric microservices (via `sentiric-api-gateway-service`).
*   Automating common tasks such as user management, dialplan configuration, and system monitoring.
*   Facilitating testing and debugging of platform functionalities.
*   Examples: `sentiric-cli user add`, `sentiric-cli dialplan list`, `sentiric-cli call active`.

**Technologies:**
*   Python (or Go)
*   Command-line parsing libraries (e.g., `argparse` in Python, `cobra` in Go).
*   HTTP/gRPC client libraries.

**API Interactions (As an API Client):**
*   Consumes APIs provided by `sentiric-api-gateway-service` (for all management and operational APIs).

**Local Development:**
1.  Clone this repository: `git clone https://github.com/sentiric/sentiric-cli.git`
2.  Navigate into the directory: `cd sentiric-cli`
3.  Install dependencies: `pip install -r requirements.txt` (Python) or `go mod tidy` (Go).
4.  Create a `.env` file from `.env.example` to configure the API Gateway URL and authentication credentials.
5.  Run the CLI locally: `python cli.py` (or build/run the Go executable).

**Configuration:**
Refer to `config/` directory and `.env.example` for CLI-specific configurations, including API endpoint URLs and authentication tokens.

**Deployment:**
This is typically distributed as a standalone executable or a Python package (`pip install sentiric-cli`).

**Contributing:**
We welcome contributions! Please refer to the [Sentiric Governance](https://github.com/sentiric/sentiric-governance) repository for coding standards and contribution guidelines.

**License:**
This project is licensed under the [License](LICENSE).
