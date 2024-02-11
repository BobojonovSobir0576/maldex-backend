from rest_framework import pagination
from rest_framework.response import Response


class CustomPagination(pagination.PageNumberPagination):
    page_size_query_param = "limit"
    page_size = 40

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {"next": self.get_next_link(), "previous": self.get_previous_link()},
                "page": self.page.number,
                "total_objects": self.page.paginator.count,
                "current_page_size": len(self.page.object_list),
                "limit": self.page.paginator.per_page,
                "total_pages": self.page.paginator.num_pages,
                "results": data,
            }
        )
