# Personal Operating System (POS) - Project Scope V2

## **Project Overview**

The Personal Operating System (POS) is a terminal-based application for personal task and knowledge management. It uses the [Textual](https://github.com/Textualize/textual) framework as its primary user interface and provides a structured way to track work items, goals, and thoughts through an interactive TUI. All interactions—including item creation, browsing, editing, and relationship visualization—are handled through Textual. Legacy CLI functionality has been deprecated.

---

## **Core Objectives**

1. Enable users to capture "Thought" items quickly and efficiently via form-based input
2. Allow linking between thoughts and other work items to show relationships and evolution
3. Provide interactive visualization tools to see thought hierarchies and link structures
4. Support branching and merging of thought processes
5. Transition entirely to a Textual-first interface, retiring CLI dependencies
6. Ensure the system remains performant and easy to use even with large knowledge graphs

---

## **Technical Architecture**

### **Integrations**

* SQLite database (existing) with schema support for links and tags
* Textual (primary UI layer) for structured, interactive TUI components

### **Functions**

* **Core Database Functions**

  * Create, retrieve, update, and delete work items
  * Link items through relationship tables
  * Query linked and tagged items efficiently

* **TUI Application Structure**

  * `TextualApp` subclass (`POSTUI`) with tabbed layout for entry, browsing, and graphing
  * Widget-based components: `ItemEntryForm`, `ItemTable`, `LinkTree`, `Message`
  * Command Palette for discoverability (Textual 2.1+ built-in)

* **User Interface Components**

  * Tree-based visualization of thought relationships
  * Responsive form-based input for items and links
  * Modal editing interface for inline updates
  * Color-coded display of item priorities and statuses

### **User Features**

* Create and edit items via form
* Link items with semantic relationship types
* View evolution and reference trees
* Filter by tags, status, priority, or type
* Use search and command palette for power navigation

---

## **Data Structures**

### **Core Tables**

1. **work\_items**

   * Stores all items including thoughts
2. **item\_links**

   * `source_id`, `target_id`, `link_type`, `created_at`
3. **item\_tags**

   * `item_id`, `tag`

### **Item Types**

* `TASK`: Regular tasks
* `LEARNING`: Learning-related items
* `RESEARCH`: Research-related items
* `THOUGHT`: Ideas and concept tracking

### **Link Types**

* `references`, `evolves-from`, `parent-child`, `inspired-by`

---

## **Implementation Strategy**

### Transition from CLI to TUI

* Archive CLI code in `legacy_cli/`
* Migrate all user-facing interactions to `pos_tui/`
* Refactor entry points to launch Textual UI by default

### TUI Structure

* **Screens**: Dashboard, LinkTree, NewItem
  - Implemented with ItemEntryForm, ItemTable, and LinkTree widgets
  - Keyboard shortcuts "1", "2", "3" switch between tabs
* **Widgets**: Forms, Tables, Trees, Modals
* **Event Handling**: Use `on_*` methods and `run_worker_thread` for async-safe DB access

### Implementation Tracking

* Progress tracked via `docs/checklist.md` based on the phased Implementation Plan
* All new features should update the checklist to reflect current status
* Overall implementation progress measured by phase completion percentages

### Testing

* Domain logic tested with standard Python testing tools
* TUI smoke tests for startup, widget rendering, and modal logic
* Use headless mode for CI compatibility

---

## **Exit Criteria for Migration**

* 100% of interactive workflows operate via Textual
* No `rich`, `cmd`, or legacy CLI imports in active code
* App launches directly into TUI (`python -m pos_tui`)
* All domain tests pass; TUI smoke tests are green
* CLI remains archived and non-executed

---

## **Versioning Policy**

This migration marks version `0.2.0`.

* Major CLI deprecation
* Textual-first rewrite
* Backward-compatible data structures

All future development will extend the TUI as the primary interface. 