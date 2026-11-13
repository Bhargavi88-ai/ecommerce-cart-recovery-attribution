import json
from typing import Dict, Any, Optional


class CampaignPersonalizationEngine:
    """Renders personalized message subjects and bodies using customer & cart context."""

    @staticmethod
    def render_template(
        template_body: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Replaces variables like {{first_name}}, {{product_name}}, {{cart_value}}, 
        {{cart_recovery_url}}, {{campaign_offer}}
        """
        result = template_body
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result

    @staticmethod
    def build_personalization_context(
        first_name: str,
        product_name: str,
        cart_value: float,
        cart_id: str,
        discount_percent: float = 0.0
    ) -> Dict[str, Any]:
        offer_str = f"{int(discount_percent)}% OFF" if discount_percent > 0 else "Free Shipping"
        recovery_url = f"https://shop.example.com/checkout/recover?cart_id={cart_id}"
        return {
            "first_name": first_name,
            "product_name": product_name,
            "cart_value": f"${cart_value:.2f}",
            "cart_id": cart_id,
            "cart_recovery_url": recovery_url,
            "campaign_offer": offer_str,
        }

