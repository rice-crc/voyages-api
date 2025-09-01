"""
This module provides APIs that are used by the Contribute Application (backend
and frontend). 
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading
import traceback
from typing import Dict, List, Any, Optional, Type, Union, Set
from collections import defaultdict, deque
from django.apps import apps
from django.db import connection, transaction
from django.db.models import Q, Model
from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from voyage.models import Voyage
from geo.common import GeoTreeFilter
import json
import logging

# Type definitions to match the TypeScript interface
NonNullFieldValue = Union[str, int, float, bool]
BaseFieldValue = Optional[NonNullFieldValue]
ResolvedEntityData = Dict[str, BaseFieldValue]
    
logger = logging.getLogger(__name__)

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

def remap(r: Dict[str, Any], remapped: List[str]):
    for f in remapped:
        key = f.replace("_id", "")
        if key in r:
            r[f] = r[key]
            del r[key]
    return r

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
        # Get all valid field names for the model
        valid_field_names = {f.name for f in model_class._meta.fields}
        # Filter out invalid field names.
        # First detect fields with _id suffix that should be remapped.
        remapped = [f for f in fields if "_id" in f and f not in valid_field_names]
        fields = [f.replace("_id", "") if f in remapped else f for f in fields]
        valid_fields = [f for f in fields if f in valid_field_names]
        if len(valid_fields) < len(fields):
            print("Invalid fields found in query: ")
            print([f for f in fields if f not in valid_fields])
            print("Expected:")
            print(valid_field_names)
        result = list(model_class.objects.filter(query).values(*valid_fields))
        if len(remapped) > 0:
            result = [remap(r, remapped) for r in result]
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

@csrf_exempt
def location_tree(_):
    return JsonResponse(GeoTreeFilter(select_all=True), safe=False)

_schemaToDbTable: Dict[str, str] = {
  'VoyageSparseDate': 'voyage_voyagesparsedate',
  'Nationality': 'voyage_nationality',
  'TonType': 'voyage_tontype',
  'RigOfVessel': 'voyage_rigofvessel',
  'Location': 'geo_location',
  'VoyageShip': 'voyage_voyageship',
  'VoyageItinerary': 'voyage_voyageitinerary',
  'VoyageSlaveNumbers': 'voyage_voyageslavesnumbers',
  'VoyageDates': 'voyage_voyagedates',
  'VoyageGrouping': 'voyage_voyagegroupings',
  'AfricanInfo': 'voyage_africaninfo',
  'CargoUnit': 'voyage_cargounit',
  'CargoType': 'voyage_cargotype',
  'VoyageCargoConnectionSchema': 'voyage_voyagecargoconnection',
  'ParticularOutcome': 'voyage_particularoutcome',
  'SlavesOutcome': 'voyage_slavesoutcome',
  'VesselOutcomeSchema': 'voyage_vesselcapturedoutcome',
  'OwnerOutcome': 'voyage_owneroutcome',
  'Resistance': 'voyage_resistance',
  'VoyageOutcome': 'voyage_voyageoutcome',
  'VoyageCrew': 'voyage_voyagecrew',
  'EnslaverAlias': 'past_enslaveralias',
  'Enslaver': 'past_enslaveridentity',
  'EnslaverAliasWithFK': 'past_enslaveralias',
  'EnslaverAliasWithIdentity': 'past_enslaveralias',
  'EnslavementRelationType': 'past_enslavementrelationtype',
  'EnslaverRole': 'past_enslaverrole',
  'EnslaverRelationRoleConn': 'past_enslaverinrelation_roles',
  'EnslaverInRelation': 'past_enslaverinrelation',
  'Enslaved': 'past_enslaved',
  'EnslavedInRelation': 'past_enslavedinrelation',
  'EnslavementRelation': 'past_enslavementrelation',
  'Voyage Source Type': 'document_sourcetype',
  'Voyage Source Short Reference': 'document_shortref',
  'Voyage Source': 'document_source',
  'Voyage Source Connection': 'document_sourcevoyageconnection',
  'Voyage': 'voyage_voyage'
}

_schemaToModel: Dict[str, Type[models.Model]] = {}
for m in apps.get_models(include_auto_created=True):
    for k, v in _schemaToDbTable.items():
        if m._meta.db_table == v:
            _schemaToModel[k] = m
_missing = set()
for k in _schemaToDbTable.keys():
    if k not in _schemaToModel:
        _missing.add(k)
if _missing:
    logger.error(f"Missing model for schema: {list(_missing)}")
else:
    logger.info("All models mapped successfully")

class ChangeSetProcessor:
    """Processes CombinedChangeSet and applies changes to Django ORM."""
    
    def __init__(self):
        self.temp_id_to_db_id: Dict[str, Any] = {}
        self.new_entity_ids: Set[str] = set()
        
    def process_changeset(self, changeset: Dict) -> Dict[str, Any]:
        """
        Process the entire changeset in a transaction.
        Returns a mapping of temporary IDs to actual database IDs.
        """
        deletions = changeset.get('deletions', [])
        updates = changeset.get('updates', [])
        
        # Validate no duplicate entity updates and no updates to deleted entities
        self._validate_no_duplicates(deletions, updates)
        
        # Collect all new entity IDs first
        self.new_entity_ids = {
            update['entityRef']['id'] 
            for update in updates 
            if update['entityRef'].get('type') == 'new'
        }
        
        # Separate new and existing entity updates
        new_updates = [u for u in updates if u['entityRef'].get('type') == 'new']
        existing_updates = [u for u in updates if u['entityRef'].get('type') != 'new']
        
        # Sort new entities by FK dependencies
        sorted_new_updates = self._topological_sort(new_updates)
        
        with transaction.atomic():
            # Process deletions first
            for deletion in deletions:
                self._process_deletion(deletion)
            
            # Process new entities in dependency order
            for update in sorted_new_updates:
                logger.debug(json.dumps(update))
                self._process_new_entity(update)
            
            # Process existing entity updates
            for update in existing_updates:
                self._process_existing_entity(update)
        
        return self.temp_id_to_db_id
    
    def _validate_no_duplicates(self, deletions: List[Dict], updates: List[Dict]):
        """Validate that each entity is updated at most once and deleted entities aren't updated."""
        updated_entities = set()
        deleted_entities = set()
        
        # Collect deleted entity references
        for deletion in deletions:
            entity_key = self._get_entity_key(deletion['entityRef'])
            deleted_entities.add(entity_key)
        
        # Check for duplicate updates and updates to deleted entities
        for update in updates:
            entity_key = self._get_entity_key(update['entityRef'])
            
            if entity_key in deleted_entities:
                raise ValueError(f"Cannot update deleted entity: {entity_key}")
            
            if entity_key in updated_entities:
                raise ValueError(f"Duplicate update for entity: {entity_key}")
            
            updated_entities.add(entity_key)
    
    def _get_entity_key(self, entity_ref: Dict) -> str:
        """Create a unique key for an entity reference."""
        return f"{entity_ref['schema']}:{entity_ref['id']}"
    
    def _topological_sort(self, new_updates: List[Dict]) -> List[Dict]:
        """
        Sort new entities based on foreign key dependencies.
        Returns sorted list or raises ValueError if cycle detected.
        """
        # Build dependency graph
        graph = defaultdict(list)  # entity_id -> list of entities that depend on it
        in_degree = defaultdict(int)  # entity_id -> number of dependencies
        entity_map = {}  # entity_id -> update dict
        
        for update in new_updates:
            entity_id = update['entityRef']['id']
            entity_map[entity_id] = update
            
            # Find FK dependencies to other new entities
            for change in update['changes']:
                if change.get('isForeignKey') and change.get('changed'):
                    fk_value = change['changed']
                    # Check if FK points to a new entity (using set membership)
                    if fk_value in self.new_entity_ids:
                        graph[fk_value].append(entity_id)
                        in_degree[entity_id] += 1
        
        # Initialize queue with entities that have no dependencies
        queue = deque()
        for update in new_updates:
            entity_id = update['entityRef']['id']
            if in_degree[entity_id] == 0:
                queue.append(entity_id)
        
        # Process queue (Kahn's algorithm)
        sorted_ids = []
        while queue:
            current_id = queue.popleft()
            sorted_ids.append(current_id)
            
            # Reduce in-degree for dependent entities
            for dependent_id in graph[current_id]:
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    queue.append(dependent_id)
        
        # Check for cycles
        if len(sorted_ids) != len(new_updates):
            raise ValueError("Circular dependency detected in new entities")
        
        # Return updates in sorted order
        return [entity_map[entity_id] for entity_id in sorted_ids]
    
    def _process_deletion(self, deletion: Dict):
        """Process a deletion operation."""
        entity_ref = deletion['entityRef']
        model_class = self._get_model_class(entity_ref['schema'])
        
        try:
            obj = model_class.objects.get(pk=entity_ref['id'])
            obj.delete()
            logger.info(f"Deleted {entity_ref['schema']} with id {entity_ref['id']}")
        except model_class.DoesNotExist:
            logger.warning(f"Entity {entity_ref['schema']} with id {entity_ref['id']} not found for deletion")
    
    def _process_new_entity(self, update: Dict):
        """Process creation of a new entity."""
        entity_ref = update['entityRef']
        model_class = self._get_model_class(entity_ref['schema'])
        
        # Prepare field values
        field_values = {}
        for change in update['changes']:
            field_name = change['property']
            value = change['changed']
            
            # Replace temporary FK references with actual IDs
            if change.get('isForeignKey') and value and value in self.new_entity_ids:
                if value not in self.temp_id_to_db_id:
                    raise ValueError(f"Foreign key references unprocessed entity: {value}")
                value = self.temp_id_to_db_id[value]
            
            field_values[field_name] = value
        
        # Create the entity - let Django handle field validation
        obj = model_class(**field_values)
        # Special cases:
        if (model_class == Voyage):
            # (domingos): I don't know why we have both id and voyage_id in the
            # model, but at this point it is better to make sure they're equal.
            obj.id = obj.voyage_id
        obj.save()
        
        # Store the mapping from temporary ID to actual database ID
        self.temp_id_to_db_id[entity_ref['id']] = obj.pk
        
        logger.info(f"Created {entity_ref['schema']} with temp id {entity_ref['id']} -> db id {obj.pk}")
    
    def _process_existing_entity(self, update: Dict):
        """Process update of an existing entity."""
        entity_ref = update['entityRef']
        model_class = self._get_model_class(entity_ref['schema'])
        
        try:
            obj = model_class.objects.get(pk=entity_ref['id'])
            
            # Apply changes
            for change in update['changes']:
                field_name = change['property']
                value = change['changed']
                
                # Replace temporary FK references with actual IDs
                if change.get('isForeignKey') and value and value in self.new_entity_ids:
                    if value not in self.temp_id_to_db_id:
                        raise ValueError(f"Foreign key references unprocessed entity: {value}")
                    value = self.temp_id_to_db_id[value]
                
                setattr(obj, field_name, value)
            
            obj.save()
            logger.info(f"Updated {entity_ref['schema']} with id {entity_ref['id']}")
            
        except model_class.DoesNotExist:
            raise ValueError(f"Entity {entity_ref['schema']} with id {entity_ref['id']} not found for update")
    
    def _get_model_class(self, schema_name: str):
        """Get Django model class from schema name."""
        # Try to get model from any installed app
        if schema_name not in _schemaToModel:
            raise ValueError(f"Model {schema_name} not found in any app")
        return _schemaToModel[schema_name]


class PublicationStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PublicationTask:
    """Represents a changeset publication task."""
    publication_key: str
    status: PublicationStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    changeset: Dict = field(default_factory=dict)
    result: Optional[Dict] = None
    error: Optional[str] = None
    id_mappings: Dict[str, Any] = field(default_factory=dict)


# TODO: move the TaskStore to the database so that it can be shared across
# workers.

class TaskStore:
    """In-memory storage for publication tasks."""
    
    def __init__(self, max_age_hours: int = 24):
        self._tasks: Dict[str, PublicationTask] = {}
        self._lock = threading.Lock()
        self.max_age_hours = max_age_hours
    
    def get(self, publication_key: str) -> Optional[PublicationTask]:
        """Get a task by publication key."""
        with self._lock:
            self._cleanup_old_tasks()
            return self._tasks.get(publication_key)
    
    def create(self, publication_key: str, changeset: Dict) -> PublicationTask:
        """Create or return existing task."""
        with self._lock:
            # Check if task already exists (idempotency)
            if publication_key in self._tasks:
                return self._tasks[publication_key]
            
            # Create new task
            task = PublicationTask(
                publication_key=publication_key,
                status=PublicationStatus.PENDING,
                created_at=datetime.now(),
                changeset=changeset
            )
            self._tasks[publication_key] = task
            return task
    
    def update_status(self, publication_key: str, status: PublicationStatus, 
                     result: Optional[Dict] = None, error: Optional[str] = None):
        """Update task status."""
        with self._lock:
            task = self._tasks.get(publication_key)
            if task:
                task.status = status
                if status == PublicationStatus.PROCESSING:
                    task.started_at = datetime.now()
                elif status in (PublicationStatus.COMPLETED, PublicationStatus.FAILED):
                    task.completed_at = datetime.now()
                if result:
                    task.result = result
                if error:
                    task.error = error
    
    def _cleanup_old_tasks(self):
        """Remove tasks older than max_age_hours."""
        cutoff = datetime.now() - timedelta(hours=self.max_age_hours)
        expired_keys = [
            key for key, task in self._tasks.items()
            if task.created_at < cutoff
        ]
        for key in expired_keys:
            del self._tasks[key]
            logger.info(f"Cleaned up expired task: {key}")


