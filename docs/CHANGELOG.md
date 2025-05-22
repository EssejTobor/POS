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
- Implemented edit functionality in Dashboard screen for modifying existing items
- Implemented delete functionality with confirmation modal in Dashboard screen
- Enhanced ItemEntryForm with comprehensive validation, error handling, and UI improvements
- Added support for editing existing items in the NewItemScreen with auto-populate form fields
- Added visual feedback and automatic dashboard refresh when creating/editing/deleting items
- Created simple test script for manual testing of dashboard edit and delete functionality
- Added support for newer Textual API patterns using the @on decorator for event handling
- Created `docs/checklist.md` to track implementation progress against the Implementation Plan
- Added Implementation Tracking section to PROJECT_SCOPE.md to formalize checklist maintenance
- Created a new Cursor rule (05_implementation_checklist.mdc) for checklist management
- Implemented comprehensive database worker thread system in `src/pos_tui/workers/`:
  - Created `BaseWorker` class with thread lifecycle management, result callbacks, and error handling
  - Implemented `DBConnectionManager` with connection pooling, thread safety, and retry logic 
  - Created specialized worker classes for item operations: `ItemFetchWorker`, `ItemSaveWorker`, `LinkWorker`
- Added extensive test coverage for the worker thread system:
  - Unit tests for worker thread functionality including success, error handling, and cancellation
  - Tests for database connection management with transactions and parameter binding
  - Tests for the item worker classes with mocked WorkSystem
  - Smoke tests for application startup and worker integration
  - Tests for item fetching with filtering and pagination
  - Visual rendering tests for UI components
- Created `EditItemModal` in `widgets/modals.py` for editing items in a modal dialog
- Added edit button to item table rows in the Actions column
- Implemented edit action handling in table context menu 
- Enhanced ItemTable with context menu support for item actions (view, edit, delete)
- Added message classes for handling edit and delete requests from the table
- Implemented optimistic UI updates with undo capability for edit and delete operations
- Added toast notifications for edit and delete operations with undo buttons
- Created update_cell method in ItemTable for direct UI updates without reload
- Implemented asynchronous database operations to keep the UI responsive
- Created first-principles validation framework in `src/pos_tui/validation/`:
  - Implemented `ValidationProtocol` base class for creating validation protocols
  - Added `ValidationResult` class for storing, displaying, and saving validation results
  - Created `introspect.py` utility for examining database state
  - Implemented `UIComponentSimulator` for validating UI components without rendering
  - Created validation protocols for item management features
  - Added validation runner with command-line interface
  - Created comprehensive documentation for the validation approach
- Updated development workflow in AGENTS.md to use first-principles validation
- Updated checklist.md to reflect the new validation approach
- Created detailed documentation in validation_protocols.md
- Established first-principles validation framework as the global testing strategy for ALL phases of the project:
  - Updated documentation to clarify this is the only testing approach to be used
  - Modified references to "tests" across all documentation to refer to validation protocols
  - Added explicit instructions for creating validation protocols for all features
  - Updated AGENTS.md, checklist.md, and validation documentation to enforce this approach
- Added LinkType enum in models.py to standardize relationship types between items
- Enhanced ItemEntryForm with linking capabilities:
  - Added linked items display section with remove functionality
  - Implemented item search through ItemSearchWorker for finding items to link
  - Added link type selector using the LinkType enum
  - Created visual indicators for linked item relationships
- Extended ItemSaveWorker to handle relationship management:
  - Implemented atomic operations for item+link updates
  - Added rollback capability for failed operations
  - Added comparison logic to efficiently process link changes (add/remove/update)
- Created ItemSearchWorker for finding items to link:
  - Added search by title or ID capability
  - Implemented exclusion of already linked items from results
  - Added search results display with click-to-link functionality
- Updated NewItemScreen to handle link submission:
  - Integrated with enhanced ItemSaveWorker
  - Added loading indicator during save operations
  - Implemented proper error handling and success notifications
- Implemented Phase 6 Navigation and Usability features:
  - Created CommandPalette widget with search functionality, categorization, and keyboard activation
  - Implemented keyboard shortcuts with ShortcutsScreen for reference
  - Added theme support with light/dark themes and theme switching
  - Created NotificationCenter for consistent error handling and user notifications
  - Implemented settings storage for persisting user preferences
  - Added comprehensive validation for navigation and usability features:
    - Created NavigationValidator for testing command palette, theme switching, keyboard shortcuts, and notifications
    - Implemented validation protocols for usability patterns
    - Added tests for keyboard navigation and focus management
    - Created tests for error handling and recovery
    - Added performance benchmarking for responsive UI
- Created detailed documentation for Textual devtools in `docs/textual_devtools.md`:
  - Instructions for using the developer console for debugging
  - Guide to live CSS editing for UI development
  - Techniques for troubleshooting worker threads
  - Common issue resolution workflows
  - Web browser preview functionality
- Added Cursor rule for Textual devtools debugging protocols to standardize troubleshooting approaches

### Changed
- **Major architectural shift**: Transitioned from CLI-first to Textual-first approach (v0.2.0)
- **Upgraded Textual framework from v2.1.2 to v3.2.0** for improved event handling, stability and compatibility with documentation
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
- Converted NewItemScreen from Container to Screen for better lifecycle management
- Enhanced ItemEntryForm with better styling and more comprehensive input controls
- Updated event handling code to use modern Textual API patterns with @on decorators
- Improved async workflow using asyncio.create_task for background operations
- Updated documentation to use generic Python testing terminology instead of pytest-specific references
- Updated CSS in `notifications.py` to be compatible with Textual 3.x by replacing `border-left-color` with proper `border` property and using correct color opacity syntax

### Fixed
- Fixed compatibility issues with the current Textual API version
- Addressed TextArea placeholder parameter not being supported
- Corrected enum references (Priority.MED instead of MEDIUM, ItemStatus.NOT_STARTED instead of NEW)
- Fixed worker handling to use asyncio.create_task for better compatibility
- Fixed missing `Click` event import in `item_details.py` by adding correct import from `textual.events`
- Removed non-existent `ConfirmModal` import from widgets `__init__.py`
- Replaced `Slider` widget with `Input` widget in `link_tree.py` for compatibility with current Textual version
- Added `ItemDetailsModal` to the `__init__.py` exports to fix import errors
- Fixed multiple instances of `worker.run()` incorrectly used instead of `worker.start()` in tree visualization code

### Deprecated
- CLI-based commands and interfaces in favor of Textual TUI
