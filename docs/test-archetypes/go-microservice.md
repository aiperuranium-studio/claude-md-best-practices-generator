# Test Archetype: Go Microservice

Simulated project context for validating `/ignite` entity selection, specialization, and gap analysis.
See [RESULTS.md](RESULTS.md) for the analysis output produced from this archetype.

---

## Tech Stack

| Dimension | Value |
|-----------|-------|
| **Language** | Go 1.22 |
| **RPC framework** | gRPC (protobuf) |
| **Database** | PostgreSQL 16 |
| **Build tool** | Make |
| **Test framework** | Go test (stdlib) + testify |
| **Infrastructure** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions |
| **Project type** | microservice |

---

## Simulated File Signals

Files that would exist in the target project root, triggering technology detection in Step 1 of `/ignite`:

```
payment-service/
├── go.mod                  # Go language signal
├── go.sum
├── Makefile                # Build tool: Make
├── Dockerfile
├── docker-compose.yml      # Infrastructure signal
├── .github/
│   └── workflows/
│       └── ci.yml          # CI/CD signal
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── handler/
│   ├── service/
│   └── repository/
├── proto/
│   └── payment.proto       # gRPC / protobuf signal
├── migrations/
│   └── 001_init.sql        # Database migrations
└── scripts/
    └── generate.sh
```

### `go.mod` (excerpt)
```
module github.com/example/payment-service

go 1.22

require (
    google.golang.org/grpc v1.64.0
    google.golang.org/protobuf v1.34.0
    github.com/jackc/pgx/v5 v5.6.0
    github.com/stretchr/testify v1.9.0
)
```

### `Makefile` (excerpt)
```makefile
.PHONY: build test lint proto

build:
	go build ./cmd/server

test:
	go test ./...

lint:
	golangci-lint run

proto:
	protoc --go_out=. --go-grpc_out=. proto/*.proto
```

---

## Architecture Notes

*As provided in conversation history to `/ignite`:*

> Building a payment microservice in Go. Uses gRPC for inter-service communication. PostgreSQL for persistence with raw SQL migrations (no ORM). Built with Make. Testify for test assertions. Deployed as a Docker container, orchestrated via Docker Compose locally, Kubernetes in production.

---

## Expected Technology Profile

```json
{
  "languages": ["go"],
  "frameworks": ["postgres", "docker"],
  "packageManagers": [],
  "testFrameworks": ["go-test"],
  "buildTools": ["make"],
  "ciCd": ["github-actions"],
  "docker": true,
  "projectType": "microservice"
}
```

---

## Notes for Reviewers

- **gRPC**: No catalog entity — high-impact gap (primary communication protocol).
- **Make**: No catalog entity — low-impact gap (universal build tool patterns apply).
- **Kubernetes**: Mentioned in conversation, not in file signals — surfaced as medium-impact gap only if detected via `.k8s/` or conversation.
- **testify**: No dedicated entity — low-impact (covered by `golang-testing`).
- Go rules (`golang/`) should all be included.
- `database-migrations` skill (tagged go+postgres) is a strong match.
