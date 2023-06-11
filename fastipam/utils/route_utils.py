from fastapi import HTTPException

from ipaddress import ip_network, IPv4Network, IPv6Network
import itertools
import uuid

from fastipam import models, schemas

# TODO: raise HTTPException in routes, for better readability.


def check_supernet_validity(
    supernet: IPv4Network | IPv6Network, subnet: IPv4Network | IPv6Network
):
    """Check if supernet is valid.

    Args:
        db_supernet (models.Subnet): Supernet from the database.
        new_subnet (IPv4Network | IPv6Network): New subnet as a ip_network object.

    Raises:
        HTTPException: Raises if supernet doesn't cover subnet address range
            or if IP versions don't match.
    """
    try:
        if not supernet.supernet_of(subnet):  # type: ignore
            raise HTTPException(
                status_code=400,
                detail="Selected supernet is not supernet of this subnet",
            )
    except TypeError:
        raise HTTPException(
            status_code=400,
            detail="Supernet and subnet IP versions don't match",
        )


def check_subnet_overlap(
    db_subnets: list[models.Subnet],
    new_subnet: IPv4Network | IPv6Network,
):
    """_summary_

    Args:
        db_subnets (list[models.Subnet]): _description_
        new_subnet (IPv4Network | IPv6Network): _description_

    Raises:
        HTTPException: _description_
    """
    for db_subnet in db_subnets:
        extg_subnet = ip_network(db_subnet.ip)
        if new_subnet.overlaps(extg_subnet):
            raise HTTPException(
                status_code=400,
                detail=f"Subnet conflicts with {extg_subnet.exploded}",
            )


def check_subnet_overlap_supernet(
    db_subnets: list[models.Subnet],
    new_subnet: IPv4Network | IPv6Network,
    supernet_ip: str,
):
    """_summary_

    Args:
        db_subnets (list[models.Subnet]): _description_
        new_subnet (IPv4Network | IPv6Network): _description_
        supernet_ip (str): IP address of supernet

    Raises:
        HTTPException: _description_
    """
    for db_subnet in db_subnets:
        extg_subnet = ip_network(db_subnet.ip)
        if (
            new_subnet.overlaps(extg_subnet)
            and extg_subnet != ip_network(supernet_ip)
            or new_subnet == ip_network(supernet_ip)
        ):  # type: ignore
            raise HTTPException(
                status_code=400,
                detail=f"Subnet conflicts with {extg_subnet.exploded}",
            )


def create_reserved_host_list(
    subnet_id: int, subnet: IPv4Network | IPv6Network, reserve: int
) -> list[schemas.HostCreate]:
    """Create a list of hosts for host reservation.

    Args:
        subnet_id (int): Subnet id for the hosts.
        subnet (IPv4Network | IPv6Network): Subnet from where the IPs are generated.
        reserve (int): Number of hosts to reserve.

    Returns:
        list: List of valid HostCreate objects
    """
    first_n_ip = itertools.islice(subnet.hosts(), reserve)
    # [next(ip_network(new_db_subnet.ip).hosts()) for _ in range(reserve)]

    reserved_hosts = [
        schemas.HostCreate(
            name=uuid.uuid4().hex,
            subnet_id=subnet_id,
            ip=ip.exploded,
            description="Reserved by IPAM",
        )
        for ip in first_n_ip
    ]

    return reserved_hosts
