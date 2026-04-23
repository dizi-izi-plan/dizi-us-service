from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, status
from app.core.dependency import get_tariff_service
from app.core.permission import admin_required
from app.schema.tariff import TariffRead, TariffCreate, TariffUpdate
from app.service.tariff import TariffService

router = APIRouter()


@router.post(
    "/",
    response_model=TariffRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_required)])
async def create_tariff(
    payload: TariffCreate,
    service: TariffService = Depends(get_tariff_service)
):
    return await service.create_tariff(payload)


@router.get("/", response_model=List[TariffRead])
async def get_all_tariffs(
    service: TariffService = Depends(get_tariff_service)
):
    return await service.get_tariffs()


@router.get("/{tariff_id}", response_model=TariffRead)
async def get_tariff(
    tariff_id: UUID,
    service: TariffService = Depends(get_tariff_service)
):
    return await service.get_tariff_by_id(tariff_id)


@router.patch(
    "/{tariff_id}",
    response_model=TariffRead,
    dependencies=[Depends(admin_required)])
async def update_tariff(
    tariff_id: UUID,
    payload: TariffUpdate,
    service: TariffService = Depends(get_tariff_service)
):
    return await service.update_tariff(tariff_id, payload)


@router.delete(
    "/{tariff_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(admin_required)])
async def delete_tariff(
    tariff_id: UUID,
    service: TariffService = Depends(get_tariff_service)
):
    await service.delete_tariff(tariff_id)
