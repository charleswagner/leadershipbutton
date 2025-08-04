### ## 📄 Documentation Templates

This section contains the official templates for all project documentation. This content will be used to create the `docs/project_conventions.md` file during the bootstrap process.

#### Template: `architecture.md`

```markdown
# Project Architecture

## 1. Core Principles

(A list of the fundamental rules that govern the system's design, e.g., security, performance, maintainability.)

## 2. System Overview

(A high-level description of the system's components and how they interact.)

## 3. Component Diagrams

(A series of diagrams using Mermaid.js syntax to visually represent the architecture.)

### 3.1. High-Level Flowchart

(A flowchart showing the main user-to-system interaction.)

### 3.2. Sequence Diagram

(A sequence diagram detailing the API calls and data flow.)

## 4. Approved Architectural Deviations Log

(A table logging any temporary, approved violations of the architectural principles for pragmatic development.)

| Task | Rule Violated | Rationale | Resolution Phase |
| :--- | :------------ | :-------- | :--------------- |
|      |               |           |                  |
```

#### Template: `spec_*.md`

```markdown
# Specification: [Feature or Module Name]

## 1. Objective

(A clear, concise goal for this specific module or script.)

## 2. Functional Requirements

### Inputs

(What does the function/class take as input? Be specific about types, formats, and constraints.)

### Outputs/Return Values

(What should it produce? Define the exact format.)

### Core Logic

(A step-by-step description of the process.)

### Error Handling

(How should failures be managed? What specific exceptions should be caught and raised?)

## 3. Non-Functional Requirements

(Dependencies, performance constraints, code style, etc.)

## 4. Examples

### Example Usage

(Provide a code snippet showing how to call the function.)

### Example Data

(Provide a small, representative sample of the input and the expected output.)
```

#### Template: `notepad.md`

```markdown
# Development Notepad

_Quick capture for ideas, tasks, and decisions_

---

## Ideas

## To Do List

## Decisions to Make

## Other Notes

---

_Use "Add to notepad:" to capture content | Use "Organize Notepad" to clean up_
```
