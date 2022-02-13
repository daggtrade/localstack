from moto.cloudwatch import cloudwatch_backends

from localstack.aws.api import HttpRequest, RequestContext
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
from localstack.services.edge import router
from localstack.services.plugins import ServiceLifecycleHook
from localstack.utils.aws import aws_stack

PATH_GET_RAW_METRICS = "/cloudwatch/metrics/raw"


class CloudwatchProvider(CloudwatchApi, ServiceLifecycleHook):
    def on_before_start(self):
        router.add(PATH_GET_RAW_METRICS, self.get_raw_metrics)

    def get_raw_metrics(self, request: HttpRequest):
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
        return {"metrics": result}

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