# Global task store (singleton for the application instance)
task_store = TaskStore()

def process_changeset_background(publication_key: str):
    """Background task to process a changeset."""
    task = task_store.get(publication_key)
    if not task:
        logger.error(f"Task not found for publication key: {publication_key}")
        return
    
    try:
        # Update status to processing
        task_store.update_status(publication_key, PublicationStatus.PROCESSING)
        logger.info(f"Starting processing for publication: {publication_key}")
        
        # Process the changeset
        processor = ChangeSetProcessor()
        
        # Close any existing DB connections to ensure thread safety
        connection.close()
        
        id_mappings = processor.process_changeset(task.changeset)
        
        # Update task with success
        task_store.update_status(
            publication_key,
            PublicationStatus.COMPLETED,
            result={
                'success': True,
                'id_mappings': id_mappings,
                'message': 'Changeset processed successfully'
            }
        )
        logger.info(f"Successfully processed publication: {publication_key}")
        
    except ValueError as e:
        logger.error(f"Validation error for publication {publication_key}: {e}")
        task_store.update_status(
            publication_key,
            PublicationStatus.FAILED,
            error=traceback.format_exc()
        )
    except Exception as e:
        logger.error(f"Unexpected error processing publication {publication_key}: {e}", exc_info=True)
        task_store.update_status(
            publication_key,
            PublicationStatus.FAILED,
            error=f"Internal error: {traceback.format_exc()}"
        )
    finally:
        # Ensure DB connection is closed
        connection.close()

