# CHANGELOG

> **Note:** For the release process and versioning guidelines, see the 'Versioning & Release Policy' section in `PROJECT_SCOPE.md`.

## **IMPORTANT: PROJECT CONTINUITY**  


## **IMPORTANT: SELF-MAINTENANCE INSTRUCTIONS**

### **Before Taking Any Action or Making Suggestions**  
1. **Read Both Files**:  
   - Read `CHANGELOG.md` and `PROJECT_SCOPE.md`.  
   - Briefly report:  
     ```
     Read [filename]: [key points relevant to current task]
     ```

2. **Review Context**:  
   - Assess existing features, known issues, and architectural decisions.

3. **Inform Responses**:  
   - Use the gathered context to guide your suggestions or actions.

4. **Proceed Only After Context Review**:  
   - Ensure all actions align with the project's scope and continuity requirements.

---

### **After Making ANY Code Changes**  
1. **Update Documentation Immediately**:  
   - Add new features/changes to the `[Unreleased]` section of `CHANGELOG.md`.  
   - Update `PROJECT_SCOPE.md` if there are changes to architecture, features, or limitations.

2. **Report Documentation Updates**:  
   - Use the following format to report updates:  
     ```
     Updated CHANGELOG.md: [details of what changed]  
     Updated PROJECT_SCOPE.md: [details of what changed] (if applicable)
     ```

3. **Ensure Alignment**:  
   - Verify that all changes align with existing architecture and features.

4. **Document All Changes**:  
   - Include specific details about:
     - New features or improvements
     - Bug fixes
     - Error handling changes
     - UI/UX updates
     - Technical implementation details

---

### **Documentation Update Protocol**
1. **Never Skip Documentation Updates**:  
   - Always update documentation, even for minor changes.

2. **Update Before Responding to the User**:  
   - Ensure documentation is complete before providing feedback or solutions.

3. **For Multiple Changes**:
   - Document each change separately.
   - Maintain chronological order.
   - Group related changes together.

4. **For Each Feature/Change, Document**:
   - What was changed.
   - Why it was changed.
   - How it works.
   - Any limitations or considerations.

5. **If Unsure About Documentation**:
   - Err on the side of over-documenting.
   - Include all relevant details.
   - Maintain consistent formatting.

---

### **Log Analysis Protocol**
1. **When Reviewing Conversation Logs**:
   - Briefly report findings using this format:  
     ```
     Analyzed conversation: [key points relevant to task]
     ```

2. **When Examining Code or Error Logs**:
   - Report findings using this format:  
     ```
     Reviewed [file/section]: [relevant findings]
     ```

3. **Include Minimal Context for Current Task**:
   - Ensure findings directly inform the current task at hand.

---

### **Critical Notes**
- This read-first, write-after approach ensures consistency and continuity across conversations.
- Documentation updates and log analysis reports are mandatory and must be completed before responding to the user.

---

## [Unreleased]

### Added
- Added missing newline at end of README.md
- Created `item_links` table for storing relationships between work items
- Added foreign key constraints and appropriate indexes for the `item_links` table
- Implemented `add_link()` method to create relationships between items with error handling
- Implemented `remove_link()` method to delete relationships between items
- Implemented `get_links()` method to retrieve both incoming and outgoing links for an item
- Added convenience methods in `WorkSystem` class for working with links (`add_link()`, `remove_link()`, `get_links()`)
- Added comprehensive unit tests for the link functionality in `tests/test_item_links.py`
- Added new `ItemType.THOUGHT` enum value with "th" value for capturing thought items
- Updated type validation in `schemas.py` to allow the new "th" type
- Modified `generate_id()` to handle the two-character "th" type for ID generation
- Added comprehensive unit tests for the thought item functionality in `tests/test_thought_item.py`
- Added minimal Textual UI stub in `src/textual_ui.py`
- Extended the `do_list` command to support filtering thoughts with `list thoughts`
- Added specialized `do_list_thoughts` command for listing all thoughts or filtering by goal
- Enhanced display formatting to highlight thought items with distinct styling
- Added special visual treatment for thoughts in the tree view
- Created unit tests for the thought listing functionality in `tests/test_list_thoughts.py`
- Added `do_link` command to create links between items from the CLI with support for custom link types
- Added `do_unlink` command to remove links between items from the CLI
- Implemented input validation for link commands to handle invalid IDs and link types
- Created comprehensive unit tests for link/unlink commands in `tests/test_link_commands.py`
- Added manual test script for link/unlink commands in `test_link_commands_manual.py`
- Added `do_link_tree` command to visualize hierarchical relationships between items
- Implemented color-coding for different relationship types (references, evolves-from, inspired-by, parent-child)
- Created organized directory structure for Textual UI components (`src/pos_tui/`)
- Added modular package structure with screens, widgets, and styles directories
- Implemented basic Textual UI application structure with tabbed interface
- Created stub implementation for Dashboard, New Item, and Link Tree screens
- Implemented Dashboard, New Item, and Link Tree screens using new ItemEntryForm,
  ItemTable, and LinkTree widgets with keyboard shortcuts
- Added command-line argument support for selecting between TUI and CLI modes
- Created legacy_cli documentation to guide users through the transition
- Added tests for main entrypoint using stubs
- Added filter bar with search and sorting on the dashboard screen

### Changed
- **Major architectural shift**: Transitioned from CLI-first to Textual-first approach (v0.2.0)
- Updated PROJECT_SCOPE.md with the new Textual-first architecture and migration plan
- Moved previous CLI-focused documentation to docs/archived/PROJECT_SCOPE_CLI.md
- Updated README.md to reflect the Textual-first approach
- Updated .cursor rules to prioritize Textual UI development over CLI commands
- Marked CLI interface as deprecated with plans for full removal
- Modified main.py to launch Textual UI by default with fallback to CLI
- Updated version number to 0.2.0 in src/__init__.py to reflect the architectural change
- Cleaned up requirements.txt to clearly indicate which packages are actually used
- Removed references to unused packages (SQLAlchemy, FastAPI) from documentation
- Updated documentation to focus on sqlite3 for database operations
- Fixed tag retrieval by querying the database directly in `get_all_tags()`
- Removed root-level `work_items.db` and added `/work_items.db` to `.gitignore` to keep the canonical database in `data/db/`
- Synced pyproject.toml version to 0.2.0 to match src/__init__.py

### Deprecated
- CLI-based commands and interfaces in favor of Textual TUI
