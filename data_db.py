from uuid import UUID
from datetime import datetime, timedelta

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
    obj = session.query(model).filter_by(**kwargs).first()  # look for an existing row matching the given unique fields (kwargs)
    if obj:                                                # if a row is found
        return obj, False                                   # return it and flag that nothing was created
    params = dict(**kwargs)                                 # start building creation params from the match fields
    if defaults:                                            # if there are extra fields to set on creation
        params.update(defaults)                             # merge defaults into the params
    obj = model(**params)                                   # instantiate the ORM object with all params
    session.add(obj)                                        # stage it for insertion in the current transaction
    session.flush()                                         # push to DB to assign PK/UUID without committing
    return obj, True                                        # return the new object and flag that we created it


def main():
    """Seed 4–5 rows per table and wire valid FKs/M2M links for quick end-to-end testing."""
    db = SessionLocal()                                                     # open a new SQLAlchemy session
    try:                                                                    # ensure we close the session even if errors happen
        dept_map = {}                                                       # hold Department objects by name for FK wiring
        for name in DEPARTMENTS:                                            # iterate each department name
            d, _ = get_or_create(db, dbm.Department, name=name)             # get existing or create new Department
            dept_map[name] = d                                              # store the Department object keyed by name

        role_map = {}                                                       # hold Role objects keyed by (dept, role)
        for dept_name, role_names in ROLES.items():                         # iterate department→roles mapping
            for rname in role_names:                                        # iterate each role in the department
                r, _ = get_or_create(                                       # get or create Role row
                    db,
                    dbm.Role,
                    name=rname,                                             # role name (part of unique constraint per dept)
                    department_id=dept_map[dept_name].id,                   # FK: tie role to its department
                )
                role_map[(dept_name, rname)] = r                            # store Role object for later lookup

        user_map = {}                                                       # hold User objects keyed by email
        for first, last, email, dept_name, role_name, _mgr in USERS:        # iterate seed users (manager handled later)
            u, _ = get_or_create(                                           # get or create User row
                db,
                dbm.User,
                first_name=first,                                           # set first name
                last_name=last,                                             # set last name (nullable allowed)
                email=email,                                                # unique email constraint
                department_id=dept_map[dept_name].id,                       # FK to chosen department
                role_id=role_map[(dept_name, role_name)].id,                # FK to chosen role (tied to dept)
            )
            user_map[email] = u                                             # store User object keyed by email

        for first, last, email, dept_name, role_name, mgr_email in USERS:   # second pass to wire managers
            if mgr_email:                                                   # if a manager email is specified
                user_map[email].reports_to = user_map[mgr_email].id         # set self-referential FK to manager’s user id

        tag_map = {}                                                        # hold Tag objects keyed by name
        for name in TAGS:                                                   # iterate tag names
            t, _ = get_or_create(db, dbm.Tag, name=name)                    # get or create Tag row
            tag_map[name] = t                                               # store Tag object keyed by name

        db.commit()                                                         # commit depts/roles/users/tags so IDs are durable

        for (title, desc, status, priority, due_in_days,
             creator_email, tag_names, assignee_emails) in TASKS:           # iterate seed tasks definition
            creator = user_map[creator_email]                               # find the creator User object by email
            due_at = datetime.utcnow() + timedelta(days=due_in_days)        # compute due_at by adding offset to now

            task = dbm.Task(                                                # build a Task ORM object (not yet saved)
                title=title,                                                # task title
                description=desc,                                           # task description (nullable)
                status=dbm.TaskStatus(status),                              # coerce string to enum (TaskStatus)
                priority=dbm.TaskPriority(priority),                        # coerce string to enum (TaskPriority)
                due_at=due_at,                                              # computed due timestamp
                created_by=creator.id,                                      # FK to users.id (creator)
            )
            if tag_names:                                                   # if any tags should be attached
                task.tags = [tag_map[n] for n in tag_names]                 # attach Tag objects via M2M relationship
            if assignee_emails:                                             # if any assignees should be attached
                task.assignees = [user_map[e] for e in assignee_emails]     # attach User objects via M2M relationship

            db.add(task)                                                    # stage the Task for insertion

        db.commit()                                                         # commit all tasks + join table rows

        print("Seed complete ✅")                                           # simple progress message
        print("Departments:", db.query(dbm.Department).count())             # count departments to verify inserts
        print("Roles:", db.query(dbm.Role).count())                         # count roles
        print("Users:", db.query(dbm.User).count())                         # count users
        print("Tags:", db.query(dbm.Tag).count())                           # count tags
        print("Tasks:", db.query(dbm.Task).count())                         # count tasks
        print("TaskAssignees:", db.query(dbm.TaskAssignee).count())         # count M2M rows for assignments
        print("TaskTags:", db.query(dbm.TaskTag).count())                   # count M2M rows for task↔tag

        print("\nSample IDs:")                                              # convenience block to copy useful UUIDs
        for email, u in user_map.items():                                   # iterate users we created
            print(f"User {email}: {u.id}")                                  # show user UUIDs
        for name, t in tag_map.items():                                     # iterate tags we created
            print(f"Tag {name}: {t.id}")                                    # show tag UUIDs

    finally:                                                                # always clean up session
        db.close()                                                          # close the session/connection to the DB


if __name__ == "__main__":
    main()