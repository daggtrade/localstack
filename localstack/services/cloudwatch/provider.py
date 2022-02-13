from moto.cloudwatch import cloudwatch_backends

from localstack.aws.api import HttpRequest, HttpResponse, RequestContext
from localstack.aws.api.cloudwatch import (
    AmazonResourceName,
    CloudwatchApi,
    ListTagsForResourceOutput,
    TagKeyList,
    TagList,
    TagResourceOutput,
    UntagResourceOutput,
)
from localstack.services.cloudwatch.cloudwatch_listener import TAGS
from localstack.utils.aws import aws_stack


class CloudwatchProvider(CloudwatchApi):
    def get_raw_metrics(self, request: HttpRequest, response: HttpResponse):
        region = aws_stack.extract_region_from_auth_header(request.headers)
        result = cloudwatch_backends[region].metric_data
        result = [
            {
                "ns": r.namespace,
                "n": r.name,
                "v": r.value,
                "t": r.timestamp,
                "d": [{"n": d.name, "v": d.value} for d in r.dimensions],
            }
            for r in result
        ]
        response.set_json({"metrics": result})

    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName
    ) -> ListTagsForResourceOutput:
        tags = TAGS.list_tags_for_resource(resource_arn)
        return ListTagsForResourceOutput(Tags=tags.get("Tags", []))

    def untag_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName, tag_keys: TagKeyList
    ) -> UntagResourceOutput:
        TAGS.untag_resource(resource_arn, tag_keys)
        return UntagResourceOutput()

    def tag_resource(
        self, context: RequestContext, resource_arn: AmazonResourceName, tags: TagList
    ) -> TagResourceOutput:
        TAGS.tag_resource(resource_arn, tags)
        return TagResourceOutput()
