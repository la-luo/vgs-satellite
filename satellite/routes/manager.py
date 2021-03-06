import logging
import re
from typing import List

from .expressions import CompositeExpression, ExpressionError
from ..db import get_session, update_model
from ..db.models.route import Route, RuleEntry
from ..operations.pipeline import build_pipeline


logger = logging.getLogger()


class EntityNotFound(Exception):
    pass


class InvalidRouteConfiguration(Exception):
    pass


def get_all() -> List[Route]:
    session = get_session()
    # Hack to handle transaction isolation. Proper fix is needed (SAT-148).
    session.commit()
    return session.query(Route).all()


def get_all_by_type(is_outbound: bool) -> List[Route]:
    return [route for route in get_all() if route.is_outbound() is is_outbound]


def get(route_id: str) -> Route:
    return get_session().query(Route).filter(Route.id == route_id).first()


def create(route_data: dict, store: bool = True) -> Route:
    route = Route(
        **{
            **route_data,
            'rule_entries_list': [
                RuleEntry(**rule_entry)
                for rule_entry in route_data.get('rule_entries_list', [])
            ],
        }
    )

    check_route(route)

    if store:
        session = get_session()
        try:
            session.add(route)
            session.commit()
        except Exception:
            session.rollback()
            raise

    return route


def update(route_id: str, route_data: dict) -> Route:
    route = get(route_id)
    if not route:
        # Have to allow route creation via update since currently FE uses the
        # update endpoint for routes import.
        return create({**route_data, 'id': route_id})

    update_model(route, route_data)

    session = get_session()

    # Do filters CRUD only if they are mentioned in the request
    if 'rule_entries_list' in route_data:
        current_filters = {entry.id: entry for entry in route.rule_entries_list}
        target_filters = []
        target_filters_ids = set()
        filters_data = route_data['rule_entries_list'] or []
        for filter_data in filters_data:
            filter = None
            filter_id = filter_data.get('id')
            if filter_id is not None:
                filter = current_filters.get(filter_id)
            if filter:
                update_model(filter, filter_data, ['id'])
            else:
                filter = RuleEntry(**filter_data)
            target_filters.append(filter)
            target_filters_ids.add(filter.id)

        for filter in route.rule_entries_list:
            if filter.id not in target_filters_ids:
                session.delete(filter)

        route.rule_entries_list = target_filters

    check_route(route)

    try:
        session.commit()
    except Exception:
        session.rollback()
        raise

    return route


def delete(route_id: str):
    route = get(route_id)
    if not route:
        raise EntityNotFound(route_id)
    session = get_session()
    session.delete(route)
    session.commit()


def replace(routes_data: List[dict]) -> List[Route]:
    routes = [create(route_data, False) for route_data in routes_data]

    session = get_session()
    with session.begin_nested():
        session.query(Route).delete()
        session.add_all(routes)

    return routes


def check_filter(fltr: RuleEntry):
    if fltr.expression_snapshot:
        try:
            CompositeExpression.build(fltr.expression_snapshot)
        except ExpressionError as exc:
            raise InvalidRouteConfiguration(f'Invalid expression: {exc}')

    if fltr.has_operations:
        try:
            build_pipeline(fltr)
        except Exception as exc:
            logger.exception(exc)
            raise InvalidRouteConfiguration(f'Invalid operations: {exc}') from exc


def check_route(route: Route):
    if route.is_outbound:
        try:
            re.compile(route.host_endpoint)
        except re.error as exc:
            raise InvalidRouteConfiguration(
                f'Invalid host pattern {route.host_endpoint}: {exc}'
            ) from exc

    for rule in route.rule_entries_list:
        check_filter(rule)
