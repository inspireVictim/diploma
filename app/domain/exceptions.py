class DomainError(Exception):
    """Base class for domain/application errors."""


class EntityNotFoundError(DomainError):
    def __init__(self, entity: str, entity_id: int) -> None:
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} with id={entity_id} was not found")
