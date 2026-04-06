import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from jinja2 import Template
from app.core.config import settings


class EmailService:
    """Service for sending email notifications"""

    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email using SMTP

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text fallback

        Returns:
            True if sent successfully
        """
        try:
            message = MIMEMultipart("alternative")
            message["From"] = settings.EMAIL_FROM
            message["To"] = to_email
            message["Subject"] = subject

            # Add plain text version
            if text_content:
                part1 = MIMEText(text_content, "plain")
                message.attach(part1)

            # Add HTML version
            part2 = MIMEText(html_content, "html")
            message.attach(part2)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=True,
            )

            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

    @staticmethod
    async def send_booking_created_email(
        craftsman_email: str,
        craftsman_name: str,
        homeowner_name: str,
        booking_title: str,
        booking_id: int,
        requested_date: str
    ):
        """Send email to craftsman when new booking is created"""
        subject = f"New Booking Request: {booking_title}"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2563eb;">New Booking Request</h2>
            <p>Hello {craftsman_name},</p>
            <p>You have received a new booking request from <strong>{homeowner_name}</strong>.</p>

            <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #1f2937;">Booking Details</h3>
                <p><strong>Job:</strong> {booking_title}</p>
                <p><strong>Requested Date:</strong> {requested_date}</p>
                <p><strong>Booking ID:</strong> #{booking_id}</p>
            </div>

            <p>Please log in to your account to review and respond to this booking request.</p>

            <a href="{settings.FRONTEND_URL}/bookings/{booking_id}"
               style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px;
                      text-decoration: none; border-radius: 6px; margin: 20px 0;">
                View Booking
            </a>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            <p style="color: #6b7280; font-size: 14px;">
                This is an automated notification from Handwerker Platform.<br>
                If you have any questions, please contact our support team.
            </p>
        </body>
        </html>
        """

        await EmailService.send_email(craftsman_email, subject, html_content)

    @staticmethod
    async def send_booking_accepted_email(
        homeowner_email: str,
        homeowner_name: str,
        craftsman_name: str,
        booking_title: str,
        booking_id: int,
        scheduled_date: str
    ):
        """Send email to homeowner when booking is accepted"""
        subject = f"Booking Accepted: {booking_title}"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #059669;">Booking Accepted!</h2>
            <p>Hello {homeowner_name},</p>
            <p>Great news! <strong>{craftsman_name}</strong> has accepted your booking request.</p>

            <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #1f2937;">Booking Details</h3>
                <p><strong>Job:</strong> {booking_title}</p>
                <p><strong>Scheduled Date:</strong> {scheduled_date}</p>
                <p><strong>Craftsman:</strong> {craftsman_name}</p>
                <p><strong>Booking ID:</strong> #{booking_id}</p>
            </div>

            <p>Please proceed with payment to confirm the booking.</p>

            <a href="{settings.FRONTEND_URL}/bookings/{booking_id}"
               style="display: inline-block; background-color: #059669; color: white; padding: 12px 24px;
                      text-decoration: none; border-radius: 6px; margin: 20px 0;">
                View Booking & Pay
            </a>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            <p style="color: #6b7280; font-size: 14px;">
                This is an automated notification from Handwerker Platform.
            </p>
        </body>
        </html>
        """

        await EmailService.send_email(homeowner_email, subject, html_content)

    @staticmethod
    async def send_booking_completed_email(
        homeowner_email: str,
        homeowner_name: str,
        craftsman_name: str,
        booking_title: str,
        booking_id: int,
        final_cost: float
    ):
        """Send email to homeowner when booking is completed"""
        subject = f"Job Completed: {booking_title}"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #059669;">Job Completed!</h2>
            <p>Hello {homeowner_name},</p>
            <p><strong>{craftsman_name}</strong> has marked your job as completed.</p>

            <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #1f2937;">Booking Summary</h3>
                <p><strong>Job:</strong> {booking_title}</p>
                <p><strong>Final Cost:</strong> €{final_cost:.2f}</p>
                <p><strong>Booking ID:</strong> #{booking_id}</p>
            </div>

            <p>We hope you're satisfied with the work! Please take a moment to leave a review.</p>

            <a href="{settings.FRONTEND_URL}/bookings/{booking_id}/review"
               style="display: inline-block; background-color: #f59e0b; color: white; padding: 12px 24px;
                      text-decoration: none; border-radius: 6px; margin: 20px 0;">
                Leave a Review
            </a>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            <p style="color: #6b7280; font-size: 14px;">
                This is an automated notification from Handwerker Platform.
            </p>
        </body>
        </html>
        """

        await EmailService.send_email(homeowner_email, subject, html_content)

    @staticmethod
    async def send_payment_confirmation_email(
        homeowner_email: str,
        homeowner_name: str,
        booking_title: str,
        amount: float,
        booking_id: int
    ):
        """Send payment confirmation email"""
        subject = f"Payment Confirmed: {booking_title}"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #059669;">Payment Confirmed</h2>
            <p>Hello {homeowner_name},</p>
            <p>Your payment has been successfully processed.</p>

            <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #1f2937;">Payment Details</h3>
                <p><strong>Job:</strong> {booking_title}</p>
                <p><strong>Amount Paid:</strong> €{amount:.2f}</p>
                <p><strong>Booking ID:</strong> #{booking_id}</p>
            </div>

            <p>The funds are held securely and will be released to the craftsman upon job completion.</p>

            <a href="{settings.FRONTEND_URL}/bookings/{booking_id}"
               style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px;
                      text-decoration: none; border-radius: 6px; margin: 20px 0;">
                View Booking
            </a>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            <p style="color: #6b7280; font-size: 14px;">
                This is an automated notification from Handwerker Platform.
            </p>
        </body>
        </html>
        """

        await EmailService.send_email(homeowner_email, subject, html_content)

    @staticmethod
    async def send_review_received_email(
        craftsman_email: str,
        craftsman_name: str,
        homeowner_name: str,
        rating: float,
        booking_title: str,
        review_id: int
    ):
        """Send email to craftsman when they receive a review"""
        subject = f"New Review Received: {rating}⭐"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #f59e0b;">New Review Received!</h2>
            <p>Hello {craftsman_name},</p>
            <p><strong>{homeowner_name}</strong> has left a review for your work on "{booking_title}".</p>

            <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #1f2937;">Rating</h3>
                <p style="font-size: 24px; color: #f59e0b; margin: 10px 0;">
                    {"⭐" * int(rating)} {rating}/5.0
                </p>
            </div>

            <p>Log in to view the full review and respond to your customer.</p>

            <a href="{settings.FRONTEND_URL}/reviews/{review_id}"
               style="display: inline-block; background-color: #f59e0b; color: white; padding: 12px 24px;
                      text-decoration: none; border-radius: 6px; margin: 20px 0;">
                View Review
            </a>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            <p style="color: #6b7280; font-size: 14px;">
                This is an automated notification from Handwerker Platform.
            </p>
        </body>
        </html>
        """

        await EmailService.send_email(craftsman_email, subject, html_content)

    @staticmethod
    async def send_welcome_email(
        user_email: str,
        user_name: str,
        user_role: str
    ):
        """Send welcome email to new users"""
        subject = "Welcome to Handwerker Platform!"

        if user_role == "homeowner":
            role_specific = """
            <p>As a homeowner, you can:</p>
            <ul>
                <li>Search for verified craftsmen in your area</li>
                <li>Book services online with transparent pricing</li>
                <li>Track job progress in real-time</li>
                <li>Pay securely through our platform</li>
                <li>Rate and review craftsmen after job completion</li>
            </ul>
            """
            cta_text = "Find Craftsmen"
            cta_link = f"{settings.FRONTEND_URL}/search"
        else:
            role_specific = """
            <p>As a craftsman, you can:</p>
            <ul>
                <li>Create your professional profile</li>
                <li>Receive booking requests from homeowners</li>
                <li>Manage your schedule and bookings</li>
                <li>Get paid automatically after job completion</li>
                <li>Build your reputation with customer reviews</li>
            </ul>
            """
            cta_text = "Complete Your Profile"
            cta_link = f"{settings.FRONTEND_URL}/profile"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h1 style="color: #2563eb;">Welcome to Handwerker Platform!</h1>
            <p>Hello {user_name},</p>
            <p>Thank you for joining Handwerker Platform - Germany's trusted marketplace for home services.</p>

            {role_specific}

            <a href="{cta_link}"
               style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px;
                      text-decoration: none; border-radius: 6px; margin: 20px 0;">
                {cta_text}
            </a>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            <p style="color: #6b7280; font-size: 14px;">
                Need help getting started? Visit our <a href="{settings.FRONTEND_URL}/help">Help Center</a><br>
                or contact us at support@handwerker-platform.de
            </p>
        </body>
        </html>
        """

        await EmailService.send_email(user_email, subject, html_content)

    @staticmethod
    async def send_verification_approved_email(
        craftsman_email: str,
        craftsman_name: str,
        company_name: Optional[str]
    ):
        """Send email when craftsman verification is approved"""
        subject = "Verification Approved - You're Now a Verified Craftsman!"

        display_name = company_name or craftsman_name

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #059669;">Congratulations! You're Verified! ✓</h2>
            <p>Hello {craftsman_name},</p>
            <p>Great news! Your documents have been reviewed and approved.</p>

            <div style="background-color: #d1fae5; padding: 20px; border-radius: 8px; border-left: 4px solid #059669; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #065f46;">
                    <strong>{display_name}</strong> is now a Verified Craftsman
                </h3>
                <p style="margin-bottom: 0;">
                    Your profile now displays a verified badge, giving customers confidence in your services.
                </p>
            </div>

            <p><strong>Benefits of being verified:</strong></p>
            <ul>
                <li>Increased visibility in search results</li>
                <li>Verified badge on your profile</li>
                <li>Higher customer trust and booking rates</li>
                <li>Access to premium features</li>
            </ul>

            <a href="{settings.FRONTEND_URL}/profile"
               style="display: inline-block; background-color: #059669; color: white; padding: 12px 24px;
                      text-decoration: none; border-radius: 6px; margin: 20px 0;">
                View Your Profile
            </a>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            <p style="color: #6b7280; font-size: 14px;">
                This is an automated notification from Handwerker Platform.
            </p>
        </body>
        </html>
        """

        await EmailService.send_email(craftsman_email, subject, html_content)
