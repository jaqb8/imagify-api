from rest_framework.renderers import JSONRenderer
import json


class NonNullJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        data = self.omit_null_values(data)
        renderer_context["response"].data = data
        return super().render(data, accepted_media_type, renderer_context)

    def omit_null_values(self, data):
        if data is None:
            return data
        if isinstance(data, list):
            return [self.omit_null_values(v) for v in data]
        if isinstance(data, dict):
            return {
                k: self.omit_null_values(v) for k, v in data.items() if v is not None
            }
        return data
