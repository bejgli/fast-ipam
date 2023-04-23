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


def create_address(db: Session, address: schemas.AddressCreate, subnet: models.Subnet):
    # TODO Create host with specified address. if address -> check available -> create
    # TODO Check if address is either ipv4 or ipv6 -> Now ipv4 is hardcoded
    used_hosts = [ip_address(addr.ip_v4) for addr in subnet.addresses]
    valid_hosts = [addr for addr in ip_network(str(subnet.ip_v4)).hosts()]

    first_addr = get_first_free(valid_hosts, used_hosts)

    if not first_addr:
        return None  # TODO ERROR HANDLING Maybe raise here and catch in route

    # TODO Check if address is either ipv4 or ipv6
    db_address = models.Address(**address.dict(), ip_v4=first_addr)

    db.add(db_address)
    db.commit()
    db.refresh(db_address)

    return db_address


def get_addresses(db: Session, skip: int | None, limit: int | None):
    return db.query(models.Address).offset(skip).limit(limit).all()


def get_address_by_id(db: Session, address_id: int):
    return db.query(models.Address).filter(models.Address.id == address_id).first()


def get_address_by_name(db: Session, address_name: str):
    return db.query(models.Address).filter(models.Address.name == address_name).first()


def delete_host_by_id(db: Session, host_id: int):
    db_host = db.query(models.Address).filter(models.Address.id == host_id)
    db_host.delete()
    db.commit()

    return db_host
