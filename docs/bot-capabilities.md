# DorisTrack — Bot Capabilities

> Reference for an external bot / AI agent working with DorisTrack.
>
> **Part 1** is a plain-language capability catalog: the domain and what the
> app can do today.
> **Part 2** is a structured action spec (name, inputs, outputs) the bot can
> use to plan operations.
>
> **Important — read first:** DorisTrack currently exposes **no REST/HTTP API**.
> It is a server-rendered Django app: every URL returns an HTML page meant for a
> human browser. The functions below exist as **Python service/selector
> functions**, callable only from inside the Django process (views, shell,
> management commands). A bot **cannot call them remotely yet**. To let a bot
> drive the app, an integration layer must be built first — see
> [Part 3: How a bot can actually invoke these](#part-3--how-a-bot-can-actually-invoke-these).

---

## Part 1 — Capability catalog

### Domain entities

| Entity | App | Key fields | Notes |
|--------|-----|-----------|-------|
| **Tutor** | `profiles` | `name`, `email` | Teacher; owns many students |
| **Student** | `profiles` | `name`, `email`, `current_level`, `target_level`, `start_date`, `priority_areas`, `tutor` | Levels: `B1`, `B2`, `C1`, `C2`. Central entity — everything links to a student |
| **Assessment** | `scores` | `student`, `date`, `notes` | One assessment session, holds several skill scores |
| **Score** | `scores` | `assessment`, `skill`, `value` (0–100) | Skills: `pronunciation`, `fluency`, `intonation`, `grammar`, `vocabulary`. One value per skill per assessment |
| **Word** | `vocabulary` | `word`, `definition`, `difficulty`, `example_sentence`, `collocations`, `mastery`, `review_count`, `times_wrong`, `next_review_date`, `ease_factor`, `current_interval_days` | Vocabulary item with spaced-repetition state. `mastery`: `new`/`learning`/`mastered`. `difficulty`: `B2`/`C1`/`C2` |
| **Quiz** | `quiz` | `student`, `week_start_date` | One weekly quiz per student/week |
| **QuizQuestion** | `quiz` | `quiz`, `question_type`, `prompt`, `correct_answer`, `student_answer`, `is_correct` | Types: `definition_to_word`, `word_to_sentence`, `sentence_rewrite` |
| **Correction** | `grammar` | `student`, `date`, `student_mistake`, `correct_version`, `grammar_rule`, `category` | Categories: `prepositions`, `verb_tenses`, `word_order`, `articles`, `other` |
| **PracticeSession** | `practice` | `student`, `date`, `practice_type`, `duration_minutes`, `notes`, `words_learned` | Types: `vocabulary`, `writing`, `idioms`, `grammar`, `conversation`, `quiz` |

### What the app can do (grouped by domain)

**Students & tutors** (`apps/profiles`)
- Look up a student by email or id; list a tutor's students; list all tutors.
- Get-or-create a student by email.

**Scores & assessments** (`apps/scores`)
- Record an assessment with a set of skill scores.
- Read score history (optionally filtered by skill), score trends over N days,
  latest score per skill.
- Detect declining skills (skills that dropped ≥3 points in the last 7 days vs.
  the previous 7 days).

**Vocabulary & spaced repetition** (`apps/vocabulary`)
- List words due for review today; count due words; list words by mastery.
- Check a review answer (grades it, advances or resets the spaced-repetition
  interval, updates mastery).
- Identify difficult words (high `times_wrong`) and compute per-word failure
  rate. Intervals used: `[1, 2, 4, 7, 15, 30]` days; correct → next interval,
  wrong → reset to 1 day.

**Quizzes** (`apps/quiz`)
- Generate a weekly quiz from words due for review (up to 10 words, 3 question
  types each).
- Submit and auto-grade an answer (exact match for `definition_to_word`;
  keyword overlap for sentence types).
- Read quiz list, quiz detail, and a results summary (score %, correct/wrong
  counts).

**Grammar corrections** (`apps/grammar`)
- Log a correction (mistake → correct version, with rule and category).
- Read corrections (filter by category / date range).
- Analytics: most common mistake categories over a period, per-week trend for a
  category, distinct categories with counts.

**Practice tracking** (`apps/practice`)
- Log a practice session.
- Compute the current consecutive-day practice streak.
- Aggregate stats over N days (total minutes, sessions, average, by type) and a
  full-year heatmap of minutes per day.

**Dashboard aggregation** (`apps/core`, `apps/dashboard`)
- One call assembles a full student dashboard: student info, score summary +
  trends + declining skills, vocabulary stats, practice streak, difficult words,
  grammar alerts, recent corrections, quiz scores, and next quiz date.

### Web pages available today (HTML, not API)

| URL | View | Purpose |
|-----|------|---------|
| `/` | `dashboard.home` | Main student dashboard |
| `/profile/` | `profiles.student_profile` | Student profile |
| `/scores/` | `scores.score_list` | Assessment list |
| `/scores/entry/` | `scores.score_entry` | Record an assessment |
| `/scores/charts/` | `scores.score_charts` | Score charts |
| `/vocabulary/review/` | `vocabulary.review_session` | Review session |
| `/vocabulary/review/complete/` | `vocabulary.review_complete` | Review complete |
| `/vocabulary/difficult/` | `vocabulary.difficult_words` | Difficult words |
| `/vocabulary/word/<id>/` | `vocabulary.word_detail` | Word detail |
| `/vocabulary/word/<id>/review/` | `vocabulary.review_single` | Review one word |
| `/quiz/` | `quiz.quiz_list` | Quiz list |
| `/quiz/take/` , `/quiz/take/<id>/` | `quiz.quiz_take` | Take a quiz |
| `/quiz/submit/<question_id>/` | `quiz.quiz_submit` | Submit an answer |
| `/quiz/results/<id>/` | `quiz.quiz_results` | Quiz results |
| `/grammar/` | `grammar.correction_list` | Corrections list |
| `/grammar/add/` | `grammar.correction_add` | Add a correction |
| `/grammar/analytics/` | `grammar.correction_analytics` | Grammar analytics |
| `/practice/` | `practice.list` | Practice list |
| `/practice/add/` | `practice.add` | Log practice |
| `/practice/heatmap/` | `practice.heatmap` | Practice heatmap |
| `/admin/` | Django admin | CRUD on all entities (staff login) |

---

## Part 2 — Action spec

These are the callable Python functions, framed as actions. Each one lists its
module path, inputs, and what it returns. A bot planning work should reference
these names; an integration layer (Part 3) maps each to a remote call.

> Convention: a `student` argument is a `Student` model instance; a
> `student_id` argument is its integer primary key.

### Write actions (mutate data)

#### `record_assessment`
- **Module:** `apps.scores.services.record_assessment`
- **Input:** `student_id: int`, `scores_dict: dict` (e.g.
  `{"pronunciation": 85, "fluency": 78}` — keys must be valid skills, values
  clamped to 0–100), `assessment_date: date`, `notes: str = ""`
- **Returns:** the created `Assessment`
- **Effect:** creates an assessment and one `Score` per valid skill key.

#### `log_correction`
- **Module:** `apps.grammar.services.log_correction`
- **Input:** `student`, `mistake: str`, `correct: str`, `rule: str = ""`,
  `category: str = "other"` (one of the grammar categories)
- **Returns:** the created `Correction` (dated today)

#### `log_practice`
- **Module:** `apps.practice.services.log_practice`
- **Input:** `student`, `practice_type: str` (one of the practice types),
  `duration_minutes: int`, `notes: str = ""`, `date_obj: date = None`
  (defaults to today)
- **Returns:** the created `PracticeSession`

#### `check_review_answer`
- **Module:** `apps.vocabulary.services.check_review_answer`
- **Input:** `word_id: int`, `student_answer: str`
- **Returns:** `{"correct": bool, "correct_answer": str, "next_review": date}`
- **Effect:** grades the answer and updates the word's review state, mastery,
  and next review date.

#### `generate_weekly_quiz`
- **Module:** `apps.quiz.services.generate_weekly_quiz`
- **Input:** `student`
- **Returns:** a `Quiz` for the current week (idempotent — returns the existing
  one if already generated)
- **Effect:** creates up to 10 words × 3 question types from words due for
  review.

#### `submit_quiz_answer`
- **Module:** `apps.quiz.services.submit_quiz_answer`
- **Input:** `question_id`, `student_answer: str`
- **Returns:** `(is_correct: bool, feedback: str)`
- **Effect:** stores and auto-grades the answer.

#### `get_or_create_student`
- **Module:** `apps.profiles.services.get_or_create_student`
- **Input:** `name: str`, `email: str`, `**kwargs` (extra `Student` fields)
- **Returns:** `(student, created: bool)`

### Read actions / insights (no mutation)

#### Scores
- `apps.scores.selectors.get_assessments(student_id, limit=None)` → assessments,
  newest first.
- `apps.scores.selectors.get_score_history(student_id, skill=None)` → all scores
  (optionally one skill).
- `apps.scores.selectors.get_score_trends(student_id, skill=None, days=30)` →
  list of `(date_iso, value)`.
- `apps.scores.selectors.get_latest_scores(student_id)` → `{skill: value}`.
- `apps.scores.services.detect_declining_skills(student_id)` →
  `{skill: {"current", "previous", "change"}}` for skills down ≥3 pts.

#### Vocabulary
- `apps.vocabulary.selectors.get_words_for_review(student)` → words due today.
- `apps.vocabulary.selectors.get_due_words_count(student)` → int.
- `apps.vocabulary.selectors.get_words_by_mastery(student, mastery)` → words.
- `apps.vocabulary.selectors.get_difficult_words(student, threshold=3)` → words
  with `times_wrong ≥ threshold`.
- `apps.vocabulary.selectors.get_difficult_words_detailed(student, limit=10)` →
  list of `{word, times_wrong, review_count, failure_rate}`.
- `apps.vocabulary.selectors.get_word_failure_rate(word_id)` → int %.

#### Quizzes
- `apps.quiz.selectors.get_quizzes(student)` → quizzes, newest first.
- `apps.quiz.selectors.get_quiz_detail(quiz_id, student)` → quiz + questions.
- `apps.quiz.selectors.get_quiz_results(quiz)` →
  `{total, correct, score, questions: [...]}`.
- `apps.quiz.services.get_quiz_results_summary(quiz)` →
  `{quiz_id, total_questions, correct_answers, wrong_answers, score_percentage, week_start_date}`.

#### Grammar
- `apps.grammar.selectors.get_corrections(student, category=None, date_from=None, date_to=None)`
  → corrections, newest first.
- `apps.grammar.selectors.get_categories(student_id)` →
  `[{category, label, count}]`.
- `apps.grammar.services.get_common_mistakes(student, period_days=30)` →
  `[{category, label, count, percentage, example}]`.
- `apps.grammar.services.get_mistake_trend(student, category, weeks=8)` →
  `[{week_start, count}]`.

#### Practice
- `apps.practice.selectors.get_sessions(student, date_from=None, date_to=None, practice_type=None)`
  → sessions, newest first.
- `apps.practice.selectors.get_heatmap_data(student, year=None)` →
  `{date_iso: minutes}`.
- `apps.practice.selectors.get_total_practice_minutes(student, days=30)` → int.
- `apps.practice.services.get_practice_streak(student)` → int (consecutive days).
- `apps.practice.services.get_practice_stats(student, days=30)` →
  `{total_minutes, total_sessions, avg_duration, by_type}`.

#### Profiles
- `apps.profiles.selectors.get_student_by_email(email)` → `Student | None`.
- `apps.profiles.selectors.get_student_profile(student_id)` → `Student | None`.
- `apps.profiles.selectors.get_students_by_tutor(tutor)` → students.
- `apps.profiles.selectors.get_all_tutors()` → tutors.

#### Dashboard (aggregate insight)
- `apps.core.selectors.get_student_dashboard_data(student)` → one dict with
  `student_info`, `score_summary`, `vocabulary_stats`, `practice_streak`,
  `difficult_words`, `grammar_alerts`, `quiz_scores`, `next_quiz_date`,
  `recent_corrections`. This is the single richest "give me everything about a
  student" call.

---

## Part 3 — How a bot can actually invoke these

The functions above are in-process Python. Pick one bridge depending on need:

1. **REST API (recommended for a remote bot).** `djangorestframework` is already
   installed but unused. Add serializers + views that wrap the service/selector
   functions above (do **not** reimplement logic in the views — call the
   existing functions, per the SoC/DRY conventions in `AGENTS.md`). Suggested
   shape:
   - `POST /api/students/{id}/assessments/` → `record_assessment`
   - `POST /api/students/{id}/corrections/` → `log_correction`
   - `POST /api/students/{id}/practice/` → `log_practice`
   - `POST /api/words/{id}/review/` → `check_review_answer`
   - `POST /api/students/{id}/quiz/` → `generate_weekly_quiz`
   - `POST /api/questions/{id}/answer/` → `submit_quiz_answer`
   - `GET  /api/students/{id}/dashboard/` → `get_student_dashboard_data`
   - plus `GET` endpoints for the read actions above.
   Document new endpoints with drf-spectacular (Swagger/ReDoc).

2. **Management command.** For a local/offline bot, wrap actions in a custom
   `manage.py` command and invoke via `make shell` / `docker compose exec`.

3. **Django admin.** For manual data entry, every entity is already editable at
   `/admin/` — no code needed.

Until one of these exists, treat this document as a **reference for what to
build / request**, not a set of endpoints the bot can call directly.
