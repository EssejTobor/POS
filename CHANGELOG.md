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
- Added cycle detection in tree visualization to prevent infinite recursion
- Implemented configurable depth limiting to handle complex relationship networks
- Created `print_link_tree` method in the Display class for hierarchical visualization
- Added comprehensive unit tests for the link tree functionality in `tests/test_link_tree.py`
- Created a detailed manual test script for link tree visualization in `test_link_tree_manual.py`
- Extended link tree tests to verify cycle references appear in the output
- Implemented core Textual UI framework in `src/textual_ui.py` with the following components:
  - `TextualApp` class with tabbed interface and keyboard shortcuts
  - `ItemEntryForm` with fields for all item properties and linking options
  - `ItemListView` with filtering and sortable data table
  - `LinkTreeView` for visualizing relationship networks between items
  - Message system for user notifications and feedback
  - Rich styling and keyboard navigation
- Added CLI commands to integrate with the Textual UI:
- `do_form` to launch the item entry form
- `do_tui` to launch the full TUI interface
- `do_tui_list` to browse items in the TUI
- Wired CLI launch commands to open specific TUI tabs
- Added graceful fallbacks when the Textual library is not available
- Implemented proper Windows terminal compatibility
- Enhanced `do_tui` command to launch the dashboard with optional `--tab` flag for starting view
- Added Textual as a first-class runtime dependency in `pyproject.toml`
- Created `src/launcher.py` to provide a direct entry point to launch the Textual UI
- Updated `run.py` to directly launch the Textual UI with fallback to CLI if import fails
- Created `src/textual_ui/widgets.py` with implementation stubs for all required widget classes

### Changed
- Unified item creation by extending the `add` command to support thought items with linking
- Enhanced `AddItemInput` schema to support optional linking parameters (`--link-to`, `--link-type`)
- Removed separate `do_add_thought` command for a more consistent user interface
- Updated help documentation with comprehensive examples for the extended `add` command
- Created unit tests for the unified add command in `tests/test_unified_add_command.py`
- Updated class docstring for `WorkSystemCLI` to document the new link and unlink commands
- Updated class docstring for `WorkSystemCLI` to document the `optimize` command
- Enhanced the Display class to support advanced tree-based relationship visualizations
- Aligned `__version__` in `src/__init__.py` with package version `0.1.0`
- Fixed lint and type issues across the codebase; added initial Textual UI stub
- Improved `do_cleanup_backups` with better error handling and user feedback
- Fixed NameError when `rich` is installed by correctly assigning fallback classes in `display.py`
- Resolved mypy errors in `textual_ui.py`
- Enhanced Textual UI; install `textual` and launch it with the `tui` command
- Added lightweight fallbacks for `pydantic` to enable tests without external
  dependencies; improved missing item messages in link tree view
- Changed application startup to launch Textual UI by default, with automatic fallback to CLI if Textual is unavailable
- Unified runtime dependencies in `pyproject.toml` and `setup.py`; removed unused
  `prompt_toolkit`

### Fixed
- Fixed import error with "No module named 'src.textual_ui.widgets'" by creating the missing module with required widget classes
- Resolved circular import in textual_ui causing startup failure

