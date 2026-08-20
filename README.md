# TeamSpace Portal

TeamSpace is a multi-role Django web application designed for enterprise internal communication and task management across Super Admins, Employees, Clients, and Customers.

---

## 🚀 Features

- **Role-Based Authentication**: Custom authentication backend supporting Username & Email login flows tailored to specific roles (`RoleBasedAuthBackend`).
- **Internal Messaging (Inbox, Drafts, Sent, Archive)**: Secure communication hub.
- **Task Management & Calendar**: Integrated workspace task tracking.
- **Team Chat & Real-time Notifications**: Internal messaging tools.
- **Dedicated Admin Control**: Direct system configuration panel for administrators.

---

## 🛠️ Project Structure

```text
teamspace/
├── custom_auth/         # Custom authentication backend & user roles
├── team_accounts/       # User profile and account management
├── team_chat/           # Real-time/Internal team messaging
├── team_mailbox/        # Internal mail system
├── team_tasks/          # Task management & calendar
├── team_notifications/  # Notification services
├── teamspace/           # Project settings & URL routing
├── templates/           # Global HTML templates
└── manage.py
