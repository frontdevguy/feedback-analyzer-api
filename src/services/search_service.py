from opensearchpy import OpenSearch
from src.utils.logger import get_logger
from config import get_config

logger = get_logger(__name__)


class SearchService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SearchService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize OpenSearch client with configuration."""
        config = get_config()
        self.opensearch_client = OpenSearch(
            hosts=[config["OPENSEARCH_ENDPOINT"]],
            http_auth=(config["OPENSEARCH_USERNAME"], config["OPENSEARCH_PASSWORD"]),
            use_ssl=True,
            verify_certs=True,
        )
        self.feedback_analysis_index = "feedback-analysis"

    def _get_dashboard_query(self):
        """Return the OpenSearch query for dashboard statistics."""
        return {
            "size": 0,
            "aggs": {
                "total_documents": {"value_count": {"field": "feedback_id"}},
                "sentiment_breakdown": {"terms": {"field": "sentiment"}},
                "top_topics": {"terms": {"field": "topics", "size": 10}},
            },
        }

    def _get_default_stats(self):
        """Return default statistics structure with zero values."""
        return {
            "num_messages": 0,
            "num_positive_messages": 0,
            "num_negative_messages": 0,
            "num_neutral_messages": 0,
            "top_topics": [],
        }

    def get_dashboard_statistics(self) -> dict:
        """
        Get statistics about documents in the feedback analysis index.
        Returns counts for total documents, sentiment breakdowns, and top topics.
        """
        try:
            response = self.opensearch_client.search(
                index=self.feedback_analysis_index, body=self._get_dashboard_query()
            )

            aggregations = response.get("aggregations", {})

            # Get total documents count
            total_docs = aggregations.get("total_documents", {}).get("value", 0)

            # Process sentiment counts
            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
            sentiment_buckets = aggregations.get("sentiment_breakdown", {}).get(
                "buckets", []
            )
            for bucket in sentiment_buckets:
                sentiment = bucket["key"].lower()
                if sentiment in sentiment_counts:
                    sentiment_counts[sentiment] = bucket["doc_count"]

            # Process top topics
            top_topics = [
                {"topic": bucket["key"], "count": bucket["doc_count"]}
                for bucket in aggregations.get("top_topics", {}).get("buckets", [])
            ]

            return {
                "num_messages": total_docs,
                "num_positive_messages": sentiment_counts["positive"],
                "num_negative_messages": sentiment_counts["negative"],
                "num_neutral_messages": sentiment_counts["neutral"],
                "top_topics": top_topics,
            }

        except Exception as e:
            logger.error(f"Error fetching OpenSearch statistics: {str(e)}")
            return self._get_default_stats()

    def _get_messages_query(self, page: int = 0, page_size: int = 100):
        """
        Return the OpenSearch query for fetching messages with pagination.

        Args:
            page: Page number (0-based)
            page_size: Number of items per page
        """
        return {
            "size": page_size,
            "from": page * page_size,
            "query": {"match_all": {}},
            "sort": [{"feedback_id": {"order": "desc"}}],
            "_source": [
                "feedback_id",
                "feedback_text",
                "sentiment",
                "topics",
                "product_name",
                "media_urls",
            ],
        }

    def get_dashboard_messages(self, page: int = 0, page_size: int = 100) -> dict:
        """
        Get messages from the feedback analysis index with pagination.

        Args:
            page: Page number (0-based)
            page_size: Number of items per page (default 100)

        Returns:
            dict containing:
                - messages: List of message documents
                - total: Total number of messages
                - page: Current page number
                - page_size: Number of items per page
        """
        try:
            response = self.opensearch_client.search(
                index=self.feedback_analysis_index,
                body=self._get_messages_query(page, page_size),
            )

            hits = response.get("hits", {})
            messages = [hit["_source"] for hit in hits.get("hits", [])]

            return {
                "messages": messages,
                "total": hits.get("total", {}).get("value", 0),
                "page": page,
                "page_size": page_size,
            }

        except Exception as e:
            logger.error(f"Error fetching OpenSearch messages: {str(e)}")
            return {"messages": [], "total": 0, "page": page, "page_size": page_size}

    def _get_wordcount_query(self):
        """Return the OpenSearch query for word count analysis with nested aggregation."""
        return {
            "size": 0,
            "aggs": {
                "top_words": {
                    "nested": {"path": "word_counts"},
                    "aggs": {
                        "words": {
                            "terms": {
                                "field": "word_counts.word",
                                "size": 15,
                                "order": {"sum_count": "desc"},
                            },
                            "aggs": {
                                "sum_count": {"sum": {"field": "word_counts.count"}}
                            },
                        }
                    },
                }
            },
        }

    def get_wordcount_analysis(self) -> dict:
        """
        Get word count analysis from the wordcount-analysis index.
        Returns a list of top 500 words with their counts, sorted by count in descending order.
        """
        try:
            response = self.opensearch_client.search(
                index="wordcount-analysis", body=self._get_wordcount_query()
            )

            # Navigate through the aggregation response
            buckets = (
                response.get("aggregations", {})
                .get("top_words", {})
                .get("words", {})
                .get("buckets", [])
            )

            # Transform buckets into word count list
            word_counts = [
                {"word": bucket["key"], "count": int(bucket["sum_count"]["value"])}
                for bucket in buckets
            ]

            return {"words": word_counts}

        except Exception as e:
            logger.error(f"Error fetching word count analysis: {str(e)}")
            return {"words": []}


def get_search_service() -> SearchService:
    """Dependency function to get SearchService instance."""
    return SearchService()
