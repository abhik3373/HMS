import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


TEMPLATES = {
    'SIGNUP_WELCOME': {
        'subject': 'Welcome to HMS! 🏥',
        'body': lambda data: f"""
Hi {data.get('name', 'User')},

Welcome to the Hospital Management System!

Your account has been created successfully as a {data.get('role', 'user')}.

{'You can now set your availability slots for patients to book.' if data.get('role') == 'Doctor' else 'You can now browse doctors and book appointments.'}

Best regards,
HMS Team
""",
    },
    'BOOKING_CONFIRMATION': {
        'subject': 'Appointment Confirmed ✅',
        'body': lambda data: f"""
Hi {data.get('recipient_name', 'User')},

Your appointment has been confirmed!

📋 Appointment Details:
   Doctor: Dr. {data.get('doctor_name', 'N/A')}
   Patient: {data.get('patient_name', 'N/A')}
   Date: {data.get('date', 'N/A')}
   Time: {data.get('start_time', 'N/A')} - {data.get('end_time', 'N/A')}

Please be on time for your appointment.

Best regards,
HMS Team
""",
    },
}


def send_email(event, context):
    """AWS Lambda handler to send emails via SMTP."""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        action = body.get('action')
        to_email = body.get('to_email')
        data = body.get('data', {})

        # Validate
        if not action or not to_email:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Missing required fields: action, to_email'})
            }

        if action not in TEMPLATES:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': f'Unknown action: {action}. Supported: {list(TEMPLATES.keys())}'})
            }

        # Build email
        template = TEMPLATES[action]
        subject = template['subject']
        message_body = template['body'](data)

        msg = MIMEMultipart()
        msg['From'] = os.environ.get('FROM_EMAIL', 'noreply@hms.com')
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message_body, 'plain'))

        # Send via SMTP
        smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        smtp_user = os.environ.get('SMTP_USER', '')
        smtp_pass = os.environ.get('SMTP_PASS', '')

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(msg['From'], to_email, msg.as_string())

        print(f"[EMAIL SENT] Action: {action} | To: {to_email}")

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'message': 'Email sent successfully',
                'action': action,
                'to': to_email
            })
        }

    except Exception as e:
        print(f"[EMAIL ERROR] {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
