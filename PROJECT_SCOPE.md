# Personal Operating System (POS) - Project Scope

## **IMPORTANT: SELF-MAINTENANCE INSTRUCTIONS**  

### **Before Taking Any Action or Making Suggestions**  
1. **Read Both Files**:  
   - Read `CHANGELOG.md` and `PROJECT_SCOPE.md`.  
   - Immediately report:  
     ```
     Initializing new conversation...  
     Read [filename]: [key points relevant to current task]  
     Starting conversation history tracking...
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

5. **Adhere to the Read-First/Write-After Approach**:  
   - Maintain explicit update reporting for consistency and continuity.

---

## **Project Overview**
The Personal Operating System (POS) is a command-line interface (CLI) tool for personal task and knowledge management. It provides a structured way to track work items, goals, and now thoughts. The core functionality includes creating, updating, and organizing items across different goals with varying priorities and statuses. 

The Thought Evolution Tracker enhancement extends POS to capture, link, and visualize the evolution of thoughts and ideas over time, creating a knowledge graph that shows how concepts develop and branch.

---

## **Core Objectives**
1. Enable users to capture "Thought" items quickly and efficiently  
2. Allow linking between thoughts and other work items to show relationships and evolution
3. Provide visualization tools to see thought hierarchies and evolution paths
4. Support branching and merging of thought processes
5. Maintain backwards compatibility with existing work item management features
6. Ensure the system remains performant and easy to use even with complex thought networks

---

## **Technical Architecture**

### **Integrations**
- SQLite database (existing) with new tables for linking items
- Rich library (existing) for formatted CLI output
- Textual library (new) for interactive forms and UI elements

### **Functions**
- **Core Database Functions**
  - Create and manage thought items
  - Link items through relationship tables
  - Query linked items efficiently
  - Support various relationship types between items

- **CLI Commands**
  - Add thoughts with optional links to existing items
  - Link and unlink existing items
  - List thoughts with filtering options
  - Visualize thought trees and evolution paths

- **User Interface Components**
  - Tree-based visualization of thought relationships
  - Form-based input for adding thoughts
  - Color-coded display of thought statuses and relationships

### **UI Features**
- Command-line interface for all core functions
- Tree visualization for linked thoughts and items
- Text-based forms for complex data entry
- Rich formatting for easier visual scanning of relationships
- Hierarchical displays of thought evolution

### **User Features**
- Create thoughts with minimal friction
- Link thoughts to other thoughts or work items
- View thought evolution paths
- Tag thoughts for better organization
- Filter and search through thought collections
- Track the development of ideas over time
- Branch and merge thought processes

---

## **Data Structures**

### **Core Tables**
1. **work_items** (existing)
   - Extended with new `THOUGHT` type
   - Stores all items including thoughts

2. **item_links** (new)
   - `source_id`: ID of the source item
   - `target_id`: ID of the target item
   - `link_type`: Type of relationship (references, evolves-from, etc.)
   - `created_at`: When the link was created

3. **item_tags** (potential future)
   - For tagging and categorizing thoughts

### **Item Types**
- `TASK`: Regular tasks (existing)
- `LEARNING`: Learning-related items (existing)
- `RESEARCH`: Research-related items (existing)
- `THOUGHT`: New type for capturing ideas and concepts

### **Link Types**
- `references`: Basic connection between items
- `evolves-from`: Shows thought evolution
- `parent-child`: Hierarchical relationship
- `inspired-by`: Influence without direct evolution

---

## **Implementation Phases**

### **Phase 1: Introduce the `item_links` Table**

**Goal:** Lay the foundation for relationships among items (including new Thought items).

1. **Entry Criteria:**
   - You have a functioning `work_items` table and the rest of the POS codebase is stable.
   - No changes have yet been made to handle `Thought` items or linking.

2. **Tasks:**
   - **Create the `item_links` table** in `database.py` with columns `(source_id, target_id, link_type, created_at)`.
   - **Add new methods** in `database.py`:
     - `add_link(source_id, target_id, link_type="references")`
     - `remove_link(source_id, target_id)`
     - `get_links(item_id)` (fetch both incoming and outgoing links)
   - Update `_create_tables()` to ensure the new table is created if not already present.

3. **Files Modified (Approximate):**  
   1. `database.py` – Add table creation logic and new methods  
   2. (Potential minor changes in) `storage.py` – If you want a pass-through function for linking/unlinking  

4. **Potential Challenges / Edge Cases:**
   - **Foreign Key Constraints**: Make sure `FOREIGN KEY (source_id)` and `FOREIGN KEY (target_id)` reference `work_items(id)`. Some SQLite configurations require enabling foreign keys explicitly (`PRAGMA foreign_keys = ON`).
   - **Indexing**: For performance, consider indexing `(source_id, target_id)` if you expect many links.
   - **Collision with Existing Migrations**: If you already have a migration system, ensure this new table does not conflict with older migrations.

5. **Verification / Testing:**
   - **Unit Tests**: 
     - Test `add_link()` with valid IDs to ensure it inserts properly.  
     - Test `get_links()` returns the correct relationships.  
     - Test `remove_link()` cleans up rows.  
   - **Manual Check**: 
     - Inspect the database schema (`.schema`) in `sqlite3` to confirm `item_links` exists.  
     - Optionally run a test script that inserts a link and verifies retrieval.

**Exit Criteria:**  
- The `item_links` table is reliably created.  
- Linking methods (`add_link`, `remove_link`, `get_links`) work with basic tests.

---

### **Phase 2: Extend `ItemType` to Include `THOUGHT`**

**Goal:** Introduce `ItemType.TH` so that "thoughts" can be stored in `work_items`, reusing existing logic as much as possible.

1. **Entry Criteria:**
   - `item_links` table creation is complete.  
   - The existing system for `work_items` is stable.

2. **Tasks:**
   - **Add new enum value** in `models.py`:
     ```python
     class ItemType(Enum):
         ...
         THOUGHT = "th"
     ```
   - **Validate** no references to the old "type must be t, l, r only" logic in your CLI or validation code. Update validations to allow `"th"`.
   - **Refactor** any Pydantic validators (`schemas.py`) to accept `th` if you're using them for CLI commands.

3. **Files Modified (Approximate):**  
   1. `models.py` – Update `ItemType`  
   2. `schemas.py` – If the add/update commands have strict checks for valid item types  
   3. Possibly `display.py` – If you want any color-coded logic for TH.

4. **Potential Challenges / Edge Cases:**
   - **Compatibility with existing code**: Ensure that adding `"th"` does not break older code expecting only `"t"`, `"l"`, or `"r"`.
   - **Default Behavior**: If your code branches by `item_type` (e.g., `if item_type == "t": do_something()`), you'll need to ensure a safe fallback for `THOUGHT`.

5. **Verification / Testing:**
   - **Unit Tests**: 
     - Try creating a "thought" item and confirm it is persisted in the database with `item_type="th"`.
   - **Manual Check**: 
     - Use a placeholder CLI command (like `add ProjectA-th-HI-Brainstorm-Initial thoughts…`) to ensure the item is stored with `THOUGHT`.

**Exit Criteria:**  
- `THOUGHT` items can be created in the `work_items` table.  
- No runtime errors or validation rejections for `th`.

---

### **Phase 3: New "Add Thought" Command (`do_add_thought`)**

**Goal:** Provide a dedicated CLI command for quickly capturing thoughts, optionally linking them to an existing item at creation time.

1. **Entry Criteria:**
   - `ItemType.TH` is recognized by the system.
   - `item_links` table is in place (though not fully used yet).

2. **Tasks:**
   - **Implement `do_add_thought`** in `cli.py`:
     - Parse user input for at least: `goal`, `title`, `description`.  
     - Optional: Accept a `--parent` or similar argument to link this thought to an existing item or thought.
   - **Linking**: If a parent is provided, call `database.add_link(new_thought_id, parent_id, link_type="evolution")` (or your chosen link type).

3. **Files Modified (Approximate):**  
   1. `cli.py` – Add `do_add_thought` method (and help text).  
   2. `storage.py` (optional) – If you'd like a convenience method like `add_thought()` separate from `add_item()`.  

4. **Potential Challenges / Edge Cases:**
   - **Input Parsing**: Deciding how to parse references or parents. Example usage might be:
     ```
     add_thought "SelfReflection" "New Idea" "Brainstorming ways to unify tasks" [--parent <item_id>]
     ```
   - **Validation**: Ensure the parent ID actually exists before linking.

5. **Verification / Testing:**
   - **Unit / Functional Tests**:
     - Command usage with and without `--parent`. 
     - Confirm the new thought is in the database with `item_type=THOUGHT`.
     - If a parent is specified, confirm a record in `item_links`.
   - **Manual Testing**:
     - Run `add_thought` and see if it prints a success message. 
     - Check `list all` or a custom command to confirm the item was created.

**Exit Criteria:**  
- You can create new Thought items via `do_add_thought`.  
- Linking a newly created Thought to an existing item is possible (if you choose to include that feature now).

---

### **Phase 4: Basic Thought Listing / Filtering**

**Goal:** Provide a way to list or filter thoughts separately from other items, so users can see all `THOUGHT` items.

1. **Entry Criteria:**
   - `THOUGHT` items can be created (Phase 2 & 3 done).

2. **Tasks:**
   - **Add `do_list_thoughts`** or extend your existing `do_list` to support a filter: `list thoughts`.
   - **Filter** by `ItemType.TH` in `storage.py` or `database.py`.
     ```python
     def get_thoughts(self):
         return self.db.get_items_by_filters(item_type=ItemType.TH)
     ```
   - **Display**: In `display.py`, you may want a special color or labeling for thoughts.

3. **Files Modified (Approximate):**  
   1. `cli.py` – Add a new command, or update `do_list`.  
   2. `storage.py` – Possibly add a helper like `get_thoughts()`.  
   3. `display.py` – Minor tweak if you want a unique color scheme.

4. **Potential Challenges / Edge Cases:**
   - **Naming Collisions**: If your CLI already has a `list all`, ensure that `list thoughts` is recognized as a special filter.
   - **No Thoughts**: If there are no `THOUGHT` items in the system, handle that gracefully.

5. **Verification / Testing:**
   - **Unit / Integration Tests**:
     - Confirm `list thoughts` displays only items of type `THOUGHT`.
   - **Manual Check**:
     - Create two items: one normal task, one thought. Run `list thoughts` and verify only the thought appears.

**Exit Criteria:**  
- Users can filter and display thoughts from the CLI, quickly verifying newly added Thought items exist.

---

### **Phase 5: Linking CLI Commands (`do_link` / `do_unlink`)**

**Goal:** Allow explicit linking/unlinking of existing items from the CLI, not just during creation.

1. **Entry Criteria:**
   - The `item_links` table is fully available.
   - Basic thought creation and listing are working.

2. **Tasks:**
   - **Add `do_link`** command in `cli.py`:
     ```plaintext
     link <source_id> <target_id> [<link_type>]
     ```
   - **Add `do_unlink`** command in `cli.py`:
     ```plaintext
     unlink <source_id> <target_id>
     ```
   - In both commands, call `database.add_link(...)` or `database.remove_link(...)`.

3. **Files Modified (Approximate):**
   1. `cli.py` – New `do_link` and `do_unlink` commands  
   2. Possibly `display.py` – If you want to confirm the link visually

4. **Potential Challenges / Edge Cases:**
   - **Invalid IDs**: The user could link non-existent IDs. You'll need a check that both IDs exist in `work_items`.
   - **Duplicate Links**: If `source_id, target_id, link_type` is unique, handle what happens if the user tries to re-link the same pair.
   - **Directionality**: By default, you might store the link in one direction. You might want to treat them as bidirectional. For consistency, decide if `source -> target` is the same as `target -> source` or if you want separate link records for both directions.

5. **Verification / Testing:**
   - **Integration Tests**:
     - Link a thought to a task, confirm the row is inserted in `item_links`.
     - Unlink them, confirm it's removed.
   - **Manual**:
     - `link <thought_id> <task_id>` -> check DB or a future "view links" command to confirm it.
     - Attempt linking with an invalid ID -> you should see a graceful error message.

**Exit Criteria:**  
- Users can create and remove links among items (including Thought->Thought or Thought->Task).

---

### **Phase 6: Enhanced CLI Display with Linked Items**

**Goal:** Show item relationships (especially around thoughts) in the CLI. Potentially create a hierarchical or tree-based display for Thought evolution.

1. **Entry Criteria:**
   - Basic linking is in place; we have data to visualize.

2. **Tasks:**
   - **Update `do_tree`** (or add a new command) to:
     - Retrieve all items plus their links (`database.get_links(item_id)`).
     - Build an in-memory graph or adjacency list to represent relationships.
     - Display them in a hierarchical manner. For example, if Thought B is linked to Thought A with `link_type="evolution"`, show B as a child node of A.
   - Optionally color or italicize thoughts.

3. **Files Modified (Approximate):**
   1. `cli.py` – Possibly update or create a new "do_thought_tree" command  
   2. `display.py` – Integrate logic to print a tree with linked items  
   3. `storage.py` – A helper method to build a relationship graph if needed

4. **Potential Challenges / Edge Cases:**
   - **Cyclic Links**: If the user links items in a cycle, you'll need to detect that or decide how to display it (a simple approach might skip cycles).
   - **Large Depth**: If a chain of thoughts references each other, the tree can become big. You might want to limit levels or detect cycles gracefully.

5. **Verification / Testing:**
   - **Integration Tests**: 
     - Create a chain of 3 thoughts, link them in a parent->child chain, confirm the displayed tree is correct.
   - **Manual**:
     - Use `link` commands in various ways, then run the tree command to see if it matches expectations.

**Exit Criteria:**  
- The user can visually see how thoughts interconnect or evolve over time in the CLI.

---

### **Phase 7: Textual Integration for Form-Based Thought Entry**

**Goal:** Reduce friction by using a Textual-based form for capturing new thoughts (and optionally editing them), rather than pure command-line syntax.

1. **Entry Criteria:**
   - The system fully supports thoughts, linking, and basic CLI visualization.

2. **Tasks:**
   - **Install** `textual` if not already done:  
     ```bash
     pip install textual
     ```
   - **Create a new module** (e.g., `textual_ui.py`) or integrate into `cli.py` with:
     - A Textual `App` that shows a form with fields: `Goal`, `Title`, `Description`, `[Optional] Parent ID`.
     - On "Submit," it calls your existing `add_thought` logic.
   - Integrate a new CLI command, e.g., `do_add_thought_form`, which launches the Textual UI in the terminal.

3. **Files Modified (Approximate):**
   1. **New file** `textual_ui.py` (or similarly named) – houses the Textual application  
   2. `cli.py` – A new command that spawns the Textual app from within the CLI.  

   (If you prefer placing everything in `cli.py`, that's also possible, but splitting it out can keep your code organized.)

4. **Potential Challenges / Edge Cases:**
   - **Terminal Compatibility**: Textual might behave differently on Windows vs. Unix-based terminals. 
   - **User Flow**: Exiting the Textual form gracefully to return to the main CLI loop.

5. **Verification / Testing:**
   - **Functional Tests**: 
     - Launch the form, fill it out, confirm a new thought is created. 
   - **Manual**:
     - Start the POS CLI, run `add_thought_form`, fill in details, and check `list thoughts`.

**Exit Criteria:**  
- Users can optionally run a Textual-based form to input new thoughts with minimal command syntax.

---

### **Phase 8: Tagging & Evolution-Specific Links (Optional Enhancement)**

**Goal:** Provide an optional advanced feature: structured relationships ("parent-child," "evolves-from"), plus tagging for more nuanced classification.

1. **Entry Criteria:**
   - All the previous capabilities are in place: THOUGHT items, linking, listing, and basic textual UI.

2. **Tasks:**
   - **Relationship Types**: Expand `link_type` usage, e.g.:
     - `parent-child`
     - `evolves-from`
     - `inspired-by`
   - **Tagging**: Add a field in `work_items` or create a new `item_tags` table. 
   - **CLI / Textual**: Provide commands or UI elements to manage these relationships/tags.

3. **Files Modified (Approximate):**
   1. `database.py` – Possibly add `item_tags` table.  
   2. `cli.py` – Add commands to tag thoughts, or specify link type on creation.  
   3. `textual_ui.py` (or relevant file) – Provide fields to add tags or pick a link type.

4. **Potential Challenges / Edge Cases:**
   - **Migration**: If you introduce a new table for tagging, handle schema changes carefully. 
   - **Complex UIs**: The more fields in the form, the more user support you'll need (e.g., validation).

5. **Verification / Testing:**
   - **Integration Tests**:
     - Add a few tags to a thought, verify they are stored and displayed.  
     - Link two thoughts with `link_type="evolves-from"` and confirm the difference in tree display.
   - **Manual**:
     - Create complex structures with tags or custom link types, confirm they appear in `do_tree` or `list`.

**Exit Criteria:**  
- The system supports advanced relationships and/or tagging, providing deeper insight into the thought-evolution journey.

---

## **Implementation Summary**

1. **Phase 1**: **Create `item_links` table** – foundational relationship logic.  
2. **Phase 2**: **Add `THOUGHT` item type** to the existing model.  
3. **Phase 3**: **New CLI command** `do_add_thought` for capturing thoughts (optionally referencing a parent).  
4. **Phase 4**: **Thought listing** (`do_list_thoughts` or a filter) so users can view `THOUGHT` items.  
5. **Phase 5**: **`do_link` / `do_unlink`** commands for linking/unlinking existing items.  
6. **Phase 6**: **Enhanced CLI display** that shows linked items as a tree/graph.  
7. **Phase 7**: **Textual-based form** for low-friction thought capture.  
8. **Phase 8** (Optional): **Tagging / advanced link types** for deeper thought evolution tracking.