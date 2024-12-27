import logging
from itertools import islice
import concurrent.futures

import requests

from ..models import Security, TradeHistory


logger = logging.getLogger(__name__)


def import_securities_and_trade_history():
    url = "https://iss.moex.com/iss/engines/stock/markets/shares/securities.json?iss.meta=off"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        moex_data = response.json()
        logger.debug("Запрос прошел успешно")
    except requests.RequestException as e:
        logger.error(f"Ошибка загрузки данных: {e}")
        return

    securities = moex_data.get("securities", {})
    columns = securities.get("columns", [])
    data = securities.get("data", [])

    existing_securities = {s.secid: s for s in Security.objects.only("secid")}

    new_objects = []
    updated_objects = []

    for row in islice(data, 100):
        security_data = dict(zip(columns, row))
        secid = security_data.get("SECID")

        if secid in existing_securities:
            obj = existing_securities[secid]
            obj.regnumber = security_data.get("REGNUMBER")
            obj.name = security_data.get("SECNAME")
            obj.emitent_title = security_data.get("SHORTNAME")
            updated_objects.append(obj)
        else:
            new_objects.append(
                Security(
                    secid=secid,
                    regnumber=security_data.get("REGNUMBER"),
                    name=security_data.get("SECNAME"),
                    emitent_title=security_data.get("SHORTNAME"),
                )
            )

    Security.objects.bulk_create(new_objects, batch_size=500)
    Security.objects.bulk_update(updated_objects, ["regnumber", "name", "emitent_title"], batch_size=500)
    logger.debug("Данные о ценных бумагах сохранены в бд")

    existing_history = set(f"{h.numtrades}-{h.security_id}" for h in TradeHistory.objects.only("numtrades", "security"))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(import_trade_history, security, existing_history) for security in new_objects + updated_objects]

        full_history = []
        for future in concurrent.futures.as_completed(futures):
            full_history.extend(future.result())

    TradeHistory.objects.bulk_create(full_history)
    logger.debug("История для ценных бумаг была добавлена")


def import_trade_history(security: Security, existing_history: set):
    url = f"https://iss.moex.com/iss/engines/stock/markets/shares/securities/{security.secid}/history.json?iss.meta=off"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        moex_data = response.json()
    except requests.RequestException as e:
        logger.error(f"Ошибка загрузки данных для {security.secid}: {e}")
        return []
    except ValueError as e:
        logger.error(f"Ошибка парсинга JSON для {security.secid}: {e}")
        return []

    sec_data = moex_data.get("securities", {})
    sec_columns = sec_data.get("columns", [])
    sec_rows = sec_data.get("data", [])

    market_data = moex_data.get("marketdata", {})
    market_columns = market_data.get("columns", [])
    market_rows = market_data.get("data", [])

    trade_history_to_create = []
    for sec_row in sec_rows:
        sec_parsed = dict(zip(sec_columns, sec_row))
        tradedate = sec_parsed.get("PREVDATE")

        for market_row in market_rows:
            market_parsed = dict(zip(market_columns, market_row))
            numtrades = market_parsed.get("NUMTRADES")
            open_price = market_parsed.get("OPEN")

            trade_key = f"{numtrades}-{security.id}"

            if trade_key not in existing_history:
                existing_history.add(trade_key)
                trade_history_to_create.append(
                    TradeHistory(
                        security=security,
                        tradedate=tradedate,
                        numtrades=numtrades,
                        open=open_price,
                    )
                )

    return trade_history_to_create
