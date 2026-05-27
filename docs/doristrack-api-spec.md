# DorisTrack — API Spec for Doris Integration

> Endpoints and payloads Doris (the tutor bot) needs to track Jeremías's progress.
> Based on the existing Django service/selector functions in `bot-capabilities.md`.
>
> **Base URL:** `https://<host>/api/`
> **Auth:** DRF token — header `Authorization: Token <key>`. One token issued
> for the Doris bot (create via `python manage.py drf_create_token <user>`).
> **Content-Type:** `application/json`
> **Interactive docs:** `/api/docs/` (Swagger), `/api/redoc/`, `/api/schema/`.
> **Error format:** structured — `{"error": {"code": "UPPERCASE_SNAKE_CASE",
> "message": "...", "details": {...}}}` (per project convention).

> **Implementation status (2026-05-26):** All phases are **implemented &
> tested** — every endpoint in this spec is live.
>
> A few response shapes differ from the examples below, as agreed:
> - `failure_rate` is an integer (e.g. `62`, not `62.5`).
> - `practice/stats` `by_type` is `{type: {sessions, minutes}}`.
> - `dashboard` → `score_summary.trends` is `{skill: [[previous, latest]]}`
>   (the two most recent scores), and `grammar_alerts[].trend` is one of
>   `improving` / `worsening` / `stable` (recent vs. older weekly counts).

---

## 1. Student Lookup

### `GET /api/students/by-email/?email=<email>`

Look up a student by email (passed as a query param to avoid URL-encoding the
`@`/`.`). Doris uses this to resolve the student ID at session start.

**Response:**
```json
{
  "id": 42,
  "name": "Jeremías Enríquez",
  "email": "jeremias@example.com",
  "current_level": "B2",
  "target_level": "C1",
  "start_date": "2025-05-01",
  "priority_areas": ["vocabulary", "grammar"]
}
```

**Errors:** `404` if not found.

---

## 2. Vocabulary & Spaced Repetition

### `GET /api/students/{student_id}/words/due/`

List words due for review today.

**Query params:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | 20 | Max words to return |

**Response:**
```json
{
  "count": 12,
  "words": [
    {
      "id": 101,
      "word": "straightaway",
      "definition": "immediately; without delay",
      "difficulty": "C1",
      "example_sentence": "I knew straightaway that something was wrong.",
      "collocations": ["right straightaway"],
      "mastery": "learning",
      "review_count": 2,
      "times_wrong": 1,
      "next_review_date": "2026-05-27"
    }
  ]
}
```

### `POST /api/words/{word_id}/review/`

Submit a review answer. Doris calls this after the student answers.

> **Review direction:** the student is shown the **definition** and must type
> the **word**. Grading is case-insensitive exact match against the word.
> `correct_answer` is therefore the word itself, not its definition.

