from django.db import connection
from django.core.mail import EmailMessage

def fetch_and_send_email():
    query = """
    SELECT 
        u.first_name AS student_first_name,
        u.last_name AS student_last_name,
        u.email AS student_email,
        p.title AS program_name,
        c.title AS course_name,
        c.timestamp AS assign_date
    FROM 
        elearn.accounts_student s
    JOIN 
        elearn.accounts_user u ON s.student_id = u.id
    JOIN 
        elearn.course_program p ON s.program_id = p.id
    JOIN 
        elearn.course_course c ON p.id = c.program_id
    WHERE 
        u.email = "emailers@aludecor.com"
    ORDER BY 
        u.first_name, u.last_name, p.title, c.title;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    if not rows:
        print("No data found for the email.")
        return

    # Extract recipient email from query results
    recipient_email = rows[0][2]
    print(f"Sending email to: {recipient_email}")

    # Format the email content as plain text
    email_body = "Program and Course Details:\n\n"
    for row in rows:
        email_body += (
            f"Student: {row[0]} {row[1]}\n"
            f"Program: {row[3]}\n"
            f"Course: {row[4]}\n"
            f"Assign Date: {row[5]}\n"
            "------------------------\n"
        )

    # Send the email
    subject = "Program and Course Details"
    from_email = ''
    to_email = [recipient_email]

    email = EmailMessage(subject, email_body, from_email, to_email)

    try:
        email.send()
        print(f"Email sent successfully to {recipient_email}")
    except Exception as e:
        print(f"Error sending email: {e}")
