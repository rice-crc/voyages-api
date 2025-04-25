"""
Django implementation of the BatchDataResolver interface.
This module provides a way to execute multiple database queries in a single request.
"""
from typing import Dict, List, Any, Optional, Union, Tuple
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Model
from django.apps import apps

# Type definitions to match the TypeScript interface
NonNullFieldValue = Union[str, int, float, bool]
BaseFieldValue = Optional[NonNullFieldValue]
ResolvedEntityData = Dict[str, BaseFieldValue]

class DataFilter:
    """Represents a filter condition on a field."""
    
    def __init__(self, field: str, value: Union[NonNullFieldValue, List[NonNullFieldValue]], operator: str = "equals"):
        self.field = field
        self.value = value
        self.operator = operator
    
    def to_q(self) -> Q:
        """Convert the filter to a Django Q object."""
        if self.operator == "in":
            return Q(**{f"{self.field}__in": self.value})
        # Default to equals
        return Q(**{self.field: self.value})


class DataQuery:
    """Represents a query on a specific model with filters."""
    
    def __init__(self, model: str, filters: List[DataFilter]):
        self.model = model.replace("_", ".", 1)  # Convert to Django model path
        self.filters = filters
    
    def get_model_class(self) -> Model:
        """Get the Django model class from the model name."""
        try:
            return apps.get_model(self.model)
        except LookupError:
            raise ValueError(f"Model {self.model} not found")
    
    def execute(self, fields: List[str]) -> List[ResolvedEntityData]:
        """Execute the query and return the results."""
        model_class = self.get_model_class()
        
        # Build the filter query
        query = Q()
        for filter_obj in self.filters:
            query &= filter_obj.to_q()
        
        # Execute the query and return the results
        queryset = model_class.objects.filter(query)
        # Convert to list of dictionaries with only the requested fields
        result = []
        for instance in queryset:
            entity_data = {}
            for field in fields:
                try:
                    value = getattr(instance, field)
                    # Ensure the value is of a compatible type
                    if value is not None and not isinstance(value, (str, int, float, bool)):
                        value = str(value)
                    entity_data[field] = value
                except AttributeError:
                    entity_data[field] = None
            result.append(entity_data)
        
        return result


class DataResolver:
    """Resolver for a single data query."""
    
    @staticmethod
    def fetch(input_data: Dict[str, Any]) -> List[ResolvedEntityData]:
        """Fetch data based on the input query."""
        query = DataQuery(
            model=input_data["query"]["model"],
            filters=[
                DataFilter(
                    field=filter_obj["field"],
                    value=filter_obj["value"],
                    operator=filter_obj.get("operator", "equals")
                )
                for filter_obj in input_data["query"]["filter"]
            ]
        )
        return query.execute(input_data["fields"])


class BatchDataResolver:
    """Resolver for multiple data queries in one batch."""
    
    @staticmethod
    def fetchBatch(batch: Dict[str, Dict[str, Any]]) -> Dict[str, List[ResolvedEntityData]]:
        """Fetch multiple queries serially and return results keyed by query ID."""
        results = {}
        for key, input_data in batch.items():
            results[key] = DataResolver.fetch(input_data)
        return results


@csrf_exempt
@require_POST
def batch_data_api(request):
    """API endpoint that handles batch data requests."""
    try:
        # Parse the request body
        batch_data = json.loads(request.body)
        # Validate the input
        if not isinstance(batch_data, dict):
            return JsonResponse({"error": "Input must be a dictionary"}, status=400)
        # Execute the batch query
        results = BatchDataResolver.fetchBatch(batch_data)
        # Return the results
        return JsonResponse(results, safe=False)
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
