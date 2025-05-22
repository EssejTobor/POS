# Textual Devtools Workflow

This document outlines how to use Textual's built-in developer tools to debug, troubleshoot, and improve the POS application.

## Version Information

The current POS application is using Textual version 3.x, which has some important differences from earlier versions:

- CSS property naming conventions have changed
- Some widgets have been renamed or reorganized
- Border style handling has been updated
- CSS color usage patterns have changed

Always check the [Textual documentation](https://textual.textualize.io/) for the latest API information.

## Developer Console

The Textual developer console is essential for debugging TUI applications where traditional `print()` statements would interfere with the UI.

### Setup

1. Open two terminal windows
2. In the first terminal, start the console:
   ```bash
   textual console
   ```
3. In the second terminal, run the application in dev mode:
   ```bash
   textual run --dev main.py
   ```
   
### Usage

- Use `print()` statements in your code - they'll appear in the console window
- Use the Textual log function for more detailed debugging:
  ```python
  from textual import log
  
  # Simple logging
  log("Debug message")
  
  # Log variables
  log(variable_name=my_variable, another_var=another_variable)
  
  # Log widget tree (very useful for UI debugging)
  log(self.tree)
  ```

- All events, key presses, and internal Textual messages will also appear in the console

### Console Options

- Increase verbosity: `textual console -v`
- Filter out message types: `textual console -x EVENT -x DEBUG`
- Use custom port: `textual console --port 7342` (then use `textual run --dev --port 7342 main.py`)

## Live CSS Editing

For rapid UI development, Textual supports live CSS editing in dev mode.

1. Run the application in dev mode:
   ```bash
   textual run --dev main.py
   ```
2. Edit any CSS files in your project
3. Changes will appear in real-time as you save the files

### Common CSS Issues

When working with Textual CSS, be aware of these common issues:

1. **Border properties**: Use the full `border` property rather than individual properties like `border-left-color`. Example:
   ```
   # INCORRECT in Textual 3.x
   border-left: solid 1;
   border-left-color: $error;
   
   # CORRECT in Textual 3.x
   border: solid $error;
   ```

2. **Color values**: When using opacity/alpha with colors, the syntax has changed in newer versions:
   ```
   # INCORRECT in Textual 3.x
   background: $error 10%;
   
   # CORRECT in Textual 3.x
   background: $error 10%;  # Check documentation for current syntax
   ```

3. **CSS selectors**: Check that your CSS selectors match the current widget hierarchy and class names

## Web Browser Preview

You can view your Textual application in a web browser, which is useful for sharing, screenshots, or testing on different screen sizes.

```bash
textual serve main.py
```

## Debugging Worker Threads

When troubleshooting worker thread issues:

1. Use the console to view worker thread lifecycle events
2. Add explicit logging before and after worker operations:
   ```python
   log("Starting worker with params", params=worker_params)
   worker.start(callback=self._on_result)
   ```
   
3. In callback functions, log the results:
   ```python
   def _on_result(self, result):
       log("Worker result received", success=result.get("success"), data=result)
       # Process result...
   ```

## Common Issues and Solutions

### Widget Imports

When receiving import errors:
1. Use the console to see the exact error
2. Check the Textual API documentation for the correct import path
3. Look for version compatibility issues (some widgets may have moved or been renamed)

### Event Handling

For event-related issues:
1. Run with increased verbosity: `textual console -v`
2. Watch for event propagation in the console
3. Verify event names and handler signatures

### Worker Thread Errors

For worker thread problems:
1. Ensure proper method calls (`start()` instead of `run()`)
2. Check for thread safety in database operations
3. Verify callback functions are receiving the expected data structure

## Recommended Workflow for New Features

1. Start the console before development
2. Use log statements liberally during initial development
3. Test UI changes with live CSS editing
4. For complex issues, use `log(self.tree)` to understand the widget hierarchy
5. Clean up debug logging before finalizing the feature

## Recommended Workflow for Troubleshooting

1. Start the console with increased verbosity
2. Add strategic log statements around the suspected issue area
3. Run the application and reproduce the issue
4. Analyze the logs to identify the root cause
5. Fix and verify with the console still running 