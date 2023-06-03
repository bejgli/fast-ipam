from sqlalchemy.orm import Session
from ipaddress import ip_network, ip_address, IPv4Address, IPv6Address
from itertools import zip_longest

from fastipam import models, schemas


# Utils
def get_first_free(
    values: list[IPv4Address | IPv6Address], reference: list[IPv4Address | IPv6Address]
) -> str | None:
    """Find the first available address in a subnet,
    by sorting the used addresses and comparing them to the valid ones.

    Args:
        values (list[IPv4Address  |  IPv6Address]): List of available IP addresses.
        reference (list[IPv4Address  |  IPv6Address]): List of used IP addresses.

    Returns:
        str | None: First available address in exploded form or None.
    """
    for v, r in zip_longest(values, sorted(reference)):
        if v != r:
            return v.exploded
    return None  # TODO ERROR HANDLING Maybe raise error here


def create_host(db: Session, host: schemas.HostCreate, subnet: models.Subnet):
    # TODO Create host with specified address. if address -> check available -> create
    # TODO Check if address is either ipv4 or ipv6 -> Now ipv4 is hardcoded
    used_hosts = [ip_address(host.ip) for host in subnet.hosts]
    valid_hosts = [host for host in ip_network(str(subnet.ip)).hosts()]

    first_addr = get_first_free(valid_hosts, used_hosts)

    if not first_addr:
        return None  # TODO ERROR HANDLING Maybe raise here and catch in route

    # TODO Check if address is either ipv4 or ipv6
    db_host = models.Host(**host.dict(), ip=first_addr)

    db.add(db_host)
    db.commit()
    db.refresh(db_host)

    return db_host


def get_hosts(
    db: Session, skip: int | None, limit: int | None, subnet_name: str | None
):
    if subnet_name:
        db_hosts = (
            db.query(models.Host)
            .join(models.Host.subnet)
            .filter(models.Subnet.name == subnet_name)
            .offset(skip)
            .limit(limit)
        )
    else:
        db_hosts = db.query(models.Host).offset(skip).limit(limit)
    return db_hosts.all()


def get_host_by_id(db: Session, host_id: int):
    return db.query(models.Host).filter(models.Host.id == host_id).first()


def get_host_by_name(db: Session, host_name: str):
    return db.query(models.Host).filter(models.Host.name == host_name).first()


def delete_host(db: Session, host_id: int):
    db_host = db.query(models.Host).filter(models.Host.id == host_id)
    db_host.delete()
    db.commit()

    return None


def update_host(db: Session, host: schemas.HostUpdate, host_id: int):
    db_host = db.query(models.Host).filter(models.Host.id == host_id).first()

    # Update only if values are not None
    for k, v in host.dict().items():
        if v:
            setattr(db_host, k, v)

    db.commit()
    db.refresh(db_host)

    return db_host
