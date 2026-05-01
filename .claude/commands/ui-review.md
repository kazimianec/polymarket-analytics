# UI Review

Perform a visual quality review of the current frontend UI.

## Steps

### 1. Take screenshots
Use Playwright MCP to screenshot all major pages/routes in the running frontend (`http://localhost:5173`).
Capture at least: the home/landing page, any main feature pages, and any modal or drawer flows.

### 2. Review against guidelines
Read `UIDesignGuidelines.md` at the project root.
For each screenshot, identify:
- **Violations** — things that clearly break a guideline
- **Improvements** — things that are acceptable but could be better

List findings grouped by page/component.

### 3. Apply fixes
Implement the highest-priority fixes:
- Spacing, alignment, and layout issues first
- Typography and colour consistency second
- Component-level polish third

Follow the conventions in `CLAUDE.md`:
- MUI components only, no raw HTML equivalents
- All tokens from the MUI theme, never hardcoded values

### 4. Verify
Re-screenshot the changed pages and confirm the issues are resolved.
Use `toHaveScreenshot()` in Playwright for any critical surfaces you want to lock in visually.
