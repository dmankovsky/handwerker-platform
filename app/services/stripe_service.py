import stripe
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.core.config import settings

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service for handling Stripe operations"""

    @staticmethod
    async def create_connected_account(
        email: str,
        country: str = "DE",
        business_type: str = "individual"
    ) -> Dict[str, Any]:
        """
        Create a Stripe Connect account for a craftsman

        Args:
            email: Craftsman's email
            country: Country code (default: DE for Germany)
            business_type: Type of business (individual or company)

        Returns:
            Dictionary with account_id
        """
        account = stripe.Account.create(
            type="express",
            country=country,
            email=email,
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
            business_type=business_type,
        )

        return {
            "account_id": account.id,
            "email": account.email,
            "type": account.type,
        }

    @staticmethod
    async def create_account_link(
        account_id: str,
        refresh_url: str,
        return_url: str
    ) -> Dict[str, Any]:
        """
        Create an account link for Stripe Connect onboarding

        Args:
            account_id: Stripe account ID
            refresh_url: URL to redirect if link expires
            return_url: URL to redirect after completion

        Returns:
            Dictionary with onboarding URL and expiration
        """
        account_link = stripe.AccountLink.create(
            account=account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type="account_onboarding",
        )

        return {
            "url": account_link.url,
            "expires_at": account_link.expires_at,
        }

    @staticmethod
    async def get_account_status(account_id: str) -> Dict[str, Any]:
        """
        Get the status of a Stripe Connect account

        Args:
            account_id: Stripe account ID

        Returns:
            Dictionary with account status information
        """
        account = stripe.Account.retrieve(account_id)

        return {
            "account_id": account.id,
            "charges_enabled": account.charges_enabled,
            "payouts_enabled": account.payouts_enabled,
            "details_submitted": account.details_submitted,
            "requirements": account.requirements,
            "email": account.email,
        }

    @staticmethod
    async def create_payment_intent(
        amount: float,
        currency: str = "eur",
        connected_account_id: Optional[str] = None,
        application_fee: Optional[float] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a payment intent for a booking

        Args:
            amount: Amount in currency units (e.g., euros)
            currency: Currency code (default: eur)
            connected_account_id: Craftsman's Stripe account ID
            application_fee: Platform fee amount
            metadata: Additional metadata

        Returns:
            Dictionary with payment intent details
        """
        # Convert to cents
        amount_cents = int(amount * 100)

        params = {
            "amount": amount_cents,
            "currency": currency,
            "automatic_payment_methods": {"enabled": True},
        }

        if metadata:
            params["metadata"] = metadata

        # If connected account specified, create payment on their behalf
        if connected_account_id:
            params["application_fee_amount"] = int(application_fee * 100) if application_fee else 0
            params["transfer_data"] = {"destination": connected_account_id}

        payment_intent = stripe.PaymentIntent.create(**params)

        return {
            "id": payment_intent.id,
            "client_secret": payment_intent.client_secret,
            "amount": amount,
            "currency": payment_intent.currency,
            "status": payment_intent.status,
        }

    @staticmethod
    async def confirm_payment_intent(payment_intent_id: str) -> Dict[str, Any]:
        """
        Confirm a payment intent

        Args:
            payment_intent_id: Stripe payment intent ID

        Returns:
            Dictionary with payment status
        """
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        return {
            "id": payment_intent.id,
            "status": payment_intent.status,
            "amount": payment_intent.amount / 100,
            "currency": payment_intent.currency,
        }

    @staticmethod
    async def create_transfer(
        amount: float,
        destination_account: str,
        currency: str = "eur",
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a transfer to a connected account

        Args:
            amount: Amount to transfer
            destination_account: Destination Stripe account ID
            currency: Currency code
            metadata: Additional metadata

        Returns:
            Dictionary with transfer details
        """
        transfer = stripe.Transfer.create(
            amount=int(amount * 100),
            currency=currency,
            destination=destination_account,
            metadata=metadata or {},
        )

        return {
            "id": transfer.id,
            "amount": transfer.amount / 100,
            "destination": transfer.destination,
            "created": datetime.fromtimestamp(transfer.created),
        }

    @staticmethod
    async def create_payout(
        account_id: str,
        amount: float,
        currency: str = "eur",
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a payout from a connected account to their bank

        Args:
            account_id: Stripe account ID
            amount: Amount to payout
            currency: Currency code
            metadata: Additional metadata

        Returns:
            Dictionary with payout details
        """
        payout = stripe.Payout.create(
            amount=int(amount * 100),
            currency=currency,
            metadata=metadata or {},
            stripe_account=account_id,
        )

        return {
            "id": payout.id,
            "amount": payout.amount / 100,
            "status": payout.status,
            "arrival_date": datetime.fromtimestamp(payout.arrival_date) if payout.arrival_date else None,
        }

    @staticmethod
    async def retrieve_balance(account_id: str) -> Dict[str, Any]:
        """
        Retrieve balance for a connected account

        Args:
            account_id: Stripe account ID

        Returns:
            Dictionary with balance information
        """
        balance = stripe.Balance.retrieve(stripe_account=account_id)

        available = sum(item["amount"] for item in balance.available) / 100
        pending = sum(item["amount"] for item in balance.pending) / 100

        return {
            "available": available,
            "pending": pending,
            "currency": balance.available[0]["currency"] if balance.available else "eur",
        }

    @staticmethod
    def construct_webhook_event(payload: bytes, sig_header: str) -> Any:
        """
        Construct and verify a Stripe webhook event

        Args:
            payload: Request body
            sig_header: Stripe signature header

        Returns:
            Stripe event object
        """
        return stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
