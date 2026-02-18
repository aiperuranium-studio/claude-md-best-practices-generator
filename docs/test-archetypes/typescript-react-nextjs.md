# Test Archetype: TypeScript React Next.js

Simulated project context for validating `/ignite` entity selection, specialization, and gap analysis.
See [RESULTS.md](RESULTS.md) for the analysis output produced from this archetype.

---

## Tech Stack

| Dimension | Value |
|-----------|-------|
| **Language** | TypeScript 5.x |
| **Framework** | React 18, Next.js 14 (App Router) |
| **Styling** | Tailwind CSS 3.x |
| **Package manager** | pnpm |
| **Test framework** | Vitest + React Testing Library |
| **Infrastructure** | Vercel (deployment) |
| **CI/CD** | GitHub Actions |
| **Project type** | web-app |

---

## Simulated File Signals

Files that would exist in the target project root, triggering technology detection in Step 1 of `/ignite`:

```
my-app/
├── package.json            # TypeScript, React, Next.js, Tailwind → languages + frameworks
├── pnpm-lock.yaml          # PM: pnpm
├── tsconfig.json           # TypeScript signal
├── next.config.ts          # Next.js signal
├── tailwind.config.ts      # Tailwind signal
├── vitest.config.ts        # Test framework: vitest
├── .github/
│   └── workflows/
│       └── ci.yml          # CI/CD signal
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── (routes)/
├── components/
│   └── ui/
├── lib/
└── public/
```

### `package.json` (excerpt)
```json
{
  "dependencies": {
    "next": "14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0"
  },
  "devDependencies": {
    "typescript": "^5.4.0",
    "tailwindcss": "^3.4.0",
    "vitest": "^1.6.0",
    "@testing-library/react": "^16.0.0",
    "pnpm": "^9.0.0"
  },
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "test": "vitest run",
    "lint": "next lint"
  }
}
```

---

## Architecture Notes

*As provided in conversation history to `/ignite`:*

> Building a full-stack web application with Next.js 14 App Router. Server Components for data fetching, Client Components for interactivity. Tailwind for styling. Vitest + React Testing Library for unit/integration tests. Deployed to Vercel. TypeScript strict mode throughout.

---

## Expected Technology Profile

```json
{
  "languages": ["typescript"],
  "frameworks": ["react"],
  "packageManagers": ["pnpm"],
  "testFrameworks": ["vitest"],
  "buildTools": [],
  "ciCd": ["github-actions"],
  "docker": false,
  "projectType": "web-app"
}
```

---

## Notes for Reviewers

- **Next.js** (`next` in `package.json`) is detected as a framework signal, but the catalog has **0 entities tagged `nextjs` or `next`** — this is a high-impact gap that must be surfaced.
- **Tailwind CSS** has no catalog entity — medium-impact gap (styling conventions).
- **Vitest** has no catalog entity — low-impact gap (test runner differences from Jest are minor).
- TypeScript rules (`typescript/`) should be included; JavaScript rules excluded (TypeScript project).
- Hook matchers from JS-only hooks should remain `**/*.ts` and `**/*.tsx`.