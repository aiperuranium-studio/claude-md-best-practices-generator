# Test Archetype: Java Spring Boot

Simulated project context for validating `/ignite` entity selection, specialization, and gap analysis.
See [RESULTS.md](RESULTS.md) for the analysis output produced from this archetype.

---

## Tech Stack

| Dimension | Value |
|-----------|-------|
| **Language** | Java 21 |
| **Framework** | Spring Boot 3.x, Spring Data JPA |
| **Database** | PostgreSQL 16 |
| **Build tool** | Gradle (Kotlin DSL) |
| **Test framework** | JUnit 5 + Mockito |
| **Infrastructure** | Docker |
| **CI/CD** | GitHub Actions |
| **Project type** | api-service |

---

## Simulated File Signals

Files that would exist in the target project root, triggering technology detection in Step 1 of `/ignite`:

```
user-service/
├── build.gradle.kts        # Gradle + Java/Kotlin signal
├── settings.gradle.kts
├── gradlew
├── Dockerfile
├── .github/
│   └── workflows/
│       └── ci.yml          # CI/CD signal
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/userservice/
│   │   │       ├── UserServiceApplication.java   # Spring Boot signal
│   │   │       ├── controller/
│   │   │       ├── service/
│   │   │       └── repository/
│   │   └── resources/
│   │       └── application.yml                   # Spring config signal
│   └── test/
│       └── java/
│           └── com/example/userservice/
└── docker-compose.yml
```

### `build.gradle.kts` (excerpt)
```kotlin
plugins {
    id("org.springframework.boot") version "3.3.0"
    id("io.spring.dependency-management") version "1.1.5"
    kotlin("jvm") version "1.9.24"
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.postgresql:postgresql")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.junit.jupiter:junit-jupiter")
}
```

### `application.yml` (excerpt)
```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/userdb
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false
```

---

## Architecture Notes

*As provided in conversation history to `/ignite`:*

> Building a user management microservice with Spring Boot 3. JPA with Hibernate for ORM, PostgreSQL as database. REST API with Spring MVC. JUnit 5 for unit tests, Spring Boot Test for integration tests. Gradle Kotlin DSL as build tool. Deployed as a Docker container.

---

## Expected Technology Profile

```json
{
  "languages": ["java"],
  "frameworks": ["spring", "jpa", "postgres", "docker"],
  "packageManagers": ["gradle"],
  "testFrameworks": ["junit"],
  "buildTools": ["gradle"],
  "ciCd": ["github-actions"],
  "docker": true,
  "projectType": "api-service"
}
```

---

## Notes for Reviewers

- **Gradle**: No catalog entity — low-impact gap (Maven-style patterns largely apply; `java-coding-standards` covers build conventions generically).
- **JUnit 5**: No dedicated catalog entity — covered by `springboot-tdd` which references JUnit 5.
- **Kotlin DSL** (`build.gradle.kts`): Minor language signal (Kotlin in build only, not production code) — should not trigger kotlin language tags.
- Spring coverage is strong: `springboot-patterns`, `springboot-security`, `springboot-tdd`, `springboot-verification`, `jpa-patterns` all apply.
- `e2e-runner` agent (tagged java) is relevant for integration/E2E test orchestration.
