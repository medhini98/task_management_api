# data_db.py
from datetime import datetime, timedelta, timezone
from app_db.database import SessionLocal
from app_db import models as dbm

# ---- helper data ----
DEPARTMENTS = ["Engineering", "Product", "Design", "Data"]
ROLES = {
    "Engineering": ["Developer", "DevOps"],
    "Product": ["PM"],
    "Design": ["UX Designer"],
    "Data": ["Data Scientist"],
}
USERS = [
    # first_name, last_name, email, dept, role, reports_to_email (or None)
    ("Medhini", "Sridharr", "medhini@example.com", "Engineering", "Developer", None),
    ("Aarav", "Khan", "aarav.khan@example.com", "Engineering", "DevOps", "medhini@example.com"),
    ("Isha", "Patel", "isha.patel@example.com", "Product", "PM", None),
    ("Ravi", "Menon", "ravi.menon@example.com", "Data", "Data Scientist", "isha.patel@example.com"),
    ("Anya", "Roy", "anya.roy@example.com", "Design", "UX Designer", "isha.patel@example.com"),
]
TAGS = ["backend", "bug", "customer-A", "ux", "research"]

TASKS = [
    # title, description, status, priority, due_days_from_now, created_by_email, tag_names, assignee_emails
    ("Build auth module", "Implement JWT-based auth with refresh tokens.",
     "in_progress", "high", 7, "medhini@example.com",
     ["backend"], ["medhini@example.com", "aarav.khan@example.com"]),
    ("Fix login bug", "Users get 500 on Safari – investigate and patch.",
     "todo", "urgent", 2, "medhini@example.com",
     ["bug", "customer-A"], ["aarav.khan@example.com"]),
    ("Usability test – onboarding", "Run 5 user sessions for new onboarding flow.",
     "blocked", "normal", 10, "isha.patel@example.com",
     ["ux"], ["anya.roy@example.com"]),
    ("Churn analysis MVP", "Baseline churn model; set up cohort tables.",
     "in_progress", "high", 14, "isha.patel@example.com",
     ["research"], ["ravi.menon@example.com"]),
    ("Groom Q4 backlog", "Prioritize epics and align dependencies.",
     "todo", "low", 21, "isha.patel@example.com",
     [], ["medhini@example.com", "isha.patel@example.com"]),
]

def get_or_create(session, model, defaults=None, **kwargs):
    """Return an existing row that matches kwargs, or create it with defaults+kwargs."""
    obj = session.query(model).filter_by(**kwargs).first()
    if obj:
        return obj, False
    params = dict(**kwargs)
    if defaults:
        params.update(defaults)
    obj = model(**params)
    session.add(obj)
    session.flush()  # assign PK/UUID
    return obj, True

def main():
    """Seed a compact dataset and wire FKs/M2M for quick E2E tests."""
    db = SessionLocal()
    try:
        # Departments
        dept_map = {}
        for name in DEPARTMENTS:
            d, _ = get_or_create(db, dbm.Department, name=name)
            dept_map[name] = d

        # Roles
        role_map = {}
        for dept_name, role_names in ROLES.items():
            for rname in role_names:
                r, _ = get_or_create(
                    db, dbm.Role,
                    name=rname,
                    department_id=dept_map[dept_name].id,
                )
                role_map[(dept_name, rname)] = r

        # Users (first pass)
        user_map = {}
        for first, last, email, dept_name, role_name, _mgr in USERS:
            u, _ = get_or_create(
                db, dbm.User,
                first_name=first,
                last_name=last,
                email=email,
                department_id=dept_map[dept_name].id,
                role_id=role_map[(dept_name, role_name)].id,
            )
            user_map[email] = u

        # Users (second pass: set manager FK)
        for _first, _last, email, _dept_name, _role_name, mgr_email in USERS:
            if mgr_email:
                user_map[email].reports_to = user_map[mgr_email].id

        # Tags
        tag_map = {}
        for name in TAGS:
            t, _ = get_or_create(db, dbm.Tag, name=name)
            tag_map[name] = t

        db.commit()  # persist so IDs are durable

        # Tasks
        for (title, desc, status, priority, due_in_days,
             creator_email, tag_names, assignee_emails) in TASKS:
            creator = user_map[creator_email]
            due_at = datetime.now(timezone.utc) + timedelta(days=due_in_days)

            task = dbm.Task(
                title=title,
                description=desc,
                status=dbm.TaskStatus(status),
                priority=dbm.TaskPriority(priority),
                due_at=due_at,
                created_by=creator.id,
            )
            if tag_names:
                task.tags = [tag_map[n] for n in tag_names]
            if assignee_emails:
                task.assignees = [user_map[e] for e in assignee_emails]

            db.add(task)

        db.commit()

        print("Seed complete ✅")
        print("Departments:", db.query(dbm.Department).count())
        print("Roles:", db.query(dbm.Role).count())
        print("Users:", db.query(dbm.User).count())
        print("Tags:", db.query(dbm.Tag).count())
        print("Tasks:", db.query(dbm.Task).count())
        print("TaskAssignees:", db.query(dbm.TaskAssignee).count())
        print("TaskTags:", db.query(dbm.TaskTag).count())

        print("\nSample IDs:")
        for email, u in user_map.items():
            print(f"User {email}: {u.id}")
        for name, t in tag_map.items():
            print(f"Tag {name}: {t.id}")

    finally:
        db.close()

if __name__ == "__main__":
    main()