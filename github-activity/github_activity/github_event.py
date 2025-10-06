# -*- coding: utf-8 -*-
"""
Github Event module
"""


class GithubEvent:
    """Represents a GitHub event and provides formatted descriptions for each event type.

    Args:
        data (dict): The event data from GitHub API.
    """

    def __init__(self, data: dict) -> None:
        """Initializes a GithubEvent instance.

        Args:
            data (dict): The event data from GitHub API.
        """
        self.payload: dict = data["payload"]
        self.event_type = data["type"]
        # Replace "T" with " ", and delete the last "Z".
        self.created_at = data["created_at"].translate(str.maketrans("T", " ", "Z"))
        self.created_date = self.created_at[:10]
        self.created_time = self.created_at[11:]
        self.repo_name = data["repo"]["name"]
        self.actor_name = data["actor"]["login"]

    @property
    def description(self) -> str:
        """Returns a human-readable description of the event.

        Returns:
            str: Description of the event.
        """
        return f"{self.actor_name} {getattr(self, self.event_type)()}"

    def CommitCommentEvent(self) -> str:
        """Description for CommitCommentEvent."""
        commit_sha, comment_id = self.payload["comment"]["commit_id"], self.payload["comment"]["id"]
        return f"created comment {comment_id} on commit {commit_sha} in {self.repo_name}."

    def CreateEvent(self) -> str:
        """Description for CreateEvent."""
        if self.payload["ref_type"] == "repository":
            return f"created repository {self.repo_name}."
        return f"created {self.payload['ref_type']} {self.payload['ref']} in {self.repo_name}."

    def DeleteEvent(self) -> str:
        """Description for DeleteEvent."""
        return f"deleted {self.payload['ref_type']} {self.payload['ref']} from {self.repo_name}."

    def ForkEvent(self) -> str:
        """Description for ForkEvent."""
        return f"forked repository {self.payload['forkee']['full_name']} to {self.repo_name}."

    def GollumEvent(self) -> str:
        """Description for GollumEvent."""
        pages = self.payload["pages"]
        return f"{pages['action']} wiki page {pages['name']} in {self.repo_name}."

    def IssueCommentEvent(self) -> str:
        """Description for IssueCommentEvent."""
        issue_number, comment_id = self.payload["issue"]["number"], self.payload["comment"]["id"]
        return f"{self.payload['action']} comment {comment_id} on issue {issue_number} in {self.repo_name}."

    def IssuesEvent(self) -> str:
        """Description for IssuesEvent."""
        return f"{self.payload['action']} issue {self.payload['issue']['number']} in {self.repo_name}."

    def MemberEvent(self) -> str:
        """Description for MemberEvent."""
        action = self.payload["action"]
        member_name = self.payload["member"]["login"]
        if action == "added":
            return f"added {member_name} as a collaborator to {self.repo_name}."
        if action == "edited":
            return f"changed permissions of collaborator {member_name} in {self.repo_name}."
        return f"removed collaborator {member_name} from {self.repo_name}."

    def PublicEvent(self) -> str:
        """Description for PublicEvent."""
        return f"changed visibility from private to public for {self.repo_name} ."

    def PullRequestEvent(self) -> str:
        """Description for PullRequestEvent."""
        action, pull_number = self.payload["action"], self.payload["number"]
        if action == "review_requested":
            return f"requested review for pull request {pull_number} in {self.repo_name}."

        if action == "ready_for_review":
            return f"marked pull request {pull_number} as ready for review in {self.repo_name}."

        if action == "review_request_removed":
            return f"removed a review request from pull request {pull_number} in {self.repo_name}."

        if action == "converted_to_draft":
            return f"converted pull request {pull_number} to a draft in {self.repo_name}."

        if action == "auto_merge_disabled":
            return f"disabled auto merge for pull request {pull_number} in {self.repo_name}."

        if action == "auto_merge_enabled":
            return f"enabled auto merge for pull request {pull_number} in {self.repo_name}."

        return f"{self.payload['action']} pull request {pull_number} in {self.repo_name}."

    def PullRequestReviewEvent(self) -> str:
        """Description for PullRequestReviewEvent."""
        pull_number, review_id = self.payload["pull_request"]["number"], self.payload["review"]["id"]
        return f"{self.payload['action']} review {review_id} on pull request {pull_number} in {self.repo_name}."

    def PullRequestReviewCommentEvent(self) -> str:
        """Description for PullRequestReviewCommentEvent."""
        pull_number, review_id, comment_id = (
            self.payload["pull_request"]["number"],
            self.payload["comment"]["pull_request_review_id"],
            self.payload["comment"]["id"],
        )
        return f"{self.payload['action']} comment {comment_id} on review {review_id} of pull request {pull_number} in {self.repo_name}."

    def PullRequestReviewThreadEvent(self) -> str:
        """Description for PullRequestReviewThreadEvent."""
        return f"{self.payload['action']} a comment thread on pull request {self.payload['pull_request']['number']} in {self.repo_name}."

    def PushEvent(self) -> str:
        """Description for PushEvent."""
        commit_count = self.payload["distinct_size"]
        return f"pushed {commit_count} commit{'s' if commit_count == 1 else ''} to {self.payload['ref']} in {self.repo_name}."

    def ReleaseEvent(self) -> str:
        """Description for ReleaseEvent."""
        tag_name = self.payload["release"]["tag_name"]
        return f"{self.payload['action']} a release tag {tag_name} in {self.repo_name}."

    def SponsorshipEvent(self) -> str:
        """Description for SponsorshipEvent."""
        action = self.payload["action"]
        if action == "pending_cancellation":
            return f"scheduled to cancel the sponsorship on {self.payload['effective_date']} in {self.repo_name}."
        if action == "pending_tier_change":
            return f"scheduled to change the sponsorship tier on {self.payload['effective_date']} in {self.repo_name}."

        if action == "tier_changed":
            return f"changed the sponsorship tier in {self.repo_name}."

        return f"{action} the sponsorship in {self.repo_name}."

    def WatchEvent(self) -> str:
        """Description for WatchEvent."""
        return f"starred repository {self.repo_name}."
