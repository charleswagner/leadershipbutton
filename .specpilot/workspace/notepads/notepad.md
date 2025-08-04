# Development Notepad

_Quick capture for ideas, tasks, and decisions_

---

## Ideas

Idea to add a command to add a new feature to the product roadmap.

### AI Response Enhancements

- **Pause for Effect Programming**: Implement pause functionality in AI responses (e.g., "Oh, honey, my heart goes out to you! (pause for effect)")
- **Gap-Filling Feature**: Add canned prompts while waiting for AI response
  - Button click immediately says "Hi there!"
  - After button release, canned prompts start talking
  - Then Gemini response comes in

### User Interface Expansion

- **Web/Mobile App**: Create webpage or app so users can press button on phone and talk to assistant
- **Text Chat Integration**: Enable text chat capability for laptop users (requested by Willa)

### Analytics & Session Management

- **Session Analytics Improvements**: Fix duration tracking (calendar time vs working time)
- **Working Time Estimation**: Calculate based on log messages, estimate work periods vs breaks
- **Development Analytics & Metrics**:
  - Session percentage tracking across vibing, architecting, designing, product designing, spec-driven development
  - Development dimension status commands
  - Performance insights: lines per hour, features per session, time per decision

### Framework Enhancements

- **Enhanced Notepad System**: Multiple notepads (notepad-1.md, notepad-2.md), cleanup commands, smart organization
- **Centralized Script Organization**: Workflow engineering tools, convention integration
- **Simplified Modes Overview**: Replace verbose bullet format with concise table showing mode, purpose, and command

## To Do List

### Immediate Actions (From Session Check)

- [ ] Create missing specifications for Firestore, multi-user, and input abstraction features
- [ ] Test framework integration compatibility
- [ ] Plan Phase 3 architectural design session

### High Priority

- [ ] Implement development analytics & metrics system
- [ ] Design enhanced notepad system (multiple notepads, cleanup commands, smart organization)
- [ ] Create simplified modes overview table

### Development Analytics Tasks

- [ ] Design development analytics architecture
- [ ] Implement session percentage tracking
- [ ] Add development dimension commands
- [ ] Create performance insights system
- [ ] Comprehensive testing for analytics features

### Enhanced Notepad System Tasks

- [ ] Add multiple notepad support
- [ ] Create cleanup commands and smart organization
- [ ] Automatic categorization and duplicate detection

### Medium Priority

- [ ] Establish centralized script organization (update conventions, create .specpilot/scripts structure)
- [ ] Centralized script organization structure and project conventions update

## Decisions to Make

### Organization Strategy

- **Centralized Organization**: Workflow scripts belong in dedicated SpecPilot location
- **Notepad Content Focus**: Summaries should reflect actual notepad content, not system status
- **Simplified Communication**: Reduce verbosity in mode overviews and user interfaces

### Technical Implementation Approach

- **Framework vs Project Separation**: How to separate framework development from project-specific notes
- **Configuration Strategy**: Single configuration file managing all SpecPilot behavior vs distributed configs
- **User Experience Priority**: Balance between feature richness and simplicity

## Other Notes

### Technical Implementation Notes

- **Config File Strategy**: Single configuration file managing all SpecPilot behavior
- **Modular Design**: Features can be enabled/disabled independently but work together when active
- **Backward Compatibility**: New unified systems should work with existing logging and commit protocols
- **Notepad Summary Format**: Controlled by `logging.notepad_summary` configuration setting
- **UI/UX Optimization**: Streamline user interfaces to reduce cognitive load and improve efficiency

### Implemented Framework Features

- **Configuration-First Approach**: All features are configurable rather than forced (implemented)
- **Integration Over Fragmentation**: Combine related features into unified systems
- **User Experience Priority**: Complexity is optional and toggleable

---

_Use "Add to notepad:" to capture content | Use "Organize Notepad" to clean up_
