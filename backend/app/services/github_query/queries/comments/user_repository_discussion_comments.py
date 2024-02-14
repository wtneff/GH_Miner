from typing import Dict, Any, List
from backend.app.services.github_query.github_graphql.query import QueryNode, PaginatedQuery, QueryNodePaginator
import backend.app.services.github_query.utils.helper as helper

class UserRepositoryDiscussionComments(PaginatedQuery):
    """
    UserRepositoryDiscussionComments constructs a paginated GraphQL query specifically for
    retrieving user repository discussion comments. It extends the PaginatedQuery class to handle
    queries that expect a large amount of data that might be delivered in multiple pages.
    """
    def __init__(self) -> None:
        """
        Initializes the UserRepositoryDiscussionComments query with specific fields and arguments
        to retrieve user repository discussion comments, including pagination handling. The query is constructed
        to fetch various details about the comments, such as creation time and pagination info.
        """
        super().__init__(
            fields=[
                QueryNode(
                    "user",
                    args={"login": "$user"},
                    fields=[
                        "login",
                        QueryNodePaginator(
                            "repositoryDiscussionComments",
                            args={"first": "$pg_size"},
                            fields=[
                                "totalCount",
                                QueryNode(
                                    "nodes",
                                    fields=["createdAt"]
                                ),
                                QueryNode(
                                    "pageInfo",
                                    fields=["endCursor", "hasNextPage"]
                                )
                            ]
                        )
                    ]
                )
            ]
        )

    @staticmethod
    def user_repository_discussion_comments(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts and returns the repository discussion comments from the raw query data.

        Args:
            raw_data (dict): The raw data returned by the GraphQL query. It's expected
                             to follow the structure: {user: {repositoryDiscussionComments: {nodes: [{createdAt: ""}, ...]}}}.
        
        Returns:
            list: A list of dictionaries, each representing a repository discussion comment and its associated data, particularly the creation date.
        """
        repository_discussion_comments = raw_data["user"]["repositoryDiscussionComments"]["nodes"]
        return repository_discussion_comments

    @staticmethod
    def created_before_time(repository_discussion_comments: List[Dict[str, Any]], time: str) -> int:
        """
        Counts how many repository discussion comments were created before a specific time.

        Args:
            repository_discussion_comments (list): A list of repository discussion comment dictionaries, each containing a "createdAt" field.
            time (str): The cutoff time as a string. All comments created before this time will be counted.

        Returns:
            int: The count of repository discussion comments created before the specified time.
        """
        counter = 0
        for repository_discussion_comment in repository_discussion_comments:
            if helper.created_before(repository_discussion_comment["createdAt"], time):
                counter += 1
            else:
                break
        return counter
