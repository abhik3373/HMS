# Mini Hospital Management System (HMS)

A robust, production-ready Mini Hospital Management System built with Django, PostgreSQL, and AWS Lambda (via Serverless Framework). This application facilitates doctor availability management, patient appointment booking, Google Calendar integration, and a background serverless email notification service.

## 🌟 Key Features

### 🧑‍⚕️ For Doctors
* **Custom Dashboard:** Track upcoming, booked, and past appointments.
* **Slot Management:** Create, edit, and delete availability time slots.
* **Google Calendar Sync:** Connect Google Calendar to automatically sync booked appointments.
* **Email Notifications:** Receive welcome emails and instant booking confirmations.

### 🤒 For Patients
* **Custom Dashboard:** View history of booked appointments and status.
* **Doctor Discovery:** Browse available doctors and their free time slots.
* **Seamless Booking:** Safely book appointments with built-in race-condition prevention (`select_for_update`).
* **Google Sync:** Add appointments directly to Google Calendar.
* **Email Notifications:** Receive welcome emails and booking confirmations.

## 🏗️ Architecture & Tech Stack

* **Backend:** Django 5.x
* **Database:** PostgreSQL (with Django ORM)
* **Authentication:** Session-based (Custom User Model for Doctors/Patients)
* **Email Service:** AWS Lambda (simulated locally via `serverless-offline`), Node.js/Python handler
* **Integrations:** Google Calendar API (OAuth2)
* **UI/UX:** Custom Vanilla CSS with responsive, dark-mode premium design.

---

## 🚀 Getting Started

Follow these steps to set up the project locally.

### Prerequisites
* Python 3.10+
* Node.js & npm (for Serverless framework)
* PostgreSQL installed and running
* Google Cloud Console account (for Calendar API credentials)

### 1. Backend Setup (Django)

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd HMS
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the `HMS` root directory and add your credentials:
   ```ini
   SECRET_KEY=your-django-secret-key
   DB_NAME=hms_db
   DB_USER=hms_user
   DB_PASSWORD=hms1234
   DB_HOST=localhost
   DB_PORT=5432
   
   # Google API
   GOOGLE_CLIENT_ID=your_client_id
   GOOGLE_CLIENT_SECRET=your_client_secret
   ```
   *Also, ensure you place your Google `credentials.json` file in the project root.*

5. **Database Setup:**
   Create the database in PostgreSQL, then run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a Superuser (Admin):**
   ```bash
   python manage.py createsuperuser
   ```

### 2. Serverless Email Service Setup

1. **Navigate to the serverless directory:**
   ```bash
   cd serverless-email
   ```

2. **Install Node dependencies:**
   ```bash
   npm install serverless@3 serverless-offline --save-dev
   ```

3. **Environment Setup:**
   Create a `.env` file inside `serverless-email/`:
   ```ini
   SMTP_USER=your_gmail@gmail.com
   SMTP_PASS=your_gmail_app_password
   ```

---

## 🏃‍♂️ Running the Application

To run the full flow, you need **two terminals** running simultaneously.

**Terminal 1: Start Django Server**
```bash
cd HMS
python manage.py runserver
```
*App will run at `http://localhost:8000`*

**Terminal 2: Start Serverless Email Service**
```bash
cd serverless-email
npx serverless offline
```
*Email service will listen on `http://localhost:4000`*

---

## 🔒 Handling Race Conditions
This application solves the classic double-booking problem. When a patient attempts to book a slot, the system uses database-level locking:
```python
with transaction.atomic():
    slot = AvailabilitySlot.objects.select_for_update().get(pk=slot_id)
    if slot.is_booked:
        return error()
    slot.is_booked = True
    slot.save()
```
This ensures that even if two patients click "Book" at the exact same millisecond, only one will succeed, and the other will be gracefully informed that the slot was taken.

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!

## 📝 License
This project is open-source and available under the MIT License.
