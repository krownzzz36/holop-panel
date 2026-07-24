#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔒 ДОСТУП «СВОЙ/ЧУЖОЙ» — бот работает только у участников нашей закрытой группы.

Идея Алексея (Енотоград), поддержана Максимом:
    «У скрипта есть полный доступ к телеге — можно после авторизации чекать,
     состоишь ли в данной группе. Если нет — дальше не работать.»
Сервер не нужен, чужие сессии нигде не хранятся — проверка идёт локально.

ЧЕСТНО: это «защита от дурака» (формулировка Алексея). Код лежит на машине
пользователя, кто умеет — вырежет проверку. Но от «переслал архив кому попало»
спасает, а это и есть главный риск: чем шире расходится, тем выше шанс, что
игра заметит и прикроет лавочку.

ПОЛЯРНОСТЬ ПРОВЕРКИ (важно): пускаем ТОЛЬКО если членство ПОДТВЕРЖДЕНО.
Любая невнятная ошибка = не подтвердили = не пускаем. Свободный проход даём
лишь при явных проблемах СЕТИ, чтобы обрыв связи не ронял ботов всем сразу.
"""

GROUP_ID = -5160104813                       # закрытая группа тестеров
GROUP_HINT = "Альфа-тестеры бота холопа"     # для понятного сообщения

DENY_MESSAGE = (
    f"🔒 ДОСТУП ЗАКРЫТ. Этот бот работает только у участников «{GROUP_HINT}». "
    f"Твой аккаунт в этой группе не найден. Если это ошибка — напиши владельцу, тебя добавят."
)

_NET_ERRORS = (ConnectionError, TimeoutError, OSError)


async def _probe_permissions(client):
    """Прямой способ: спросить свои права в группе. Не участник → упадёт."""
    await client.get_permissions(GROUP_ID, "me")
    return True


async def _probe_dialogs(client):
    """Запасной способ: группа должна быть в списке диалогов участника."""
    async for d in client.iter_dialogs():
        if d.id == GROUP_ID:
            return True
    return False


async def check_access(client):
    """(allowed, message). Пускаем только при ПОДТВЕРЖДЁННОМ членстве."""
    net_err = None
    for probe in (_probe_permissions, _probe_dialogs):
        try:
            if await probe(client):
                return True, ""
        except _NET_ERRORS as e:
            net_err = e                    # проблема связи — запомним, решим в конце
        except Exception:
            pass                           # этим способом не подтвердилось — пробуем следующий
    if net_err is not None:
        return True, (f"⚠️ нет связи для проверки доступа ({type(net_err).__name__}) — "
                      f"продолжаю работу")
    return False, DENY_MESSAGE


async def enforce_access(client, log_fn=print):
    """Проверить доступ и вернуть True/False. Сообщение печатаем через log_fn."""
    allowed, msg = await check_access(client)
    if msg:
        log_fn(msg)
    return allowed
