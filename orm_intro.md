# ORM Exploration Exercise — Individual Research

**Format:** Individual. Each of the 11 developers explores a **different** ORM.
**Output:** A filled-in version of the table below, plus a short (2–3 min) share-out to the group at the end.
**Method:** You can read the official documentation (quickstart / getting started / models / relations pages) + install and run a small example if you have time.

---

## Why This Exercise

Before you build your own mini-ORM this week, look at how existing, production ORMs solve the exact same problems you're about to solve yourself: declaring fields, registering models, handling relationships, generating queries, and avoiding the N+1 problem.

---

## Suggested Assignment (one per developer)

Some example of ORM that you can use:

1. **SQLAlchemy** (Python)
2. **Peewee** (Python)
3. **Tortoise ORM** (Python, async)
4. **Pony ORM** (Python)
5. **SQLModel** (Python)
6. **Piccolo** (Python, async)
7. **Prisma** (TypeScript/Node)
8. **TypeORM** (TypeScript/Node)
9. **Sequelize** (JavaScript/Node)
10. **MikroORM** (TypeScript/Node)
11. **Objection.js** (JavaScript/Node)

You can choose any other ORM except Odoo

---

## What to Find

For each row: read the concept explanation, then find and write down how **your assigned ORM** answers it.

| #  | Concept (anchor explanation)                                                                                                                                                                                                                                | Your ORM's answer |
|----|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|
| 1  | **Active Record vs Data Mapper.** Active Record: the model object knows how to save/load itself (`instance.save()`). Data Mapper: a separate layer handles persistence (`session.add(instance); session.commit()`). Which style does your ORM follow?       |                   |
| 2  | **Field / column declaration.** How do you declare a typed field on a model (e.g. a string, an integer, a boolean)? Paste a short example. This is the equivalent of the `Field` descriptor you'll build on Day 1.                                          |                   |
| 3  | **Model registration mechanism.** How does the ORM "know about" every model in the project without you manually registering them somewhere? (metaclass, decorator, base class scanning, explicit registry call — name the mechanism if the docs mention it) |                   |
| 4  | **Schema generation / migrations.** Does the ORM generate the database table directly from the model, or does it require a separate migration step/tool? What's that tool called (if any)?                                                                  |                   |
| 5  | **Basic CRUD syntax.** What does create, read/filter, update, and delete look like? One short example of each.                                                                                                                                              |                   |
| 6  | **Many-to-one relationship** (the "many" side referencing a single related record — equivalent of `Many2one`). What's it called, and what does declaring one look like?                                                                                     |                   |
| 7  | **One-to-many relationship** (the reverse side — equivalent of `One2many`). Is it declared explicitly, or inferred automatically from the many-to-one side?                                                                                                 |                   |
| 8  | **Many-to-many relationship** (equivalent of `Many2many`). Does the ORM hide the join/association table completely, or do you ever interact with it directly?                                                                                               |                   |
| 9  | **Laziness.** When you write a filter/query, does it execute immediately, or does it return an object representing the query that only executes later (on iteration, `.all()`, `.first()`, etc.)? How do you tell, from the docs, which one it is?          |                   |
| 10 | **Query chaining.** Can you narrow an existing query by calling another method on it (e.g. `.filter(...).filter(...)` or `.where(...).where(...)`), without re-querying from scratch? Show an example if the docs have one.                                 |                   |
| 11 | **The N+1 problem.** Does the documentation mention this problem by name? What's the ORM's built-in fix called (e.g. eager loading, `select_related`/`prefetch_related`-style methods, `.include()`, `.with()`, `JOIN FETCH`)?                              |                   |
| 12 | **Computed / virtual fields.** Does the ORM support a field whose value is derived from other fields via code, rather than stored directly in the database? What's it called?                                                                               |                   |
| 13 | **Transactions.** Is there an explicit transaction API (e.g. `session.begin()`, `transaction.atomic()`), or is it handled implicitly per operation/request?                                                                                                 |                   |

---

## Bonus

These go beyond what you'll build in the mini-ORM this week, but they're worth 5 extra minutes if your assigned ORM has clear answers:

| Concept (anchor explanation)                                                                                                                                                                                                                                                                                                  | Your ORM's answer |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|
| **Filter/domain syntax.** Odoo uses a list-of-tuples "domain" syntax to filter records, e.g. `[('name', '=', 'Acme')]`. Does your ORM have an equivalent structured filter syntax, or does it rely on chained method calls / raw expressions instead?                                                                         |                   |
| **Batch/collection return type.** Does a query return a plain list, or a special collection object with its own methods (the ancestor of what you'll build as `RecordSet` this week)?                                                                                                                                         |                   |
| **Model inheritance.** Can one model extend or reuse fields from another (single-table inheritance, mixins, abstract base models)? Odoo has a very distinctive mechanism here (`_inherit` extends an existing model in place, `_inherits` delegates to another model) — does your ORM support anything similar, even loosely? |                   |
| **Implicit vs explicit session/connection scope.** Do you ever see or manage a "session"/"connection" object directly in basic usage, or is it fully hidden behind the model API?                                                                                                                                             |                   |

---

## Share-Out Format

2–3 minutes per person:

1. Active Record or Data Mapper, and one sentence on what that felt like to use.
2. The one concept from the table that took the longest to find a clear answer for, or that the documentation explained the least clearly, what made it hard?
3. One thing your ORM does that genuinely surprised you, or that you wouldn't have guessed was needed before doing this research.

