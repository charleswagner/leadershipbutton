# Development Notepad

_Quick capture for ideas, tasks, and decisions_

---

## Ideas

### Enhanced Development Analytics & Metrics

- **Session Percentage Tracking**: Show percentage time spent vibing, architecting, designing, product designing, and spec-driven development
- **Development Dimension Commands**: Add command to get status update on current development focus across all dimensions
- **Performance Insights**: Lines per hour, features per session, time per decision for continuous improvement

### Enhanced Notepad System

- **Multiple Notepads**: Allow notepad-1.md, notepad-2.md, etc. while keeping notepad.md as mandatory default
- **Advanced Notepad Commands**: Add cleanup commands that analyze implemented items and recommend deletions
- **Smart Organization**: Automatic categorization and duplicate detection

### Centralized Script Organization

- **Workflow Engineering**: Centralized tools for development process automation and enhancement
- **Convention Integration**: Update all project conventions to reference centralized script location

### Simplified Modes Overview

- **Replace verbose bullet format** with simple table showing mode, purpose, and command
- **Streamline user experience** by reducing cognitive load during mode selection
- **Maintain all functionality** while improving readability and quick reference

## To Do List

### High Priority

- **Implement development analytics & metrics system** (session percentage tracking, dimension status commands)
- **Design enhanced notepad system** (multiple notepads, cleanup commands, smart organization)
- **Create simplified modes overview table** (replace verbose format with concise table)

### Medium Priority

- **Establish centralized script organization** (update conventions, create .specpilot/scripts structure)

### Active Tasks

- **Centralized script organization structure** and project conventions update
- **Simplified modes overview table** creation and implementation

## Decisions to Make

### Organization Strategy

- **Centralized organization**: Workflow scripts belong in dedicated SpecPilot location
- **Notepad content focus**: Summaries should reflect actual notepad content, not system status
- **Simplified communication**: Reduce verbosity in mode overviews and user interfaces

## Other Notes

### Technical Implementation Notes

- **Config file strategy**: Single configuration file managing all SpecPilot behavior
- **Modular design**: Features can be enabled/disabled independently but work together when active
- **Backward compatibility**: New unified systems should work with existing logging and commit protocols
- **Notepad summary format**: Controlled by `logging.notepad_summary` configuration setting
- **UI/UX optimization**: Streamline user interfaces to reduce cognitive load and improve efficiency

### Implemented Framework Features

- **Configuration-first approach**: All features are configurable rather than forced (implemented)
- **Integration over fragmentation**: Combine related features into unified systems
- **User experience priority**: Complexity is optional and toggleable

---

_Use "Add to notepad:" to capture content | Use "Organize Notepad" to clean up_
