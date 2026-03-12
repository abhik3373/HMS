# HMS Project Report and Architecture Documentation

## 1. Project Overview
The Mini Hospital Management System (HMS) is a web-based application designed to bridge the gap between healthcare professionals (Doctors) and patients. It streamlines appointment management by enabling doctors to set their availability, and patients to seamlessly view and book these time slots.

**Key Objectives:**
- Prevent double-booking (race conditions) during concurrent booking attempts.
- Notify actors instantly via email and calendar sync upon successful appointments.
- Separate core responsibilities (Web Application vs Background Services) mimicking enterprise architectures.

---

## 2. System Architecture

The project employs a **Service-Oriented Architecture (SOA)** approach:

### 2.1 The Core Django Monolith (`hms_project/`)
The main backend is structured into domain-driven Django applications:
* **Accounts (`accounts/`)**: Manages the custom `User` model, extending Django's default `AbstractUser` with a `role` field ('doctor' vs 'patient') and OAuth tokens (`google_token`).
* **Doctors (`doctors/`)**: Manages `AvailabilitySlot` models where doctors define their working hours.
* **Patients (`patients/`)**: Manages `Appointment` records. Implements the core transaction logic for slot booking.
* **Core (`core/`)**: Houses cross-cutting concerns (decorators for role-based access control, the email service caller, and Google Calendar helper).

### 2.2 The Serverless Email Service (`serverless-email/`)
To decouple email delivery from the main request-response cycle, email notifications are handled by a separate microservice:
* Built with **AWS Lambda / Serverless Framework** (running locally via `serverless-offline`).
* Receives a JSON payload via an HTTP POST request.
* Renders email templates (e.g., `SIGNUP_WELCOME`, `BOOKING_CONFIRMATION`).
* Dispatches SMTP emails via `smtp.gmail.com` using app passwords.

---

## 3. Database Design

We use **PostgreSQL** for data integrity and ACID compliance, which is vital for transactional booking.

### **Entity-Relationship Overview:**

1. **User (Custom)**
   - Fields: `username`, `email`, `role`, `google_token`
   - Role determines what dashboards and actions the user can access.

2. **AvailabilitySlot**
   - Fields: `doctor` (FK to User), `date`, `start_time`, `end_time`, `is_booked` (Boolean)
   - *Constraint:* A `unique_together` constraint on `doctor`, `date`, `start_time`, `end_time` prevents the creation of duplicate availability records for a single doctor.

3. **Appointment**
   - Fields: `patient` (FK to User), `slot` (OneToOneField to AvailabilitySlot), `status`, `doctor_calendar_event_id`, `patient_calendar_event_id`
   - *Constraint:* The `OneToOneField` ensures that a single `AvailabilitySlot` can only ever be attached to ONE `Appointment`. This is a database-level safeguard against double-booking.

---

## 4. Key Workflows and Pipelines

### 4.1. Authentication Pipeline
- **Method:** Session-based authentication via Django's auth middleware.
- **Workflow:** Users hit the unified `/accounts/login/` page. Upon successful auth, they are redirected automatically based on their mapped role (Role-based AC). `is_doctor` and `is_patient` decorators intercept unauthorized traffic.

### 4.2. Slot Booking Pipeline (The Critical Path)
The most sensitive operation in the application is the `book_slot` view.
It assumes a scenario where 10 patients attempt to click "Book" on the exact same second.

**The Solution:**
```python
with transaction.atomic():
    slot = AvailabilitySlot.objects.select_for_update().get(pk=slot_id)
    if slot.is_booked:
        # Race condition caught: The first request locked the row and marked it booked.
        # This request arrived second and is safely rejected.
        return error()
    slot.is_booked = True
    slot.save()
    Appointment.objects.create(...)
```
- **`select_for_update()`**: Tells the PostgreSQL database to apply an exclusive database row-level lock. The first request locks the row. Immediate concurrent requests hit a wall and must wait until the first transaction finishes. Once unlocked, the second request reads the updated `is_booked=True` state, gracefully failing.

### 4.3. Third-Party Integrations Pipeline
To avoid hanging the `POST /book/` request (which would ruin the UX), third party integrations fire in background threads immediately after the database transaction concludes safely.

**A. Google Calendar Sync (`core/calendar_helper.py`)**
- A thread retrieves the stored `google_token` for the appropriate user.
- Re-constructs Google API credentials.
- Injects a new `.insert()` event payload containing patient and doctor details.
- Captures the generated Event IDs and saves them back to the `Appointment`.

**B. Email Notification Sync (`core/email_service.py`)**
- A thread executes a `requests.post()` call to the `serverless-offline` Lambda API endpoint.
- If the endpoint is down or times out (configured to 10 seconds), the parent request is entirely unaffected, catching the error and failing gracefully.

---

## 5. UI/UX and Asset Architecture
- **Vanilla CSS:** To avoid bloat and demonstrate deep knowledge of the DOM, no complex frameworks (like Tailwind/Bootstrap) were used. Variables (`var(--primary)`, `var(--bg-card)`) control a premium, responsive dark-mode theme across all apps.
- **Feedback Loops:** `messages.success` and `messages.error` popups guide users seamlessly.
- **Animations:** Subtle pop-in scale transforms give modern flair to the booking confirmation interfaces.

---

## 6. Security Considerations
- CSRF Protection enabled globally across all POST forms.
- Data Validation: The `AvailabilityForm` strictly prohibits creating slots in the past, or end times before start times.
- Token Storage: External API credentials (Google OAuth JSON) are stored physically outside the version-controlled codebase, keeping secrets out of git.

## 7. Future Enhancements
Given more time, the next phases would include:
1. Paginating the Doctor/Slot lists using AJAX.
2. Integrating a task queue like `Celery` with Redis instead of native Python `threading` to ensure message delivery if the parent pod dies.
3. Implementing caching for static assets and doctor lists to enhance performance times further.