@csrf_exempt
@require_POST
def publish_batch(request):
    """
    Initiate processing of a CombinedChangeSet.
    Expects JSON body with 'publication_key' and 'changeset'.
    """
    try:
        # Parse JSON body
        if not request.body:
            return JsonResponse({'error': 'Empty request body'}, status=400)
        
        data = json.loads(request.body)
        
        # Extract publication key and changeset
        publication_key = data.get('key')
        if not publication_key:
            return JsonResponse({'error': 'Missing idempotency key'}, status=400)
        
        changeset = data.get('changeset')
        if not changeset:
            return JsonResponse({'error': 'Missing changeset'}, status=400)
        
        # Create or get existing task (idempotency)
        task = task_store.create(publication_key, changeset)
        
        # If task is already completed or failed, return immediately
        if task.status == PublicationStatus.COMPLETED:
            return JsonResponse(task.result)
        elif task.status == PublicationStatus.FAILED:
            return JsonResponse({'error': task.error}, status=400)
        elif task.status == PublicationStatus.PROCESSING:
            return JsonResponse({
                'status': 'processing',
                'publication_key': publication_key,
                'message': 'Publication is already being processed'
            })
        
        # Start background processing for new task
        thread = threading.Thread(
            target=process_changeset_background,
            args=(publication_key,),
            daemon=True
        )
        thread.start()
        
        return JsonResponse({
            'status': 'accepted',
            'publication_key': publication_key,
            'message': 'Publication queued for processing'
        }, status=202)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in publish_batch: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

def publication_status(request, publication_key):
    """
    Check the status of a publication task.
    Returns current status and result if completed.
    """
    try:
        task = task_store.get(publication_key)
        
        if not task:
            return JsonResponse({
                'error': 'Publication not found',
                'publication_key': publication_key
            }, status=404)
        
        # Build response based on task status
        response = {
            'publication_key': publication_key,
            'status': task.status,
            'created_at': task.created_at.isoformat(),
        }
        
        if task.started_at:
            response['started_at'] = task.started_at.isoformat()
        
        if task.completed_at:
            response['completed_at'] = task.completed_at.isoformat()
            duration = (task.completed_at - task.started_at).total_seconds()
            response['duration_seconds'] = duration
        
        if task.status == PublicationStatus.COMPLETED:
            response.update(task.result)
        elif task.status == PublicationStatus.FAILED:
            response['error'] = task.error
            return JsonResponse(response, status=400)
        elif task.status == PublicationStatus.PROCESSING:
            response['message'] = 'Publication is being processed'
        elif task.status == PublicationStatus.PENDING:
            response['message'] = 'Publication is queued for processing'
        
        return JsonResponse(response)
        
    except Exception as e:
        logger.error(f"Error checking publication status: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