**Request:** (for word #101 `"straightaway"`)
```json
{
  "student_answer": "straightaway"
}
```

**Response:**
```json
{
  "correct": true,
  "correct_answer": "straightaway",
  "next_review": "2026-06-02",
  "mastery": "mastered",
  "current_interval_days": 7
}
```

**Errors:** `400` (`VALIDATION_ERROR`) if `student_answer` is empty, `404`
(`WORD_NOT_FOUND`) if word not found.

### `GET /api/students/{student_id}/words/difficult/`

Get the hardest words (high `times_wrong`).

**Query params:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | 10 | Max words to return |
| `threshold` | int | 3 | Minimum `times_wrong` to qualify |

**Response:**
```json
{
  "words": [
    {
      "id": 87,
      "word": "virtually",
      "times_wrong": 5,
      "review_count": 8,
      "failure_rate": 62
    }
  ]
}
```

### `GET /api/students/{student_id}/words/by-mastery/{mastery}/`

List words filtered by mastery level.

**Path params:** `mastery` — one of `new`, `learning`, `mastered`.

**Response:**
```json
{
  "words": [
    {
      "id": 45,
      "word": "vow",
      "definition": "a solemn promise",
      "difficulty": "C1",
      "mastery": "learning",
      "next_review_date": "2026-05-28"
    }
  ]
}
```

### `POST /api/students/{student_id}/words/`

Add a new vocabulary word.

**Request:**
```json
{
  "word": "keep at bay",
  "definition": "to prevent something from coming close or happening",
  "difficulty": "C1",
  "example_sentence": "She kept the illness at bay with daily exercise.",
  "collocations": ["hold at bay", "keep something at bay"]
}
```

**Response:**
```json
{
  "id": 203,
  "word": "keep at bay",
  "definition": "to prevent something from coming close or happening",
  "difficulty": "C1",
  "mastery": "new",
  "next_review_date": "2026-05-28",
  "review_count": 0,
  "times_wrong": 0
}
```

**Errors:** `400` if word already exists or fields missing, `404` if student not found.

---

## 3. Grammar Corrections

### `POST /api/students/{student_id}/corrections/`

Log a grammar correction. Doris calls this every time she corrects the student.

**Request:**
```json
{
  "student_mistake": "I didn't remembered the word",
  "correct_version": "I didn't remember the word",
  "grammar_rule": "After 'didn't', use the base form of the verb",
  "category": "verb_tenses"
}
```

**Categories:** `prepositions`, `verb_tenses`, `word_order`, `articles`, `other`.

**Response:**
```json
{
  "id": 57,
  "student": 42,
  "date": "2026-05-27",
  "student_mistake": "I didn't remembered the word",
  "correct_version": "I didn't remember the word",
  "grammar_rule": "After 'didn't', use the base form of the verb",
  "category": "verb_tenses"
}
```

### `GET /api/students/{student_id}/corrections/`

List corrections with optional filters.

**Query params:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `category` | string | all | Filter by category |
| `date_from` | date | none | Start date (inclusive) |
| `date_to` | date | none | End date (inclusive) |
| `limit` | int | 50 | Max results |

**Response:**
```json
{
  "corrections": [
    {
      "id": 57,
      "date": "2026-05-27",
      "student_mistake": "I didn't remembered the word",
      "correct_version": "I didn't remember the word",
      "grammar_rule": "After 'didn't', use the base form of the verb",
      "category": "verb_tenses"
    }
  ]
}
```

### `GET /api/students/{student_id}/corrections/analytics/`

Common mistake categories and trends.

**Query params:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `period_days` | int | 30 | Lookback period |

**Response:**
```json
{
  "period_days": 30,
  "categories": [
    {
      "category": "prepositions",
      "label": "Prepositions",
      "count": 14,
      "percentage": 45.2,
      "example": "worthy about → worthy of"
    },
    {
      "category": "verb_tenses",
      "label": "Verb Tenses",
      "count": 8,
      "percentage": 25.8,
      "example": "I didn't remembered → I didn't remember"
    }
  ]
}
```

### `GET /api/students/{student_id}/corrections/trend/{category}/`

Weekly trend for a specific grammar category.

**Query params:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `weeks` | int | 8 | Number of weeks to show |

**Response:**
```json
{
  "category": "prepositions",
  "trend": [
    { "week_start": "2026-03-30", "count": 5 },
    { "week_start": "2026-04-06", "count": 3 },
    { "week_start": "2026-04-13", "count": 2 }
  ]
}
```

---

## 4. Scores & Assessments

### `POST /api/students/{student_id}/assessments/`

Record an assessment with skill scores.

**Request:**
```json
{
  "scores": {
    "pronunciation": 72,
    "fluency": 68,
    "intonation": 79,
    "grammar": 76,
    "vocabulary": 67
  },
  "assessment_date": "2026-05-27",
  "notes": "End of May assessment"
}
```

**Response:**
```json
{
  "id": 12,
  "student": 42,
  "date": "2026-05-27",
  "notes": "End of May assessment",
  "scores": {
    "pronunciation": 72,
    "fluency": 68,
    "intonation": 79,
    "grammar": 76,
    "vocabulary": 67
  }
}
```

### `GET /api/students/{student_id}/scores/`

Get score history.

**Query params:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `skill` | string | all | Filter: `pronunciation`, `fluency`, `intonation`, `grammar`, `vocabulary` |
| `limit` | int | 20 | Max assessments to return |

**Response:**
```json
{
  "scores": [
    {
      "assessment_id": 12,
      "date": "2026-05-27",
      "scores": {
        "pronunciation": 72,
        "fluency": 68,
        "intonation": 79,
        "grammar": 76,
        "vocabulary": 67
      }
    }
  ]
}
```

### `GET /api/students/{student_id}/scores/latest/`

Get the most recent score per skill.

**Response:**
```json
{
  "pronunciation": 72,
  "fluency": 68,
  "intonation": 79,
  "grammar": 76,
  "vocabulary": 67
}
```

### `GET /api/students/{student_id}/scores/declining/`

Detect skills that dropped ≥3 points in the last 7 days.

**Response:**
```json
{
  "declining": {
    "intonation": {
      "current": 71,
      "previous": 79,
      "change": -8
    }
  }
}
```

---

## 5. Practice Sessions

### `POST /api/students/{student_id}/practice/`

Log a practice session.

**Request:**
```json
{
  "practice_type": "vocabulary",
  "duration_minutes": 25,
  "notes": "Reviewed Set 1 and Set 2 words, scored 3/5 and 4/5",
  "date": "2026-05-27"
}
```

**Practice types:** `vocabulary`, `writing`, `idioms`, `grammar`, `conversation`, `quiz`.

**Response:**
```json
{
  "id": 88,
  "student": 42,
  "date": "2026-05-27",
  "practice_type": "vocabulary",
  "duration_minutes": 25,
  "notes": "Reviewed Set 1 and Set 2 words, scored 3/5 and 4/5"
}
```

### `GET /api/students/{student_id}/practice/`

List practice sessions with filters.

**Query params:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `practice_type` | string | all | Filter by type |
| `date_from` | date | none | Start date |
| `date_to` | date | none | End date |
| `limit` | int | 20 | Max results |

### `GET /api/students/{student_id}/practice/streak/`

Get current consecutive-day practice streak.

**Response:**
```json
{
  "streak": 14
}
```

### `GET /api/students/{student_id}/practice/stats/`

Aggregate practice statistics.

**Query params:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `days` | int | 30 | Lookback period |

**Response:**
```json
{
  "total_minutes": 320,
  "total_sessions": 18,
  "avg_duration": 17.8,
  "by_type": {
    "vocabulary": { "sessions": 10, "minutes": 180 },
    "grammar": { "sessions": 4, "minutes": 60 },
    "writing": { "sessions": 4, "minutes": 80 }
  }
}
```

---

## 6. Quizzes

### `POST /api/students/{student_id}/quiz/generate/`

Generate a weekly quiz (idempotent — returns existing if already generated).

**Response:**
```json
{
  "quiz_id": 7,
  "week_start_date": "2026-05-25",
  "total_questions": 15,
  "questions": [
    {
      "id": 201,
      "question_type": "definition_to_word",
      "prompt": "What word means 'a solemn promise'?",
      "correct_answer": "vow"
    },
    {
      "id": 202,
      "question_type": "word_to_sentence",
      "prompt": "Use 'straightaway' in a sentence.",
      "correct_answer": "I knew straightaway that something was wrong."
    },
    {
      "id": 203,
      "question_type": "sentence_rewrite",
      "prompt": "Rewrite: 'I didn't remembered the word' (fix the error)",
      "correct_answer": "I didn't remember the word"
    }
  ]
}
```

### `POST /api/questions/{question_id}/answer/`

Submit an answer to a quiz question.

**Request:**
```json
{
  "student_answer": "promise"
}
```

**Response:**
```json
{
  "is_correct": false,
  "feedback": "Close! The answer is 'vow' — a solemn promise."
}
```

### `GET /api/students/{student_id}/quizzes/`

List past quizzes with results.

**Response:**
```json
{
  "quizzes": [
    {
      "quiz_id": 7,
      "week_start_date": "2026-05-25",
      "score_percentage": 73.3,
      "correct_answers": 11,
      "wrong_answers": 4,
      "total_questions": 15
    }
  ]
}
```

### `GET /api/quizzes/{quiz_id}/results/`

Detailed results for a specific quiz.

**Response:**
```json
{
  "quiz_id": 7,
  "total_questions": 15,
  "correct_answers": 11,
  "wrong_answers": 4,
  "score_percentage": 73.3,
  "questions": [
    {
      "id": 201,
      "question_type": "definition_to_word",
      "prompt": "What word means 'a solemn promise'?",
      "student_answer": "promise",
      "correct_answer": "vow",
      "is_correct": false
    }
  ]
}
```

---

## 7. Dashboard

### `GET /api/students/{student_id}/dashboard/`

One call to get everything about a student. Doris uses this for progress reports.

**Response:**
```json
{
  "student_info": {
    "name": "Jeremías Enríquez",
    "current_level": "B2",
    "target_level": "C1",
    "start_date": "2025-05-01",
    "priority_areas": ["vocabulary", "grammar"]
  },
  "score_summary": {
    "latest": { "pronunciation": 72, "fluency": 68, "intonation": 79, "grammar": 76, "vocabulary": 67 },
    "trends": { "grammar": [[73, 76]], "vocabulary": [[66, 67]] },
    "declining": { "intonation": { "current": 71, "previous": 79, "change": -8 } }
  },
  "vocabulary_stats": {
    "total_words": 33,
    "new": 10,
    "learning": 15,
    "mastered": 8,
    "due_today": 6
  },
  "practice_streak": 14,
  "difficult_words": [
    { "word": "virtually", "times_wrong": 5, "failure_rate": 62.5 }
  ],
  "grammar_alerts": [
    { "category": "prepositions", "count": 14, "trend": "improving" }
  ],
  "recent_corrections": [
    { "date": "2026-05-27", "mistake": "worthy about", "correct": "worthy of", "category": "prepositions" }
  ],
  "quiz_scores": [
    { "quiz_id": 7, "week": "2026-05-25", "score": 73.3 }
  ],
  "next_quiz_date": "2026-06-01"
}
```

---

## Priority Summary

| Phase | Endpoints | Why first |
|-------|-----------|-----------|
| **Phase 1** (MVP) | `words/due/`, `words/{id}/review/`, `corrections/` POST, `students/by-email/` | Core daily workflow — practice + grammar tracking |
| **Phase 2** | `words/` POST, `corrections/` GET + analytics, `practice/` POST + streak + stats | Full vocabulary management + practice logging |
| **Phase 3** | `assessments/`, `scores/`, `declining/`, `quiz/`, `dashboard/` | Periodic testing + full progress overview |

---

## Notes for Implementation

- **DRF serializers** should validate inputs (e.g., score values 0–100, valid categories).
- **Call existing functions** — don't reimplement logic in views. Every endpoint maps to an existing service/selector function.
- **Auth** — DRF `TokenAuthentication`; one token for the Doris bot. All
  endpoints require `IsAuthenticated`. Single student ID; no multi-student
  switching needed yet.
- **Docs** — endpoints are documented with `drf-spectacular`
  (`@extend_schema`); browse at `/api/docs/`.
- **Pagination** — list endpoints take a `limit` query param; add
  `?page=&page_size=` only if data grows.
- **Error format** — structured: `{"error": {"code": "UPPERCASE_SNAKE_CASE",
  "message": "...", "details": {...}}}`. Field-level validation messages go
  under `details` with `code: VALIDATION_ERROR`.
