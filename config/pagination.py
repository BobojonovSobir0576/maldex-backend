from rest_framework import pagination
from rest_framework.response import Response


class CustomPagination(pagination.PageNumberPagination):
    # Specify the query parameter used to determine page size
    page_size_query_param = "limit"
    # Default page size
    page_size = 40

    def get_paginated_response(self, data):
        """
        Customize the paginated response format.
        """
        return Response(
            {
                # Pagination links for navigating to next and previous pages
                "links": {"next": self.get_next_link(), "previous": self.get_previous_link()},
                # Current page number
                "page": self.page.number,
                # Total number of objects across all pages
                "total_objects": self.page.paginator.count,
                # Number of objects in the current page
                "current_page_size": len(self.page.object_list),
                # Page size
                "limit": self.page.paginator.per_page,
                # Total number of pages
                "total_pages": self.page.paginator.num_pages,
                # Paginated results
                "results": data,
            }
        )
