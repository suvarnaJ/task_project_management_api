# Task / Project Management API - PostgreSQL vs MongoDB

Two implementations of the same FastAPI application:

- `version_a_postgres/` - Neon PostgreSQL using SQLAlchemy 2.x
- `version_b_mongodb/` - MongoDB Atlas using PyMongo

Both versions expose the same business operations and comparable REST endpoints.

## Features

| Feature | Endpoint |
|---|---|
| Create project | `POST /projects` |
| List projects | `GET /projects` |
| Create task | `POST /projects/{project_id}/tasks` |
| Assign task | `PATCH /tasks/{task_id}/assign` |
| Update status | `PATCH /tasks/{task_id}/status` |
| Retrieve tasks | `GET /tasks` |
| Filter tasks | `GET /tasks?project_id=...&status_filter=IN_PROGRESS&assignee=...` |
| Retrieve one task | `GET /tasks/{task_id}` |
| Delete task | `DELETE /tasks/{task_id}` |

Status values: `TODO`, `IN_PROGRESS`, `DONE`, `BLOCKED`.

## Run either implementation

Follow the setup instructions in the relevant version folder. Run only one server at a time on port 8000, or change the port for one server.

Interactive API documentation: `http://127.0.0.1:8000/docs`.

## Example API workflow

1. `POST /projects`
```json
{
  "name": "E-commerce Platform",
  "description": "Build the online shopping platform"
}
```
2. Copy the returned project `id`.
3. `POST /projects/{project_id}/tasks`
```json
{
  "title": "Build product API",
  "description": "Implement product CRUD endpoints"
}
```
4. Copy the returned task `id`.
5. `PATCH /tasks/{task_id}/assign`
```json
{
  "assignee": "Amit"
}
```
6. `PATCH /tasks/{task_id}/status`
```json
{
  "status": "IN_PROGRESS"
}
```
7. `GET /tasks?status_filter=IN_PROGRESS`
8. `DELETE /tasks/{task_id}`

**Important:** PostgreSQL IDs are integers; MongoDB IDs are 24-character hexadecimal ObjectId strings. Use the exact ID returned by the API in subsequent calls.

## Database schema and relationship

### PostgreSQL

Two normalized tables:

**projects**
- `id` - primary key
- `name`
- `description`
- `created_at`

**tasks**
- `id` - primary key
- `project_id` - foreign key to `projects.id`
- `title`
- `description`
- `assignee`
- `status`
- `created_at`

Relationship: one Project has many Tasks (one-to-many). A foreign key enforces that each task references an existing project. SQLAlchemy relationship and database cascade behavior support parent-child lifecycle management. For production, also configure and test database-level cascade behavior and migrations.

### MongoDB

Two collections:

**projects**
```json
{
  "_id": "ObjectId",
  "name": "E-commerce Platform",
  "description": "Build the online shopping platform",
  "created_at": "date"
}
```

**tasks**
```json
{
  "_id": "ObjectId",
  "project_id": "ObjectId reference",
  "title": "Build product API",
  "description": "Implement product CRUD endpoints",
  "assignee": "Amit",
  "status": "IN_PROGRESS",
  "created_at": "date"
}
```

The task's `project_id` is a logical reference. MongoDB does not automatically enforce referential integrity like a relational foreign key. The API checks that the project exists before inserting a task.

## PostgreSQL vs MongoDB comparison

| Area | PostgreSQL | MongoDB |
|---|---|---|
| Schema | Defined tables and column types | Flexible BSON documents |
| Relationships | Native foreign keys and joins | References or embedded documents |
| Querying | SQL, joins, grouping, aggregates | Filter documents, aggregation pipeline |
| Flexibility | Schema changes usually require migrations | Fields can vary between documents |
| Normalization | Strong support for normalized data | Often denormalized around access patterns |
| Consistency | ACID transactions; constraints | Atomic single-document writes and multi-document transactions |
| Scalability | Vertical scaling and read replicas; horizontal options | Sharding and replica sets |
| Development experience | SQLAlchemy models, constraints, migrations | Direct document mapping and flexible models |
| Best fit | Structured, related business data | Variable or document-oriented data |

## Which database would I choose for production?

**My choice: PostgreSQL (Neon PostgreSQL).**

Reasons:
1. Projects and Tasks have a clear one-to-many relationship.
2. Foreign keys prevent orphan tasks and protect data integrity.
3. SQL joins make project-level task reporting straightforward.
4. Transactions help maintain consistency when multiple related records change.
5. The schema is predictable: task title, status, assignee and project reference are structured fields.
6. SQLAlchemy and Alembic provide a mature development and migration workflow.

MongoDB is also a valid choice if task documents have highly variable structures, if the application is document-centric, or if the access patterns favor embedding task data inside projects. Its flexible schema is useful, but flexibility alone is not a reason to choose it.

**Conclusion:** For this specific project/task management application, PostgreSQL is the better default production choice because relational integrity and structured querying are more important than schema flexibility.

## Suggested GitHub submission

1. Create a GitHub repository named `task-project-management-api`.
2. Upload both version folders and this root README.
3. Add `.env.example` files, but never upload actual `.env` files or database passwords.
4. Add screenshots of successful Swagger API calls for both databases.
5. Include the YouTube comparison video link below after publishing it.

## YouTube comparison video plan (8-10 minutes)

| Time | What to demonstrate |
|---|---|
| 0:00-0:45 | Introduce the assignment and explain the two databases |
| 0:45-2:00 | Explain PostgreSQL tables, primary key and foreign key |
| 2:00-3:15 | Run PostgreSQL version and create a project and task |
| 3:15-4:15 | Assign task, update status and filter tasks |
| 4:15-5:15 | Explain MongoDB collections and ObjectId references |
| 5:15-6:30 | Run MongoDB version and repeat the same API operations |
| 6:30-8:00 | Compare schema, relationships, queries and flexibility |
| 8:00-9:00 | Discuss scalability and development experience |
| 9:00-10:00 | Give your production database recommendation |

### Suggested video title

**PostgreSQL vs MongoDB | Same FastAPI Project Built Twice | Real Code Comparison**

### Suggested opening

"In this project, I have implemented the same Task and Project Management REST API using two different databases: PostgreSQL and MongoDB. Both applications support creating projects, creating and assigning tasks, updating task status, filtering and deleting tasks. Let's compare how the same business requirements are implemented differently and decide which database is better for production."

### Suggested closing

"After implementing both versions, I would select PostgreSQL for this application because Projects and Tasks have a structured one-to-many relationship, and referential integrity, transactions and SQL querying are important. MongoDB remains a strong alternative when the data structure is more flexible or document-oriented."

YouTube video URL: **Add your published video link here.**

## Production improvements (beyond assignment scope)

- Use Alembic for PostgreSQL schema migrations.
- Add authentication and role-based authorization.
- Replace free-text assignee with a Users table/collection and validate user IDs.
- Add pagination and sorting to task listing.
- Add automated tests with pytest and FastAPI TestClient.
- Add structured logging, monitoring, Docker and CI/CD.
- Configure secrets, TLS, backups and least-privilege database access.
- Consider indexes based on measured query patterns.
