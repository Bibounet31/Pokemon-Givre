# Front-end

Vite + React + strict TypeScript. See the [main README](../README.md) for the architecture, how to run
the project and the API contract.

| Command | What it does |
| --- | --- |
| `npm run dev` | dev server on http://localhost:5173 (regenerates the API types first) |
| `npm run build` | type-check and production build (regenerates the API types first) |
| `npm run lint` | ESLint with typescript-eslint |
| `npm run gen:api` | generate `src/api/schema.d.ts` from `../backend/openapi.json` |
