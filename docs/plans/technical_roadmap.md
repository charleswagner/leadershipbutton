# Technical Roadmap: The Leadership & EQ Coach

This document is the master execution plan. Autonomous Mode will read this file and execute the first unchecked task.

---

## Phase 1: Laptop Prototype

- **Objective**: Build and validate the entire software workflow on a laptop.

- **Key Deliverables**:
  - [ ] Create the implementation spec for the audio handling module: `docs/specs/leadership_button/audio_handler.md`.
  - [ ] Implement the audio handling module: `src/leadership_button/audio_handler.py`.
  - [ ] Create the implementation spec for the Google Cloud API client: `docs/specs/leadership_button/api_client.md`.
  - [ ] Implement the API client module: `src/leadership_button/api_client.py`.
  - [ ] Create the implementation spec for the main application loop: `docs/specs/leadership_button/main_loop.md`.
  - [ ] Implement the main application loop: `src/leadership_button/main_loop.py`.
  - [ ] Create the main executable script that ties everything together: `src/main.py`.

---

## Phase 2: Raspberry Pi Hardware Setup

- **Objective**: Adapt the software for the physical hardware.

- **Key Deliverables**:
  - [ ] Update the `audio_handler.py` spec to include hardware button logic.
  - [ ] Update the `audio_handler.py` implementation to use `RPi.GPIO`.
  - [ ] Test the full end-to-end loop on the device.

---

## Phase 3: Deployment

- **Objective**: Turn the device into a standalone appliance.

- **Key Deliverables**:
  - [ ] Create a `systemd` service file to run the script on boot.
  - [ ] Document the final setup process in the main `README.md`.
