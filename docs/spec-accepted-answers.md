# Feature Spec: Accepted Answers for Vocabulary Review

## Problem

The review endpoint (`POST /api/words/{word_id}/review/`) uses exact string matching against the `word` field. This causes false negatives when the student gives a correct answer that doesn't match exactly.

**Examples of false negatives:**
| Word in DB | Student Answer | Why it's correct | Currently marked |
|------------|---------------|------------------|-----------------|
| `to shut down` | `shut down` | Prefix "to" is optional | ❌ Wrong |
| `to sit tight` | `sit tight` | Prefix "to" is optional | ❌ Wrong |
| `to choke` | `choke` | Prefix "to" is optional | ❌ Wrong |
| `last (verb)` | `last` | Part-of-speech tag in name | ❌ Wrong |

## Proposed Solution

Add an `accepted_answers` field to the Word model — a list of alternative strings that should also be considered correct during review grading.

### Model Changes

**Word model — add field:**

```python
accepted_answers = models.JSONField(
    default=list,
    blank=True,
    help_text="List of alternative answers accepted as correct (in addition to the main word)."
)
```

**Examples:**
```json
{
  "word": "to shut down",
  "accepted_answers": ["shut down"],
  ...
}
```

```json
{
  "word": "to sit tight",
  "accepted_answers": ["sit tight"],
  ...
}
```

```json
{
  "word": "to choke",
  "accepted_answers": ["choke"],
  ...
}
```

### Review Logic Changes

In the review grading logic (wherever the student answer is compared to the word), update the match check:

**Current logic (pseudocode):**
```python
is_correct = normalize(student_answer) == normalize(word.word)
```

**New logic:**
```python
normalized_answer = normalize(student_answer)
normalized_word = normalize(word.word)

# Check main word
is_correct = normalized_answer == normalized_word

# Check accepted answers if not already matched
if not is_correct and word.accepted_answers:
    is_correct = any(
        normalized_answer == normalize(alt)
        for alt in word.accepted_answers
    )
```

### Serializer Changes

Include `accepted_answers` in:
- `WordSerializer` (list/detail views) — so it's visible in the API
- `WordCreateSerializer` (create endpoint) — so it can be set when adding words

### Admin Panel Changes

Add `accepted_answers` to the Word admin form so it can be edited through the admin UI.

### API Schema

The `accepted_answers` field should:
- Be an array of strings
- Default to `[]` (empty list)
- Be optional on create/update
- Be visible on GET responses

## Acceptance Criteria

1. ✅ `accepted_answers` field exists on the Word model
2. ✅ Review endpoint accepts answers matching either `word` OR any entry in `accepted_answers`
3. ✅ Field is editable via admin panel
4. ✅ Field is included in API responses (GET word list/detail)
5. ✅ Field can be set via POST/PUT/PATCH on the word endpoint
6. ✅ Empty `accepted_answers` list behaves same as current (no change to existing behavior)

## Suggested Default Values

For existing words with known prefix issues:

| Word | Suggested `accepted_answers` |
|------|------------------------------|
| to shut down | `["shut down"]` |
| to sit tight | `["sit tight"]` |
| to choke | `["choke"]` |
| to keep at bay | `["keep at bay"]` |
| to drive crazy | `["drive crazy"]` |
| to tell time | `["tell time"]` |
| to dot | `["dot"]` |
| to strike | `["strike"]` |
| to assess | `["assess"]` |
| to commit | `["commit"]` |
| to unleash | `["unleash"]` |
| to turn out | `["turn out"]` |
| that being said | `["that said", "having said that"]` |
