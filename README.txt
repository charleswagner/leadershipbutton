# The Leadership & EQ Coach

This project is a hardware and software prototype for a tangible, interactive device that provides insightful leadership and emotional intelligence (EQ) coaching.

## Getting Started

### Prerequisites

* Python 3.9+
* A Google Cloud account with the necessary APIs enabled.

### Installation

1.  Clone the repository:
    ```bash
    git clone <your-repo-url>
    cd leadership_button
    ```
2.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
3.  Authenticate with Google Cloud:
    ```bash
    gcloud auth application-default login
    ```

## Development Workflow

This project uses a highly structured, spec-driven workflow powered by a custom Cursor AI prompt. **To configure your environment correctly, you MUST follow these steps:**

1.  Open the file `settings/spec_driven_prompt.md`.
2.  Copy the entire contents of the file.
3.  In Cursor, open your "Spec-Driven Python" custom mode and paste the contents into the "Instructions" box.

This will ensure your AI partner follows the same rules and protocols defined for this project.
