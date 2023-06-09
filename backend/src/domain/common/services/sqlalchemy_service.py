from typing import Any, Generic

from src.domain.common.exceptions import SQLAlchemyServiceException
from src.domain.common.interfaces import AsyncDBServiceInterface
from src.domain.common.repositories import AsyncSQLAlchemyRepository
from src.domain.common.typevars import CreateDTO, Entity, Model, UpdateDTO


class AsyncSQLAlchemyService(AsyncDBServiceInterface, Generic[Entity, CreateDTO, UpdateDTO]):
    """
    Asynchronous SQLAlchemy service implementation.
    """

    def __init__(
        self,
        model: type[Model],
        entity: type[Entity],
        *,
        repository: type[AsyncSQLAlchemyRepository] = AsyncSQLAlchemyRepository,
    ) -> None:
        self._entity = entity
        self._repository = repository(model=model)

    async def receive(self, *, row_id: Any) -> Entity:
        row = await self._repository.receive(row_id=row_id)
        entity = self._entity.from_orm(row)
        return entity

    async def bulk_receive(self, order_by: list[str] | None = None) -> list[Entity]:
        rows = await self._repository.bulk_receive(order_by=order_by)
        entities = [self._entity.from_orm(row) for row in rows]
        return entities

    async def create(self, dto: CreateDTO) -> Entity:
        entities_array = await self.bulk_create(dtos=[dto])
        return entities_array[0]

    async def bulk_create(self, dtos: list[CreateDTO]) -> list[Entity]:
        rows = await self._repository.bulk_create(dtos=dtos)
        entities = [self._entity.from_orm(row) for row in rows]
        return entities

    async def update(self, row_id: Any, dto: UpdateDTO) -> Entity:
        entities_array = await self.bulk_update(row_ids=[row_id], dto=dto)

        if not entities_array:
            raise SQLAlchemyServiceException(
                f'{self.__name__} cannot find object with id "{row_id}"'
            )

        return entities_array[0]

    async def bulk_update(self, row_ids: Any, dto: UpdateDTO) -> list[Entity]:
        rows = await self._repository.bulk_update(row_ids=row_ids, dto=dto)
        entities = [self._entity.from_orm(row) for row in rows]
        return entities

    async def delete(self, row_id: Any) -> None:
        await self.bulk_delete(row_ids=[row_id])

    async def bulk_delete(self, row_ids: list[Any]) -> None:
        await self._repository.bulk_delete(row_ids=row_ids)
