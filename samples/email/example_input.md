# The Dev Digest — Issue #42 🚀

*Your weekly roundup of engineering updates, shipped features, and team highlights.*

---

## 👋 Welcome Back

Hello, team! Another sprint is in the books. This edition covers everything from our new infrastructure rollout and product releases to the learning resources we've discovered this week. Grab a coffee, settle in, and let's catch up.

---

## 🚢 Shipped This Week

### Feature: Real-Time Notifications

After months of iteration, **real-time push notifications** are now live for all users. This was a significant undertaking across four separate teams:

- **Backend:** Migrated from polling to a WebSocket-based architecture using Redis pub/sub.
- **iOS & Android:** Native push integration via APNs and FCM, achieving sub-200ms delivery latency.
- **Frontend:** Added a notification bell component with unread badge counts.
- **QA:** Ran 1,400+ automated test scenarios across device and browser combinations.

> "This was a true cross-functional effort. We went from 0 to production in 8 weeks." — *Maria L., Engineering Lead*

### Improvement: Database Query Optimisation

Our platform database was accumulating slow queries under peak load. The infrastructure team diagnosed and resolved the root causes:

1. Added composite indexes to the `user_events` table, reducing P99 latency from **1,400 ms** to **38 ms**.
2. Rewrote a critical reporting query to use window functions instead of correlated subqueries.
3. Enabled connection pooling via PgBouncer, cutting idle connection overhead by 60%.

---

## 🐛 Bugs Squashed

| Bug ID | Description | Severity | Status |
|--------|-------------|----------|--------|
| #2041 | Logout button unresponsive on Safari 16 | High | ✅ Fixed |
| #2089 | CSV export truncated for >10k rows | Medium | ✅ Fixed |
| #2103 | Avatar upload fails silently on slow connections | Medium | ✅ Fixed |
| #2118 | Timezone offset error in scheduled reports | Low | 🔄 In Review |

---

## 📊 Metrics Spotlight

Here are the numbers that made us smile this week:

- **Uptime:** 99.97% (SLA target: 99.9%)
- **Active Users (WAU):** 84,200 — up 12% week-over-week
- **API Response Time (P50):** 42 ms
- **Deployment Frequency:** 14 deploys across production environments
- **Error Rate:** 0.03% — the lowest on record 🎉

---

## 📚 Reading List

The team has been sharing some great articles in our `#eng-reads` Slack channel. Here are the top picks this week:

- [The Log: What every software engineer should know about real-time data](https://engineering.linkedin.com/distributed-systems/log-what-every-software-engineer-should-know-about-real-time-datas-unifying) — A classic distributed systems primer from LinkedIn Engineering.
- [An Illustrated Guide to OAuth and OpenID Connect](https://developer.okta.com/blog/2019/10/21/illustrated-guide-to-oauth-and-oidc) — Clear visuals for auth concepts that trip people up.
- [My Favourite PostgreSQL Extensions](https://www.crunchydata.com/blog/my-favorite-postgresql-extensions-part-two) — Handy extension round-up from Crunchy Data.

---

## 🧑‍💻 Spotlight: Onboarding Our New Engineers

We welcomed **three new engineers** to the team this sprint! Here's what they're working on in their first few weeks:

**Alex K.** — Joining the platform team. Already submitted a PR fixing a race condition in our job queue. 🔥

**Priya M.** — Embedded with the data team. Setting up her local development environment and contributing to the analytics pipeline.

**Tobias R.** — Working with the frontend guild on our design system migration from Bootstrap to Tailwind CSS.

*Please give them a warm welcome in `#introductions`!*

---

## 🗓️ Upcoming

- **Monday:** Sprint planning, 10:00 AM CEST
- **Wednesday:** Architecture review — Event-driven messaging proposal
- **Thursday:** All-hands company update (link in calendar invite)
- **Friday:** Optional: Lunch & Learn — "Intro to eBPF"

---

## 💬 Quote of the Week

> "The best code is no code at all. Every new line of code you willingly bring into the world is code that has to be debugged, code that has to be read and understood, code that has to be supported."
>
> — *Jeff Atwood, Co-founder of Stack Overflow*

---

*Thanks for reading The Dev Digest. Have something to share for next week? Drop it in `#newsletter` on Slack.*

*— The Engineering Team*
