import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from jinja2 import Template
from app.core.config import settings
from app.services.i18n_service import t


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
        requested_date: str,
        language: str = "de"
    ):
        """Send email to craftsman when new booking is created"""
        subject = t("email.booking_created_subject", language, title=booking_title)

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2563eb;">{t("notifications.booking_created_title", language)}</h2>
            <p>{t("common.hello", language)} {craftsman_name},</p>
            <p>{t("notifications.booking_created_message", language, homeowner_name=homeowner_name)}</p>

            <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #1f2937;">{t("booking.booking_details", language)}</h3>
                <p><strong>{t("booking.job_title", language)}:</strong> {booking_title}</p>
                <p><strong>{t("booking.requested_date", language)}:</strong> {requested_date}</p>
                <p><strong>ID:</strong> #{booking_id}</p>
            </div>

            <p>{t("email.login_to_review", language, lang=language)}</p>

            <a href="{settings.FRONTEND_URL}/bookings/{booking_id}"
               style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px;
                      text-decoration: none; border-radius: 6px; margin: 20px 0;">
                {t("email.view_booking", language)}
            </a>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            <p style="color: #6b7280; font-size: 14px;">
                {t("email.automated_notification", language)}<br>
                {t("email.contact_support_help", language, lang=language)}
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
        scheduled_date: str,
        language: str = "de"
    ):
        """Send email to homeowner when booking is accepted"""
        subject = t("email.booking_accepted_subject", language, title=booking_title)

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #059669;">{t("notifications.booking_accepted_title", language)}</h2>
            <p>{t("common.hello", language)} {homeowner_name},</p>
            <p>{t("email.great_news", language)} <strong>{craftsman_name}</strong> {t("email.has_accepted", language)}</p>

            <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #1f2937;">{t("booking.booking_details", language)}</h3>
                <p><strong>{t("booking.job_title", language)}:</strong> {booking_title}</p>
                <p><strong>{t("booking.scheduled_date", language)}:</strong> {scheduled_date}</p>
                <p><strong>{t("craftsman.profile", language)}:</strong> {craftsman_name}</p>
                <p><strong>ID:</strong> #{booking_id}</p>
            </div>

            <p>{t("email.proceed_with_payment", language)}</p>

            <a href="{settings.FRONTEND_URL}/bookings/{booking_id}"
               style="display: inline-block; background-color: #059669; color: white; padding: 12px 24px;
                      text-decoration: none; border-radius: 6px; margin: 20px 0;">
                {t("email.view_booking_and_pay", language)}
            </a>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            <p style="color: #6b7280; font-size: 14px;">
                {t("email.automated_notification", language)}
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
        final_cost: float,
        language: str = "de"
    ):
        """Send email to homeowner when booking is completed"""
        subject = t("email.booking_completed_subject", language, title=booking_title)

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #059669;">{t("notifications.booking_completed_title", language)}</h2>
            <p>{t("common.hello", language)} {homeowner_name},</p>
            <p><strong>{craftsman_name}</strong> {t("email.has_completed", language)}</p>

            <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #1f2937;">{t("booking.booking_details", language)}</h3>
                <p><strong>{t("booking.job_title", language)}:</strong> {booking_title}</p>
                <p><strong>{t("booking.final_cost", language)}:</strong> €{final_cost:.2f}</p>
                <p><strong>ID:</strong> #{booking_id}</p>
            </div>

            <p>{t("email.hope_satisfied", language)}</p>

            <a href="{settings.FRONTEND_URL}/bookings/{booking_id}/review"
               style="display: inline-block; background-color: #f59e0b; color: white; padding: 12px 24px;
                      text-decoration: none; border-radius: 6px; margin: 20px 0;">
                {t("email.leave_review", language)}
            </a>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            <p style="color: #6b7280; font-size: 14px;">
                {t("email.automated_notification", language)}
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
        booking_id: int,
        language: str = "de"
    ):
        """Send payment confirmation email"""
        subject = t("email.payment_confirmed_subject", language, title=booking_title)

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #059669;">{t("notifications.payment_confirmed_title", language)}</h2>
            <p>{t("common.hello", language)} {homeowner_name},</p>
            <p>{t("email.payment_processed", language)}</p>

            <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #1f2937;">{t("payment.payment", language)}</h3>
                <p><strong>{t("booking.job_title", language)}:</strong> {booking_title}</p>
                <p><strong>{t("payment.amount", language)}:</strong> €{amount:.2f}</p>
                <p><strong>ID:</strong> #{booking_id}</p>
            </div>

            <p>{t("email.funds_held_securely", language)}</p>

            <a href="{settings.FRONTEND_URL}/bookings/{booking_id}"
               style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px;
                      text-decoration: none; border-radius: 6px; margin: 20px 0;">
                {t("email.view_booking", language)}
            </a>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            <p style="color: #6b7280; font-size: 14px;">
                {t("email.automated_notification", language)}
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
        review_id: int,
        language: str = "de"
    ):
        """Send email to craftsman when they receive a review"""
        subject = t("email.review_received_subject", language, rating=rating)

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #f59e0b;">{t("notifications.review_received_title", language)}</h2>
            <p>{t("common.hello", language)} {craftsman_name},</p>
            <p><strong>{homeowner_name}</strong> {t("email.has_left_review", language, booking_title=booking_title)}</p>

            <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #1f2937;">{t("review.rating", language)}</h3>
                <p style="font-size: 24px; color: #f59e0b; margin: 10px 0;">
                    {"⭐" * int(rating)} {rating}/5.0
                </p>
            </div>

            <p>{t("email.view_full_review", language)}</p>

            <a href="{settings.FRONTEND_URL}/reviews/{review_id}"
               style="display: inline-block; background-color: #f59e0b; color: white; padding: 12px 24px;
                      text-decoration: none; border-radius: 6px; margin: 20px 0;">
                {t("email.view_review", language)}
            </a>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            <p style="color: #6b7280; font-size: 14px;">
                {t("email.automated_notification", language)}
            </p>
        </body>
        </html>
        """

        await EmailService.send_email(craftsman_email, subject, html_content)

    @staticmethod
    async def send_welcome_email(
        user_email: str,
        user_name: str,
        user_role: str,
        language: str = "de"
    ):
        """Send welcome email to new users"""
        subject = t("email.welcome_subject", language)

        if user_role == "homeowner":
            role_specific = f"""
            <p>{t("email.as_homeowner", language)}</p>
            <ul>
                <li>{t("email.find_verified_craftsmen", language)}</li>
                <li>{t("email.book_services_online", language)}</li>
                <li>{t("email.track_job_progress", language)}</li>
                <li>{t("email.pay_securely", language)}</li>
                <li>{t("email.rate_and_review", language)}</li>
            </ul>
            """
            cta_text = t("email.find_craftsmen_cta", language)
            cta_link = f"{settings.FRONTEND_URL}/search"
        else:
            role_specific = f"""
            <p>{t("email.as_craftsman", language)}</p>
            <ul>
                <li>{t("email.create_profile", language)}</li>
                <li>{t("email.receive_booking_requests", language)}</li>
                <li>{t("email.manage_schedule", language)}</li>
                <li>{t("email.get_paid_automatically", language)}</li>
                <li>{t("email.build_reputation", language)}</li>
            </ul>
            """
            cta_text = t("email.complete_profile", language)
            cta_link = f"{settings.FRONTEND_URL}/profile"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h1 style="color: #2563eb;">{subject}</h1>
            <p>{t("common.hello", language)} {user_name},</p>
            <p>{t("email.thank_you_joining", language)}</p>

            {role_specific}

            <a href="{cta_link}"
               style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px;
                      text-decoration: none; border-radius: 6px; margin: 20px 0;">
                {cta_text}
            </a>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            <p style="color: #6b7280; font-size: 14px;">
                {t("email.need_help", language)} <a href="{settings.FRONTEND_URL}/help">{t("email.help_center_link", language)}</a><br>
                {t("email.or_contact", language)} support@handwerker-platform.de
            </p>
        </body>
        </html>
        """

        await EmailService.send_email(user_email, subject, html_content)

    @staticmethod
    async def send_verification_approved_email(
        craftsman_email: str,
        craftsman_name: str,
        company_name: Optional[str],
        language: str = "de"
    ):
        """Send email when craftsman verification is approved"""
        subject = t("email.verification_approved_subject", language)

        display_name = company_name or craftsman_name

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #059669;">{t("notifications.verification_approved_title", language)} ✓</h2>
            <p>{t("common.hello", language)} {craftsman_name},</p>
            <p>{t("email.great_news", language)}</p>

            <div style="background-color: #d1fae5; padding: 20px; border-radius: 8px; border-left: 4px solid #059669; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #065f46;">
                    <strong>{display_name}</strong> {t("email.now_verified", language)}
                </h3>
                <p style="margin-bottom: 0;">
                    {t("email.verified_badge_info", language)}
                </p>
            </div>

            <p><strong>{t("email.benefits_verified", language)}</strong></p>
            <ul>
                <li>{t("email.increased_visibility", language)}</li>
                <li>{t("email.verified_badge", language)}</li>
                <li>{t("email.higher_trust", language)}</li>
                <li>{t("email.premium_features", language)}</li>
            </ul>

            <a href="{settings.FRONTEND_URL}/profile"
               style="display: inline-block; background-color: #059669; color: white; padding: 12px 24px;
                      text-decoration: none; border-radius: 6px; margin: 20px 0;">
                {t("email.view_profile", language)}
            </a>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            <p style="color: #6b7280; font-size: 14px;">
                {t("email.automated_notification", language)}
            </p>
        </body>
        </html>
        """

        await EmailService.send_email(craftsman_email, subject, html_content)
