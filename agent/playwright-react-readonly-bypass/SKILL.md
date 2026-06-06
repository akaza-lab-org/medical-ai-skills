---
name: playwright-react-readonly-bypass
description: Playwright workaround for automating controlled inputs (like React/Vue customized Datepickers) when regular `fill()` fails because the input is marked as `readonly` or its state does not sync properly.
---

# Playwright React Readonly Input Bypass

## Problem

When automating Single Page Applications (React, Vue, etc.) using Playwright, you may encounter custom datepickers or complex inputs that are strictly `readonly`. Normally, a user clicks the input, a calendar popup appears, and they click a date.
Using `locator.fill('2026-04-10')` will fail because Playwright respects the HTML `readonly` attribute. 
Even if you evaluate a script to remove `readonly`, simple input dispatching might not trigger React's synthetic event system properly, leaving the internal component state empty or causing validation errors upon form submission.

## Solution

Temporarily remove the `readOnly` DOM attribute, directly invoke the native `HTMLInputElement.prototype.value` setter (bypassing React's wrapper), manually dispatch valid `input` and `change` events that bubble up to trigger React's synthetic event listener, and then restore `readOnly`.

## Implementation

```python
import time

def fill_date_input(page, locator, date_str: str) -> None:
    """
    Sets the value of a React-controlled, Readonly HTML input field using native setters.
    
    Args:
        page: The Playwright page object.
        locator: Focusable Playwright locator targeting the input element.
        date_str: The correct formatted string (e.g. "2026-04-10").
    """
    handle = locator.element_handle()
    if handle is None:
        raise RuntimeError("input element not found")
        
    page.evaluate(
        """({el, value}) => {
            const prevReadonly = !!el.readOnly;
            
            // Bypass React's overridden value setter to trigger state updates
            const valueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              "value"
            )?.set;
            
            if (!valueSetter) {
              throw new Error("value setter not found");
            }
            
            // 1. Unlock the element
            el.readOnly = false;
            el.focus();
            
            // 2. Set the native value
            valueSetter.call(el, value);
            
            // 3. Dispatch bubbling events so React's SyntheticEvent can pick them up
            el.dispatchEvent(new Event("input", { bubbles: true }));
            el.dispatchEvent(new Event("change", { bubbles: true }));
            
            // 4. Trigger blur hooks and restore original state
            el.blur();
            el.readOnly = prevReadonly;
        }""",
        {"el": handle, "value": date_str},
    )
    
    # Optional wait to allow React transitions to settle (e.g., closing popups, validation)
    time.sleep(0.2)
```

## Usage

```python
dl_modal = page.locator(".modal-container")
start_input = dl_modal.locator("input[placeholder*='開始']").first

# Using regular fill() fails!
# start_input.fill("2026-04-01")  # Raises Error

# Bypass correctly:
fill_date_input(page, start_input, "2026-04-01")
```

## When to use

- Interacting with `Datepicker`, `Timepicker` components in React.
- An input says `readonly` but secretly stores its internal value on an underlying model.
- You want to skip writing messy calendar popup automation (clicking month, year arrows, then specific days). This setter trick directly injects the value string, simulating a perfect date completion and syncing React state.
