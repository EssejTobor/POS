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
- Added `AddThoughtInput` schema in `schemas.py` for validating thought creation input
- Implemented `do_add_thought` command in CLI for quickly capturing thoughts
- Added support for linking thoughts to existing items during creation with customizable link types
- Created unit tests for the add_thought command in `tests/test_add_thought_command.py`

### Changed
[Document all changes here.]

