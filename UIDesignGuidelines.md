# UI Design Guidelines

> **This is a stub.** Fill in the sections below once you have established your project's brand and visual direction.
> Until then, the generic defaults below apply.

---

## Brand Positioning

_Fill in per project._

Examples to consider:
- Who are the users? (developers, consumers, enterprise operators…)
- What feeling should the product evoke? (powerful, calm, playful, trustworthy…)
- What products does it sit alongside or compete with?

---

## Visual Principles

These generic defaults apply until overridden per project:

1. **Clarity over cleverness** — every element has a purpose; remove what doesn't earn its place
2. **Consistent rhythm** — spacing follows a single scale (MUI theme spacing units); never one-off values
3. **Restrained palette** — primary + neutral + one accent; avoid colour fights
4. **Accessible by default** — WCAG AA contrast on all text and interactive elements

---

## What to Do

### Layout
- Use a consistent max-width container for page content
- Align to an 8 px grid (MUI `spacing(1)` = 8 px)
- Group related elements with whitespace, not borders
- Left-align body text; centre sparingly (hero headings only)

### Typography
- One typeface family throughout
- Limit heading levels in use on a single page (H1 + H2 usually sufficient)
- Body text: 16 px / 1.5 line-height minimum
- Use weight (not size) to create hierarchy within the same level

### Colour
- Reserve the primary colour for primary actions (one per view)
- Use neutral tones for backgrounds and borders
- Use semantic colours (error, warning, success) only for their semantic meaning

### Motion & Animation
- Transitions ≤ 200 ms for micro-interactions
- Entrance animations ≤ 400 ms
- No animation without a clear purpose (feedback, orientation, delight)

---

## What to Avoid

- Hardcoded colours or spacing outside the MUI theme
- Multiple competing calls-to-action on the same view
- Decorative icons or illustrations that don't communicate meaning
- Gradients, shadows, or blur effects used for decoration rather than depth cues
- Truncating text without a tooltip or expand affordance
- Empty states with no guidance ("No data" alone is not enough)

---

## Design Philosophy

> "Good design is as little design as possible." — Dieter Rams

Guiding questions for every decision:
- Does this element help the user complete a task?
- Would removing it hurt anything?
- Is this consistent with every other page in the product?

---

## Implementation Notes

_Fill in per project._

Things to document here once established:
- MUI theme file location and key customised tokens
- Icon library in use and naming conventions
- Any custom component variants added to the theme
- Screenshot baseline locations for visual regression tests
