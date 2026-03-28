"""Google Ads API client for marketing agent system."""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.auth.exceptions import RefreshError

from ...core.config import settings


class GoogleAdsClientWrapper:
    """Wrapper for Google Ads API client with error handling and retry logic."""

    def __init__(self):
        self.client: Optional[GoogleAdsClient] = None
        self.logger = logging.getLogger("google_ads_client")
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Google Ads client with credentials."""
        try:
            config = {
                "developer_token": settings.GOOGLE_ADS_DEVELOPER_TOKEN,
                "client_id": settings.GOOGLE_ADS_CLIENT_ID,
                "client_secret": settings.GOOGLE_ADS_CLIENT_SECRET,
                "refresh_token": settings.GOOGLE_ADS_REFRESH_TOKEN,
                "use_proto_plus": True,
                "login_customer_id": settings.GOOGLE_ADS_CUSTOMER_ID,
            }

            self.client = GoogleAdsClient.load_from_dict(config)
            self.logger.info("Google Ads client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Ads client: {str(e)}")
            raise

    def validate_credentials(self) -> bool:
        """Validate Google Ads credentials."""
        try:
            if not self.client:
                return False

            # Try to get account summary to validate credentials
            customer_service = self.client.get_service("CustomerService")
            customer = customer_service.get_customer(
                resource_name=customer_service.customer_path(settings.GOOGLE_ADS_CUSTOMER_ID)
            )

            self.logger.info(f"Credentials validated for customer: {customer.descriptive_name}")
            return True
        except (GoogleAdsException, RefreshError) as e:
            self.logger.error(f"Credential validation failed: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during validation: {str(e)}")
            return False

    async def get_campaigns(self, customer_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all campaigns for a customer."""
        customer_id = customer_id or settings.GOOGLE_ADS_CUSTOMER_ID

        try:
            ga_service = self.client.get_service("GoogleAdsService")

            query = """
                SELECT
                  campaign.id,
                  campaign.name,
                  campaign.status,
                  campaign.advertising_channel_type,
                  campaign.start_date,
                  campaign.end_date,
                  campaign.budget,
                  metrics.impressions,
                  metrics.clicks,
                  metrics.cost_micros,
                  metrics.conversions
                FROM campaign
                ORDER BY campaign.id
            """

            stream = ga_service.search_stream(
                customer_id=customer_id,
                query=query
            )

            campaigns = []
            for batch in stream:
                for row in batch.results:
                    campaign = {
                        "id": row.campaign.id,
                        "name": row.campaign.name,
                        "status": row.campaign.status.name,
                        "channel_type": row.campaign.advertising_channel_type.name,
                        "start_date": row.campaign.start_date,
                        "end_date": row.campaign.end_date if row.campaign.end_date else None,
                        "budget": row.campaign.budget,
                        "metrics": {
                            "impressions": row.metrics.impressions if row.metrics.impressions else 0,
                            "clicks": row.metrics.clicks if row.metrics.clicks else 0,
                            "cost_micros": row.metrics.cost_micros if row.metrics.cost_micros else 0,
                            "conversions": row.metrics.conversions if row.metrics.conversions else 0,
                        }
                    }
                    campaigns.append(campaign)

            self.logger.info(f"Retrieved {len(campaigns)} campaigns for customer {customer_id}")
            return campaigns

        except GoogleAdsException as e:
            self.logger.error(f"Google Ads API error getting campaigns: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting campaigns: {str(e)}")
            raise

    async def create_campaign(self, customer_id: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new campaign."""
        try:
            campaign_service = self.client.get_service("CampaignService")
            campaign_budget_service = self.client.get_service("CampaignBudgetService")
            operation_service = self.client.get_service("GoogleAdsService")

            # Create budget operation
            budget_operation = self.client.get_type("CampaignBudgetOperation")
            budget = budget_operation.create
            budget.name = f"Budget for {campaign_data['name']}"
            budget.amount_micros = campaign_data.get("budget_micros", 10000000)  # Default 10 USD
            budget.delivery_method = campaign_data.get("delivery_method", "STANDARD")

            # Create campaign operation
            campaign_operation = self.client.get_type("CampaignOperation")
            campaign = campaign_operation.create
            campaign.name = campaign_data["name"]
            campaign.advertising_channel_type = campaign_data.get("channel_type", "SEARCH")

            if "start_date" in campaign_data:
                campaign.start_date = campaign_data["start_date"]
            else:
                campaign.start_date = datetime.now().strftime("%Y%m%d")

            if "end_date" in campaign_data:
                campaign.end_date = campaign_data["end_date"]

            campaign.status = campaign_data.get("status", "PAUSED")  # Start paused for review
            campaign.campaign_budget = budget_operation.create.resource_name

            # Add network settings
            network_settings = self.client.get_type("NetworkSettings")
            network_settings.target_google_search = True
            network_settings.target_search_network = True
            network_settings.target_content_network = False
            network_settings.target_partner_search_network = False
            campaign.network_settings = network_settings

            # Execute operations
            budget_response = campaign_budget_service.mutate_campaign_budgets(
                customer_id=customer_id,
                operations=[budget_operation]
            )

            campaign_response = campaign_service.mutate_campaigns(
                customer_id=customer_id,
                operations=[campaign_operation]
            )

            result = {
                "budget_id": budget_response.results[0].resource_name,
                "campaign_id": campaign_response.results[0].resource_name,
                "name": campaign_data["name"],
                "status": "created"
            }

            self.logger.info(f"Created campaign {campaign_data['name']} for customer {customer_id}")
            return result

        except GoogleAdsException as e:
            self.logger.error(f"Google Ads API error creating campaign: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating campaign: {str(e)}")
            raise

    async def update_campaign_budget(self, customer_id: str, campaign_id: str,
                                   new_budget_micros: int) -> bool:
        """Update campaign budget."""
        try:
            campaign_service = self.client.get_service("CampaignService")

            # Get current campaign
            query = f"""
                SELECT campaign.campaign_budget
                FROM campaign
                WHERE campaign.id = {campaign_id}
            """

            ga_service = self.client.get_service("GoogleAdsService")
            stream = ga_service.search_stream(customer_id=customer_id, query=query)

            budget_resource_name = None
            for batch in stream:
                for row in batch.results:
                    budget_resource_name = row.campaign.campaign_budget
                    break

            if not budget_resource_name:
                raise ValueError(f"Campaign {campaign_id} not found")

            # Update budget
            budget_service = self.client.get_service("CampaignBudgetService")
            budget_operation = self.client.get_type("CampaignBudgetOperation")
            budget = budget_operation.update
            budget.resource_name = budget_resource_name
            budget.amount_micros = new_budget_micros

            budget_service.mutate_campaign_budgets(
                customer_id=customer_id,
                operations=[budget_operation]
            )

            self.logger.info(f"Updated budget for campaign {campaign_id} to {new_budget_micros} micros")
            return True

        except GoogleAdsException as e:
            self.logger.error(f"Google Ads API error updating budget: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error updating budget: {str(e)}")
            raise

    async def get_keyword_ideas(self, customer_id: str, keyword_seed: List[str],
                              location_ids: Optional[List[str]] = None,
                              language_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get keyword ideas using Google Ads Keyword Planner."""
        try:
            keyword_plan_idea_service = self.client.get_service("KeywordPlanIdeaService")

            # Build request
            request = self.client.get_type("GenerateKeywordIdeasRequest")
            request.customer_id = customer_id
            request.keyword_seed.keywords.extend(keyword_seed)

            if location_ids:
                for location_id in location_ids:
                    location_info = self.client.get_type("LocationInfo")
                    location_info.geo_target_constant = f"geoTargetConstants/{location_id}"
                    request.geo_target_constants.append(location_info)

            if language_id:
                request.language = self.client.get_service("GoogleAdsService").language_constant_path(language_id)

            # Generate ideas
            ideas = keyword_plan_idea_service.generate_keyword_ideas(request=request)

            keyword_ideas = []
            for idea in ideas:
                keyword_data = {
                    "text": idea.text,
                    "avg_monthly_searches": idea.keyword_idea_metrics.avg_monthly_searches,
                    "competition": idea.keyword_idea_metrics.competition.name,
                    "competition_index": idea.keyword_idea_metrics.competition_index,
                    "low_top_of_page_bid_micros": idea.keyword_idea_metrics.low_top_of_page_bid_micros,
                    "high_top_of_page_bid_micros": idea.keyword_idea_metrics.high_top_of_page_bid_micros,
                }
                keyword_ideas.append(keyword_data)

            self.logger.info(f"Generated {len(keyword_ideas)} keyword ideas for seeds: {keyword_seed}")
            return keyword_ideas

        except GoogleAdsException as e:
            self.logger.error(f"Google Ads API error getting keyword ideas: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting keyword ideas: {str(e)}")
            raise

    async def get_campaign_performance(self, customer_id: str, campaign_id: str,
                                     start_date: str, end_date: str) -> Dict[str, Any]:
        """Get performance metrics for a campaign."""
        try:
            ga_service = self.client.get_service("GoogleAdsService")

            query = f"""
                SELECT
                  campaign.id,
                  campaign.name,
                  segments.date,
                  metrics.impressions,
                  metrics.clicks,
                  metrics.cost_micros,
                  metrics.conversions,
                  metrics.conversions_value,
                  metrics.ctr,
                  metrics.average_cpc,
                  metrics.all_conversions
                FROM campaign
                WHERE campaign.id = {campaign_id}
                AND segments.date >= '{start_date}'
                AND segments.date <= '{end_date}'
                ORDER BY segments.date
            """

            stream = ga_service.search_stream(
                customer_id=customer_id,
                query=query
            )

            daily_metrics = []
            total_metrics = {
                "impressions": 0,
                "clicks": 0,
                "cost_micros": 0,
                "conversions": 0,
                "conversions_value": 0,
                "all_conversions": 0
            }

            for batch in stream:
                for row in batch.results:
                    daily_data = {
                        "date": row.segments.date,
                        "impressions": row.metrics.impressions,
                        "clicks": row.metrics.clicks,
                        "cost_micros": row.metrics.cost_micros,
                        "conversions": row.metrics.conversions,
                        "conversions_value": row.metrics.conversions_value,
                        "ctr": row.metrics.ctr,
                        "average_cpc": row.metrics.average_cpc,
                        "all_conversions": row.metrics.all_conversions
                    }
                    daily_metrics.append(daily_data)

                    # Accumulate totals
                    total_metrics["impressions"] += row.metrics.impressions
                    total_metrics["clicks"] += row.metrics.clicks
                    total_metrics["cost_micros"] += row.metrics.cost_micros
                    total_metrics["conversions"] += row.metrics.conversions
                    total_metrics["conversions_value"] += row.metrics.conversions_value
                    total_metrics["all_conversions"] += row.metrics.all_conversions

            result = {
                "campaign_id": campaign_id,
                "date_range": {"start": start_date, "end": end_date},
                "daily_metrics": daily_metrics,
                "total_metrics": total_metrics,
                "summary": {
                    "ctr": total_metrics["clicks"] / total_metrics["impressions"] if total_metrics["impressions"] > 0 else 0,
                    "average_cpc": total_metrics["cost_micros"] / total_metrics["clicks"] if total_metrics["clicks"] > 0 else 0,
                    "conversion_rate": total_metrics["conversions"] / total_metrics["clicks"] if total_metrics["clicks"] > 0 else 0,
                    "roas": total_metrics["conversions_value"] / (total_metrics["cost_micros"] / 1000000) if total_metrics["cost_micros"] > 0 else 0,
                }
            }

            self.logger.info(f"Retrieved performance for campaign {campaign_id}")
            return result

        except GoogleAdsException as e:
            self.logger.error(f"Google Ads API error getting performance: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error getting performance: {str(e)}")
            raise