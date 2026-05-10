# tools/send_email.py
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL     = os.getenv("SENDER_EMAIL")

def send_booking_confirmation(
    to_email:   str,
    name:       str,
    unit_id:    int,
    day:        str,
    time:       str,
    booking_id: int
) -> bool:
    """Send tour booking confirmation email via SendGrid."""
    message = Mail(
        from_email = SENDER_EMAIL,
        to_emails  = to_email,
        subject    = f"🏠 Tour Confirmed — Unit #{unit_id}",
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <div style="background: #3C3489; color: white; padding: 24px; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0; font-size: 24px;">🏠 Tour Confirmed!</h1>
          </div>
          <div style="background: #f9f9f9; padding: 24px; border-radius: 0 0 8px 8px;">
            <p style="font-size: 16px;">Hi <strong>{name}</strong>,</p>
            <p>Your property tour has been confirmed. Here are your details:</p>
            <div style="background: white; padding: 16px; border-radius: 8px; margin: 16px 0;
                        border-left: 4px solid #3C3489;">
              <p>📋 <strong>Booking ID:</strong> #{booking_id}</p>
              <p>🏢 <strong>Unit:</strong> #{unit_id}</p>
              <p>📅 <strong>Day:</strong> {day}</p>
              <p>🕐 <strong>Time:</strong> {time}</p>
            </div>
            <p>Please arrive 5 minutes early. If you need to reschedule, 
               reply to this email.</p>
            <p style="margin-top: 24px;">See you soon!<br>
               <strong>Property Management Team</strong></p>
          </div>
        </div>
        """
    )
    try:
        sg     = SendGridAPIClient(SENDGRID_API_KEY)
        result = sg.send(message)
        return result.status_code == 202
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_maintenance_confirmation(
    to_email:    str,
    name:        str,
    unit_id:     int,
    issue:       str,
    priority:    str,
    ticket_id:   int
) -> bool:
    """Send maintenance ticket confirmation email."""
    priority_colors = {
        "emergency": "#C0392B",
        "high":      "#E67E22",
        "medium":    "#F1C40F",
        "low":       "#1D9E75",
    }
    color = priority_colors.get(priority, "#999")

    message = Mail(
        from_email = SENDER_EMAIL,
        to_emails  = to_email,
        subject    = f"🔧 Maintenance Ticket #{ticket_id} Received",
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <div style="background: #085041; color: white; padding: 24px; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0; font-size: 24px;">🔧 Maintenance Request Received</h1>
          </div>
          <div style="background: #f9f9f9; padding: 24px; border-radius: 0 0 8px 8px;">
            <p style="font-size: 16px;">Hi <strong>{name}</strong>,</p>
            <p>We've received your maintenance request. Here are the details:</p>
            <div style="background: white; padding: 16px; border-radius: 8px; margin: 16px 0;
                        border-left: 4px solid #085041;">
              <p>🎫 <strong>Ticket ID:</strong> #{ticket_id}</p>
              <p>🏢 <strong>Unit:</strong> #{unit_id}</p>
              <p>🔧 <strong>Issue:</strong> {issue}</p>
              <p>⚡ <strong>Priority:</strong> 
                <span style="color: {color}; font-weight: bold;">
                  {priority.upper()}
                </span>
              </p>
            </div>
            <p>Our team will contact you shortly to arrange access.</p>
            <p style="margin-top: 24px;">Thank you for letting us know!<br>
               <strong>Property Management Team</strong></p>
          </div>
        </div>
        """
    )
    try:
        sg     = SendGridAPIClient(SENDGRID_API_KEY)
        result = sg.send(message)
        return result.status_code == 202
    except Exception as e:
        print(f"Email error: {e}")
        return False