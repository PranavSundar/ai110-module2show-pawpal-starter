# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I started with a small set of classes. Owner holds name, availabli_minutes_per_day, preferences, max_tasks. Pet holds name/species/needs/age. Task holds title, duration, priority. Scheduler takes these and builds a daily plan.

**b. Design changes**

I rewrote the skeleton to concrete backend logic, added new classes/fields from your design critique, and made the scheduler use priority + deadline to build a plan fitting the owner's daily budget. Owner and Pet got basic behaviors (preferences, energy), and Task now includes unique task_id and scheduling timestamps. DailyPlan now tracks tasks and total time, and the Scheduler uses ConstraintEngine to keep logic modular with explicit constraint handling. Finally, PawPalApp stub methods connect to scheduler behavior.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**
Constraints: time budget, priority, completion status, and recurrence are used. ConstraintEngine.apply_constraints() filters out completed tasks and respects max task/day and availability.
Chosen constraints: time and priority are most important because pet care must fit into owner capacity and high-risk tasks are handled first.


**b. Tradeoffs**

The current conflict detector only checks for exact or simple overlapping start/end alignments, but it does not manage partial overlaps with different durations in a sophisticated way (for example, one task from 8:00-8:30 and another 8:15-8:45). This keeps logic lightweight and predictable but means some schedule subtleties might not be optimized.
For a basic pet care planner, minimizing crash-risk and keeping explanations simple outweighs handling highly complex interval packing.

---

## 3. AI Collaboration

**a. How you used AI**
Used AI for design advice, test plan drafting, and refactoring from a skeleton to working methods. Prompts asking “what edge cases to test” and “how to map implementation to UML” were most helpful.

**b. Judgment and verification**
Judgment: I rejected any path that contradicted project requirements (e.g., missing Task.mark_complete recurrence). I verified by reading pawpal_system.py and running pytest. As a result, AI suggestions were treated as drafts, then finalized with code inspection and tests.

---

## 4. Testing and Verification

**a. What you tested**
Tested: task completion and recurrence, sort-by-time correctness, and conflict detection. Important because these are core scheduler features in the prompt.


**b. Confidence**
Confidence: high, but I’d next check DST/date boundaries, simultaneous promotion tie-breaks, and invalid input handling.
Edge cases next: leap day recurrence, missing/past deadlines, and out-of-budget scenarios.

---

## 5. Reflection

**a. What went well**
Properly implementing full flow from model classes to UI and getting passing tests quickly.

**b. What you would improve**
Adding richer conflict resolution (auto-reschedule/weighter overlap handling) and better task editing UI.

**c. Key takeaway**
Start with clean class behavior + tests, then wire UI. Also, use AI for scaffolding, but always verify with code and tests.
