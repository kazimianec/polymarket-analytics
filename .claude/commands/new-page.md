# New Page

Scaffold a new frontend page named **$ARGUMENTS**.

## What to create

### 1. Page component — `frontend/src/pages/<PageName>Page.tsx`
- MUI layout — use `Box`, `Container`, `Typography`, `Stack`, etc.
- Handle all three states: **loading**, **empty**, and **error**
- Typed props interface, no `any`
- Import and use the TanStack Query hook from step 2

### 2. API hook — `frontend/src/api/use<PageName>.ts`
- TanStack Query `useQuery` (or `useMutation` if needed)
- Typed return data — define the response type in `frontend/src/types/`
- Handle error and loading states explicitly

### 3. Route registration — `frontend/src/App.tsx`
- Add the new route to the React Router config

## Conventions
- MUI components only — no raw HTML equivalents (`<button>`, `<input>`, etc.)
- All colours, spacing, and typography from the MUI theme — never hardcoded values
- TanStack Query owns server state; Zustand owns UI state — never mixed
- All components and props fully typed
- Always show a loading skeleton or spinner while data fetches
- Always show a user-friendly error message if the request fails
- Always handle the empty-data case with a helpful prompt
